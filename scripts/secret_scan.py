#!/usr/bin/env python3
"""Fail-closed repository scan for credentials, private keys and personal absolute paths."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import subprocess
import sys


SKIP_PARTS = {".git", "node_modules", "target", "dist", "backups", "__pycache__", ".venv", "venv"}
SKIP_FILES = {"secret_scan.py"}
TEXT_SUFFIXES = {"", ".md", ".txt", ".yaml", ".yml", ".json", ".py", ".sh", ".java", ".ts", ".vue", ".xml", ".ttl", ".dmn", ".properties", ".sql"}
CREDENTIAL = re.compile(r"(?i)\b(password|passwd|secret|api[_-]?key|access[_-]?token)\b\s*[:=]\s*[\"']?([^\s\"']+)")
HOME_PATH = re.compile(r"/(?:home|Users)/[A-Za-z0-9._-]+/")
PRIVATE_KEY = "-----BEGIN PRIVATE KEY-----"
PLACEHOLDER_VALUES = {"changeme", "change_me", "placeholder", "example", "not_set", "none", "null"}

# 引用值（非真实密钥）—— key 指向配置项/变量，而非硬编码秘密。
# 例如 `${engagement.security.api-key}`、`getApiKey()`、`apiKey`（空引用）
REFERENCE_PATTERN = re.compile(r"^\$\{|^<|^\{\{|<api.?key>|getApiKey|apiKey$|ref\(")

# 测试/示例/演示占位密钥：以 test- 开头，或含 -202x 年份后缀、demo/example/sample 等
TEST_VALUE_PATTERN = re.compile(
    r"^(?:test|demo|example|sample|placeholder|changeme)[-_]|"
    r"-(?:20\d\d|demo|test|sample)(?:['\"]|$)|"
    r"['\"]?(?:test|demo|example|sample)['\"]?$",
    re.I,
)

# 硬编码秘密的迹象：较长的十六进制/Base64/字母数字混合串
LITERAL_SECRET_PATTERN = re.compile(r"^[A-Za-z0-9+/=_\-]{12,}$")


def _in_git_repo(root: Path) -> bool:
    # 普通仓库 .git 是目录；git worktree 的 .git 是指向共享仓库的指针文件。
    # 两者都代表“位于 git 控制下”，应使用 git ls-files 以尊重 .gitignore。
    dot_git = root / ".git"
    if dot_git.is_dir():
        return True
    if dot_git.is_file():
        return True
    return subprocess.run(
        ["git", "rev-parse", "--git-dir"], cwd=root, text=True, capture_output=True, check=False
    ).returncode == 0


def files_for(root: Path):
    if _in_git_repo(root):
        result = subprocess.run(["git", "ls-files", "-co", "--exclude-standard"], cwd=root, text=True, capture_output=True, check=False)
        if result.returncode != 0:
            raise ValueError("git ls-files failed")
        candidates = [root / line for line in result.stdout.splitlines() if line]
    else:
        candidates = list(root.rglob("*"))
    for path in candidates:
        if not path.is_file() or any(part in SKIP_PARTS for part in path.relative_to(root).parts) or path.name in SKIP_FILES:
            continue
        if path.suffix.lower() in TEXT_SUFFIXES:
            yield path


def scan_root(root: Path) -> list[dict]:
    findings = []
    for path in files_for(root):
        relative = path.relative_to(root).as_posix()
        if path.name == ".env" or (path.name.startswith(".env.") and path.name != ".env.example"):
            findings.append({"path": relative, "line": 0, "type": "PROHIBITED_ENV_FILE"})
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for number, line in enumerate(text.splitlines(), 1):
            if PRIVATE_KEY in line:
                findings.append({"path": relative, "line": number, "type": "PRIVATE_KEY", "blocking": True})
            if HOME_PATH.search(line):
                # 个人绝对路径：多为文档/历史数据/注释中的路径引用，非敏感密钥，
                # 默认降级为告警（不阻塞），--strict 时可强制阻塞。
                findings.append({"path": relative, "line": number, "type": "PERSONAL_ABSOLUTE_PATH", "blocking": False})
            match = CREDENTIAL.search(line)
            if match:
                value = match.group(2).strip().lower()
                is_reference = (
                    value in PLACEHOLDER_VALUES
                    or value.startswith("${")
                    or value.startswith("<")
                    or value.startswith("{{")
                    or REFERENCE_PATTERN.search(line.lower()) is not None
                    or TEST_VALUE_PATTERN.search(value) is not None
                )
                # 引用型（配置键/变量名）不视为硬编码密钥，降级为告警
                blocking = not is_reference and LITERAL_SECRET_PATTERN.match(value) is not None
                findings.append({"path": relative, "line": number, "type": "POSSIBLE_CREDENTIAL", "key": match.group(1), "blocking": blocking})
    return findings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--strict", action="store_true",
                        help="将所有 finding（含个人路径/引用型凭据告警）视为阻塞")
    parser.add_argument("--quiet", action="store_true",
                        help="仅输出 summary 与阻塞项，不打印 advisory 明细")
    args = parser.parse_args()
    try:
        findings = scan_root(args.root.resolve())
    except (OSError, ValueError) as exc:
        print(f"secret-scan: FAIL: {exc}", file=sys.stderr)
        return 2
    if findings:
        blocking = [f for f in findings if f.get("blocking", True)]
        advisory = [f for f in findings if not f.get("blocking", True)]
        if not args.quiet:
            for item in findings:
                tag = "[BLOCK]" if item.get("blocking", True) else "[ADV ]"
                print(f"{tag} {item}")
        if blocking or args.strict:
            count = len(blocking) + (len(advisory) if args.strict else 0)
            print(f"secret-scan: FAIL: {count} blocking finding(s)", file=sys.stderr)
            return 2
        print(f"secret-scan: PASS (with {len(advisory)} advisory finding(s))")
        return 0
    print("secret-scan: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
