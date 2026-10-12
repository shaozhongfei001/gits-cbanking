#!/usr/bin/env python3
"""ONTO1 WI-A2｜消费者扫描变异复验（S4）。

目的：证明 `onto1_consumer_scan.py` 的门禁断言**不是空转**。
每个用例都是"注入已知故障 ⇒ 门禁必须 FAIL"或"注入已知样本 ⇒ 必须被检出"，
任何一条未按预期表现即整体 FAIL。

用例矩阵
    T01~T05 检出能力（合成根：类名/对象属性/IRI 字面量/ID 家族/文件名引用）
    T06     无规则匹配 ⇒ 门禁 FAIL（fail-closed，不得静默忽略）
    T07     基线类计数少 1 ⇒ 基线装载 FAIL（fail-closed）
    T08     基线哈希漂移 ⇒ 基线装载 FAIL（fail-closed）
    T09     只扫单仓（KERT 期望命中缺失）⇒ 门禁 FAIL（期望值锚定有牙齿）
    T10     规则把全部命中豁免化 ⇒ 门禁 FAIL（净义务锚点有牙齿）
    T11     规则全部落 PENDING_TRIAGE ⇒ 门禁 FAIL（处置完成度有牙齿）
    T12     对照：正式规则 + 正式缓存 ⇒ 门禁 PASS（证明以上 FAIL 不是恒真）
"""

from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCANNER = ROOT / "scripts/onto1_consumer_scan.py"
EVIDENCE_DIR = ROOT / "loops/ONTO1-ontology-split/evidence"
REAL_RULES = EVIDENCE_DIR / "consumer-scan-dispositions.json"
REAL_HITS = EVIDENCE_DIR / "consumer-scan-hits.jsonl"


def load_scanner():
    spec = importlib.util.spec_from_file_location("onto1_consumer_scan", SCANNER)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


SYNTHETIC_TREE = {
    "a/class_sample.py": "def f():\n    return OperatingCase\n",
    "a/prop_sample.py": "x = authorizedBy\n",
    "a/iri_sample.ttl": "@prefix gits: <https://gits.bank.example/ontology/core#> .\n: s gits-core .\n",
    "a/ids_sample.py": (
        'MAP = "KM-CORP-RM-OUTREACH"\n'
        'AC = "AC-PRODUCT-RECOMMEND-001"\n'
        'ASSET = "ASSET-KNOW-PRODUCT-CARDS"\n'
        'SP = "SP-15"\n'
        'KI = "KI-FRONT-001"\n'
        'KD = "KD-DOC-001"\n'
        'CTR = "CTR-SEM-002"\n'
    ),
    "a/d3a_sample.py": '"""依据 D3-A。"""\n',
}


