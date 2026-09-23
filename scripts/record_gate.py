#!/usr/bin/env python3
"""Execute one controlled gate, archive output, and atomically update evidence."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import os
from pathlib import Path
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]


def atomic_json(path: Path, value: dict) -> None:
    fd, raw = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    tmp = Path(raw)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(tmp, path)
    finally:
        tmp.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--loop", required=True)
    parser.add_argument("--gate", required=True)
    parser.add_argument("--actor", required=True)
    parser.add_argument("--actor-role", choices=("implementation", "independent_qa"), required=True)
    parser.add_argument("--revision-note", default=None,
                        help="D-15：若本纪元的重记属『制品 revision 变更后重记』而非『修复尝试』，"
                             "须显式给出说明以开启新的 revision 纪元（不写则不放过）")
    args = parser.parse_args()
    loop = ROOT / "loops" / args.loop
    try:
        spec = json.loads((loop / "LOOP.yaml").read_text(encoding="utf-8"))
        evidence_path = loop / "EVIDENCE.json"
        evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
        gate = next((item for item in spec["gates"] if item["id"] == args.gate), None)
        if not gate:
            raise ValueError(f"unknown gate: {args.gate}")
        if gate.get("owner_kind") != args.actor_role:
            raise ValueError("actor role does not own this gate")
        state = json.loads((loop / "STATE.json").read_text(encoding="utf-8"))
        if state.get("status") != "in_progress":
            raise ValueError("gates may execute only while loop status is in_progress")
        if args.actor_role == "implementation" and args.actor != state.get("implementation_actor"):
            raise ValueError("implementation actor must hold the loop baton")
        if args.actor_role == "independent_qa" and args.actor == state.get("implementation_actor"):
            raise ValueError("implementation actor cannot self-sign independent QA")

        iter_log = loop / "memory/waves/W0-ITER.md"
        spec_text = iter_log.read_text(encoding="utf-8")
        # D-15：预算按 **revision 纪元** 计数 —— 只统计最后一个 `## Revision epoch` 标记之后的尝试。
        # 原意是阻止『对同一失败门禁无限重试』；而『制品 revision 变更后的重记』与之在计数上不可区分，
        # 故改为分纪元计数，且**开启新纪元必须显式说明**（不写即不放过，避免静默绕过）。
        markers = list(re.finditer(r"(?m)^## Revision epoch (\d+)｜", spec_text))
        epoch = int(markers[-1].group(1)) if markers else 0
        scope = spec_text[markers[-1].start():] if markers else spec_text
        attempts = scope.count(f"Gate: `{args.gate}`")
        max_attempts = int(spec.get("repair_policy", {}).get("max_attempts_per_gate", 0))
        if max_attempts < 1:
            raise ValueError("max_attempts_per_gate 未配置")
        if attempts >= max_attempts:
            if not args.revision_note:
                raise ValueError(
                    f"gate attempt budget exhausted: {attempts}/{max_attempts}（revision 纪元 {epoch}）"
                    " —— 若确属**制品 revision 变更后的重记**，须以 --revision-note 显式开启新纪元（D-15）")
            epoch += 1
            with iter_log.open("a", encoding="utf-8") as stream:
                stream.write(f"\n## Revision epoch {epoch}｜{args.revision_note}｜"
                             f"{dt.datetime.now(dt.timezone.utc).isoformat()}\n"
                             "- 依 **D-15**：预算按 revision 纪元计数（修复尝试与 revision 重记口径分离）。\n")
            attempts = 0

        now = dt.datetime.now(dt.timezone.utc)
        stamp = now.strftime("%Y%m%dT%H%M%SZ")
        log = loop / "evidence" / f"{args.gate}-{stamp}.log"
        log.parent.mkdir(parents=True, exist_ok=True)
        result = subprocess.run(gate["command"], cwd=ROOT, shell=True, executable="/bin/bash", text=True, capture_output=True, check=False)
        output = f"COMMAND={gate['command']}\nEXIT_CODE={result.returncode}\nSTDOUT\n{result.stdout}\nSTDERR\n{result.stderr}"
        log.write_text(output, encoding="utf-8")
        relative_log = log.relative_to(ROOT).as_posix()
        output_hash = hashlib.sha256(log.read_bytes()).hexdigest()
        evidence["gates"][args.gate] = {
            # exit 3 = INCOMPLETE/NOT_EVALUATED ⇒ 板面记 inconclusive（PENDING_EXTERNAL_AUTHORITY），
            # 不得与 FAIL 混同（"FAIL 不得换口径"的反向也成立：未判定不得被记成失败）。
            "status": ("pass" if result.returncode == 0
                       else ("inconclusive" if result.returncode == 3 else "fail")),
            "command": gate["command"],
            "exit_code": result.returncode,
            "actor": args.actor,
            "actor_role": args.actor_role,
            "executed_at": now.isoformat(),
            "evidence_file": relative_log,
            "output_sha256": output_hash,
        }
        atomic_json(evidence_path, evidence)

        attempts += 1
        with iter_log.open("a", encoding="utf-8") as stream:
            stream.write(f"\n## Attempt {attempts + 1}｜{stamp}\n\n- Gate: `{args.gate}`\n- Revision epoch: {epoch}\n- Command: `{gate['command']}`\n- Exit: `{result.returncode}`\n- Evidence: `{relative_log}`\n- SHA256: `{output_hash}`\n")
        if result.returncode != 0:
            with (loop / "FAILURES.md").open("a", encoding="utf-8") as stream:
                stream.write(f"\n## {stamp}｜{args.gate}\n\n- Command: `{gate['command']}`\n- Exit: `{result.returncode}`\n- Evidence: `{relative_log}`\n- Classification: `PENDING_ROOT_CAUSE`\n- Next: diagnose, record root cause, fix, rerun the original gate.\n")
        print(output)
        return result.returncode
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"record-gate: FAIL: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
