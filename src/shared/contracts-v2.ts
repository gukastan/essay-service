import { z } from "zod";
import { countCharacters } from "./characters";

const text = z.string().refine((value) => value.trim().length > 0, "Required text");
const boundedText = (limit: number) => text.refine((value) => Array.from(value).length <= limit);
export const HttpUrlSchema = z.url({ protocol: /^https?$/ }).max(2048);
const optionalText = (schema: z.ZodType<string>) =>
  z.preprocess(
    (value) => (typeof value === "string" && value.trim() === "" ? undefined : value),
    schema.optional(),
  );
export const DraftRequestV2Schema = z
  .strictObject({
    company: boundedText(120),
    role: boundedText(160),
    question: boundedText(3000),
    experience: boundedText(12000),
    jobPostingUrl: optionalText(HttpUrlSchema),
    jobPostingText: optionalText(boundedText(16000)),
  })
  .readonly();
export type DraftRequestV2 = z.infer<typeof DraftRequestV2Schema>;
export const RequestIdSchema = z.uuid().brand<"RequestId">();
export const SourceIdSchema = text.brand<"SourceId">();
export const CompanyFactIdSchema = text.brand<"CompanyFactId">();
export const JobRequirementIdSchema = text.brand<"JobRequirementId">();
export const ExperienceEvidenceIdSchema = text.brand<"ExperienceEvidenceId">();
export const ClaimIdSchema = text.brand<"ClaimId">();
export type RequestId = z.infer<typeof RequestIdSchema>;
export type SourceId = z.infer<typeof SourceIdSchema>;
export type CompanyFactId = z.infer<typeof CompanyFactIdSchema>;
export type JobRequirementId = z.infer<typeof JobRequirementIdSchema>;
export type ExperienceEvidenceId = z.infer<typeof ExperienceEvidenceIdSchema>;
export type ClaimId = z.infer<typeof ClaimIdSchema>;
const sourceFields = {
  id: SourceIdSchema,
  title: text,
  checkedAt: z.iso.datetime({ offset: true }),
  publishedAt: text.optional(),
  closingAt: text.optional(),
  excerpt: text,
};
export const SourceSchema = z
  .discriminatedUnion("kind", [
    z.strictObject({ ...sourceFields, kind: z.literal("official"), url: HttpUrlSchema }),
    z.strictObject({
      ...sourceFields,
      kind: z.literal("user_provided"),
      url: HttpUrlSchema.optional(),
    }),
  ])
  .readonly();
export type Source = z.infer<typeof SourceSchema>;
export const CompanyFactSchema = z
  .strictObject({
    id: CompanyFactIdSchema,
    text,
    sourceIds: z.array(SourceIdSchema).min(1).readonly(),
  })
  .readonly();
export const JobRequirementSchema = z
  .strictObject({
    id: JobRequirementIdSchema,
    text,
    sourceIds: z.array(SourceIdSchema).min(1).readonly(),
  })
  .readonly();
export const ExperienceEvidenceSchema = z
  .strictObject({
    id: ExperienceEvidenceIdSchema,
    quote: text,
    start: z.number().int().nonnegative(),
    end: z.number().int().positive(),
    category: z.enum(["action", "result", "learning", "context"]),
  })
  .refine((value) => value.end > value.start)
  .readonly();
export type ExperienceEvidence = z.infer<typeof ExperienceEvidenceSchema>;
export const ClaimSchema = z
  .strictObject({
    id: ClaimIdSchema,
    text,
    kind: z.enum(["user_fact", "company_fact", "interpretation", "future_plan"]),
    evidenceIds: z
      .array(z.union([ExperienceEvidenceIdSchema, CompanyFactIdSchema, JobRequirementIdSchema]))
      .readonly(),
  })
  .refine(
    (value) => !["user_fact", "company_fact"].includes(value.kind) || value.evidenceIds.length > 0,
  )
  .readonly();
export const FitReasonSchema = z
  .strictObject({
    experienceEvidenceIds: z.array(ExperienceEvidenceIdSchema).min(1).readonly(),
    jobRequirementIds: z.array(JobRequirementIdSchema).min(1).readonly(),
    reason: text,
  })
  .readonly();