class Harness:
    def __init__(self) -> None:
        self.results: list[tuple[str, bool, str]] = []
        self.tmp = Path(tempfile.mkdtemp(prefix="onto1-scan-mutation-"))

    def record(self, name: str, ok: bool, detail: str = "") -> None:
        self.results.append((name, ok, detail))
        print(f"{'PASS' if ok else 'FAIL'}  {name}  {detail}")

    # ---------------- 检出能力（合成根） ----------------
    def run_detection_cases(self, module) -> None:
        repo_root = self.tmp / "repo"
        for rel, content in SYNTHETIC_TREE.items():
            target = repo_root / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")

        original = dict(module.REPO_ROOTS)
        module.REPO_ROOTS = {"synth": repo_root}
        try:
            result = module.scan(["synth"])
        finally:
            module.REPO_ROOTS = original
        tokens = {(hit["category"], hit["token"]) for hit in result["hits"]}
        lookups = {
            "T01 合成根检出 owl_class": ("owl_class", "OperatingCase"),
            "T02 合成根检出 owl_object_property": ("owl_object_property", "authorizedBy"),
            "T03 合成根检出 IRI 字面量": ("iri_or_file_ref", "IRI_BANK_EXAMPLE"),
            "T04a 合成根检出 KM-": ("id_pattern", "KM-CORP-RM-OUTREACH"),
            "T04b 合成根检出 AC-（语义名）": ("id_pattern", "AC-PRODUCT-RECOMMEND-001"),
            "T04c 合成根检出 ASSET-": ("id_pattern", "ASSET-KNOW-PRODUCT-CARDS"),
            "T04d 合成根检出 SP-": ("id_pattern", "SP-15"),
            "T04e 合成根检出 KI-": ("id_pattern", "KI-FRONT-001"),
            "T04f 合成根检出 KD-": ("id_pattern", "KD-DOC-001"),
            "T04g 合成根检出 CTR-": ("id_pattern", "CTR-SEM-002"),
            "T05a 合成根检出文件名引用": ("iri_or_file_ref", "FILE_GITS_CORE"),
            "T05b 合成根检出 D3-A 残留": ("d3a_residual", "D3-A"),
        }
        for name, key in lookups.items():
            self.record(name, key in tokens, "" if key in tokens else f"missing {key}")

    # ---------------- 门禁 FAIL 用例（子进程） ----------------
    def run_gate(self, extra_env_rules: Path, hits: Path | None = None,
                 roots: list[str] | None = None) -> subprocess.CompletedProcess:
        out_dir = self.tmp / f"out-{len(self.results)}"
        out_dir.mkdir(parents=True, exist_ok=True)
        command = [sys.executable, str(SCANNER), "--gate", "--rules", str(extra_env_rules),
                   "--out-dir", str(out_dir)]
        if roots:
            command += ["--roots", *roots]
        if hits is not None:
            command += ["--hits-file", str(hits)]
        return subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)

    def case_no_rule(self) -> None:
        rules = self.tmp / "rules-no-match.json"
        rules.write_text(json.dumps({
            "schema": "onto1_consumer_dispositions/v1",
            "rules": [{"id": "X", "match": {"pathGlob": "no/such/path"}, "disposition": "FOLLOW_MIGRATION"}],
        }), encoding="utf-8")
        proc = self.run_gate(rules)
        self.record("T06 无规则匹配 ⇒ 门禁 FAIL",
                    proc.returncode != 0 and ("A4" in proc.stderr or "A4" in proc.stdout),
                    f"exit={proc.returncode}")

    def case_baseline_count(self, module) -> None:
        import hashlib
        ttl = module.BASELINE_TTL.read_text(encoding="utf-8")
        trimmed = ttl.replace("gits:Task a owl:Class", "gits:Task a owl:ObjectProperty", 1)
        tmp_ttl = self.tmp / "gits-core-31.ttl"
        tmp_ttl.write_text(trimmed, encoding="utf-8")
        # 把期望哈希改为被变异文件的哈希 ⇒ 让执行走到"计数断言"，单独验证它有牙齿
        mutated_prefix = hashlib.sha256(tmp_ttl.read_bytes()).hexdigest()[:16]
        try:
            module.load_baseline_terms(tmp_ttl, expected_prefix=mutated_prefix)
            self.record("T07 基线类计数 31 ≠ 32 ⇒ FAIL", False, "no error raised")
        except RuntimeError as exc:
            ok = "count mismatch" in str(exc)
            self.record("T07 基线类计数 31 ≠ 32 ⇒ FAIL", ok, str(exc)[:70])

    def case_baseline_hash(self, module) -> None:
        ttl = module.BASELINE_TTL.read_text(encoding="utf-8")
        tmp_ttl = self.tmp / "gits-core-drift.ttl"
        tmp_ttl.write_text(ttl + "\n# drift\n", encoding="utf-8")
        try:
            module.load_baseline_terms(tmp_ttl)
            self.record("T08 基线哈希漂移 ⇒ FAIL", False, "no error raised")
        except RuntimeError as exc:
            self.record("T08 基线哈希漂移 ⇒ FAIL", True, str(exc)[:60])

    def case_single_repo(self) -> None:
        """只保留 gits 命中 ⇒ KERT 的期望命中缺失 ⇒ A3 必须 FAIL。"""
        subset = self.tmp / "hits-gits-only.jsonl"
        kept = [line for line in REAL_HITS.read_text(encoding="utf-8").splitlines()
                if line.strip() and json.loads(line)["repo"] == "gits"]
        subset.write_text("\n".join(kept) + "\n", encoding="utf-8")
        proc = self.run_gate(REAL_RULES, hits=subset)
        self.record("T09 单仓缓存 ⇒ 期望命中缺失 ⇒ 门禁 FAIL",
                    proc.returncode != 0 and "A3" in proc.stderr + proc.stdout,
                    f"exit={proc.returncode}")

    def case_all_exempt(self) -> None:
        """把全部命中豁免化 ⇒ A6 净义务锚点缺失 ⇒ 必须 FAIL。"""
        rules = self.tmp / "rules-all-exempt.json"
        rules.write_text(json.dumps({
            "schema": "onto1_consumer_dispositions/v1",
            "rules": [
                {"id": "X1", "match": {"category": "id_pattern"}, "disposition": "EXEMPT_SEED_DATA"},
                {"id": "X2", "match": {}, "disposition": "EXEMPT_SEED_DATA"},
            ],
        }), encoding="utf-8")
        proc = self.run_gate(rules)
        self.record("T10 全部豁免化 ⇒ 净义务缺失 ⇒ 门禁 FAIL",
                    proc.returncode != 0 and "A6" in proc.stderr + proc.stdout,
                    f"exit={proc.returncode}")

    def case_all_pending(self) -> None:
        """全部落 PENDING_TRIAGE ⇒ A4b 必须 FAIL（处置表未完成不得通过）。"""
        rules = self.tmp / "rules-all-pending.json"
        rules.write_text(json.dumps({
            "schema": "onto1_consumer_dispositions/v1",
            "rules": [{"id": "P", "match": {}, "disposition": "PENDING_TRIAGE"}],
        }), encoding="utf-8")
        proc = self.run_gate(rules)
        self.record("T11 全部 PENDING ⇒ 门禁 FAIL",
                    proc.returncode != 0 and "A4b" in proc.stderr + proc.stdout,
                    f"exit={proc.returncode}")

    def case_control_pass(self) -> None:
        proc = self.run_gate(REAL_RULES)
        self.record("T12 对照：正式规则+正式缓存 ⇒ PASS",
                    proc.returncode == 0, f"exit={proc.returncode}")

    def cleanup(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)


def main() -> int:
    if not REAL_HITS.is_file():
        print("onto1-consumer-scan-tests: FAIL: run --report first to build hits cache", file=sys.stderr)
        return 2
    harness = Harness()
    module = load_scanner()
    try:
        harness.run_detection_cases(module)
        harness.case_no_rule()
        harness.case_baseline_count(module)
        harness.case_baseline_hash(module)
        harness.case_single_repo()
        harness.case_all_exempt()
        harness.case_all_pending()
        harness.case_control_pass()
    finally:
        harness.cleanup()

    failed = [name for name, ok, _ in harness.results if not ok]
    print(f"\nonto1-consumer-scan-tests: {len(harness.results) - len(failed)}/{len(harness.results)} passed")
    if failed:
        print(f"FAILED CASES: {failed}", file=sys.stderr)
        print("onto1-consumer-scan-tests: FAIL", file=sys.stderr)
        return 2
    print("onto1-consumer-scan-tests: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
