import { Annotation } from "@langchain/langgraph";
import type {
  AnalysisResult,
  DraftRequestV2,
  DraftResponseV2,
  RequestId,
  ResearchResult,
  ReviewResult,
  WriterResult,
} from "@/shared/contracts-v2";

export class WorkflowStateError extends Error {
  readonly name = "WorkflowStateError";
  constructor(readonly code: "IMMUTABLE_CONTEXT" | "REVISION_DECREASE") {
    super(
      {
        IMMUTABLE_CONTEXT: "Immutable workflow context cannot be overwritten",
        REVISION_DECREASE: "Revision count cannot decrease",
      }[code],
    );
  }
}

function writeOnce<T>() {
  return Annotation<T | null, T>({
    reducer: (current, incoming) => {
      if (current !== null) throw new WorkflowStateError("IMMUTABLE_CONTEXT");
      return incoming;
    },
    default: () => null,
  });
}

export type WorkflowUsage = {
  readonly modelCalls: number;
  readonly searches: number;
  readonly pageReads: number;
  readonly nativeToolCallsReserved: number;
};
export type DeterministicChecks = {
  readonly characterCount: number;
  readonly lengthValid: boolean;
  readonly evidenceValid: boolean;
  readonly issues: readonly string[];
};

// Runtime budgets remain outside the graph; usage is a coordinator-owned snapshot.
export const WorkflowState = Annotation.Root({
  requestId: writeOnce<RequestId>(),
  inputSnapshot: writeOnce<DraftRequestV2>(),
  deadline: writeOnce<number>(),
  research: Annotation<ResearchResult | null>({
    reducer: (_, value) => value,
    default: () => null,
  }),
  analysis: Annotation<AnalysisResult | null>({
    reducer: (_, value) => value,
    default: () => null,
  }),
  draft: Annotation<string | null>({ reducer: (_, value) => value, default: () => null }),
  claimMap: Annotation<WriterResult["claimMap"]>({
    reducer: (_, value) => value,
    default: () => [],
  }),
  fitReasons: Annotation<WriterResult["fitReasons"]>({
    reducer: (_, value) => value,
    default: () => [],
  }),
  deterministicChecks: Annotation<DeterministicChecks | null>({
    reducer: (_, value) => value,
    default: () => null,
  }),
  review: Annotation<ReviewResult | null>({ reducer: (_, value) => value, default: () => null }),
  revisionCount: Annotation<0 | 1>({
    reducer: (current, next) => {
      if (current === 1 && next !== 1) throw new WorkflowStateError("REVISION_DECREASE");
      return next;
    },
    default: () => 0,
  }),
  usage: Annotation<WorkflowUsage>({
    reducer: (_, value) => value,
    default: () => ({ modelCalls: 0, searches: 0, pageReads: 0, nativeToolCallsReserved: 0 }),
  }),
  outcome: Annotation<DraftResponseV2 | null>({
    reducer: (_, value) => value,
    default: () => null,
  }),
});
export type WorkflowStateValue = Readonly<typeof WorkflowState.State>;
export type WorkflowStateUpdate = Readonly<typeof WorkflowState.Update>;
