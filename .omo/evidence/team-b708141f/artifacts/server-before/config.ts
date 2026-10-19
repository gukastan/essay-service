import { z } from "zod";

export const modelConfigSchema = z.object({
  apiKey: z.string().trim().min(1),
  model: z
    .string()
    .trim()
    .min(1)
    .regex(/^[a-zA-Z0-9._:-]+$/),
});
export type ModelConfig = Readonly<z.infer<typeof modelConfigSchema>>;

export function readModelConfig() {
  return modelConfigSchema.safeParse({
    apiKey: process.env["OPENAI_API_KEY"],
    model: process.env["OPENAI_MODEL"],
  });
}
