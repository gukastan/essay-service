# ESSAY-9 contracts/state handoff

Owner: A / contracts-state. Date: 2026-10-19. Scope: only package.json, pnpm-lock.yaml, src/shared/contracts-v2.ts + test, src/server/workflow/state.ts + test. No commits, API route, product roles or v1 edits.

## Contracts

Runtime Zod schemas export PascalCase names (DraftRequestV2Schema, DraftResponseV2Schema, SourceSchema, ResearchResultSchema, AnalysisResultSchema, WriterResultSchema, ReviewResultSchema). Request/response and role result types inferred and readonly. Branded IDs distinguish request/source/company fact/job requirement/experience evidence/claim IDs. Required input text preserves original whitespace/UTF-16 offsets while rejecting blank strings and measuring maximums by code points. Optional empty material becomes undefined (omitted by JSON serialization). Official sources require HTTP(S) URL/excerpt; user supplied source can omit URL. Ready validates length/count; error and needs_input reject draft/raw extra fields.

WorkflowState uses real LangGraph Annotation.Root; requestId/inputSnapshot/deadline reject subsequent writes. Research/analysis have independent channels. Runtime ExecutionBudget remains outside state; usage is a coordinator snapshot. WorkflowStateValue/WorkflowStateUpdate export readonly views. Every state channel has an explicit initial null/empty-array/zero-value default, verified through a real minimal graph. Reducer failures use WorkflowStateError (IMMUTABLE_CONTEXT/REVISION_DECREASE); a real graph test rejects revision rollback. No checkpointer or product graph introduced.

## Exact versions

@langchain/langgraph 1.5.1, @langchain/core 1.2.18, zod 4.6.7 exact package pins. Existing OpenAI 7.39.0 and Next 16.4.2 unchanged. LangGraph requires core ^1.1.48 and Zod ^3.25.32 || ^4.2.0; installed versions satisfy. Node v26.7.0 used for local checks, repository engine >=22. Frozen lockfile installation passes.

## Evidence and binary observables

All paths below relative to repository root, under .omo/evidence/essay9-contracts/.

| Scenario | Invocation | Binary observable | Artifact |
|---|---|---|---|
| Input bounds, optional material, response variants, source/claim structure | pnpm exec vitest run src/shared/contracts-v2.test.ts src/server/workflow/state.test.ts | 26 tests pass; invalid shapes reject and valid shapes parse | focused-tests.log |
| Real graph parallel completion orders | same focused invocation, real LangGraph foundation suite | both orders join exactly once with both fields present | focused-tests.log |
| Immutable context and zero retry | same focused invocation | overwrite rejects for all3 context fields; failed node called once | focused-tests.log |
| Strict TypeScript | pnpm typecheck | exit0 | typecheck.log |
| Assigned-file lint | pnpm exec biome check src/shared/contracts-v2.ts src/shared/contracts-v2.test.ts src/server/workflow/state.ts src/server/workflow/state.test.ts | exit0, no fixes | lint.log |
| Dependency lock consistency | pnpm install --frozen-lockfile | exit0; lockfile up to date | install.log |
| Installed versions | node reads installed package manifests | exact pinned versions printed | versions.log |
| No assertion/any escape hatches | project TypeScript AST scan using createSourceFile/forEachChild | 0 forbidden AST nodes | manual-code-audit.log |

Full regression before provider wire adaptation:130pass/1fail; failure is unsupported optional source dates in OpenAI zodTextFormat, coordinated with C. Preserved in regression-before-wire-fix.log. After the provider wire adaptation, the aggregate run passes137 tests; exact count and invocation captured in regression-tests.log.

## Limits and self-review

This is structural contract validation, not the future evidence resolver: quote correspondence, cross-reference existence, provenance/DNS verification, semantic claims and complete four-role/API flow remain ESSAY-10 onward. Branded IDs do not themselves prove runtime references exist. Schema acceptance of a ready fixture does not prove factual correctness. No production deployment/hosting180s claim.

Responsibilities are boundary contracts and graph state, respectively; no hidden unknown values cross boundaries, no assertions/any/enums, no logging or defensive exception wrappers, no broad API additions. Contracts file210 pure LOC is in skill warning band; propose separate evidence schemas if next change adds more. Other pure LOC117/85/126 (latest counts in manual-code-audit.log). The bundled checker cannot run: Bun absent and its TS7 unstable imports unavailable in installed TypeScript5.9; this is explicitly not a pass (code-audit.log). Compatible project AST audit and strict compile are recorded instead.

Official docs consulted via Context7: https://docs.langchain.com/oss/javascript/langgraph/use-graph-api and /workflows-agents and /fault-tolerance. Bundled Next use-server documentation read; this implementation adds no Server Action or directive.

## Approved hosted-search metric follow-up

WorkflowUsage now includes nativeToolCallsReserved:number, initial0. The real graph fixture updates this to2 alongside modelCalls1 while direct searches/pageReads remain0, then asserts the output. ExecutionBudget owns reservation enforcement; graph usage remains its snapshot.

Minimal relevant rerun: `pnpm exec vitest run src/shared/contracts-v2.test.ts src/server/workflow/state.test.ts` passes26 tests in native-metric-tests.log; `pnpm typecheck` currently fails on the concurrent provider edit native-provider.ts:57 (OpenAI7.39 types lack max_tool_calls), captured in native-metric-typecheck.log and sent to C for resolution; scoped `pnpm exec biome check src/server/workflow/state.ts src/server/workflow/state.test.ts` exits0 in native-metric-lint.log. Compatible TypeScript AST scan reports0 forbidden nodes in native-metric-audit.log. All logs under .omo/evidence/essay9-contracts/. Full137-test regression above predates this metric-only change; leader owns final aggregate integration run. Responsibilities and boundary/error design remain unchanged; no new assertions or catch/logging layers.
