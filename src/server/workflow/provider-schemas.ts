import { z } from "zod";
import { ResearchResultSchema, SourceSchema } from "@/shared/contracts-v2";

// OpenAI requires every wire field; optional domain values are represented by null.
const sourceWireFields = {
  publishedAt: z.string().nullable(),
  closingAt: z.string().nullable(),
};
const sourceVariants = SourceSchema.unwrap().options;
const SourceModelOutputSchema = z.discriminatedUnion("kind", [
  sourceVariants[0].extend(sourceWireFields),
  sourceVariants[1].extend({
    ...sourceWireFields,
    url: sourceVariants[1].shape.url.unwrap().nullable(),
  }),
]);
export const ResearchModelOutputSchema = ResearchResultSchema.unwrap().extend({
  sources: z.array(SourceModelOutputSchema),
});
export type ResearchModelOutput = z.infer<typeof ResearchModelOutputSchema>;

export function normalizeResearchModelOutput(output: ResearchModelOutput) {
  return ResearchResultSchema.parse({
    ...output,
    sources: output.sources.map(({ publishedAt, closingAt, url, ...source }) => ({
      ...source,
      ...(publishedAt === null ? {} : { publishedAt }),
      ...(closingAt === null ? {} : { closingAt }),
      ...(url === null ? {} : { url }),
    })),
  });
}
