from pathlib import Path
import json
import shutil
import subprocess
import sys
import time
import unittest


ROOT = Path(__file__).resolve().parents[2]


class LoopGuardTest(unittest.TestCase):
    def test_dummy_command_is_rejected(self):
        loop_id = f"TST-guard-{int(time.time() * 1000)}"
        destination = ROOT / "loops" / loop_id
        try:
            created = subprocess.run(
                [sys.executable, str(ROOT / "scripts/new_loop.py"), "--loop-id", loop_id, "--holder", "test_actor"],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, created.returncode, created.stdout + created.stderr)
            spec_path = destination / "LOOP.yaml"
            spec = json.loads(spec_path.read_text(encoding="utf-8"))
            spec["gates"][0]["command"] = "echo pass"
            spec_path.write_text(json.dumps(spec, indent=2) + "\n", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts/loop_guard.py"), "--loop", loop_id],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(0, result.returncode)
            self.assertIn("dummy command prohibited", result.stderr)
        finally:
            shutil.rmtree(destination, ignore_errors=True)


    def test_evidence_log_with_braces_is_not_a_placeholder(self):
        """R-1（PC-i1 F-PC-i1-04）：`evidence/` 是**原始证据**，含连续双花括号不得判为占位符；
        但 `memory/` 等**文档**仍必须被判 FAIL —— 两侧同测，防"顺手放宽"。"""
        loop_id = f"TST-guard-evidence-{int(time.time() * 1000)}"
        destination = ROOT / "loops" / loop_id
        braces = chr(123) + chr(123)
        try:
            created = subprocess.run(
                [sys.executable, str(ROOT / "scripts/new_loop.py"), "--loop-id", loop_id, "--holder", "test_actor"],
                cwd=ROOT, text=True, capture_output=True, check=False,
            )
            self.assertEqual(0, created.returncode, created.stdout + created.stderr)

            evidence_dir = destination / "evidence"
            evidence_dir.mkdir(parents=True, exist_ok=True)
            (evidence_dir / "probe.log").write_text(f"failed output quoting source: {braces}x{braces}\n", encoding="utf-8")
            evidence_only = subprocess.run(
                [sys.executable, str(ROOT / "scripts/loop_guard.py"), "--loop", loop_id],
                cwd=ROOT, text=True, capture_output=True, check=False,
            )
            self.assertEqual(0, evidence_only.returncode, evidence_only.stdout + evidence_only.stderr)

            doc = destination / "memory" / "PROBE.md"
            doc.write_text(f"doc with the same token: {braces}y{braces}\n", encoding="utf-8")
            with_doc = subprocess.run(
                [sys.executable, str(ROOT / "scripts/loop_guard.py"), "--loop", loop_id],
                cwd=ROOT, text=True, capture_output=True, check=False,
            )
            self.assertNotEqual(0, with_doc.returncode)
            self.assertIn("unresolved placeholders", with_doc.stderr)
            self.assertIn("memory/PROBE.md", with_doc.stderr)
            self.assertNotIn("evidence/probe.log", with_doc.stderr)
        finally:
            shutil.rmtree(destination, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
