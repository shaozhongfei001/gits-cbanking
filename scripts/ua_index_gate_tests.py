#!/usr/bin/env python3
"""代码事实索引门禁的变异复验（证明 ua_index_gate.py 的断言不是空转）。

本仓惯例：无负例测试的门禁 PASS 不予采信。本脚本对门禁逐条注入已知故障，
要求判 FAIL；恢复后要求 PASS。任一注入未被捕获即报失败。

运行：make index-gate-tests
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
GATE = REPO / "scripts" / "ua_index_gate.py"
PROCESS_DOC = "docs/governance/CODE-FACT-INDEX-PROCESS.md"
RULE_FILE = ".codebuddy/rules/code-fact-index/RULE.mdc"


def git(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "-c", "user.email=gate@test", "-c", "user.name=gate-test", *args],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )


class IndexGateFixture(unittest.TestCase):
    """在临时目录构造一个"合规"的索引工作区，再逐项注入故障。"""

    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="ua-index-gate-"))
        self.root = self.tmp / "repo"
        self.root.mkdir()
        (self.root / "docs/governance").mkdir(parents=True)
        (self.root / ".codebuddy/rules/code-fact-index").mkdir(parents=True)
        (self.root / ".ua").mkdir()

        shutil.copy(REPO / ".understandignore", self.root / ".understandignore")
        shutil.copy(REPO / PROCESS_DOC, self.root / PROCESS_DOC)
        shutil.copy(REPO / RULE_FILE, self.root / RULE_FILE)
        (self.root / ".gitignore").write_text(".ua/\n", encoding="utf-8")

        graph = {
            "version": "1.0.0",
            "project": {"name": "fixture", "description": "fixture graph（DERIVED 派生视图）"},
            "nodes": [{"id": "repo|file:a.java", "type": "file", "name": "a.java", "filePath": "a.java"}],
            "edges": [],
            "layers": [{"id": "repo|layer:core", "name": "core", "description": "d", "nodeIds": ["repo|file:a.java"]}],
            "tour": [],
            "humanView": {"derived": True, "notAuthoritative": True, "note": "DERIVED"},
        }
        self.write_json(".ua/knowledge-graph.json", graph)
        (self.root / ".ua/meta.json").write_text("{}\n", encoding="utf-8")

        git(self.root, "init", "-q")
        git(self.root, "add", ".gitignore", ".understandignore", PROCESS_DOC, RULE_FILE)
        git(self.root, "commit", "-q", "-m", "fixture baseline")
        head = git(self.root, "rev-parse", "HEAD").stdout.strip()
        self.write_json(
            ".ua/merge-meta.json",
            {
                "mergedAt": "2026-09-15T06:37:38Z",
                "gitsCommit": head,
                "kertCommit": head,
            },
        )
        self.write_json(".ua/meta.json", {"lastAnalyzedAt": "2026-09-15T05:05:32Z", "gitCommitHash": head})

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    # ---- helpers -------------------------------------------------------
    def write_json(self, rel: str, payload) -> None:
        text = json.dumps(payload, ensure_ascii=False, indent=2) if not isinstance(payload, str) else payload
        (self.root / rel).write_text(text + "\n", encoding="utf-8")

    def read_text(self, rel: str) -> str:
        return (self.root / rel).read_text(encoding="utf-8")

    def run_gate(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(GATE), "--root", str(self.root), "--json", *args],
            text=True,
            capture_output=True,
            check=False,
        )

    def status_of(self, result: subprocess.CompletedProcess) -> str:
        try:
            return json.loads(result.stdout)["status"]
        except (json.JSONDecodeError, KeyError, TypeError):
            return f"UNPARSABLE({result.stdout[:120]!r} {result.stderr[:120]!r})"

    # ---- cases ---------------------------------------------------------
    def test_baseline_passes(self) -> None:
        result = self.run_gate()
        self.assertEqual(result.returncode, 0, msg=f"baseline should not block: {result.stdout}{result.stderr}")
        self.assertIn(self.status_of(result), {"PASS", "WARN"})

    def test_real_repo_baseline_passes(self) -> None:
        result = subprocess.run(
            [sys.executable, str(GATE), "--json"], text=True, capture_output=True, check=False
        )
        self.assertEqual(result.returncode, 0, msg=f"real repo must satisfy the redlines: {result.stdout}")

    def test_m1_credential_pattern_commented_out_fails(self) -> None:
        path = self.root / ".understandignore"
        path.write_text(self.read_text(".understandignore").replace("\n*.pem\n", "\n# *.pem\n"), encoding="utf-8")
        self.assert_mutation_caught("R2", "凭据排除被注释")

    def test_m2_credential_pattern_deleted_fails(self) -> None:
        path = self.root / ".understandignore"
        path.write_text(self.read_text(".understandignore").replace("\n*.jar\n", "\n"), encoding="utf-8")
        self.assert_mutation_caught("R2", "凭据排除被删除")

    def test_m3_self_recursion_pattern_removed_fails(self) -> None:
        path = self.root / ".understandignore"
        path.write_text(self.read_text(".understandignore").replace("\n.ua/\n", "\n"), encoding="utf-8")
        self.assert_mutation_caught("R2", ".ua/ 自我递归排除被删除")

    def test_m4_artifact_not_ignored_fails(self) -> None:
        (self.root / ".gitignore").write_text("# emptied\n", encoding="utf-8")
        self.assert_mutation_caught("R1", "派生视图未被忽略")

    def test_m5_artifact_tracked_fails(self) -> None:
        git(self.root, "add", "-f", ".ua/knowledge-graph.json")
        self.assert_mutation_caught("R1", "派生视图被 git 跟踪")

    def test_m6_authority_marker_stripped_fails(self) -> None:
        graph = json.loads(self.read_text(".ua/knowledge-graph.json"))
        graph["humanView"] = {"derived": False, "notAuthoritative": False, "note": ""}
        graph["project"]["description"] = "无标记图"
        self.write_json(".ua/knowledge-graph.json", graph)
        self.assert_mutation_caught("R3", "非权威标记被剥离")

    def test_m7_graph_corrupted_fails(self) -> None:
        (self.root / ".ua/knowledge-graph.json").write_text('{"nodes": [', encoding="utf-8")
        self.assert_mutation_caught("R4", "索引 JSON 损坏")

    def test_m8_graph_empty_fails(self) -> None:
        graph = json.loads(self.read_text(".ua/knowledge-graph.json"))
        graph["nodes"] = []
        self.write_json(".ua/knowledge-graph.json", graph)
        self.assert_mutation_caught("R4", "索引内容为空")

    def test_m9_process_doc_deleted_fails(self) -> None:
        (self.root / PROCESS_DOC).unlink()
        self.assert_mutation_caught("R5", "流程文档缺失")

    def test_m10_process_doc_redline_rewritten_fails(self) -> None:
        path = self.root / PROCESS_DOC
        path.write_text(self.read_text(PROCESS_DOC).replace("回源", "参考"), encoding="utf-8")
        self.assert_mutation_caught("R5", "流程文档回源约束被改写")

    def test_m11_rule_file_deleted_fails(self) -> None:
        (self.root / RULE_FILE).unlink()
        self.assert_mutation_caught("R5", "角色规则缺失")

    def test_m12_credentials_file_deleted_fails(self) -> None:
        (self.root / ".understandignore").unlink()
        self.assert_mutation_caught("R2", "采集边界文件缺失（缺输入不得默认放行）")

    def test_m13_stale_index_advisory_but_blocks_in_require_mode(self) -> None:
        git(self.root, "commit", "-q", "--allow-empty", "-m", "drift commit")
        advisory = self.run_gate("--max-drift", "0")
        self.assertEqual(advisory.returncode, 0, msg="默认模式索引过期只应告警")
        self.assertEqual(self.status_of(advisory), "WARN")
        strict = self.run_gate("--max-drift", "0", "--require")
        self.assertEqual(strict.returncode, 2, msg="--require 下索引过期必须阻塞")

    def test_m14_missing_index_blocks_in_require_mode(self) -> None:
        shutil.rmtree(self.root / ".ua")
        self.assertEqual(self.run_gate().returncode, 0, msg="索引缺失默认不应阻塞（本机未建索引是常态）")
        self.assertEqual(self.run_gate("--require").returncode, 2, msg="--require 下索引缺失必须阻塞")

    def test_m15_stale_by_age_blocks_in_require_mode(self) -> None:
        self.assertEqual(self.run_gate("--max-age-days", "-1", "--require").returncode, 2)

    def test_restore_after_mutations_passes(self) -> None:
        """恢复即 PASS：证明上面的 FAIL 由注入引起，而非门禁恒失败。"""
        for mutate, restore in (
            (lambda: (self.root / ".understandignore").unlink(), lambda: shutil.copy(REPO / ".understandignore", self.root / ".understandignore")),
            (lambda: (self.root / PROCESS_DOC).unlink(), lambda: shutil.copy(REPO / PROCESS_DOC, self.root / PROCESS_DOC)),
        ):
            mutate()
            self.assertEqual(self.run_gate().returncode, 2)
            restore()
            self.assertEqual(self.run_gate().returncode, 0)

    # ---- assertion -----------------------------------------------------
    def assert_mutation_caught(self, rule: str, label: str) -> None:
        result = self.run_gate()
        self.assertEqual(
            result.returncode,
            2,
            msg=f"变异未被捕获（{rule} {label}）：门禁断言疑似空转\n{result.stdout}{result.stderr}",
        )
        payload = json.loads(result.stdout)
        self.assertIn(rule, " ".join(payload["failures"]), msg=f"未以 {rule} 归类：{payload['failures']}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
