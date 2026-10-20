"""NAVER job-detail sections bound to one explicit posting card."""

from dataclasses import dataclass
from html.parser import HTMLParser
from typing import final, override
from urllib.parse import urlsplit


@dataclass(frozen=True, slots=True)
class RequirementSection:
    posting_title: str
    heading: str
    text: str


@final
class SectionParser(HTMLParser):
    """Mutable tokenizer for the reviewed NAVER card/detail DOM, not page-wide headings."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.depth = 0
        self.cards = 0
        self.card_depth = 0
        self.section_depth = 0
        self.title: list[str] = []
        self.heading: list[str] = []
        self.body: list[str] = []
        self.capture_title = False
        self.capture_heading = False
        self.hidden = 0
        self.sections: list[RequirementSection] = []

    @override
    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        classes = next((value or "" for key, value in attrs if key == "class"), "").split()
        if tag in {"script", "style", "template", "noscript"}:
            self.hidden += 1
        if self.hidden:
            return
        if tag == "div":
            self.depth += 1
            if "card_wrap" in classes:
                self.cards += 1
                self.card_depth = self.depth
            if self.card_depth and "detail_box" in classes:
                self.section_depth = self.depth
                self.heading = []
                self.body = []
        if tag == "h4" and self.card_depth:
            self.capture_title = "card_title" in classes
            self.capture_heading = bool(self.section_depth and "detail_title" in classes)
        if self.section_depth and not self.capture_heading:
            self.body.append(" ")

    @override
    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "template", "noscript"} and self.hidden:
            self.hidden -= 1
            return
        if self.hidden:
            return
        if tag == "h4":
            self.capture_title = False
            self.capture_heading = False
        if tag == "div":
            if self.section_depth == self.depth:
                heading = " ".join("".join(self.heading).split())
                if heading in {"What You'll Do", "Required Skills"}:
                    self.sections.append(
                        RequirementSection(
                            " ".join("".join(self.title).split()),
                            heading,
                            " ".join("".join(self.body).split()),
                        )
                    )
                self.section_depth = 0
            if self.card_depth == self.depth:
                self.card_depth = 0
            self.depth -= 1
        if self.section_depth:
            self.body.append(" ")

    @override
    def handle_data(self, data: str) -> None:
        if self.hidden:
            return
        if self.capture_title:
            self.title.append(data)
        if self.capture_heading:
            self.heading.append(data)
        if self.section_depth and not self.capture_heading:
            self.body.append(data)


def extract_sections(url: str, html: str) -> tuple[RequirementSection, ...]:
    parsed = urlsplit(url)
    if parsed.hostname != "recruit.navercorp.com" or parsed.path != "/rcrt/view.do":
        return ()
    parser = SectionParser()
    parser.feed(html)
    return tuple(parser.sections) if parser.cards == 1 else ()
