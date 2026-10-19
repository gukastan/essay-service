import { z } from "zod";

const requiredText = z.string().refine((value) => value.trim().length > 0, "필수 항목입니다.");
export const draftRequestSchema = z.object({
  company: requiredText,
  role: requiredText,
  question: requiredText,
  experience: requiredText,
});
export type DraftRequest = Readonly<z.infer<typeof draftRequestSchema>>;
export type DraftField = keyof DraftRequest;
export const fieldErrorsSchema = z.object({
  company: z.string().optional(),
  role: z.string().optional(),
  question: z.string().optional(),
  experience: z.string().optional(),
});
export type FieldErrors = z.infer<typeof fieldErrorsSchema>;
const generationCalls = z.union([z.literal(1), z.literal(2)]);
export const draftResponseSchema = z.discriminatedUnion("status", [
  z.object({
    status: z.literal("ready"),
    draft: z.string(),
    characterCount: z.number().int(),
    generationCalls,
  }),
  z.object({ status: z.literal("needs_input"), message: z.string(), generationCalls }),
  z.object({
    status: z.literal("error"),
    code: z.enum([
      "INVALID_INPUT",
      "LENGTH_RETRY_EXHAUSTED",
      "MODEL_ERROR",
      "MODEL_TIMEOUT",
      "CONFIG_ERROR",
    ]),
    message: z.string(),
    fieldErrors: fieldErrorsSchema.optional(),
  }),
]);
export type DraftResponse = Readonly<z.infer<typeof draftResponseSchema>>;

export function assertNever(value: never): never {
  throw new TypeError(`Unexpected variant: ${String(value)}`);
}
