"""Operator-maintained company identities; model output cannot add trust roots."""

import re
from dataclasses import dataclass
from typing import Final
from urllib.parse import urlsplit


@dataclass(frozen=True, slots=True)
class CompanyAnchor:
    company: str
    aliases: tuple[str, ...]
    hosts: tuple[str, ...]
    provenance_url: str
    require_employer: bool = False


# Operator-reviewed primary career directories, 2026-10-20; exact hosts only.
DEFAULT_ANCHORS: Final = (
    CompanyAnchor(
        "NAVER",
        ("NAVER", "네이버"),
        ("www.navercorp.com", "recruit.navercorp.com"),
        "https://www.navercorp.com/main",
        require_employer=True,
    ),
    CompanyAnchor(
        "Kakao",
        ("Kakao", "카카오"),
        ("www.kakaocorp.com", "careers.kakao.com"),
        "https://www.kakaocorp.com/page/",
        require_employer=True,
    ),
    CompanyAnchor("OpenAI", ("OpenAI", "오픈AI"), ("openai.com",), "https://openai.com/careers/"),
    CompanyAnchor(
        "Anthropic",
        ("Anthropic", "앤트로픽"),
        ("www.anthropic.com", "anthropic.com"),
        "https://www.anthropic.com/careers/jobs",
    ),
)


def contains(text: str, value: str) -> bool:
    return (
        re.search(
            r"(?<!\w)" + re.escape(" ".join(value.casefold().split())) + r"(?!\w)",
            " ".join(text.casefold().split()),
        )
        is not None
    )


def trusted_url(url: str, anchor: CompanyAnchor) -> bool:
    parsed = urlsplit(url)
    return (
        parsed.scheme == "https" and parsed.hostname in anchor.hosts and parsed.port in {None, 443}
    )
