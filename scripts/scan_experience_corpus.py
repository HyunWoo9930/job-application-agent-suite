#!/usr/bin/env python3
"""Scan local self-introduction corpus and extract reusable experience candidates."""

from __future__ import annotations

import argparse
import json
import re
import zipfile
from pathlib import Path
from typing import Any

TEXT_EXTS = {".txt", ".md", ".markdown", ".rst"}
DOCX_EXTS = {".docx"}
SUPPORTED_EXTS = TEXT_EXTS | DOCX_EXTS

ACTION_KEYWORDS = [
    "개선",
    "구축",
    "설계",
    "개발",
    "최적화",
    "자동화",
    "분석",
    "운영",
    "해결",
    "리팩토링",
]


def read_text_file(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def read_docx(path: Path) -> str:
    with zipfile.ZipFile(path) as zf:
        raw = zf.read("word/document.xml").decode("utf-8", errors="ignore")
    # Lightweight XML strip for prompt pre-processing.
    raw = re.sub(r"<[^>]+>", " ", raw)
    raw = re.sub(r"\s+", " ", raw).strip()
    return raw


def extract_text(path: Path) -> str:
    ext = path.suffix.lower()
    if ext in TEXT_EXTS:
        return read_text_file(path)
    if ext in DOCX_EXTS:
        return read_docx(path)
    return ""


def split_chunks(text: str) -> list[str]:
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    parts = re.split(r"(?<=[.!?。！？])\s+|\n+", text)
    return [p.strip() for p in parts if p.strip()]


def score_chunk(chunk: str) -> tuple[int, int]:
    metric_hits = len(re.findall(r"\d+(\.\d+)?\s*(%|배|건|명|ms|초|분|시간|원|개)", chunk))
    action_hits = sum(1 for kw in ACTION_KEYWORDS if kw in chunk)
    return metric_hits, action_hits


def build_candidate(file_path: Path, chunk: str, idx: int) -> dict[str, Any]:
    metric_hits, action_hits = score_chunk(chunk)
    title = chunk[:36] + ("..." if len(chunk) > 36 else "")
    confidence = "high" if metric_hits >= 1 and action_hits >= 1 else ("medium" if action_hits >= 1 else "low")
    return {
        "id": f"{file_path.stem[:12]}-{idx:03d}",
        "source_file": str(file_path),
        "title": title,
        "excerpt": chunk[:260],
        "signal": {
            "metric_hits": metric_hits,
            "action_hits": action_hits,
        },
        "confidence": confidence,
    }


def score_candidate(c: dict[str, Any]) -> int:
    conf = {"high": 3, "medium": 2, "low": 1}.get(str(c.get("confidence", "")).lower(), 0)
    signal = c.get("signal", {})
    metric_hits = int(signal.get("metric_hits", 0))
    action_hits = int(signal.get("action_hits", 0))
    return conf * 10 + metric_hits * 3 + action_hits * 2


def scan_dir(root: Path, max_files: int, max_candidates: int) -> dict[str, Any]:
    files = [p for p in sorted(root.rglob("*")) if p.is_file() and p.suffix.lower() in SUPPORTED_EXTS]
    files = files[:max_files]

    candidates: list[dict[str, Any]] = []
    for path in files:
        text = extract_text(path)
        chunks = split_chunks(text)
        scored = []
        for i, c in enumerate(chunks, start=1):
            metric_hits, action_hits = score_chunk(c)
            if metric_hits == 0 and action_hits == 0:
                continue
            scored.append((metric_hits, action_hits, i, c))
        scored.sort(key=lambda x: (x[0], x[1], len(x[3])), reverse=True)
        for metric_hits, action_hits, i, c in scored[:10]:
            candidates.append(build_candidate(path, c, i))
            if len(candidates) >= max_candidates:
                break
        if len(candidates) >= max_candidates:
            break

    ranked = sorted(candidates, key=score_candidate, reverse=True)
    scanned_experience_list = [
        {
            "id": c["id"],
            "source_file": c["source_file"],
            "title": c["title"],
            "confidence": c["confidence"],
        }
        for c in ranked
    ]
    suggested_for_use_now = [
        {
            "id": c["id"],
            "source_file": c["source_file"],
            "title": c["title"],
            "reason": "수치/행동 신호가 높아 재사용 우선 후보",
            "confidence": c["confidence"],
        }
        for c in ranked[: min(12, len(ranked))]
    ]

    return {
        "corpus_path": str(root),
        "scanned_files": len(files),
        "supported_extensions": sorted(SUPPORTED_EXTS),
        "candidates": ranked,
        "scanned_experience_list": scanned_experience_list,
        "suggested_for_use_now": suggested_for_use_now,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan self-introduction corpus for reusable experiences.")
    parser.add_argument(
        "--path",
        default=str(Path.home() / "Desktop" / "취업" / "자기소개서"),
        help='Corpus directory (default: "~/Desktop/취업/자기소개서")',
    )
    parser.add_argument("--max-files", type=int, default=50, help="Max files to scan")
    parser.add_argument("--max-candidates", type=int, default=80, help="Max candidate chunks")
    parser.add_argument("--write-output", default=None, help="Optional output JSON path")
    parser.add_argument("--state-input", default=None, help="Optional pipeline state JSON path to merge candidates")
    parser.add_argument("--write-state", default=None, help="Optional output state JSON path")
    args = parser.parse_args()

    root = Path(args.path).expanduser()
    if not root.exists() or not root.is_dir():
        raise SystemExit(f"invalid directory: {root}")

    result = scan_dir(root, max_files=args.max_files, max_candidates=args.max_candidates)
    text = json.dumps(result, ensure_ascii=False, indent=2)
    print(text)

    if args.write_output:
        Path(args.write_output).write_text(text, encoding="utf-8")

    if args.state_input and args.write_state:
        state_path = Path(args.state_input)
        state = json.loads(state_path.read_text(encoding="utf-8"))
        if not isinstance(state, dict):
            raise SystemExit("state-input must be a JSON object")
        state["essay_corpus_path"] = str(root)
        state["essay_corpus_candidates"] = result.get("candidates", [])
        Path(args.write_state).write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
