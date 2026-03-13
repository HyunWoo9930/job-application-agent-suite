#!/usr/bin/env python3
"""Print one agent prompt template with optional variable interpolation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

AGENT_FILES = {
    "agent-00": "agent-00-intake-validator.md",
    "00": "agent-00-intake-validator.md",
    "intake": "agent-00-intake-validator.md",
    "validator": "agent-00-intake-validator.md",
    "agent-01": "agent-01-company-role-analyst.md",
    "agent-01a": "agent-01a-industry-analyst.md",
    "agent-01b": "agent-01b-company-analyst.md",
    "agent-01c": "agent-01c-role-analyst.md",
    "01": "agent-01-company-role-analyst.md",
    "01a": "agent-01a-industry-analyst.md",
    "01b": "agent-01b-company-analyst.md",
    "01c": "agent-01c-role-analyst.md",
    "company": "agent-01-company-role-analyst.md",
    "industry": "agent-01a-industry-analyst.md",
    "company-business": "agent-01b-company-analyst.md",
    "company-role": "agent-01-company-role-analyst.md",
    "analyst": "agent-01-company-role-analyst.md",
    "role-analyst": "agent-01c-role-analyst.md",
    "job-role": "agent-01c-role-analyst.md",
    "agent-02": "agent-02-experience-miner.md",
    "agent-02a": "agent-02a-corpus-experience-recommender.md",
    "02": "agent-02-experience-miner.md",
    "02a": "agent-02a-corpus-experience-recommender.md",
    "experience": "agent-02-experience-miner.md",
    "miner": "agent-02-experience-miner.md",
    "corpus": "agent-02a-corpus-experience-recommender.md",
    "corpus-experience": "agent-02a-corpus-experience-recommender.md",
    "recommender": "agent-02a-corpus-experience-recommender.md",
    "agent-03": "agent-03-question-experience-matcher.md",
    "03": "agent-03-question-experience-matcher.md",
    "matcher": "agent-03-question-experience-matcher.md",
    "match": "agent-03-question-experience-matcher.md",
    "agent-03b": "agent-03b-experience-refiner.md",
    "03b": "agent-03b-experience-refiner.md",
    "refiner": "agent-03b-experience-refiner.md",
    "refine": "agent-03b-experience-refiner.md",
    "tail-question": "agent-03b-experience-refiner.md",
    "agent-03c": "agent-03c-metric-evidence-tracker.md",
    "03c": "agent-03c-metric-evidence-tracker.md",
    "metric": "agent-03c-metric-evidence-tracker.md",
    "metrics": "agent-03c-metric-evidence-tracker.md",
    "evidence-tracker": "agent-03c-metric-evidence-tracker.md",
    "agent-04": "agent-04-drafting-assistant.md",
    "04": "agent-04-drafting-assistant.md",
    "draft": "agent-04-drafting-assistant.md",
    "drafting": "agent-04-drafting-assistant.md",
    "agent-05": "agent-05-tone-customizer.md",
    "05": "agent-05-tone-customizer.md",
    "tone": "agent-05-tone-customizer.md",
    "customizer": "agent-05-tone-customizer.md",
    "agent-06": "agent-06-ai-style-and-qa-reviewer.md",
    "06": "agent-06-ai-style-and-qa-reviewer.md",
    "feedback": "agent-06-ai-style-and-qa-reviewer.md",
    "review": "agent-06-ai-style-and-qa-reviewer.md",
    "ai-style": "agent-06-ai-style-and-qa-reviewer.md",
    "agent-07": "agent-07-final-packager.md",
    "07": "agent-07-final-packager.md",
    "package": "agent-07-final-packager.md",
    "packager": "agent-07-final-packager.md",
    "final-pack": "agent-07-final-packager.md",
}


def load_vars(path: str | None) -> dict[str, str]:
    if not path:
        return {}
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("--input JSON must be an object")
    return {str(k): str(v) for k, v in data.items()}


def interpolate(template: str, values: dict[str, str]) -> str:
    out = template
    for key, value in values.items():
        out = out.replace("{{" + key + "}}", value)
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Print one agent prompt template.")
    parser.add_argument("--agent", required=False, help="agent id or alias (e.g. agent-06, feedback, drafting)")
    parser.add_argument("--input", default=None, help="JSON file for {{var}} substitution")
    parser.add_argument("--list", action="store_true", help="List available agent ids and aliases")
    args = parser.parse_args()

    if args.list:
        print("Available canonical agents:")
        for agent_id in sorted({k for k in AGENT_FILES if k.startswith("agent-")}):
            print(f"- {agent_id}")
        print("\nCommon aliases:")
        aliases = sorted({k for k in AGENT_FILES if not k.startswith("agent-")})
        print(", ".join(aliases))
        return 0

    if not args.agent:
        raise SystemExit("missing --agent (or use --list)")

    alias = args.agent.strip().lower()
    file_name = AGENT_FILES.get(alias)
    if not file_name:
        valid = ", ".join(sorted({k for k in AGENT_FILES if k.startswith("agent-")}))
        raise SystemExit(f"unknown agent alias: {args.agent}\nuse one of: {valid} or known aliases")

    root = Path(__file__).resolve().parents[1]
    ref_path = root / "references" / file_name
    text = ref_path.read_text(encoding="utf-8")
    values = load_vars(args.input)
    print(interpolate(text, values))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
