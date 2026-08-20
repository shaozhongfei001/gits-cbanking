"""契约化 Markdown 文件读写封装：写 frontmatter+正文、原子替换、相对路径。

契约要求：
- 生成物只读（read_only_generated）；
- 路径使用工作区相对路径；不承载宿主绝对路径；
- 每次更新采用原子替换。
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import yaml

from .errors import ContractError


def dump_contract(file_path: Path, values: dict, body: str) -> str:
    """把字段 dict + 正文写为契约化 Markdown（原子写入）。返回写入的文本。"""
    values = {k: v for k, v in values.items() if v is not None}
    fm = yaml.safe_dump(values, sort_keys=False, allow_unicode=True, default_flow_style=False).rstrip("\n")
    text = f"---\n{fm}\n---\n{body}"
    if not text.endswith("\n"):
        text += "\n"
    _atomic_write(file_path, text)
    return text


def _atomic_write(file_path: Path, text: str) -> None:
    file_path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(file_path.parent), prefix=".dktmp-", suffix=".md")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, file_path)
    except BaseException:
        if os.path.exists(tmp):
            os.remove(tmp)
        raise


def normalize_contract_body(sections: dict[str, str]) -> str:
    """按给定标题顺序拼接正文。sections: {H2标题: 内容}。"""
    out = []
    for title, content in sections.items():
        out.append(f"## {title}\n\n{content.strip()}")
    return "\n\n".join(out)