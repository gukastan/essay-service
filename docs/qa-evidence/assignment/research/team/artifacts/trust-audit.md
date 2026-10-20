# ESSAY-10 trust design memo

Status: design recommendation; final implementation audit pending. Reviewed 2026-10-20.

## Trust root decision

Use maintained exact company aliases mapped to exact HTTPS official hosts, with provenance and review date. This is an explicit operator trust decision with limited company coverage, not an automated ownership proof. A search model's label, TLS, similar domain, company-name text or JSON-LD is insufficient. Unknown companies must use explicitly labelled user_provided posting evidence or needs_input. Do not fabricate findings or claim general company coverage.

Primary provenance browsed directly:
- OpenAI: https://openai.com/careers/ links to https://openai.com/careers/search/. Use exact openai.com host; do not infer every subdomain is trusted.
- Anthropic: https://www.anthropic.com/careers links to https://www.anthropic.com/careers/jobs. That listing links individual external Greenhouse jobs. Exact www.anthropic.com host is the initial root; an external ATS host by itself is never an anchor.
- SSRF guidance: https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html (OWASP primary guidance).

An external job must be linked from a freshly fetched trusted official page; retain that identity/link evidence as well as the job excerpt. Prefer exact linked URL authorization. Do not authorize all tenants of an ATS host; do not follow an authorized ATS URL through an untrusted destination and retain official status.

## Evidence acceptance

Source excerpt must support company identity and the requested role's requirements. An incidental role mention elsewhere on a values page cannot establish a requirement. Literal quotation establishes text provenance, not semantic relevance or ownership. Conflict affecting identity or core requirements, ambiguous company/role, or instructions pretending to be evidence must fail closed. Avoid interpreting arbitrary company values as job requirements. Unknown-company pasted posting remains user_provided, never official. Research inputs include only company, role, optional posting; never question or experience. One hosted research model call only; no validation or summary model.

## Direct HTTP attack checklist

- Parse each initial URL and every redirect before network access. Permit only intended HTTP(S) schemes; reject userinfo, malformed hosts/ports and nonstandard ports. Official provenance should use authenticated HTTPS.
- Resolve all A/AAAA answers and reject the entire resolution if any answer is not public unicast. Include loopback, private, link-local, multicast, unspecified, reserved and IPv4-mapped IPv6 cases. Consider mapped/transition addresses explicitly rather than relying on one broad property.
- Pin an approved numeric IP for the actual socket; preserve original hostname for certificate verification, TLS SNI and HTTP Host. Checking DNS then allowing the HTTP client to resolve again is a rebinding vulnerability. Disable proxy environment and retries; do not silently fall back to another unresolved address.
- Redirects consume the same direct-read budget; validate every target and destination trust. Detect loops or let the three-read cap terminate them. No unlimited redirect follow.
- Bound streamed body bytes to 1 MiB per response, including missing/lying Content-Length and compressed expansion. Keep cleaned text at 12,000 Unicode code points total. Treat truncation as incomplete evidence, not proof that absent conflicting material does not exist.
- Three direct reads maximum and the original shared research 45-second deadline include DNS, connect, redirects and body iteration. Timeouts must not reset per chunk/hop or leave background I/O running indefinitely.
- Test the real transport seam, not only the URL checker: assert actual numeric peer routing, hostname verification and no second DNS resolution; reject mixed safe/unsafe addresses before connection.

## Review perspectives

Loaded programming/SKILL.md and remove-ai-slops/SKILL.md. Final review will check meaningful behavioral tests, no prose-pinning or implementation-mirroring tests, no unnecessary extraction/normalization layers. URL/IP/HTML parsing at the untrusted network boundary is justified by this goal; speculative general-purpose trust frameworks are not.
