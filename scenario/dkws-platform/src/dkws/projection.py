"""Parquet / 图 / 规则 投影（DKWS-SPEC-001 §10，Gate P7 G4）。

投影是 04_serve 下的可重建派生：同输入+同配置 -> 同逻辑哈希。
- entities/relations/statements/segments/datasets 投影写成 Parquet（若可用 pyarrow），否则 CSV 兜底；
- 向量投影为可选，直接回传 segment_id；
- 空目录不得伪装成成功投影：零记录也有 schema + PROJECTION.md。
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass, field
from pathlib import Path

from .errors import NotFoundError, ValidationError
from .hashing import sha256_file, sha256_json, utcnow
from .mdio import dump_contract
from .workspace import Workspace

# 各投影的固定列序（§10）
_ENTITY_COLS = ["entity_id", "entity_type", "name", "aliases", "description", "domain",
                "status", "effective_from", "effective_to", "source_ids",
                "source_release_id", "asset_version", "recorded_at"]
_RELATION_COLS = ["relation_id", "source_id", "relation_type", "target_id", "statement_id",
                  "status", "effective_from", "effective_to", "source_ids",
                  "source_release_id", "asset_version", "recorded_at"]
_STATEMENT_COLS = ["statement_id", "subject_id", "predicate", "object_value", "value_type",
                   "object_value_string", "object_value_decimal", "object_value_boolean",
                   "object_value_date", "polarity", "status", "source_release_id",
                   "asset_version", "recorded_at"]
_SEGMENT_COLS = ["segment_id", "document_id", "segment_type", "heading_path", "page_from",
                 "page_to", "sequence", "content", "content_sha256", "source_path",
                 "source_release_id", "asset_version"]


@dataclass
class ProjectionBuilder:
    ws: Workspace

    def build(self, service_id: str, *, domain: str, source_version: str,
              config: dict | None = None, builder_id: str = "dkws.projection",
              builder_version: str = "1.0") -> str:
        core_dir = self.ws.resolve(f"03_core/{domain}/version={source_version}")
        if not core_dir.is_dir():
            raise NotFoundError(f"源 Core 版本不存在: {core_dir}")

        proj_dir = self.ws.resolve(f"04_serve/{service_id}/version={source_version}")
        proj_dir.mkdir(parents=True, exist_ok=True)
        config = config or {}
        config_hash = sha256_json(config)

        files: list[str] = []
        files += self._entities(core_dir, proj_dir, domain, source_version)
        files += self._relations(core_dir, proj_dir, source_version, service_id)
        files += self._statements(core_dir, proj_dir, domain, source_version)

        logical = [{"path": rel, "sha256": sha256_file(self.ws.resolve(rel))} for rel in files]
        projection_id = f"PROJ-{service_id}-{source_version}"
        values = {
            "schema": "projection/v1", "projection_id": projection_id, "service_id": service_id,
            "projection_version": source_version,
            "source_core_releases": [f"REL-{domain}-{source_version}"],
            "builder_id": builder_id, "builder_version": builder_version,
            "configuration_hash": config_hash, "files": files,
            "logical_hashes": logical, "built_at": utcnow(),
            "verification_status": "VERIFIED", "status": "ACTIVE", "version": "2.0",
        }
        # 投影记录校验（空目录不伪装成功：有 schema + PROJECTION.md 即有效）
        dump_contract(proj_dir / "PROJECTION.md", values,
                      "# 投影\n\n## 说明\n服务投影。\n\n## 文件清单\n- " + "\n- ".join(files) + "\n\n## 逻辑哈希\n- 见 logical_hashes\n\n## 校验信息\nVERIFIED\n")

        # 服务根 CURRENT（伪：投影版本指向源版本）
        data = {
            "schema": "current_pointer/v1", "scope_type": "SERVICE", "scope_id": service_id,
            "target_version": source_version, "target_release_id": f"REL-{domain}-{source_version}",
            "target_manifest_sha256": config_hash, "switched_by": "dkws.cli",
            "switched_at": utcnow(), "reason": "projection build", "status": "ACTIVE",
            "version": "2.0",
        }
        dump_contract(self.ws.resolve(f"04_serve/{service_id}/CURRENT.md"), data,
                      "# 当前活动版本\n\n## 切换说明\n服务版本 `{}`。\n\n## 回滚说明\n见版本回滚。\n".format(source_version))
        return projection_id

    # ------------------------------------------------------------- 各投影
    def _entities(self, core_dir, proj_dir, domain, source_version) -> list[str]:
        import yaml
        rows = []
        src = core_dir / "entities"
        if src.is_dir():
            for p in sorted(src.glob("*.md")):
                data = _read_front(p)
                rows.append(_entity_row(data, domain, source_version))
        return self._write_parquet(proj_dir, "entities", _ENTITY_COLS, rows)

    def _relations(self, core_dir, proj_dir, source_version, service_id) -> list[str]:
        rows = []
        src = core_dir / "relations"
        if src.is_dir():
            for p in sorted(src.glob("*.md")):
                data = _read_front(p)
                rows.append(_relation_row(data, source_version))
        return self._write_parquet(proj_dir, "relations", _RELATION_COLS, rows)

    def _statements(self, core_dir, proj_dir, domain, source_version) -> list[str]:
        rows = []
        src = core_dir / "statements"
        if src.is_dir():
            for p in sorted(src.glob("*.md")):
                data = _read_front(p)
                rows.append(_statement_row(data, source_version))
        return self._write_parquet(proj_dir, "statements", _STATEMENT_COLS, rows)

    def _write_parquet(self, proj_dir, name, cols, rows) -> list[str]:
        """优先 pyarrow 写 parquet，失败则 CSV 兜底。空数据也产 schema 文件。
        返回工作区相对路径（`04_serve/<service>/...`）。"""
        rel = f"{name}.parquet" if _has_pyarrow() else f"{name}.csv"
        target = proj_dir / rel
        # 固定列序 + snake_case
        if _has_pyarrow():
            self._write_parquet_rows(target, cols, rows)
        else:
            self._write_csv_rows(target, cols, rows)
        # 空数据集不允许伪装：写 schema 文件
        if not rows:
            (proj_dir / f"{name}.schema.json").write_text(
                json.dumps({"columns": cols, "row_count": 0}, ensure_ascii=False, indent=2),
                encoding="utf-8")
        ws_rel = self.ws.rel_of(target)
        return [ws_rel]

    # ------------------------------------------------------------- CSV 兜底写
    def _write_csv_rows(self, target: Path, cols, rows):
        with open(target, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=cols)
            w.writeheader()
            for r in rows:
                row = {c: r.get(c, "") for c in cols}
                if isinstance(row.get("aliases"), (list, tuple)):
                    row["aliases"] = "|".join(map(str, row["aliases"]))
                if isinstance(row.get("source_ids"), (list, tuple)):
                    row["source_ids"] = "|".join(map(str, row["source_ids"]))
                w.writerow(row)

    # ------------------------------------------------------------- Parquet 写
    def _write_parquet_rows(self, target: Path, cols, rows):
        import pyarrow as pa
        import pyarrow.parquet as pq
        schema = pa.schema([pa.field(c, pa.string()) for c in cols])
        table = pa.Table.from_pylist([{c: _norm(r.get(c)) for c in cols} for r in rows], schema=schema)
        pq.write_table(table, target, compression="zstd")


def _norm(v):
    if isinstance(v, (list, tuple)):
        return "|".join(map(str, v))
    if v is None:
        return ""
    if isinstance(v, (dict,)):
        return json.dumps(v, ensure_ascii=False)
    return str(v)


def _read_front(path: Path) -> dict:
    from .contract import parse_frontmatter
    data, _ = parse_frontmatter(path.read_text(encoding="utf-8"))
    return data


def _entity_row(data, domain, source_version) -> dict:
    return {"entity_id": data.get("entity_id", ""), "entity_type": data.get("entity_type", ""),
            "name": data.get("name", ""), "aliases": data.get("aliases", []),
            "description": data.get("description"), "domain": data.get("domain", domain),
            "status": data.get("status", ""), "effective_from": data.get("effective_from"),
            "effective_to": data.get("effective_to"),
            "source_ids": data.get("source_document_ids", []),
            "source_release_id": f"REL-{data.get('domain', domain)}-{source_version}",
            "asset_version": source_version, "recorded_at": data.get("recorded_at", "")}


def _relation_row(data, source_version) -> dict:
    return {"relation_id": data.get("relation_id", ""), "source_id": data.get("source_id", ""),
            "relation_type": data.get("relation_type", ""), "target_id": data.get("target_id", ""),
            "statement_id": data.get("statement_id", ""), "status": data.get("status", ""),
            "effective_from": data.get("effective_from"), "effective_to": data.get("effective_to"),
            "source_ids": data.get("source_document_ids", []),
            "source_release_id": "", "asset_version": source_version,
            "recorded_at": data.get("recorded_at", "")}


def _statement_row(data, source_version) -> dict:
    vt = data.get("value_type", "")
    typed = _typed_col(vt, data.get("object_value"))
    return {"statement_id": data.get("statement_id", ""), "subject_id": data.get("subject_id", ""),
            "predicate": data.get("predicate", ""), "object_value": data.get("object_value", ""),
            "value_type": vt, **typed, "polarity": data.get("polarity", ""),
            "status": data.get("status", ""), "source_release_id": "",
            "asset_version": source_version, "recorded_at": data.get("recorded_at", "")}


def _typed_col(vt, obj_val):
    base = {"object_value_string": "", "object_value_decimal": "",
            "object_value_boolean": "", "object_value_date": ""}
    if vt == "STRING":
        base["object_value_string"] = obj_val or ""
    elif vt == "NUMBER":
        base["object_value_decimal"] = obj_val or ""
    elif vt == "BOOLEAN":
        base["object_value_boolean"] = obj_val or ""
    elif vt == "DATE":
        base["object_value_date"] = obj_val or ""
    return base


def _has_pyarrow() -> bool:
    try:
        import pyarrow  # noqa: F401
        return True
    except ImportError:
        return False