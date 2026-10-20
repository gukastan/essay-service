# Bounded NAVER DOM fixture provenance

On 2026-10-20 this QA worker read the public page `https://recruit.navercorp.com/rcrt/view.do?annoId=30005457` with:

`curl --fail --silent --show-error --max-time 20 'https://recruit.navercorp.com/rcrt/view.do?annoId=30005457' --output /tmp/essay10-naver-section-fixture.html`

Exit status was 0. Download SHA-256: `f4b1db00dca6c7c1c456381c4b84ba4f39952793b0b875670e34f263e6aff9ec`. The full public body is temporary, not a permanent test input. No model/API call or credential was used.

Observed structural boundaries: one `div.card_wrap`; its `h4.card_title` carries the posting title; each `div.detail_box` has an `h4.detail_title` plus a body containing nested `p`, `div`, and `span` elements. Recognized duty/requirement headings are `What You'll Do` and `Required Skills`; the nearby `Who We Are` and `Preferred Skills` sections are separate.

`assignment/tests/naver_section_fixture.py` reconstructs this bounded DOM shape with synthetic JSON-LD, the public title and one short public Korean bullet. It is a deterministic local fixture, not a stored copy of the full posting or a claim that its vacancy remains open.

`sections-first.txt` records two pre-integration positive failures and 11 passing negative cases. `sections-node-first.txt` records all 14 scenarios passing, including the actual stdio MCP/SDK local-HTTP node path. Final acceptance and source binding are recorded in the refreshed verification report.
