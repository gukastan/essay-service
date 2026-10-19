import { END, START, StateGraph } from "@langchain/langgraph";
import { describe, expect, it } from "vitest";
import {
  AnalysisResultSchema,
  DraftRequestV2Schema,
  RequestIdSchema,
  ResearchResultSchema,
} from "@/shared/contracts-v2";
import { WorkflowState, WorkflowStateError } from "./state";

const initial = {
  requestId: RequestIdSchema.parse("60b490f2-3536-4b19-a89e-80808cd7cdb9"),
  inputSnapshot: DraftRequestV2Schema.parse({
    company: "회사",
    role: "직무",
    question: "문항",
    experience: "경험",
  }),
  deadline: Date.now() + 180000,
};
const research = ResearchResultSchema.parse({
  resolvedCompany: null,
  sources: [],
  companyFacts: [],
  jobRequirements: [],
  gaps: ["공고 필요"],
});
const analysis = AnalysisResultSchema.parse({
  questionRequirements: [],
  experienceEvidence: [],
  gaps: ["경험 필요"],
});

describe("real LangGraph foundation", () => {
  it("initializes every declared state channel at runtime", async () => {
    const graph = new StateGraph(WorkflowState)
      .addNode("identity", () => ({}))
      .addEdge(START, "identity")
      .addEdge("identity", END)
      .compile();
    expect(await graph.invoke(initial)).toEqual({
      ...initial,
      research: null,
      analysis: null,
      draft: null,
      claimMap: [],
      fitReasons: [],
      deterministicChecks: null,
      review: null,
      revisionCount: 0,
      usage: { modelCalls: 0, searches: 0, pageReads: 0, nativeToolCallsReserved: 0 },
      outcome: null,
    });
  });
  it("rejects a revision rollback with a typed state error", async () => {
    const graph = new StateGraph(WorkflowState)
      .addNode("revise", (): { readonly revisionCount: 1 } => ({ revisionCount: 1 }))
      .addNode("rollback", (): { readonly revisionCount: 0 } => ({ revisionCount: 0 }))
      .addEdge(START, "revise")
      .addEdge("revise", "rollback")
      .addEdge("rollback", END)
      .compile();
    await expect(graph.invoke(initial)).rejects.toBeInstanceOf(WorkflowStateError);
  });
  it.each(["research", "analysis"])("joins once with %s finishing first", async (first) => {
    let release = () => {};
    const done = new Promise<void>((resolve) => {
      release = resolve;
    });
    let joins = 0;
    const graph = new StateGraph(WorkflowState)
      .addNode("researchFixture", async () => {
        if (first === "research") release();
        else await done;
        return { research };
      })
      .addNode("analysisFixture", async () => {
        if (first === "analysis") release();
        else await done;
        return { analysis };
      })
      .addNode("joinFixture", (state) => {
        expect(state.research).toEqual(research);
        expect(state.analysis).toEqual(analysis);
        joins += 1;
        return { usage: { modelCalls: 1, searches: 0, pageReads: 0, nativeToolCallsReserved: 2 } };
      })
      .addEdge(START, "researchFixture")
      .addEdge(START, "analysisFixture")
      .addEdge(["researchFixture", "analysisFixture"], "joinFixture")
      .addEdge("joinFixture", END)
      .compile();
    const result = await graph.invoke(initial);
    expect(joins).toBe(1);
    expect(result.inputSnapshot).toEqual(initial.inputSnapshot);
    expect(result.deadline).toBe(initial.deadline);
    expect(result.usage).toEqual({
      modelCalls: 1,
      searches: 0,
      pageReads: 0,
      nativeToolCallsReserved: 2,
    });
  });
  it.each(["inputSnapshot", "requestId", "deadline"])("blocks %s overwrite", async (key) => {
    const graph = new StateGraph(WorkflowState)
      .addNode("overwrite", () => ({
        [key]:
          initial[
            key === "requestId" ? "requestId" : key === "deadline" ? "deadline" : "inputSnapshot"
          ],
      }))
      .addEdge(START, "overwrite")
      .addEdge("overwrite", END)
      .compile();
    await expect(graph.invoke(initial)).rejects.toThrow("Immutable workflow context");
  });
  it("does not retry a failed node", async () => {
    let calls = 0;
    const graph = new StateGraph(WorkflowState)
      .addNode(
        "failure",
        () => {
          calls += 1;
          throw new Error("fixture failure");
        },
        { retryPolicy: { maxAttempts: 1 } },
      )
      .addEdge(START, "failure")
      .addEdge("failure", END)
      .compile();
    await expect(graph.invoke(initial)).rejects.toThrow("fixture failure");
    expect(calls).toBe(1);
  });
});
