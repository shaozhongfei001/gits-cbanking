"""工作区初始化和元数据（DKWS-SPEC-001 §3/§4）。五层目录布局 + 元数据 + 可见性/大小约束。

工作区布局：
    01_raw/       原始接入
    02_work/      加工产物
    03_core/      核心知识（受控，按 domain/version）
    04_serve/     服务投影
    90_control/   控制面（catalog/schema/decisions/jobs/logs/lineage/quality）
"""

from __future__ import annotations

from pathlib import Path

import yaml

from .errors import ConflictError, NotFoundError

META_FILE = "dkws.meta.yaml"
LAYERS = ["01_raw", "02_work", "03_core", "04_serve", "90_control"]

DEFAULT_META = {
    "schema_version": "dkws/0.1",
    "spec_version": "1.0",
    "mode": "simulation",
    "read_only_generated": True,
    "max_bytes_per_file": 8 * 1024 * 1024,   # 8 MiB 单文件上限（演示）
    "max_batch_files": 256,
    "allow_http": False,
    "created_at": "",
}

_WORKSPACE_MARKERS = [META_FILE, *LAYERS]


def _guard_path(root: Path) -> None:
    if not root.exists():
        raise NotFoundError(f"工作区不存在: {root}")
    resolved = root.resolve()
    for layer in LAYERS:
        if not (resolved / layer).is_dir():
            raise ConflictError(f"工作区缺少层目录 {layer}（{resolved}）")


class Workspace:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.meta_file = self.root / META_FILE

    # ------------------------------------------------------------- init
    @classmethod
    def init(cls, root: Path, *, by: str = "dkws.cli", reason: str = "init") -> "Workspace":
        root.mkdir(parents=True, exist_ok=True)
        meta = dict(DEFAULT_META)
        from .hashing import utcnow
        meta["created_at"] = utcnow()
        meta["created_by"] = by
        meta["reason"] = reason
        for layer in LAYERS:
            (root / layer).mkdir(parents=True, exist_ok=True)
        # 控制面子目录就绪
        for sub in ("catalog", "catalog/services", "decisions", "logs", "lineage",
                    "schema", "schema/vocabulary", "schema/mappings", "schema/policies",
                    "quality", "quality/rules", "jobs"):
            (root / "90_control" / sub).mkdir(parents=True, exist_ok=True)
        (root / "02_work" / "U").mkdir(parents=True, exist_ok=True)
        (root / "02_work" / "Q").mkdir(parents=True, exist_ok=True)
        meta_file = root / META_FILE
        meta_file.write_text(yaml.safe_dump(meta, sort_keys=False, allow_unicode=True), encoding="utf-8")
        return cls(root)

    # ------------------------------------------------------------- open
    @classmethod
    def open(cls, root: Path) -> "Workspace":
        ws = cls(root)
        _guard_path(root)
        return ws

    # ------------------------------------------------------------- meta
    def load_meta(self) -> dict:
        if not self.meta_file.exists():
            raise NotFoundError(f"工作区元数据缺失: {self.meta_file}")
        return yaml.safe_load(self.meta_file.read_text(encoding="utf-8"))

    def update_meta(self, **changes) -> dict:
        meta = self.load_meta()
        meta.update(changes)
        self.meta_file.write_text(yaml.safe_dump(meta, sort_keys=False, allow_unicode=True), encoding="utf-8")
        return meta

    # ------------------------------------------------------------- inspect
    def inspect(self) -> dict:
        _guard_path(self.root)
        meta = self.load_meta()
        layers = {}
        for layer in LAYERS:
            layers[layer] = _tree(self.root / layer)
        return {
            "root": str(self.root),
            "schema": meta.get("schema_version"),
            "meta": meta,
            "layers": layers,
        }

    # ------------------------------------------------------------- path guard
    def resolve(self, rel: str | Path) -> Path:
        """把工作区相对路径解析为绝对路径；拒绝越界（路径穿越防护，§20 安全）。"""
        p = (self.root / rel).resolve()
        if not p.is_relative_to(self.root):
            from .errors import SecurityError
            raise SecurityError(f"路径越出工作区边界: {rel}")
        return p

    def rel_of(self, path: Path) -> str:
        resolved = path.resolve()
        return str(resolved.relative_to(self.root))


def _tree(path: Path) -> list[str]:
    if not path.is_dir():
        return []
    out = []
    for p in sorted(path.rglob("*")):
        if p.is_file():
            out.append(str(p.relative_to(path)))
    return out