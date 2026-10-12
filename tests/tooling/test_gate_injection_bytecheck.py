"""F-4 非空转证据：`gate_injection_tests._audit_and_restore` 的字节级漂移检出与自还原。

背景（Owner 2026-09-23 授权）：原"未留痕"核验只比对 `git status` **行文本**，
对**运行前已 dirty** 的文件内容漂移**检测不到、也不回滚**（1B DIAG-4 / 1C 独立发现）。

本测试证明新核验**不是空转**：
  ① 无漂移 ⇒ 不误报；
  ② 有备份的漂移 ⇒ **逐字节还原且哈希复原**；
  ③ 无备份的漂移 ⇒ 列入"无法还原"（调用方据此 `FAIL`，fail-closed，不静默放过）。
"""
from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location(
    "gate_injection_tests", ROOT / "scripts" / "gate_injection_tests.py")
gi = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gi)


class ByteCheckTest(unittest.TestCase):
    def setUp(self):
        self._td = tempfile.TemporaryDirectory(prefix="git-inj-bytecheck-")
        self.tree = Path(self._td.name)
        self._orig_root, self._orig_snap = gi.ROOT, gi._SNAP_DIR
        gi.ROOT = self.tree
        gi._SNAP_DIR = self.tree / "_snap"
        gi._SNAP_DIR.mkdir()
        (self.tree / "specs").mkdir()
        self.rel = "specs/watched.json"
        (self.tree / self.rel).write_text('{"v": 1}', encoding="utf-8")

    def tearDown(self):
        gi.ROOT, gi._SNAP_DIR = self._orig_root, self._orig_snap
        self._td.cleanup()

    def _snapshot(self):
        return gi._snapshot_paths([self.rel])

    def test_no_drift_is_not_reported(self):
        hashes, backups, unbaked = self._snapshot()
        self.assertEqual([], unbaked)
        drifted, restored, unrestorable = gi._audit_and_restore(hashes, backups)
        self.assertEqual([], drifted)
        self.assertEqual([], restored)
        self.assertEqual([], unrestorable)

    def test_drift_with_backup_is_detected_and_restored_bytewise(self):
        hashes, backups, _ = self._snapshot()
        target = self.tree / self.rel
        target.write_text('{"v": 999}', encoding="utf-8")      # 模拟"被本次运行改写"
        drifted, restored, unrestorable = gi._audit_and_restore(hashes, backups)
        self.assertEqual([self.rel], drifted)
        self.assertEqual([self.rel], restored)
        self.assertEqual([], unrestorable)
        self.assertEqual('{"v": 1}', target.read_text(encoding="utf-8"))   # 逐字节复原

    def test_drift_without_backup_is_fatal_not_silent(self):
        hashes, _backups, _ = self._snapshot()
        (self.tree / self.rel).write_text('{"v": 999}', encoding="utf-8")
        drifted, restored, unrestorable = gi._audit_and_restore(hashes, {})  # 无备份
        self.assertEqual([self.rel], drifted)
        self.assertEqual([], restored)
        self.assertEqual([self.rel], unrestorable)   # ⇒ 调用方 FAIL（fail-closed）


if __name__ == "__main__":
    unittest.main()
