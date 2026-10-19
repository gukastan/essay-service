# ESSAY-9 provider verification

Date: 2026-10-19. Owner: member C. No active ulw-loop attempt (status returned ULW_LOOP_PLAN_MISSING), evidence therefore under .omo/evidence. No real credentials, headers, user experience or question content captured. Shared repository; no v1 files modified by this member.

| Criterion / exact scenario | Invocation | Binary observable | Artifact |
| --- | --- | --- | --- |
| Installed OpenAI7.39/current model accepts strict JSON | RUN_V2_PROVIDER_PROBE=1 node tests/probe-v2-provider.mjs | first status completed, output {ok:true} | live-probe.json |
| Existing credential supports native search | same invocation, second request | completed + one reported search action | live-probe.json |
| Strict JSON and native search share one generation call | RUN_V2_PROVIDER_PROBE=1 node tests/probe-v2-provider.mjs --combined | completed + JSON URL + one reported search action | live-combined.json |
| Probes stay opt-in | node tests/probe-v2-provider.mjs | SKIPPED before client construction | probe-default.txt |
| Adapter caps/cancellation context, strict output/error paths, input privacy, schema wire compatibility, Unicode/URL boundaries | pnpm exec vitest run src/server/workflow/providers.test.ts src/server/workflow/native-provider.test.ts tests/probe-v2-provider.live.test.ts | 27 tests passed, one opt-in live test skipped with flag absent, exit0 | unit-tests.txt |
| TypeScript compatibility with actual peer contracts/budget | pnpm typecheck | tsc exit0 | typecheck.txt |
| Formatting | pnpm exec biome check src/server/workflow/providers.ts src/server/workflow/provider-schemas.ts src/server/workflow/providers.test.ts tests/probe-v2-provider.mjs | no fixes/errors, exit0 | lint.txt |
| Required post-write measurement | awk 'NF && !/^[[:space:]]*\/\// {n[FILENAME]++} END {for(f in n) print f,n[f]}' <four source paths above> | each <250 pure LOC | loc.txt |

Intermediate actual research schema incompatibility retained in schema-failure-before-fix.txt. Fixed with required-nullable model wire schema and explicit domain normalization; final complete provider scenario rerun is unit-tests.txt.

The 27 tests use a mocked SDK/injected search/page providers: no paid traffic or real page-reader validation claimed. Live evidence is four explicitly authorized requests (2+1 exploratory, then1 production adapter), retries0. Exploratory requests max_output_tokens400; final production adapter max_output_tokens3000. Public company/role-only search. No other paid requests executed. Runtime normal model requests have role token caps and shared budgets; missing provider usage is represented by null, never fabricated as zero.

Architecture review: native-provider.ts owns native research transport; providers.ts owns tool-free model and injected boundaries; provider-schemas.ts owns research wire conversion; tests own behavioral verification; manual probe owns compatibility observation. External model and injected research data are parsed at boundaries; SDK helper builds schema before reserving a dispatch; no any, unsafe assertions, non-null assertions or new logging framework. Incomplete/invalid JSON errors omit data payload. Provider call failures propagate without retry. providers.test.ts is in 200–250 warning band (219 lines); split into model/research tests before further substantial growth.

User approved current-key native search with hosted tool-call2 cap instead of independent internal query/page counts. native-provider.ts implements that strategy; final live-adapter.json records server-echoed cap2. Search/Page interfaces remain injected alternatives with no fake default. Existing search2/page3 budget protects supplied operations only. Internal query/page/byte caps remain neither controllable nor claimed. Actual safe DNS/redirect/1MiB page reader, officiality verification, stage orchestration and complete role prompts belong to ESSAY-10 onward. Host180s support/fullv2 QA not verified here. See ADR for explicit alternatives and official API reference.


## Accepted native strategy verification

- Scenario: actual production native adapter + budget, one public company/role request. Invocation: `RUN_V2_NATIVE_ADAPTER_PROBE=1 pnpm exec vitest run tests/probe-v2-provider.live.test.ts`. Observable:1 test passed; serverToolCallLimit2; reported1 action; reserved2; modelCalls1; returned parsed HTTPS careers URL. Artifacts: `live-adapter.json`, `live-adapter-run.txt`.
- Scenario: offline native cap forwarding/projection/deadline/errors and tool-call count validation. Invocation: provider tests command in table. Observable:27 passed; default opt-in live test skipped before credential load/client construction. Artifact:`unit-tests.txt`.
- SDK HTTP type omits documented max_tool_calls; explicit intersection payload preserves field without unsafe cast. Official reference https://developers.openai.com/api/reference/resources/responses/methods/create and actual server echoed2. Native source metadata is unverified; downstream official verification is not implemented here.
- Final post-write architectural audit: source modules under250 lines, typed runtime boundaries, safe error serialization in manual live test, no raw SDK bodies/headers/keys in artifacts; no extra logging framework or broad refactor. Source reader SSRF work and research semantics remain future scope.
