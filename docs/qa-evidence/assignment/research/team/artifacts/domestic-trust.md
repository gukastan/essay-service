# Domestic company trust anchors — ESSAY-10

Reviewed: 2026-10-20. Scope authorized: NAVER/네이버 and Kakao/카카오, alongside existing OpenAI/Anthropic. No product edits. Operator-maintained trust decisions; not general automatic ownership discovery.

## NAVER

- Canonical company: NAVER. Exact supported input aliases: NAVER, 네이버 (case-insensitive Latin matching). Do not treat NAVER Cloud, NAVER LABS, NAVER WEBTOON, NAVER FINANCIAL, SNOW, NAVER Z or NAVER I&S as aliases.
- Corporate provenance: https://www.navercorp.com/main (https://www.navercorp.com/ redirects here). Its navigation directly links recruitment at https://recruit.navercorp.com/.
- Recruitment directory: https://recruit.navercorp.com/rcrt/list.do, linked by Jobs from recruitment home.
- Exact approved corporate host: www.navercorp.com. Exact recruitment host: recruit.navercorp.com. Do not wildcard *.navercorp.com or *.naver.com; portal/blog hosting is not a company hiring root.
- Verified individual page: https://recruit.navercorp.com/rcrt/view.do?annoId=30005457. Direct page read returned a NAVER-labelled job title, explicit NAVER recruiting-company field, role description, responsibility and skill sections. The employer is a posting attribute; the shared logo/footer is not sufficient.
- Supported detail route observation: /rcrt/view.do with a concrete annoId. Directory /rcrt/list.do and generic people/culture/value pages are not individual job evidence. The route is not /jobs and the role need not be embedded in its URL.
- Shared-site caution: recruitment homepage includes an affiliates filter and group-company material. Listing footer links separate recruitment domains for NAVER Cloud, SNOW, NAVER LABS, WEBTOON, FINANCIAL and I&S. Merely being linked from the official root does not make a subsidiary job a NAVER job. Accept only an unambiguous exact employer label within the specific posting. Reject ambiguous/multiple employer identity.

## Kakao

- Canonical company: Kakao. Exact supported aliases: Kakao, 카카오 (case-insensitive Latin matching). Kakao Pay, Kakao Games, Kakao Mobility and other group companies are not aliases.
- Corporate provenance: https://www.kakaocorp.com/page/. Its recruitment navigation directly links https://careers.kakao.com/index.
- Exact approved corporate host: www.kakaocorp.com. Exact recruitment host: careers.kakao.com. Do not wildcard *.kakao.com; service/account/developer domains are not job provenance.
- Primary indexed recruitment directory: https://careers.kakao.com/jobs. Primary indexed group filter: https://careers.kakao.com/jobs?company=SUBSIDIARY&page=1. Primary indexed individual route example: https://careers.kakao.com/jobs/S-4295 (Kakao Games listing); another is https://careers.kakao.com/jobs/P-14549. These are route observations, not a trustworthy employer decision based on the S/P prefix.
- Direct web reads of /index, group-filter directory and both example detail URLs returned only the JavaScript enablement shell. Search-indexed snippets of those primary pages exposed company fields and affiliate listings, but this is NOT direct fetched posting evidence and MUST NOT be promoted to official job evidence in the product.
- Require explicit exact posting employer 카카오/Kakao, role identity and requirements obtained by the bounded direct reader. A query company=KAKAO, path prefix, logo/footer or host cannot replace that evidence. If only a JavaScript shell is available, return needs_input and accept labelled user_provided posting text as the fallback. No browser automation or new rendering framework is required for ESSAY-10.
- Primary indexed P-14549 text includes a potential future change of employing entity. Treat any actual fetched employer-transition/conflict notice as identity ambiguity and request clarification; do not silently assert current/future Kakao employment.

## Executable policy boundary

Add only the above exact aliases/hosts with corporate-to-careers provenance links and review date. Recruitment host trust establishes publisher identity, not employer identity for every posting. A domestic source needs all of: approved publisher, recognized individual posting route, exact employer in posting-specific context, role-specific supported quotation, checked timestamp. Missing any item is needs_input; external group links do not expand this initial registry. Retain corporate/link and job provenance in report sources where relevant. Avoid hardcoded job outputs or broad country-specific parsers; these URLs are examples/provenance, not canned production findings.

## Evidence quality

NAVER corporate->careers->directory linkage and concrete NAVER detail content were directly read from primary sites. Kakao corporate->careers linkage was directly read; Kakao detail content and shared-site employer examples were visible only in primary-domain indexed results, with direct reads returning a shell. This distinction limits what may be claimed as verified runtime support. No paid model call, credentials, or submission action was used.
