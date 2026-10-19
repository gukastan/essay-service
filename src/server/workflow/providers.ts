import OpenAI from "openai";
import { zodTextFormat } from "openai/helpers/zod";
import { z } from "zod";
import { DraftRequestV2Schema, HttpUrlSchema } from "@/shared/contracts-v2";
import type { ModelConfig } from "../config";
import type { ExecutionBudget, OperationContext } from "./budget";

export const ROLE_OUTPUT_TOKENS = {
  research: 3000,
  analysis: 3000,
  writer: 4000,
  review: 2000,
} as const;
export type ModelRole = keyof typeof ROLE_OUTPUT_TOKENS;
export type StructuredModelRequest<T> = {
  readonly role: ModelRole;
  readonly instructions: string;
  readonly input: string;
  readonly schema: z.ZodType<T>;
};
export type ModelResult<T> = {
  readonly value: T;
  readonly usage: { readonly inputTokens: number; readonly outputTokens: number } | null;
};
export interface ModelProvider {
  generate<T>(request: StructuredModelRequest<T>, budget: ExecutionBudget): Promise<ModelResult<T>>;
}

export class ProviderResponseError extends Error {
  readonly name = "ProviderResponseError";
  constructor(readonly code: "incomplete" | "invalid_output") {
    super(`Provider response: ${code}`);
  }
}

export function createOpenAIModelProvider(config: ModelConfig): ModelProvider {
  const client = new OpenAI({ apiKey: config.apiKey, maxRetries: 0, timeout: 30_000 });
  return {
    async generate<T>(request: StructuredModelRequest<T>, budget: ExecutionBudget) {
      // Build the supported strict wire schema before reserving a network call.
      const format = zodTextFormat(request.schema, `essay_v2_${request.role}`);
      return budget.run(
        "model",
        async ({ signal, timeoutMs }) => {
          const response = await client.responses.create(
            {
              model: config.model,
              reasoning: { effort: "low" },
              store: false,
              max_output_tokens: ROLE_OUTPUT_TOKENS[request.role],
              instructions: request.instructions,
              input: request.input,
              text: { format },
            },
            { signal, timeout: timeoutMs, maxRetries: 0 },
          );
          if (response.status !== "completed") throw new ProviderResponseError("incomplete");
          try {
            const raw: unknown = JSON.parse(response.output_text);
            const value = request.schema.parse(raw);
            return {
              value,
              usage: response.usage
                ? {
                    inputTokens: response.usage.input_tokens,
                    outputTokens: response.usage.output_tokens,
                  }
                : null,
            };
          } catch (error) {
            if (error instanceof SyntaxError || error instanceof z.ZodError) {
              // Do not expose model output or user evidence through parser errors.
              throw new ProviderResponseError("invalid_output");
            }
            throw error;
          }
        },
        request.role === "research" ? "research" : "request",
      );
    },
  };
}

const searchInputSchema = z.object({
  company: DraftRequestV2Schema.unwrap().shape.company,
  role: DraftRequestV2Schema.unwrap().shape.role,
});
export type SearchInput = Readonly<z.infer<typeof searchInputSchema>>;
const searchHitSchema = z.object({ title: z.string(), url: HttpUrlSchema, snippet: z.string() });
export type SearchHit = Readonly<z.infer<typeof searchHitSchema>>;
const pageSchema = z.object({
  url: HttpUrlSchema,
  text: z.string(),
  checkedAt: z.iso.datetime(),
});
export type ReadPage = Readonly<z.infer<typeof pageSchema>>;

// Implementations must perform one counted operation, with retries disabled.
// A production page reader must enforce DNS/redirect safety and 1 MiB streaming
// bounds. This foundation deliberately supplies no unverified network reader.
export interface SearchProvider {
  search(input: SearchInput, context: OperationContext): Promise<readonly SearchHit[]>;
}
export interface PageReader {
  read(url: string, context: OperationContext): Promise<ReadPage>;
}
export type ResearchProviders = {
  readonly search: SearchProvider;
  readonly pages: PageReader;
};

export function createResearchTools(providers: ResearchProviders, budget: ExecutionBudget) {
  return {
    search(input: SearchInput): Promise<readonly SearchHit[]> {
      // Project to public company/role fields even if passed a wider request object.
      const publicInput = searchInputSchema.parse({ company: input.company, role: input.role });
      return budget.run("search", async (context) =>
        z.array(searchHitSchema).parse(await providers.search.search(publicInput, context)),
      );
    },
    read(url: string): Promise<ReadPage> {
      const parsedUrl = HttpUrlSchema.parse(url);
      return budget.run("page", async (context) =>
        pageSchema.parse(await providers.pages.read(parsedUrl, context)),
      );
    },
  };
}
