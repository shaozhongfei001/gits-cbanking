#!/usr/bin/env python3
"""Fail if CI does not invoke check_contract_index_refs.py (prevents grep empty-pass)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WF = ROOT / ".github/workflows/ci.yml"
NEEDLE = "scripts/check_contract_index_refs.py"


def main() -> int:
    if not WF.is_file():
        print("FAIL: .github/workflows/ci.yml not found", file=sys.stderr)
        return 2
    text = WF.read_text(encoding="utf-8")
    if NEEDLE not in text:
        print(f"FAIL: CI workflow must call {NEEDLE}", file=sys.stderr)
        return 2
    print("PASS: CI workflow invokes check_contract_index_refs.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
