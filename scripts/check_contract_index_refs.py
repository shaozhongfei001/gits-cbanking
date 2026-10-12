#!/usr/bin/env python3
"""Fail-closed check: CONTRACT_INDEX authority_source count is non-zero and files exist."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "specs/CONTRACT_INDEX.yaml"


def main() -> int:
    if not INDEX.is_file():
        print("FAIL: specs/CONTRACT_INDEX.yaml not found", file=sys.stderr)
        return 2
    try:
        payload = json.loads(INDEX.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"FAIL: CONTRACT_INDEX is not parseable JSON: {exc}", file=sys.stderr)
        return 2
    contracts = payload.get("contracts")
    if not isinstance(contracts, list) or not contracts:
        print("FAIL: contracts list is empty", file=sys.stderr)
        return 2
    sources = []
    for item in contracts:
        src = item.get("authority_source")
        if isinstance(src, str) and src.strip():
            sources.append(src.strip())
    unique = sorted(set(sources))
    if len(unique) < 1:
        print("FAIL: unique authority_source count is 0", file=sys.stderr)
        return 2
    missing = [src for src in unique if not (ROOT / src).is_file()]
    if missing:
        for src in missing:
            print(f"MISSING: {src}", file=sys.stderr)
        return 2
    print(f"PASS: {len(unique)} unique authority_source file(s); {len(contracts)} contract records")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
