#!/usr/bin/env python3
"""Save/load job-application analysis artifacts in local cache directory."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

DEFAULT_CACHE_ROOT = Path.home() / "Desktop" / "회사 직무 분석"


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("input JSON must be an object")
    return data


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def slugify(value: str) -> str:
    value = value.strip()
    value = re.sub(r"[\\/:*?\"<>|]+", "-", value)
    value = re.sub(r"\s+", "_", value)
    return value or "unknown"


def analysis_key(state: dict[str, Any]) -> str:
    company = str(state.get("company_name") or "").strip()
    role = str(state.get("role_title") or "").strip()
    return f"{slugify(company)}__{slugify(role)}"


def normalize_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if value in (None, ""):
        return []
    return [value]


def combine_unique(*values: Any) -> list[Any]:
    merged: list[Any] = []
    seen: set[str] = set()
    for value in values:
        for item in normalize_list(value):
            key = json.dumps(item, ensure_ascii=False, sort_keys=True) if isinstance(item, dict) else str(item)
            if key in seen:
                continue
            seen.add(key)
            merged.append(item)
    return merged


def first_non_empty(*values: Any) -> Any:
    for value in values:
        if value not in (None, "", [], {}):
            return value
    return ""


def synthesize_agent01_output(outputs: dict[str, Any]) -> dict[str, Any]:
    a01a = outputs.get("agent-01a", {})
    a01b = outputs.get("agent-01b", {})
    a01c = outputs.get("agent-01c", {})
    if not all(isinstance(item, dict) and item for item in (a01a, a01b, a01c)):
        return {}

    return {
        "role_summary": first_non_empty(a01c.get("role_summary"), a01c.get("role_analysis_summary")),
        "competency_table": normalize_list(a01c.get("competency_table")),
        "culture_and_tone_hints": combine_unique(
            a01b.get("culture_and_tone_hints"),
            a01b.get("strengths_and_differentiators"),
            a01a.get("trend_and_change_map"),
        ),
        "talent_profile_mapping": combine_unique(
            a01b.get("talent_profile_mapping"),
            a01b.get("strengths_and_differentiators"),
        ),
        "industry_analysis_summary": first_non_empty(a01a.get("industry_analysis_summary"), a01a.get("industry_summary")),
        "company_analysis_summary": first_non_empty(a01b.get("company_analysis_summary"), a01b.get("company_summary")),
        "role_analysis_summary": first_non_empty(a01c.get("role_analysis_summary"), a01c.get("role_summary")),
        "role_keyword_map": combine_unique(
            a01c.get("role_keyword_map"),
            a01c.get("role_keywords"),
            a01a.get("industry_keywords"),
            a01b.get("company_keywords"),
        ),
        "motivation_hooks": combine_unique(a01a.get("motivation_hooks"), a01b.get("motivation_hooks")),
        "future_contribution_hooks": combine_unique(
            a01a.get("future_contribution_hooks"),
            a01b.get("future_contribution_hooks"),
        ),
        "job_fit_hooks": combine_unique(a01c.get("job_fit_hooks")),
    }


def render_markdown_section(title: str, value: Any) -> str:
    lines = [f"## {title}"]
    if isinstance(value, dict):
        for key, item in value.items():
            lines.append(f"- **{key}**: {json.dumps(item, ensure_ascii=False)}" if isinstance(item, (dict, list)) else f"- **{key}**: {item}")
    elif isinstance(value, list):
        if not value:
            lines.append("- 없음")
        for item in value:
            lines.append(f"- {json.dumps(item, ensure_ascii=False)}" if isinstance(item, (dict, list)) else f"- {item}")
    else:
        lines.append(str(value) if value not in (None, "") else "- 없음")
    return "\n".join(lines)


def write_markdown(path: Path, title: str, payload: dict[str, Any]) -> None:
    lines = [f"# {title}"]
    for key, value in payload.items():
        lines.append("")
        lines.append(render_markdown_section(key, value))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def save_outputs(state: dict[str, Any], cache_root: Path) -> dict[str, Any]:
    key = analysis_key(state)
    base = cache_root / key
    outputs = state.get("agent_outputs", {})
    if not isinstance(outputs, dict):
        outputs = {}

    synthesized = synthesize_agent01_output(outputs)
    if synthesized and not outputs.get("agent-01"):
        outputs["agent-01"] = synthesized

    saved_agents: list[str] = []
    snapshot_dir = base / "snapshots" / datetime.now().strftime("%Y%m%d-%H%M%S")
    json_targets = {
        "agent-01a": "agent-01a-industry-latest.json",
        "agent-01b": "agent-01b-company-latest.json",
        "agent-01c": "agent-01c-role-latest.json",
    }
    md_targets = {
        "agent-01a": "industry-analysis-latest.md",
        "agent-01b": "company-analysis-latest.md",
        "agent-01c": "role-analysis-latest.md",
        "agent-01": "combined-analysis-latest.md",
    }
    for agent_id, output in outputs.items():
        if not isinstance(output, dict) or not output:
            continue
        latest_name = json_targets.get(agent_id, f"{agent_id}-latest.json")
        snapshot_name = latest_name.replace("-latest.json", ".json")
        write_json(base / latest_name, output)
        write_json(snapshot_dir / snapshot_name, output)
        if agent_id in md_targets:
            title = {
                "agent-01a": "Industry Analysis",
                "agent-01b": "Company Analysis",
                "agent-01c": "Role Analysis",
                "agent-01": "Combined Analysis",
            }[agent_id]
            write_markdown(base / md_targets[agent_id], title, output)
            write_markdown(snapshot_dir / md_targets[agent_id].replace("-latest.md", ".md"), title, output)
        saved_agents.append(agent_id)

    meta = {
        "company_name": state.get("company_name"),
        "role_title": state.get("role_title"),
        "updated_at": datetime.now().isoformat(timespec="seconds"),
        "saved_agents": saved_agents,
    }
    write_json(base / "meta.json", meta)
    return {"cache_dir": str(base), "saved_agents": saved_agents}


def load_agent01(state: dict[str, Any], cache_root: Path) -> dict[str, Any]:
    key = analysis_key(state)
    base = cache_root / key
    p = base / "agent-01-latest.json"
    outputs = state.get("agent_outputs", {})
    if not isinstance(outputs, dict):
        outputs = {}
    if p.exists():
        payload = json.loads(p.read_text(encoding="utf-8"))
        if isinstance(payload, dict) and payload:
            outputs["agent-01"] = payload
            state["agent_outputs"] = outputs
            state["_cache_agent01_loaded_from"] = str(p)
            return state
    subagent_paths = {
        "agent-01a": base / "agent-01a-industry-latest.json",
        "agent-01b": base / "agent-01b-company-latest.json",
        "agent-01c": base / "agent-01c-role-latest.json",
    }
    loaded = False
    for agent_id, path in subagent_paths.items():
        if not path.exists():
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, dict) and payload:
            outputs[agent_id] = payload
            loaded = True
    synthesized = synthesize_agent01_output(outputs)
    if loaded and synthesized:
        outputs["agent-01"] = synthesized
        state["agent_outputs"] = outputs
        state["_cache_agent01_loaded_from"] = str(base)
    return state


def main() -> int:
    parser = argparse.ArgumentParser(description="Persist or load analysis artifacts cache.")
    parser.add_argument("--input", required=True, help="Path to pipeline state JSON")
    parser.add_argument(
        "--cache-root",
        default=str(DEFAULT_CACHE_ROOT),
        help='Cache root directory (default: "~/Desktop/회사 직무 분석")',
    )
    parser.add_argument(
        "--mode",
        choices=["save", "load-agent01", "save-and-load-agent01"],
        default="save",
        help="Operation mode",
    )
    parser.add_argument(
        "--write-output",
        default=None,
        help="Optional path to write updated state JSON (for load modes)",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    state = load_json(input_path)
    cache_root = Path(args.cache_root).expanduser()

    report: dict[str, Any] = {"mode": args.mode}
    if args.mode in ("load-agent01", "save-and-load-agent01"):
        state = load_agent01(state, cache_root)
        if state.get("_cache_agent01_loaded_from"):
            report["cache_agent01_loaded_from"] = state["_cache_agent01_loaded_from"]

    if args.mode in ("save", "save-and-load-agent01"):
        report.update(save_outputs(state, cache_root))

    if args.write_output:
        write_json(Path(args.write_output), state)
        report["write_output"] = args.write_output

    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
