import json
from typing import Final

from agent.source_page import FetchedPage, extract_page
from tests.research_fixture import CHECKED

NAVER_URL: Final = "https://recruit.navercorp.com/rcrt/view.do?annoId=30005457"
ROLE: Final = "N배송 운영 지원"
TITLE: Final = "[NAVER] 네이버쇼핑 부문별 운영 담당자 (계약) - N배송 운영 지원 부문"
QUOTE: Final = "고객·파트너사, 유관부서와의 원활한 커뮤니케이션이 가능하신 분"
MODEL_METADATA: Final = "Recruiting department NAVER Working conditions Temporary"


def section(heading: str, text: str) -> str:
    return (
        f'<div class="detail_box"><h4 class="detail_title">{heading}</h4>'
        f'<p class="detail_text"><div class="O0"><span>• </span>'
        f"<span><span>{text}</span></span></div></p></div>"
    )


def card(contents: str, title: str = TITLE) -> str:
    return (
        f'<div class="card_wrap"><div class="card_title_box">'
        f'<h4 class="card_title">{title}</h4></div>{contents}</div>'
    )


def naver_page(body: str, employer: str = "NAVER") -> FetchedPage:
    posting = json.dumps(
        {
            "@type": "JobPosting",
            "title": TITLE,
            "hiringOrganization": {"@type": "Organization", "name": employer},
        }
    )
    html = f'<script type="application/ld+json">{posting}</script>{body}'
    return extract_page(NAVER_URL, html.encode(), CHECKED)
