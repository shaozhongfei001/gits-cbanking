"""文档登记 + 规范化 + 稳定切片（DKWS-SPEC-001 §9.3/§9.4，Gate P4 G1 文档类）。

- 文档登记（DOCUMENT.md）幂等；
- 规范化（NORMALIZED.md）：确定性清理，同输入同输出；
- 稳定切片（segments/*.md）：按 heading/段/表/列表，序列号稳定，重跑产出相同。
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from .errors import NotFoundError, ValidationError
from .hashing import sha256_text, utcnow
from .contract import get_schema
from .mdio import dump_contract
from .workspace import Workspace

_NL_RE = re.compile(r"\r\n|\r")
_REPEAT_SPACE = re.compile(r"[ \t]{2,}")
_LINE_SPACE = re.compile(r"[ \t]+")


def normalize_text(text: str) -> str:
    """确定性规范化（§9.3）：LF、去 BOM、去除行尾空格、合并重复空行。"""
    text = text.lstrip("\ufeff")
    text = _NL_RE.sub("\n", text)
    lines = [line.rstrip() for line in text.split("\n")]
    out_lines = []
    blank = 0
    for line in lines:
        if line == "":
            blank += 1
            if blank <= 1:
                out_lines.append("")
        else:
            blank = 0
            out_lines.append(line)
    result = "\n".join(out_lines).strip() + "\n"
    return result


def split_blocks(normalized: str) -> list[dict]:
    """把规范化文本拆为块：结构块（标题段落/代码/表格/列表）。返回 dict 列表。"""
    blocks: list[dict] = []
    lines = normalized.split("\n")
    i = 0
    in_code = False
    code_buf: list[str] = []
    while i < len(lines):
        line = lines[i]
        if line.startswith("```"):
            if in_code:
                code_buf.append(line)
                blocks.append({"type": "CODE", "content": "\n".join(code_buf), "heading": "(code)"})
                code_buf = []
                in_code = False
            else:
                in_code = True
                code_buf = [line]
            i += 1
            continue
        if in_code:
            code_buf.append(line)
            i += 1
            continue
        if line.startswith("#"):
            blocks.append({"type": "HEADING", "content": line, "heading": line.lstrip("#").strip()})
            i += 1
            continue
        if line.startswith("|") and i + 1 < len(lines) and "|" in lines[i + 1]:
            buf = []
            while i < len(lines) and lines[i].startswith("|"):
                buf.append(lines[i])
                i += 1
            blocks.append({"type": "TABLE", "content": "\n".join(buf), "heading": _heading_for(blocks)})
            continue
        if line.strip().startswith(("- ", "* ", "+ ")):
            buf = []
            while i < len(lines) and lines[i].strip().startswith(("- ", "* ", "+ ")):
                buf.append(lines[i])
                i += 1
            blocks.append({"type": "LIST", "content": "\n".join(buf), "heading": _heading_for(blocks)})
            continue
        # paragraph gather
        buf = [line]
        i += 1
        while i < len(lines) and lines[i].strip() and not lines[i].startswith("#") and \
                not lines[i].startswith("```") and not lines[i].startswith("|"):
            buf.append(lines[i])
            i += 1
        blocks.append({"type": "PARAGRAPH", "content": "\n".join(buf).strip(), "heading": _heading_for(blocks)})
    return [b for b in blocks if b["content"].strip()]


def _heading_for(blocks: list[dict]) -> str:
    for b in reversed(blocks):
        if b["type"] == "HEADING":
            return b["heading"]
    return "(untitled)"


@dataclass
class SliceOutcome:
    document_id: str
    normalized_id: str
    segment_count: int
    blocks: list[dict] = field(default_factory=list)


class DocumentPipeline:
    def __init__(self, ws: Workspace):
        self.ws = ws

    def register(self, doc_id: str, *, name: str, source_file: str, domain: str,
                 classification: str = "INTERNAL", owner: str = "demo", language: str = "zh",
                 requested_by: str = "dkws.cli") -> str:
        """登记文档（幂等：同 doc_id 已存在则返回）。"""
        rel = f"01_raw/{domain}/D/{doc_id}.md"
        if (self.ws.root / rel).exists():
            return rel
        values = {
            "schema": "document/v1", "document_id": doc_id, "name": name,
            "source_file": source_file, "language": language, "doc_type": "MARKDOWN",
            "classification": classification, "owner": owner, "tags": [],
            "extracted_at": utcnow(), "version": "1.0",
        }
        dump_contract(self.ws.root / rel, values,
                      "# 文档\n\n## 摘要\n演示文档登记。\n\n## 内容范围\n- \n\n## 版本记录\n- v1.0 初版\n")
        return rel

    def normalize_and_slice(self, doc_id: str, domain: str, source_text: str) -> SliceOutcome:
        """规范化并切片，产出 NORMALIZED.md + segments/*.md。幂等重建。"""
        work_dir = self.ws.resolve(f"02_work/U/{doc_id}")
        norm_text = normalize_text(source_text)
        text_sha = sha256_text(norm_text)
        normalized_id = f"NOR-{doc_id}"
        seg_dir = work_dir / "segments"

        norm_values = {
            "schema": "normalized_document/v1", "normalized_id": normalized_id,
            "source_document_id": doc_id, "normalized_at": utcnow(),
            "rules_used": ["det-norm-1.0"], "textsha256": text_sha,
            "token_count": len(norm_text.split()), "version": "1.0",
        }
        dump_contract(work_dir / "NORMALIZED.md", norm_values,
                      "# 规范化文本\n\n## 规范化说明\n确定性清理：LF、去BOM、行尾空格。\n\n## 原文链接\n`01_raw/{}/D/{}.md`\n\n## 清理清单\n- 统一换行\n".format(domain, doc_id))

        blocks = split_blocks(norm_text)
        for seq, block in enumerate(blocks, start=1):
            sid = f"{doc_id}-S{seq:04d}"
            content_sha = sha256_text(block["content"])
            seg_values = {
                "schema": "segment/v1", "segment_id": sid, "document_id": doc_id,
                "normalized_id": normalized_id,
                "segment_type": _map_type(block["type"]),
                "heading_path": block.get("heading", "(untitled)"),
                "page_from": 1, "page_to": 1, "sequence": seq,
                "content_sha256": content_sha, "char_count": len(block["content"]),
                "version": "1.0",
            }
            dump_contract(seg_dir / f"{sid}.md", seg_values,
                          "# 片段\n\n## 内容\n\n```text\n{}\n```\n\n## 清洗记录\n无。\n\n## 来源\n`{}/D/{}.md`\n".format(block["content"], domain, doc_id))
        return SliceOutcome(document_id=doc_id, normalized_id=normalized_id,
                            segment_count=len(blocks), blocks=blocks)


def _map_type(block_type: str) -> str:
    return {"HEADING": "HEADING", "PARAGRAPH": "PARAGRAPH", "TABLE": "TABLE",
            "LIST": "LIST", "CODE": "CODE"}.get(block_type, "PARAGRAPH")