#!/usr/bin/env python3
"""Prepare and validate chained inputs for job-application agent workflow."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


PIPELINE = [
    "agent-00",
    "agent-01a",
    "agent-01b",
    "agent-01c",
    "agent-01",
    "agent-02a",
    "agent-02",
    "agent-03",
    "agent-03b",
    "agent-03c",
    "agent-04",
    "agent-05",
    "agent-06",
    "agent-07",
]
DEFAULT_CACHE_ROOT = Path.home() / "Desktop" / "회사 직무 분석"
DEFAULT_CORPUS_PATH = str(Path.home() / "Desktop" / "취업" / "자기소개서")
DEFAULT_APPROVAL_MODE = "manual_per_step"
REQUIRED_RUN_DIR_FILES = [
    "state.json",
    "02a_scan_report.md",
    "04_draft.txt",
    "05_tone.txt",
    "06_qa.json",
    "external_feedback.md",
    "07_package.md",
]


@dataclass
class StepState:
    agent: str
    status: str
    missing_fields: list[str]
    input_payload: dict[str, Any]


def load_json(path: str | Path) -> dict[str, Any]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("input JSON must be an object")
    return data


def write_json(path: str | Path, payload: dict[str, Any]) -> None:
    Path(path).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def slugify(value: str) -> str:
    value = value.strip()
    value = re.sub(r"[\\/:*?\"<>|]+", "-", value)
    value = re.sub(r"\s+", "_", value)
    return value or "unknown"


def ensure_run_dir_layout(run_dir: Path, seed_state: dict[str, Any] | None) -> Path:
    run_dir.mkdir(parents=True, exist_ok=True)
    for name in REQUIRED_RUN_DIR_FILES:
        p = run_dir / name
        if p.exists():
            continue
        if name.endswith(".json"):
            if name == "state.json" and seed_state is not None:
                write_json(p, seed_state)
            else:
                p.write_text("{}\n", encoding="utf-8")
        else:
            p.write_text("", encoding="utf-8")
    return run_dir / "state.json"


def maybe_hydrate_agent01_from_cache(state: dict[str, Any], cache_root: Path) -> dict[str, Any]:
    outputs = state.get("agent_outputs", {})
    if not isinstance(outputs, dict):
        outputs = {}
    if isinstance(outputs.get("agent-01"), dict) and outputs.get("agent-01"):
        return state

    company_name = str(state.get("company_name") or "").strip()
    role_title = str(state.get("role_title") or "").strip()
    if not company_name or not role_title:
        return state

    key = f"{slugify(company_name)}__{slugify(role_title)}"
    latest_file = cache_root / key / "agent-01-latest.json"
    if latest_file.exists():
        cached = json.loads(latest_file.read_text(encoding="utf-8"))
        if isinstance(cached, dict) and cached:
            outputs["agent-01"] = cached
            state["agent_outputs"] = outputs
            state["_cache_agent01_loaded_from"] = str(latest_file)
            return state

    subagent_files = {
        "agent-01a": cache_root / key / "agent-01a-industry-latest.json",
        "agent-01b": cache_root / key / "agent-01b-company-latest.json",
        "agent-01c": cache_root / key / "agent-01c-role-latest.json",
    }
    loaded = False
    for agent_id, path in subagent_files.items():
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
        state["_cache_agent01_loaded_from"] = str(cache_root / key)
    return state


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

    role_keyword_map = combine_unique(
        a01c.get("role_keyword_map"),
        a01c.get("role_keywords"),
        a01a.get("industry_keywords"),
        a01b.get("company_keywords"),
    )
    motivation_hooks = combine_unique(a01a.get("motivation_hooks"), a01b.get("motivation_hooks"))
    future_contribution_hooks = combine_unique(
        a01a.get("future_contribution_hooks"),
        a01b.get("future_contribution_hooks"),
    )
    job_fit_hooks = combine_unique(a01c.get("job_fit_hooks"))
    role_summary = first_non_empty(a01c.get("role_summary"), a01c.get("role_analysis_summary"))
    culture_and_tone_hints = combine_unique(
        a01b.get("culture_and_tone_hints"),
        a01b.get("strengths_and_differentiators"),
        a01a.get("trend_and_change_map"),
    )
    talent_profile_mapping = combine_unique(
        a01b.get("talent_profile_mapping"),
        a01b.get("strengths_and_differentiators"),
        a01c.get("core_responsibility_map"),
    )
    red_flags = combine_unique(
        a01c.get("red_flags_to_avoid"),
        a01b.get("direction_and_challenge_map"),
        a01a.get("risk_and_pressure_factors"),
    )
    writing_strategy = [
        "지원동기 문항은 industry_analysis_summary와 company_analysis_summary를 우선 연결한다.",
        "입사 후 포부 문항은 future_contribution_hooks와 company direction을 먼저 반영한다.",
        "직무 역량 문항은 role_analysis_summary, job_fit_hooks, role_keyword_map을 우선 사용한다.",
        "명시 근거가 약한 산업/직무 추론은 [inference] 표시를 유지한다.",
        "후속 agent에는 종합 output(agent-01)만 전달해도 동작하도록 키 필드를 유지한다.",
    ]

    return {
        "role_summary": role_summary,
        "competency_table": normalize_list(a01c.get("competency_table")),
        "culture_and_tone_hints": culture_and_tone_hints,
        "talent_profile_mapping": talent_profile_mapping,
        "red_flags_to_avoid": red_flags,
        "writing_strategy_for_applicant": writing_strategy,
        "industry_analysis_summary": first_non_empty(a01a.get("industry_analysis_summary"), a01a.get("industry_summary")),
        "company_analysis_summary": first_non_empty(a01b.get("company_analysis_summary"), a01b.get("company_summary")),
        "role_analysis_summary": first_non_empty(a01c.get("role_analysis_summary"), a01c.get("role_summary")),
        "role_keyword_map": role_keyword_map,
        "motivation_hooks": motivation_hooks,
        "future_contribution_hooks": future_contribution_hooks,
        "job_fit_hooks": job_fit_hooks,
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


def write_markdown_report(path: Path, title: str, payload: dict[str, Any]) -> None:
    lines = [f"# {title}"]
    for key, value in payload.items():
        lines.append("")
        lines.append(render_markdown_section(key, value))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def save_outputs_to_cache(state: dict[str, Any], cache_root: Path) -> dict[str, Any]:
    outputs = state.get("agent_outputs", {})
    if not isinstance(outputs, dict):
        outputs = {}

    company_name = str(state.get("company_name") or "").strip()
    role_title = str(state.get("role_title") or "").strip()
    if not company_name or not role_title:
        return {"cache_saved_agents": []}

    key = f"{slugify(company_name)}__{slugify(role_title)}"
    base = cache_root / key
    base.mkdir(parents=True, exist_ok=True)
    snapshot_dir = base / "snapshots" / datetime.now().strftime("%Y%m%d-%H%M%S")
    snapshot_dir.mkdir(parents=True, exist_ok=True)

    synthesized = synthesize_agent01_output(outputs)
    if synthesized and not outputs.get("agent-01"):
        outputs["agent-01"] = synthesized

    saved_agents: list[str] = []
    md_targets = {
        "agent-01a": "industry-analysis-latest.md",
        "agent-01b": "company-analysis-latest.md",
        "agent-01c": "role-analysis-latest.md",
        "agent-01": "combined-analysis-latest.md",
    }
    json_targets = {
        "agent-01a": "agent-01a-industry-latest.json",
        "agent-01b": "agent-01b-company-latest.json",
        "agent-01c": "agent-01c-role-latest.json",
    }
    for agent_id, output in outputs.items():
        if not isinstance(output, dict) or not output:
            continue
        latest_name = json_targets.get(agent_id, f"{agent_id}-latest.json")
        latest_path = base / latest_name
        latest_path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
        snap_name = latest_name.replace("-latest.json", ".json")
        snap_path = snapshot_dir / snap_name
        snap_path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
        if agent_id in md_targets:
            md_path = base / md_targets[agent_id]
            snap_md_path = snapshot_dir / md_targets[agent_id].replace("-latest.md", ".md")
            title = {
                "agent-01a": "Industry Analysis",
                "agent-01b": "Company Analysis",
                "agent-01c": "Role Analysis",
                "agent-01": "Combined Analysis",
            }[agent_id]
            write_markdown_report(md_path, title, output)
            write_markdown_report(snap_md_path, title, output)
        saved_agents.append(agent_id)

    meta = {
        "company_name": company_name,
        "role_title": role_title,
        "updated_at": datetime.now().isoformat(timespec="seconds"),
        "saved_agents": saved_agents,
    }
    (base / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"cache_dir": str(base), "cache_saved_agents": saved_agents}


def compute_budget(char_limit: int | None) -> int | None:
    if not isinstance(char_limit, int) or char_limit <= 0:
        return None
    return max(char_limit - 20, min(char_limit, round(char_limit * 0.9)))


def is_manual_per_step(state: dict[str, Any]) -> bool:
    return str(state.get("step_approval_mode") or DEFAULT_APPROVAL_MODE) == "manual_per_step"


def is_approved(state: dict[str, Any], agent: str) -> bool:
    approvals = state.get("step_approvals", {})
    if not isinstance(approvals, dict):
        return False
    return bool(approvals.get(agent))


def normalize_questions(state: dict[str, Any]) -> list[dict[str, Any]]:
    q_list = state.get("application_questions", [])
    normalized: list[dict[str, Any]] = []

    if isinstance(q_list, list):
        for idx, q in enumerate(q_list, start=1):
            if not isinstance(q, dict):
                continue
            qid = q.get("question_id") or f"Q{idx:02d}"
            text = q.get("question_text") or ""
            char_limit = q.get("char_limit")
            normalized.append(
                {
                    "question_id": qid,
                    "question_text": text,
                    "char_limit": char_limit,
                    "recommended_char_budget": compute_budget(char_limit),
                }
            )

    if not normalized:
        q_text = state.get("question_text")
        q_limit = state.get("char_limit")
        if q_text:
            qid = state.get("question_id") or "Q01"
            normalized.append(
                {
                    "question_id": qid,
                    "question_text": q_text,
                    "char_limit": q_limit,
                    "recommended_char_budget": compute_budget(q_limit),
                }
            )

    return normalized


def build_step_states(state: dict[str, Any]) -> list[StepState]:
    outputs = state.get("agent_outputs", {})
    if not isinstance(outputs, dict):
        outputs = {}

    normalized_questions = normalize_questions(state)

    primary_question = normalized_questions[0] if normalized_questions else {}

    outputs["agent-01"] = outputs.get("agent-01") or synthesize_agent01_output(outputs)

    a01_input = {
        "company_name": state.get("company_name"),
        "role_title": state.get("role_title"),
        "job_posting_text_or_link": state.get("job_posting_text_or_link"),
        "industry_context": state.get("industry_context", ""),
    }
    a01a_input = dict(a01_input)
    a01b_input = dict(a01_input)
    a01c_input = dict(a01_input)
    a01_synth_input = {
        **a01_input,
        "industry_analysis_summary": outputs.get("agent-01a", {}).get("industry_analysis_summary")
        or outputs.get("agent-01a", {}).get("industry_summary"),
        "company_analysis_summary": outputs.get("agent-01b", {}).get("company_analysis_summary")
        or outputs.get("agent-01b", {}).get("company_summary"),
        "role_analysis_summary": outputs.get("agent-01c", {}).get("role_analysis_summary")
        or outputs.get("agent-01c", {}).get("role_summary"),
        "industry_keywords": outputs.get("agent-01a", {}).get("industry_keywords"),
        "company_keywords": outputs.get("agent-01b", {}).get("company_keywords"),
        "role_keyword_map": outputs.get("agent-01c", {}).get("role_keyword_map"),
        "competency_table": outputs.get("agent-01c", {}).get("competency_table"),
        "motivation_hooks": combine_unique(
            outputs.get("agent-01a", {}).get("motivation_hooks"),
            outputs.get("agent-01b", {}).get("motivation_hooks"),
        ),
        "future_contribution_hooks": combine_unique(
            outputs.get("agent-01a", {}).get("future_contribution_hooks"),
            outputs.get("agent-01b", {}).get("future_contribution_hooks"),
        ),
        "job_fit_hooks": outputs.get("agent-01c", {}).get("job_fit_hooks"),
    }
    a00_input = {
        "company_name": state.get("company_name"),
        "role_title": state.get("role_title"),
        "job_posting_text_or_link": state.get("job_posting_text_or_link"),
        "application_questions": normalized_questions,
        "candidate_profile": state.get("candidate_profile"),
        "experience_notes": state.get("experience_notes"),
        "forbidden_claims_or_constraints": state.get("forbidden_claims_or_constraints")
        or state.get("forbidden_words_or_phrases", []),
    }
    a02a_input = {
        "application_questions": normalized_questions,
        "role_keyword_map": outputs.get("agent-01", {}).get("role_keyword_map"),
        "essay_corpus_path": state.get("essay_corpus_path", DEFAULT_CORPUS_PATH),
        "essay_corpus_candidates": state.get("essay_corpus_candidates"),
        "candidate_profile": state.get("candidate_profile"),
        "new_experience_notes": state.get("new_experience_notes", []),
    }
    a02_input = {
        "candidate_profile": state.get("candidate_profile"),
        "experience_notes": state.get("experience_notes")
        or outputs.get("agent-02a", {}).get("draft_ready_experience_notes"),
        "target_role_keywords": state.get("target_role_keywords") or outputs.get("agent-01", {}).get("role_keyword_map"),
        "question_text": primary_question.get("question_text") or state.get("question_text"),
        "char_limit": primary_question.get("char_limit") or state.get("char_limit"),
    }
    a03_input = {
        "application_questions": normalized_questions,
        "evidence_cards": outputs.get("agent-02", {}).get("evidence_cards"),
        "competency_table": outputs.get("agent-01", {}).get("competency_table"),
    }
    a03b_input = {
        "application_questions": normalized_questions,
        "matching_table": outputs.get("agent-03", {}).get("matching_table"),
        "evidence_cards": outputs.get("agent-02", {}).get("evidence_cards"),
        "competency_table": outputs.get("agent-01", {}).get("competency_table"),
    }
    a03c_input = {
        "application_questions": normalized_questions,
        "refined_evidence_cards": outputs.get("agent-03b", {}).get("refined_evidence_cards")
        or outputs.get("agent-02", {}).get("evidence_cards"),
        "matching_table": outputs.get("agent-03", {}).get("matching_table"),
    }
    a04_input = {
        "question_plans": outputs.get("agent-03b", {}).get("drafting_handoff")
        or outputs.get("agent-03", {}).get("matching_table")
        or normalized_questions,
        "target_tone": state.get("target_tone", ""),
        "selected_evidence_cards": outputs.get("agent-03c", {}).get("verified_evidence_cards")
        or outputs.get("agent-03b", {}).get("refined_evidence_cards")
        or outputs.get("agent-02", {}).get("evidence_cards"),
        "metric_usage_guidelines": outputs.get("agent-03c", {}).get("metric_usage_guidelines"),
        "role_keyword_map": outputs.get("agent-01", {}).get("role_keyword_map"),
        "motivation_hooks": outputs.get("agent-01", {}).get("motivation_hooks"),
        "future_contribution_hooks": outputs.get("agent-01", {}).get("future_contribution_hooks"),
        "job_fit_hooks": outputs.get("agent-01", {}).get("job_fit_hooks"),
    }
    a05_input = {
        "draft_answer": outputs.get("agent-04", {}).get("draft_answer"),
        "company_tone_hints": outputs.get("agent-01", {}).get("culture_and_tone_hints"),
        "forbidden_words_or_phrases": state.get("forbidden_words_or_phrases", []),
    }
    a06_input = {
        "final_draft": outputs.get("agent-05", {}).get("revised_draft") or outputs.get("agent-04", {}).get("draft_answer"),
        "question_text": primary_question.get("question_text") or state.get("question_text"),
        "char_limit": primary_question.get("char_limit") or state.get("char_limit"),
    }
    a07_input = {
        "question_text": primary_question.get("question_text") or state.get("question_text"),
        "char_limit": primary_question.get("char_limit") or state.get("char_limit"),
        "final_recommended_version": outputs.get("agent-06", {}).get("final_recommended_version"),
        "qa_checklist": outputs.get("agent-06", {}).get("final_qa_checklist"),
        "flagged_lines": outputs.get("agent-06", {}).get("flagged_lines_table"),
        "version_notes": state.get("version_notes", ""),
        "external_feedback_notes": state.get("external_feedback_notes", ""),
    }

    required_map = {
        "agent-00": ["company_name", "role_title", "job_posting_text_or_link"],
        "agent-01a": ["company_name", "role_title", "job_posting_text_or_link"],
        "agent-01b": ["company_name", "role_title", "job_posting_text_or_link"],
        "agent-01c": ["company_name", "role_title", "job_posting_text_or_link"],
        "agent-01": ["industry_analysis_summary", "company_analysis_summary", "role_analysis_summary"],
        "agent-02a": ["application_questions", "role_keyword_map", "essay_corpus_path", "candidate_profile"],
        "agent-02": ["candidate_profile", "experience_notes", "target_role_keywords"],
        "agent-03": ["application_questions", "evidence_cards", "competency_table"],
        "agent-03b": ["application_questions", "matching_table", "evidence_cards", "competency_table"],
        "agent-03c": ["application_questions", "refined_evidence_cards", "matching_table"],
        "agent-04": ["question_plans", "selected_evidence_cards"],
        "agent-05": ["draft_answer", "company_tone_hints"],
        "agent-06": ["final_draft", "question_text", "char_limit"],
        "agent-07": ["question_text", "char_limit", "final_recommended_version", "qa_checklist"],
    }

    input_map = {
        "agent-00": a00_input,
        "agent-01a": a01a_input,
        "agent-01b": a01b_input,
        "agent-01c": a01c_input,
        "agent-01": a01_synth_input,
        "agent-02a": a02a_input,
        "agent-02": a02_input,
        "agent-03": a03_input,
        "agent-03b": a03b_input,
        "agent-03c": a03c_input,
        "agent-04": a04_input,
        "agent-05": a05_input,
        "agent-06": a06_input,
        "agent-07": a07_input,
    }

    states: list[StepState] = []
    manual_approval = is_manual_per_step(state)

    for agent in PIPELINE:
        payload = input_map[agent]
        missing: list[str] = []
        for key in required_map[agent]:
            value = payload.get(key)
            if value is None or value == "" or value == []:
                missing.append(key)

        # Hard gate: corpus discovery must approve proceeding to agent-02.
        if agent == "agent-02":
            ready_flag = outputs.get("agent-02a", {}).get("ready_for_agent_02")
            if ready_flag is False:
                missing.append("agent-02a.ready_for_agent_02=true")

        # Hard gate: external feedback is mandatory before final packaging.
        if agent == "agent-07" and bool(state.get("external_feedback_required", True)):
            if not state.get("external_feedback_notes"):
                missing.append("external_feedback_notes")

        agent_output = outputs.get(agent)
        has_meaningful_output = bool(agent_output)
        if agent == "agent-00" and not has_meaningful_output and bool(outputs.get("agent-01")):
            has_meaningful_output = True

        if has_meaningful_output:
            if manual_approval and not is_approved(state, agent):
                status = "awaiting_approval"
            else:
                status = "complete"
        else:
            status = "ready" if not missing else "blocked"

        states.append(StepState(agent=agent, status=status, missing_fields=missing, input_payload=payload))

    return states


def next_action_from_steps(steps: list[StepState]) -> dict[str, Any]:
    next_step = next((s for s in steps if s.status != "complete"), None)
    if not next_step:
        return {"type": "done", "agent": None, "status": "done"}

    if next_step.status == "awaiting_approval":
        return {
            "type": "approval_required",
            "agent": next_step.agent,
            "status": next_step.status,
            "instruction": f"Set step_approvals.{next_step.agent}=true in state.json after user confirms.",
        }

    if next_step.status == "blocked":
        missing = next_step.missing_fields
        if "agent-02a.ready_for_agent_02=true" in missing:
            return {
                "type": "additional_input_required",
                "agent": "agent-02a",
                "status": "blocked",
                "instruction": "Collect missing non-corpus experiences and rerun agent-02a.",
                "missing_fields": missing,
            }
        return {
            "type": "missing_input",
            "agent": next_step.agent,
            "status": next_step.status,
            "missing_fields": missing,
        }

    return {
        "type": "run_agent",
        "agent": next_step.agent,
        "status": next_step.status,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate and orchestrate agent pipeline state.")
    parser.add_argument("--input", default=None, help="Path to pipeline state JSON")
    parser.add_argument("--run-dir", default=None, help="Question-level run directory containing state.json")
    parser.add_argument(
        "--init-run-dir",
        action="store_true",
        help="Create run directory scaffold (state/artifact files) before loading state",
    )
    parser.add_argument(
        "--cache-root",
        default=str(DEFAULT_CACHE_ROOT),
        help='Cache root directory (default: "~/Desktop/회사 직무 분석")',
    )
    parser.add_argument(
        "--no-cache-load",
        action="store_true",
        help="Disable automatic loading of agent-01 output from cache",
    )
    parser.add_argument(
        "--no-cache-save",
        action="store_true",
        help="Disable automatic saving of available agent outputs to cache",
    )
    parser.add_argument(
        "--write-next-input",
        default=None,
        help="Optional path to write next runnable agent input payload JSON",
    )
    parser.add_argument(
        "--write-state",
        default=None,
        help="Optional path to write the normalized/updated state JSON",
    )
    parser.add_argument(
        "--essay-corpus-path",
        default=None,
        help='Override essay corpus directory for agent-02a (default: "~/Desktop/취업/자기소개서")',
    )
    args = parser.parse_args()

    if not args.input and not args.run_dir:
        raise SystemExit("Provide --input or --run-dir")

    seed_state: dict[str, Any] | None = None
    if args.input and args.run_dir and args.init_run_dir:
        seed_state = load_json(args.input)

    if args.run_dir:
        run_dir = Path(args.run_dir).expanduser()
        state_path = run_dir / "state.json"
        if args.init_run_dir:
            state_path = ensure_run_dir_layout(run_dir, seed_state)
        elif not state_path.exists():
            raise SystemExit(f"state.json not found in run_dir: {run_dir}")
        state = load_json(state_path)
    else:
        state_path = Path(args.input).expanduser()
        state = load_json(state_path)

    # Default behavior for new manual flow.
    state.setdefault("step_approval_mode", DEFAULT_APPROVAL_MODE)
    state.setdefault("step_approvals", {})
    state.setdefault("external_feedback_required", True)
    state.setdefault("agent_outputs", {})

    if args.essay_corpus_path:
        state["essay_corpus_path"] = str(Path(args.essay_corpus_path).expanduser())

    cache_root = Path(args.cache_root).expanduser()
    if not args.no_cache_load:
        state = maybe_hydrate_agent01_from_cache(state, cache_root)

    cache_save_report: dict[str, Any] = {}
    if not args.no_cache_save:
        cache_save_report = save_outputs_to_cache(state, cache_root)

    steps = build_step_states(state)
    action = next_action_from_steps(steps)

    report = {
        "pipeline": [
            {
                "agent": s.agent,
                "status": s.status,
                "missing_fields": s.missing_fields,
            }
            for s in steps
        ],
        "next_agent": action.get("agent"),
        "next_agent_status": action.get("status", "done"),
        "next_action": action,
        "step_approval_mode": state.get("step_approval_mode"),
        "external_feedback_required": bool(state.get("external_feedback_required", True)),
    }

    if args.run_dir:
        report["run_dir"] = str(Path(args.run_dir).expanduser())
        report["required_artifacts"] = REQUIRED_RUN_DIR_FILES

    if state.get("_cache_agent01_loaded_from"):
        report["cache_agent01_loaded_from"] = state["_cache_agent01_loaded_from"]
    if cache_save_report:
        report.update(cache_save_report)

    print(json.dumps(report, ensure_ascii=False, indent=2))

    if args.write_next_input and action.get("type") == "run_agent":
        next_agent = action["agent"]
        next_step = next((s for s in steps if s.agent == next_agent), None)
        if next_step:
            Path(args.write_next_input).write_text(
                json.dumps(next_step.input_payload, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            print(f"\n[next-input] wrote payload for {next_agent} -> {args.write_next_input}")

    write_state_target = args.write_state
    if not write_state_target and args.run_dir:
        write_state_target = str(Path(args.run_dir).expanduser() / "state.json")
    if write_state_target:
        write_json(Path(write_state_target).expanduser(), state)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
