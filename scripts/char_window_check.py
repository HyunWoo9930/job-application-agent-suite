#!/usr/bin/env python3
"""Validate that draft length is within [char_limit - window, char_limit]."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def read_text(file_path: str | None) -> str:
    if file_path:
        return Path(file_path).read_text(encoding="utf-8")
    return sys.stdin.read()


def main() -> int:
    parser = argparse.ArgumentParser(description="Check character window for application draft.")
    parser.add_argument("--file", default=None, help="Path to draft text file (optional if using stdin)")
    parser.add_argument("--char-limit", type=int, required=True, help="Character limit N")
    parser.add_argument(
        "--window",
        type=int,
        default=20,
        help="Allowed under-limit window. Default: 20 (valid range is N-20..N)",
    )
    parser.add_argument(
        "--count-mode",
        choices=["raw", "no-newline", "no-space"],
        default="raw",
        help="Character counting mode. raw: 그대로, no-newline: 줄바꿈 제외, no-space: 공백/줄바꿈 제외",
    )
    args = parser.parse_args()

    text = read_text(args.file)
    if args.count_mode == "no-newline":
        counted = text.replace("\n", "").replace("\r", "")
    elif args.count_mode == "no-space":
        counted = "".join(ch for ch in text if not ch.isspace())
    else:
        counted = text
    char_count = len(counted)

    min_chars = args.char_limit - args.window
    max_chars = args.char_limit

    print("=== Character Window Check ===")
    print(f"count_mode: {args.count_mode}")
    print(f"char_count: {char_count}")
    print(f"allowed_range: {min_chars}..{max_chars}")

    if char_count < min_chars:
        print(f"status: FAIL (too short by {min_chars - char_count} chars)")
        return 1
    if char_count > max_chars:
        print(f"status: FAIL (too long by {char_count - max_chars} chars)")
        return 1

    print("status: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
