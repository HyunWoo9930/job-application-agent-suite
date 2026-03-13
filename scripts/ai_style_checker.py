#!/usr/bin/env python3
"""Heuristic checker for AI-like patterns in Korean application drafts."""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from pathlib import Path

GENERIC_PHRASES = [
    "성장",
    "역량",
    "도전",
    "가치",
    "최선을 다",
    "문제를 해결",
    "협업",
    "소통",
    "주도적",
    "기여",
    "보탬",
    "최적화",
    "신뢰",
    "확신",
    "분명",
]

DECLARATIVE_ENDINGS = [
    "기여하겠습니다",
    "성장하겠습니다",
    "노력하겠습니다",
    "보탬이 되겠습니다",
    "최선을 다하겠습니다",
]


def read_text(file_path: str | None) -> str:
    if file_path:
        return Path(file_path).read_text(encoding="utf-8")
    return sys.stdin.read()


def split_sentences(text: str) -> list[str]:
    # Keep sentence endings so declaration-style checks can inspect full lines.
    parts = re.split(r"(?<=[.!?。！？])\s+", text.strip())
    return [p.strip() for p in parts if p.strip()]


def text_lines(text: str) -> list[tuple[int, str]]:
    lines: list[tuple[int, str]] = []
    for idx, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if stripped:
            lines.append((idx, stripped))
    return lines


def tokenize(text: str) -> list[str]:
    return re.findall(r"[가-힣A-Za-z0-9]+", text)


def repeated_ngrams(tokens: list[str], n: int = 3, min_count: int = 2) -> list[tuple[str, int]]:
    if len(tokens) < n:
        return []
    grams = [" ".join(tokens[i : i + n]) for i in range(len(tokens) - n + 1)]
    counts = Counter(grams)
    return sorted([(g, c) for g, c in counts.items() if c >= min_count], key=lambda x: (-x[1], x[0]))


def detect_generic_phrases(text: str) -> list[tuple[str, int]]:
    found: list[tuple[str, int]] = []
    for phrase in GENERIC_PHRASES:
        count = text.count(phrase)
        if count:
            found.append((phrase, count))
    return sorted(found, key=lambda x: (-x[1], x[0]))


def detect_declarative_endings(lines: list[tuple[int, str]]) -> list[tuple[int, str]]:
    flagged: list[tuple[int, str]] = []
    for line_no, line in lines:
        compact = re.sub(r"\s+", "", line)
        if any(ending in compact for ending in DECLARATIVE_ENDINGS):
            flagged.append((line_no, line))
    return flagged


def repeated_sentence_starters(sentences: list[str], k: int = 2) -> list[tuple[str, int]]:
    starters = []
    for s in sentences:
        tokens = tokenize(s)
        if not tokens:
            continue
        starters.append(" ".join(tokens[:k]))
    counts = Counter(starters)
    return sorted([(st, c) for st, c in counts.items() if c >= 2], key=lambda x: (-x[1], x[0]))


def risk_level(score: int) -> str:
    if score >= 7:
        return "HIGH"
    if score >= 4:
        return "MEDIUM"
    return "LOW"


def flagged_line_report(lines: list[tuple[int, str]]) -> list[tuple[int, str, str]]:
    """Return per-line issues with line number for deterministic rewrites."""
    flagged: list[tuple[int, str, str]] = []
    for line_no, line in lines:
        compact = re.sub(r"\s+", "", line)
        line_tokens = tokenize(line)
        generic_hits = [p for p in GENERIC_PHRASES if p in line]
        if generic_hits:
            flagged.append((line_no, "generic", f"generic phrases: {', '.join(generic_hits[:3])}"))
        if any(ending in compact for ending in DECLARATIVE_ENDINGS):
            flagged.append((line_no, "declarative", "declaration-style ending"))
        if len(line_tokens) > 28:
            flagged.append((line_no, "long-line", "sentence likely too long for readability"))
    return flagged


def main() -> int:
    parser = argparse.ArgumentParser(description="Check AI-like writing patterns.")
    parser.add_argument("--file", help="Path to input text file", default=None)
    args = parser.parse_args()

    text = read_text(args.file).strip()
    if not text:
        print("[error] no text provided")
        return 1

    sentences = split_sentences(text)
    lines = text_lines(text)
    tokens = tokenize(text)
    avg_sentence_len = (len(tokens) / len(sentences)) if sentences else 0.0

    generic_hits = detect_generic_phrases(text)
    repeated_trigrams = repeated_ngrams(tokens, n=3, min_count=2)
    declarative_hits = detect_declarative_endings(lines)
    repeated_starters = repeated_sentence_starters(sentences, k=2)
    flagged_lines = flagged_line_report(lines)

    score = 0
    if avg_sentence_len > 22:
        score += 2
    elif avg_sentence_len > 18:
        score += 1

    generic_unique = len(generic_hits)
    generic_total = sum(c for _, c in generic_hits)
    if generic_total >= 8:
        score += 3
    elif generic_total >= 4:
        score += 2
    elif generic_total >= 2:
        score += 1
    if generic_unique >= 3:
        score += 1

    repeated_count = len(repeated_trigrams)
    if repeated_count >= 2:
        score += 2
    elif repeated_count == 1:
        score += 1

    declarative_count = len(declarative_hits)
    if declarative_count >= 2:
        score += 2
    elif declarative_count == 1:
        score += 1

    starter_repeat_count = len(repeated_starters)
    if starter_repeat_count >= 2:
        score += 1

    print("=== AI Style Heuristic Report ===")
    print(f"sentences: {len(sentences)}")
    print(f"tokens: {len(tokens)}")
    print(f"avg_sentence_len: {avg_sentence_len:.2f}")
    print(f"risk: {risk_level(score)} (score={score})")

    print("\n[generic phrase hits]")
    if generic_hits:
        for phrase, count in generic_hits:
            print(f"- {phrase}: {count}")
    else:
        print("- none")

    print("\n[repeated 3-grams]")
    if repeated_trigrams:
        for gram, count in repeated_trigrams[:20]:
            print(f"- {gram}: {count}")
    else:
        print("- none")

    print("\n[declarative ending hits]")
    if declarative_hits:
        for line_no, line in declarative_hits[:20]:
            print(f"- L{line_no}: {line}")
    else:
        print("- none")

    print("\n[repeated sentence starters]")
    if repeated_starters:
        for starter, count in repeated_starters:
            print(f"- {starter}: {count}")
    else:
        print("- none")

    print("\n[flagged lines with line_no]")
    if flagged_lines:
        for line_no, issue_type, reason in flagged_lines[:30]:
            print(f"- L{line_no} [{issue_type}]: {reason}")
    else:
        print("- none")

    print("\n[note]")
    print("Strict heuristic mode is enabled. Treat MEDIUM/HIGH as revise-required.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
