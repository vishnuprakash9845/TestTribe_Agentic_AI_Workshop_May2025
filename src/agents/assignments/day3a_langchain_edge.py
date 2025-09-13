# Assignment: Day-1
"""
Agent entrypoint: edgecase_agent

Run via module mode for reliable imports:
  python -m src.agents.assignments.day3a_langchain_edge --input data/requirements/login.txt

This file is intentionally small and imports core helpers from `src.core`.
"""

from __future__ import annotations

from pathlib import Path
import json
from typing import List, Dict
import argparse
import time
from langchain.prompts import PromptTemplate
from src.core import chat, pick_requirement, parse_json_safely, to_rows, write_csv

ROOT = Path(__file__).resolve().parents[3]
REQ_DIR = ROOT / "data" / "requirements"
OUT_DIR = ROOT / "outputs" / "assignments"  # where outputs are written
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_CSV = OUT_DIR / "edgecase_cases.csv"  # CSV output path
LAST_RAW_JSON = OUT_DIR / "edgecase.json"

PROMPTS_DIR = ROOT / "src" / "core" / "prompts"
SYSTEM_PROMPT = (
    PROMPTS_DIR / "edge_testcase_system.txt").read_text(encoding="utf-8")
USER_TEMPLATE_STR = (
    PROMPTS_DIR / "edge_testcase_user.txt").read_text(encoding="utf-8")
USER_TEMPLATE = PromptTemplate.from_template(USER_TEMPLATE_STR)

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
    parser.add_argument("input", nargs="?",
                        help="path to requirement .txt file")
    parser.add_argument("-i", "--input", dest="input_flag",
                        help="path to requirement .txt file")
    args = parser.parse_args()

    import logging
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s"
    )
    logger = logging.getLogger(__name__)

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
    logger.debug(
        "Calling chat: provider payload msgs=%d (sys=1,user=1)", len(messages))
    raw = chat(messages, timeout=300)

    try:
        cases = parse_json_safely(raw, LAST_RAW_JSON)
    except (ValueError, json.JSONDecodeError) as exc:
        # gentle retry nudge — a pragmatic teaching technique: show how a
        # small reminder can correct common model format mistakes.
        logger.exception(
            "Initial parse_json_safely failed; will nudge and retry. Raw saved at %s",
            LAST_RAW_JSON,
        )
        nudge = (
            raw + "\n\nREMINDER: Return a pure JSON array only, matching the schema."
        )
        try:
            cases = parse_json_safely(nudge, LAST_RAW_JSON)
        except (ValueError, json.JSONDecodeError) as exc2:
            # Surface a clear runtime error with a pointer to the saved raw
            # output so students can debug model responses during the session.
            logger.error(
                "Could not parse model output after nudge; see %s", LAST_RAW_JSON
            )
            raise RuntimeError(
                f"Could not parse model output as JSON. See {LAST_RAW_JSON}.\nError: {exc}"
            ) from exc2

    rows = to_rows(cases)
    write_csv(rows, OUT_CSV)

    logger.info("✅ Wrote %d test cases to: %s",
                len(rows), OUT_CSV.relative_to(ROOT))
    logger.info("ℹ️  Raw model output saved at: %s",
                LAST_RAW_JSON.relative_to(ROOT))


if __name__ == "__main__":
    start_time = time.time()
    main()
    end_time = time.time()
    print(f"Execution time: {end_time - start_time:.4f} seconds")


# To run the agent:
# 1. Install the required packages:
#   ```
#   pip install -r requirements.txt
#   ```
# 2. Run the script:
#  ```
#   python -m src.agents.assignments.day3a_langchain_edge --input path/to/requirement.txt
#   ```
#   python -m src.agents.assignments.day3a_langchain_edge --input data/requirements/signup.txt
