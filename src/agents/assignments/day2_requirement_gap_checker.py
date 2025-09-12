"""
Agent entrypoint: testcase_agent

Run via module mode for reliable imports:
  python -m src.agents.assignments.day2_requirement_gap_checker --input data/requirements/login.txt

This file is intentionally small and imports core helpers from `src.core`.
"""

from __future__ import annotations

from pathlib import Path
import json
from typing import List, Dict
import argparse

from src.core import chat, pick_requirement, parse_json_safely, to_rows, write_csv

# The functions imported from `src.core` are small, dependency-free helpers
# used to keep this agent focused on orchestration (easy for students to read
# and extend): `chat` (LLM call), `pick_requirement` (choose input file),
# `parse_json_safely` (robust JSON parsing), `to_rows` and `write_csv`.

# Paths (easy-to-change constants for students)
ROOT = Path(__file__).resolve().parents[3]
# directory with .txt requirement files
REQ_DIR = ROOT / "data" / "requirements"
OUT_DIR = ROOT / "outputs" / "assignments"  # where outputs are written
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_CSV = OUT_DIR / "requirement_gap.csv"  # CSV output path
# file where raw LLM text is saved
LAST_RAW_JSON = OUT_DIR / "requirement_gap.json"

# Classroom note: these constants are intentionally simple and visible so
# students can easily change input/output locations when experimenting.

SYSTEM_PROMPT = """You are a senior QA assistant.
Think step-by-step about the requirement and produce ONLY a JSON array report listing gaps with suggested requirement text
test cases using this schema:

[
  {
    "id": "G-001",
    "source_file": "login.txt",
    "category": "security|performance|error-handling|acceptance",
    "description": "Short description of the missing requirement",
    "severity": "High|Medium|Low",
    "suggested_requirement": "One-line actionable requirement text"
  }
]

Rules:
- Return JSON ONLY (no prose, no fences).
- Steps should be short, imperative, and precise.
"""

USER_TEMPLATE = 'Requirement:\n"""{requirement_text}"""'  # user content injected
# `USER_TEMPLATE` wraps the requirement text so the model sees a clear input
# block; we keep it simple for students to inspect and modify.

Message = Dict[str, str]
"""Type alias for message dicts sent to the `chat` helper.

Each message is a dict with `role` and `content` strings, matching the
minimal interface used by provider-agnostic chat helpers in the exercises.
"""


def main() -> None:
    """Run the testcase agent end-to-end.

    Flow:
    1. Pick a requirement file (CLI arg or first file in `data/requirements`).
    2. Read the requirement text.
    3. Build a system + user message pair and call `chat(messages)`.
    4. Save raw model output to `outputs/last_raw.json` and parse it as JSON.
    5. Convert parsed cases to CSV rows and write `outputs/test_cases.csv`.

    Error handling and teaching hooks:
    - We save the raw model text to `LAST_RAW_JSON` so students can inspect
      model failures or formatting issues.
    - If parsing fails, we perform a single "nudge" retry that reminds the
      model to return pure JSON. If it still fails we raise a helpful error
      pointing to the raw file.
    - The agent is deliberately thin: it focuses on orchestration. Students
      can extend it later to add retries, rate-limiting, human-in-the-loop
      review pages, or direct integrations with Jira/TestRail.
    """

    # Accept either a positional arg or --input / -i flag for the requirement path.
    parser = argparse.ArgumentParser()
    parser.add_argument("inputs", nargs="?",
                        help="path to requirement .txt file")
    parser.add_argument("-i", "--inputs", dest="input_flag",
                        help="path to requirement .txt file")
    args = parser.parse_args()

    chosen = args.input_flag or args.input
    req_path = pick_requirement(chosen, REQ_DIR)
    requirement_text = req_path.read_text(encoding="utf-8").strip()

    messages: List[Message] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": USER_TEMPLATE.format(requirement_text=requirement_text),
        },
    ]

    # Call the LLM via the provider-agnostic `chat` function. The returned
    # `raw` is the assistant's text; for Day-1 we expect the model to return
    # a pure JSON array (see SYSTEM_PROMPT) so downstream parsing is simple.
    raw = chat(messages)

    try:
        cases = parse_json_safely(raw, LAST_RAW_JSON)
    except (ValueError, json.JSONDecodeError) as exc:
        # gentle retry nudge — a pragmatic teaching technique: show how a
        # small reminder can correct common model format mistakes.
        nudge = (
            raw + "\n\nREMINDER: Return a pure JSON array only, matching the schema."
        )
        try:
            cases = parse_json_safely(nudge, LAST_RAW_JSON)
        except (ValueError, json.JSONDecodeError) as exc2:
            # Surface a clear runtime error with a pointer to the saved raw
            # output so students can debug model responses during the session.
            raise RuntimeError(
                f"Could not parse model output as JSON. See {LAST_RAW_JSON}.\nError: {exc}"
            ) from exc2

    rows = to_rows(cases, "requirement")
    write_csv(rows, OUT_CSV, "requirement")

    print(f"✅ Wrote {len(rows)} requirements to: {OUT_CSV.relative_to(ROOT)}")
    print(f"ℹ️  Raw model output saved at: {LAST_RAW_JSON.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