export const ReviewIssueSchema = z
  .strictObject({
    code: text,
    claimIds: z.array(ClaimIdSchema).readonly(),
    reason: text,
    action: z.enum(["revise", "needs_input"]),
  })
  .readonly();
export const ResearchResultSchema = z
  .strictObject({
    resolvedCompany: text.nullable(),
    sources: z.array(SourceSchema).readonly(),
    companyFacts: z.array(CompanyFactSchema).readonly(),
    jobRequirements: z.array(JobRequirementSchema).readonly(),
    gaps: z.array(text).readonly(),
  })
  .readonly();
export type ResearchResult = z.infer<typeof ResearchResultSchema>;
export const AnalysisResultSchema = z
  .strictObject({
    questionRequirements: z
      .array(z.strictObject({ id: text.brand<"QuestionRequirementId">(), text }).readonly())
      .readonly(),
    experienceEvidence: z.array(ExperienceEvidenceSchema).readonly(),
    gaps: z.array(text).readonly(),
  })
  .readonly();
export type AnalysisResult = z.infer<typeof AnalysisResultSchema>;
export const WriterResultSchema = z
  .strictObject({
    draft: text,
    claimMap: z.array(ClaimSchema).readonly(),
    fitReasons: z.array(FitReasonSchema).readonly(),
  })
  .readonly();
export type WriterResult = z.infer<typeof WriterResultSchema>;
export const ReviewResultSchema = z
  .strictObject({
    verdict: z.enum(["pass", "revise", "needs_input"]),
    issues: z.array(ReviewIssueSchema).readonly(),
    revisionInstructions: z.array(text).readonly(),
  })
  .refine((value) => value.verdict !== "pass" || value.issues.length === 0)
  .readonly();
export type ReviewResult = z.infer<typeof ReviewResultSchema>;
export const RevisionCountSchema = z.union([z.literal(0), z.literal(1)]);
export const UsageV2Schema = z
  .strictObject({
    modelCalls: z.number().int().min(0).max(6),
    revisionCount: RevisionCountSchema,
  })
  .readonly();
export const DraftResponseV2Schema = z
  .discriminatedUnion("status", [
    z
      .strictObject({
        status: z.literal("ready"),
        requestId: RequestIdSchema,
        draft: text,
        characterCount: z.number().int().min(801).max(1000),
        sources: z.array(SourceSchema).readonly(),
        evidence: z
          .strictObject({
            companyFacts: z.array(CompanyFactSchema).readonly(),
            jobRequirements: z.array(JobRequirementSchema).readonly(),
            experienceEvidence: z.array(ExperienceEvidenceSchema).readonly(),
            claimMap: z.array(ClaimSchema).readonly(),
            fitReasons: z.array(FitReasonSchema).readonly(),
          })
          .readonly(),
        reviewSummary: z.literal("생성 당시 검토 통과"),
        usage: UsageV2Schema,
      })
      .refine((value) => countCharacters(value.draft) === value.characterCount),
    z.strictObject({
      status: z.literal("needs_input"),
      requestId: RequestIdSchema,
      message: text,
      missingFields: z
        .array(
          z.enum(["company", "role", "question", "experience", "jobPostingUrl", "jobPostingText"]),
        )
        .min(1)
        .readonly(),
      questions: z.array(text).min(1).readonly(),
      reasonCode: z.enum([
        "COMPANY_AMBIGUOUS",
        "JOB_EVIDENCE_MISSING",
        "EXPERIENCE_INSUFFICIENT",
        "EVIDENCE_INSUFFICIENT",
      ]),
    }),
    z.strictObject({
      status: z.literal("error"),
      requestId: RequestIdSchema,
      message: text,
      code: z.enum([
        "INVALID_INPUT",
        "V2_DISABLED",
        "LENGTH_VALIDATION_FAILED",
        "QUALITY_CHECK_FAILED",
        "CONFIG_ERROR",
        "MODEL_ERROR",
        "SEARCH_ERROR",
        "INVALID_RESPONSE",
        "TIMEOUT",
        "CANCELLED",
        "BUDGET_EXCEEDED",
      ]),
    }),
  ])
  .readonly();
export type DraftResponseV2 = z.infer<typeof DraftResponseV2Schema>;
