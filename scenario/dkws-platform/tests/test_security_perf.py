"""P9 安全与性能门禁测试（标准库 unittest）。"""

import sys
import tempfile
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from dkws import schemas  # noqa: F401,E402
from dkws.docs import DocumentPipeline, normalize_text  # noqa: E402
from dkws.errors import SecurityError  # noqa: E402
from dkws.workspace import Workspace  # noqa: E402


class TestSecurity(unittest.TestCase):
    def test_path_traversal_blocked(self):
        with tempfile.TemporaryDirectory() as td:
            ws = Workspace.init(Path(td) / "ws")
            with self.assertRaises(SecurityError):
                ws.resolve("../../etc/passwd")
            with self.assertRaises(SecurityError):
                ws.resolve("/etc/passwd")

    def test_no_absolute_host_path_in_artifacts(self):
        with tempfile.TemporaryDirectory() as td:
            ws = Workspace.init(Path(td) / "ws")
            pipe = DocumentPipeline(ws)
            pipe.register("D-SEC", name="s", source_file="s.md", domain="knowledge")
            pipe.normalize_and_slice("D-SEC", "knowledge", "# T\n\nbody\n")
            for layer in ("02_work", "03_core"):
                base = ws.root / layer
                if not base.is_dir():
                    continue
                for p in base.rglob("*.md"):
                    if p.is_file():
                        self.assertNotIn(Path(td).resolve().__str__(), p.read_text(encoding="utf-8"))


class TestSensitiveLogging(unittest.TestCase):
    def test_logger_redacts_sensitive(self):
        from dkws.logging import FileLogger
        with tempfile.TemporaryDirectory() as td:
            log_path = Path(td) / "a.log"
            logger = FileLogger(log_path)
            logger.info("j1", "ingest", "E", "credential=supersecret password=hunter2")
            content = log_path.read_text(encoding="utf-8")
            self.assertNotIn("supersecret", content)
            self.assertNotIn("hunter2", content)


class TestPerformance(unittest.TestCase):
    def test_slice_within_budget(self):
        with tempfile.TemporaryDirectory() as td:
            ws = Workspace.init(Path(td) / "ws")
            pipe = DocumentPipeline(ws)
            text = ("## 节%d\n\n" * 200 % tuple(range(1, 201)))
            pipe.register("D-PERF", name="p", source_file="p.md", domain="knowledge")
            t0 = time.perf_counter()
            pipe.normalize_and_slice("D-PERF", "knowledge", text)
            elapsed = time.perf_counter() - t0
            # 性能门禁：切片 200 节在宽松预算内完成（避免 CI 抖动，上限放宽）
            self.assertLess(elapsed, 5.0)

    def test_normalize_deterministic(self):
        self.assertEqual(normalize_text("a\r\nb\r\n"), normalize_text("a\nb\n"))
        self.assertEqual(normalize_text("\ufeffx\n"), "x\n")


if __name__ == "__main__":
    unittest.main()