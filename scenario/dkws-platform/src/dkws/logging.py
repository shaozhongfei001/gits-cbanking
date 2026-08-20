"""结构化日志（DKWS-SPEC-001 §9.20 / §20）。

- 路径：90_control/logs/<YYYY-MM-DD>/<job_id>.log；UTF-8、LF、仅追加。
- 每行：timestamp level job_id component event_code message key=value...
- level: DEBUG/INFO/WARN/ERROR/FATAL。
- 禁止记录凭据/完整敏感字段/整篇原文；SHA-256 由调用方计算。
"""

from __future__ import annotations

import re
import threading
from pathlib import Path

from .hashing import utcnow

_LEVELS = ("DEBUG", "INFO", "WARN", "ERROR", "FATAL")
_SENSITIVE = re.compile(r"(token|secret|password|api[_-]?key|credential|authorization|bearer)", re.IGNORECASE)


_KEY_VALUE = re.compile(
    r"(?i)(\b(?:token|secret|password|api[_-]?key|credential|authorization|bearer)\b"
    r")(\s*[:=]\s*)(\S+)")

_SENSITIVE_WHOLE = re.compile(r"\S*(?:token|secret|password|api[_-]?key|credential|authorization|bearer)\S*",
                              re.IGNORECASE)


def _sanitize(message: str) -> str:
    """脱敏：敏感 key=value 对或敏感词本身均替换为 [REDACTED]。"""
    message = _KEY_VALUE.sub(lambda m: f"{m.group(1)}{m.group(2)}[REDACTED]", message)
    return _SENSITIVE_WHOLE.sub("[REDACTED]", message)


class FileLogger:
    _lock = threading.Lock()

    def __init__(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.path = path

    def log(self, level: str, job_id: str, component: str, event_code: str, message: str, **kvs) -> None:
        assert level in _LEVELS, f"非法日志级别 {level}"
        safe_msg = _sanitize(message)
        kv = " ".join(f"{k}={v}" for k, v in kvs.items())
        line = f"{utcnow()} {level} {job_id} {component} {event_code} {safe_msg}"
        if kv:
            line += " " + kv
        with self._lock:
            with open(self.path, "a", encoding="utf-8", newline="\n") as fh:
                fh.write(line + "\n")

    def info(self, job_id, component, event_code, message, **kvs):
        self.log("INFO", job_id, component, event_code, message, **kvs)

    def warn(self, job_id, component, event_code, message, **kvs):
        self.log("WARN", job_id, component, event_code, message, **kvs)

    def error(self, job_id, component, event_code, message, **kvs):
        self.log("ERROR", job_id, component, event_code, message, **kvs)