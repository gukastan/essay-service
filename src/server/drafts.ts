import OpenAI from "openai";
import { z } from "zod";
import { countCharacters, isValidDraftLength, normalizeLineEndings } from "@/shared/characters";
import { assertNever, type DraftRequest, type DraftResponse } from "@/shared/contracts";
import type { ModelConfig } from "./config";
import { generateModelOutput, MODEL_TIMEOUT_MS, type ModelRequest } from "./model";

const nonemptyText = z.string().refine((value) => value.trim().length > 0);
const modelOutputSchema = z.discriminatedUnion("status", [
  z
    .object({ status: z.literal("draft"), draft: nonemptyText, message: z.null().optional() })
    .strict(),
  z
    .object({ status: z.literal("needs_input"), message: nonemptyText, draft: z.null().optional() })
    .strict(),
]);

class ModelTimeoutError extends Error {}

export type DraftOutcome = { readonly httpStatus: number; readonly body: DraftResponse };

export async function createDraft(input: DraftRequest, config: ModelConfig): Promise<DraftOutcome> {
  let rewrite: ModelRequest["rewrite"];
  for (const generationCalls of [1, 2] as const) {
    const controller = new AbortController();
    let timer: ReturnType<typeof setTimeout> | undefined;
    try {
      const timeout = new Promise<never>((_resolve, reject) => {
        timer = setTimeout(() => {
          reject(new ModelTimeoutError());
          controller.abort();
        }, MODEL_TIMEOUT_MS);
      });
      const request: ModelRequest = rewrite ? { input, rewrite } : { input };
      const raw = await Promise.race([
        generateModelOutput(request, controller.signal, config),
        timeout,
      ]);
      const output = modelOutputSchema.safeParse(raw);
      if (!output.success) return modelFailure();
      switch (output.data.status) {
        case "needs_input":
          return {
            httpStatus: 200,
            body: { status: "needs_input", message: output.data.message, generationCalls },
          };
        case "draft": {
          const draft = normalizeLineEndings(output.data.draft);
          const characterCount = countCharacters(draft);
          if (isValidDraftLength(characterCount)) {
            return {
              httpStatus: 200,
              body: { status: "ready", draft, characterCount, generationCalls },
            };
          }
          rewrite = { draft, characterCount };
          break;
        }
        default:
          assertNever(output.data);
      }
    } catch (error) {
      if (error instanceof ModelTimeoutError || error instanceof OpenAI.APIConnectionTimeoutError) {
        return {
          httpStatus: 504,
          body: {
            status: "error",
            code: "MODEL_TIMEOUT",
            message: "초안 생성 시간이 초과되었습니다. 잠시 후 다시 시도해 주세요.",
          },
        };
      }
      // no-excuse-ok: catch — provider boundary must redact all foreign error details.
      return modelFailure();
    } finally {
      clearTimeout(timer);
    }
  }
  return {
    httpStatus: 422,
    body: {
      status: "error",
      code: "LENGTH_RETRY_EXHAUSTED",
      message:
        "한 번 수정한 뒤에도 801~1,000자를 맞추지 못했습니다. 경험을 보완한 뒤 다시 시도해 주세요.",
    },
  };
}

function modelFailure(): DraftOutcome {
  return {
    httpStatus: 502,
    body: {
      status: "error",
      code: "MODEL_ERROR",
      message: "초안을 생성하지 못했습니다. 잠시 후 다시 시도해 주세요.",
    },
  };
}
