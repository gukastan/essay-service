import { readModelConfig } from "@/server/config";
import { createDraft } from "@/server/drafts";
import { type DraftResponse, draftRequestSchema, type FieldErrors } from "@/shared/contracts";

export const runtime = "nodejs";
export const maxDuration = 65;

export async function POST(request: Request): Promise<Response> {
  let body: unknown;
  try {
    body = await request.json();
  } catch {
    // no-excuse-ok: catch — malformed or unreadable request bodies are input failures.
    return invalidInput({});
  }
  const parsed = draftRequestSchema.safeParse(body);
  if (!parsed.success) {
    const fieldErrors: FieldErrors = {};
    for (const issue of parsed.error.issues) {
      const field = issue.path[0];
      if (
        field === "company" ||
        field === "role" ||
        field === "question" ||
        field === "experience"
      ) {
        fieldErrors[field] = "내용을 입력해 주세요.";
      }
    }
    return invalidInput(fieldErrors);
  }
  const config = readModelConfig();
  if (!config.success) {
    return Response.json(
      {
        status: "error",
        code: "CONFIG_ERROR",
        message: "모델 설정이 필요합니다. 서버의 API 키와 모델명을 확인해 주세요.",
      } satisfies DraftResponse,
      { status: 500 },
    );
  }
  const result = await createDraft(parsed.data, config.data);
  return Response.json(result.body, { status: result.httpStatus });
}

function invalidInput(fieldErrors: FieldErrors): Response {
  return Response.json(
    {
      status: "error",
      code: "INVALID_INPUT",
      message: "기업명, 직무, 문항과 경험을 모두 올바르게 입력해 주세요.",
      fieldErrors,
    } satisfies DraftResponse,
    { status: 400 },
  );
}
