import { describe, expect, it } from "vitest";
import {
  ClaimSchema,
  DraftRequestV2Schema,
  DraftResponseV2Schema,
  ExperienceEvidenceSchema,
  SourceSchema,
} from "./contracts-v2";

const input = { company: "회사", role: "직무", question: "문항", experience: " 원문\r\n경험 " };
const requestId = "60b490f2-3536-4b19-a89e-80808cd7cdb9";
describe("v2 boundary contracts", () => {
  it("preserves experience offsets and omits empty optional material", () => {
    const result = DraftRequestV2Schema.parse({
      ...input,
      jobPostingUrl: "  ",
      jobPostingText: "",
    });
    expect(result.experience).toBe(input.experience);
    expect(result.jobPostingUrl).toBeUndefined();
    expect(result.jobPostingText).toBeUndefined();
    expect(Object.isFrozen(result)).toBe(true);
  });
  it.each(["company", "role", "question", "experience"])("rejects blank %s", (field) => {
    expect(DraftRequestV2Schema.safeParse({ ...input, [field]: " \n" }).success).toBe(false);
  });
  it.each([
    ["company", 120],
    ["role", 160],
    ["question", 3000],
    ["experience", 12000],
    ["jobPostingText", 16000],
  ])("measures %s bounds in Unicode code points", (field, limit) => {
    const length = Number(limit);
    expect(DraftRequestV2Schema.safeParse({ ...input, [field]: "😀".repeat(length) }).success).toBe(
      true,
    );
    expect(
      DraftRequestV2Schema.safeParse({ ...input, [field]: "😀".repeat(length + 1) }).success,
    ).toBe(false);
  });
  it("rejects unsafe URL protocols and unknown request fields", () => {
    expect(
      DraftRequestV2Schema.safeParse({ ...input, jobPostingUrl: "file:///etc/passwd" }).success,
    ).toBe(false);
    expect(DraftRequestV2Schema.safeParse({ ...input, secret: "x" }).success).toBe(false);
  });
  it("requires official source URL and excerpt, while accepting user supplied text", () => {
    const source = { id: "s1", title: "공고", checkedAt: "2026-10-19T08:00:00Z", excerpt: "업무" };
    expect(SourceSchema.safeParse({ ...source, kind: "official" }).success).toBe(false);
    expect(
      SourceSchema.safeParse({
        ...source,
        kind: "official",
        url: "https://example.com",
        excerpt: "",
      }).success,
    ).toBe(false);
    expect(SourceSchema.safeParse({ ...source, kind: "user_provided" }).success).toBe(true);
  });
  it("rejects inverted quote ranges and unsupported factual claims", () => {
    expect(
      ExperienceEvidenceSchema.safeParse({
        id: "e1",
        quote: "경험",
        start: 4,
        end: 2,
        category: "action",
      }).success,
    ).toBe(false);
    expect(
      ClaimSchema.safeParse({ id: "c1", text: "성과", kind: "user_fact", evidenceIds: [] }).success,
    ).toBe(false);
  });
  it("accepts needs_input without a draft and rejects draft leakage", () => {
    const response = {
      status: "needs_input",
      requestId,
      message: "경험 필요",
      missingFields: ["experience"],
      questions: ["어떤 경험인가요?"],
      reasonCode: "EXPERIENCE_INSUFFICIENT",
    };
    expect(DraftResponseV2Schema.safeParse(response).success).toBe(true);
    expect(DraftResponseV2Schema.safeParse({ ...response, draft: "leak" }).success).toBe(false);
    expect(
      DraftResponseV2Schema.safeParse({
        status: "error",
        requestId,
        code: "MODEL_ERROR",
        message: "실패",
        raw: "secret",
      }).success,
    ).toBe(false);
  });
  it.each([800, 801, 1000, 1001])("validates ready length %i and reported count", (length) => {
    const response = {
      status: "ready",
      requestId,
      draft: "가".repeat(length),
      characterCount: length,
      sources: [],
      evidence: {
        companyFacts: [],
        jobRequirements: [],
        experienceEvidence: [],
        claimMap: [],
        fitReasons: [],
      },
      reviewSummary: "생성 당시 검토 통과",
      usage: { modelCalls: 4, revisionCount: 0 },
    };
    expect(DraftResponseV2Schema.safeParse(response).success).toBe(length >= 801 && length <= 1000);
    expect(
      DraftResponseV2Schema.safeParse({ ...response, characterCount: length + 1 }).success,
    ).toBe(false);
  });
});
