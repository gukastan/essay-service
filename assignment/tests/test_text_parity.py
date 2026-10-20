"""The same Unicode fixtures used in the real Vue browser harness."""

import json
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

import pytest

from agent.contracts import ExperienceEvidence, count_characters, evidence_matches, normalize_text


@dataclass(frozen=True, slots=True)
class TextFixture:
    source: str
    normalized: str
    count: int
    start: int
    end: int
    quote: str


@pytest.mark.parametrize(
    "fixture",
    [
        TextFixture("한글 문장", "한글 문장", 5, 3, 5, "문장"),
        TextFixture("가😀\r\n나", "가😀\n나", 4, 1, 3, "😀\n"),
        TextFixture("가é🧑‍💻\r끝", "가é🧑‍💻\n끝", 8, 3, 6, "🧑‍💻"),
    ],
)
def test_python_matches_javascript_codepoint_boundary(fixture: TextFixture) -> None:
    # Given
    helper = Path(__file__).resolve().parents[1] / "web" / "foundation.mjs"
    node = shutil.which("node")
    assert node is not None
    script = """
      import { normalizeLf, codePointLength, codePointSlice } from './web/foundation.mjs';
      const [source, start, end] = JSON.parse(process.argv[1]);
      process.stdout.write(JSON.stringify([
        normalizeLf(source), codePointLength(source), codePointSlice(source,start,end)
      ]));
    """
    evidence = ExperienceEvidence.model_validate(
        {
            "id": "e1",
            "quote": fixture.quote,
            "start": fixture.start,
            "end": fixture.end,
            "category": "action",
        }
    )
    # When: fixed test script and arguments, no shell or untrusted executable.
    result = subprocess.run(  # noqa: S603
        [
            node,
            "--input-type=module",
            "-e",
            script,
            json.dumps([fixture.source, fixture.start, fixture.end]),
        ],
        cwd=helper.parent.parent,
        capture_output=True,
        text=True,
        check=True,
        timeout=10,
    )
    # Then
    assert json.loads(result.stdout) == [fixture.normalized, fixture.count, fixture.quote]
    assert normalize_text(fixture.source) == fixture.normalized
    assert count_characters(fixture.source) == fixture.count
    assert evidence_matches(fixture.source, evidence)
