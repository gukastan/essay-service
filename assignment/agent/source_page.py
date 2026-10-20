"""Bounded page extraction: visible text and explicit navigation links only."""

from dataclasses import dataclass
from datetime import datetime
from html.parser import HTMLParser
from typing import Final, Literal, final, override
from urllib.parse import urljoin

from agent.source_sections import RequirementSection, extract_sections
from agent.source_structured import Posting, postings

MAX_PAGE_BYTES: Final = 1024 * 1024
MAX_PAGE_TEXT: Final = 12000


@final
class PageReadError(Exception):
    def __init__(
        self,
        code: Literal[
            "TIMEOUT",
            "UNSAFE_URL",
            "ACCESS_DENIED",
            "EMPTY",
            "TOO_LARGE",
            "INVALID_PAGE",
            "NETWORK_ERROR",
        ],
    ) -> None:
        self.code = code
        super().__init__(code)


@dataclass(frozen=True, slots=True)
class FetchedPage:
    url: str
    text: str
    links: tuple[str, ...]
    checked_at: datetime
    postings: tuple[Posting, ...] = ()
    requirement_sections: tuple[RequirementSection, ...] = ()


@final
class PageParser(HTMLParser):
    """Mutable HTML tokenizer; executable and nonvisible containers are discarded."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.links: list[str] = []
        self.hidden: list[str] = []
        self.structured = False
        self.json_parts: list[str] = []
        self.postings: list[Posting] = []

    @override
    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "script" and ("type", "application/ld+json") in attrs:
            self.structured = True
            self.json_parts = []
        if tag in {"script", "style", "noscript", "template"}:
            self.hidden.append(tag)
        if self.hidden:
            return
        if tag == "a":
            self.links.extend(value for key, value in attrs if key == "href" and value)
        self.parts.append(" ")

    @override
    def handle_endtag(self, tag: str) -> None:
        if tag == "script" and self.structured:
            self.postings.extend(postings("".join(self.json_parts)))
            self.structured = False
        if self.hidden and self.hidden[-1] == tag:
            _ = self.hidden.pop()
        if not self.hidden:
            self.parts.append(" ")

    @override
    def handle_data(self, data: str) -> None:
        if self.structured:
            self.json_parts.append(data)
        if not self.hidden:
            self.parts.append(data)


def extract_page(url: str, body: bytes, checked_at: datetime) -> FetchedPage:
    parser = PageParser()
    try:
        html = body.decode("utf-8", errors="strict")
        parser.feed(html)
    except UnicodeDecodeError:
        raise PageReadError("INVALID_PAGE") from None
    text = " ".join("".join(parser.parts).split())[:MAX_PAGE_TEXT]
    if not text:
        raise PageReadError("EMPTY")
    return FetchedPage(
        url,
        text,
        tuple(urljoin(url, link) for link in parser.links),
        checked_at,
        tuple(parser.postings),
        tuple(section for section in extract_sections(url, html) if section.text in text),
    )
