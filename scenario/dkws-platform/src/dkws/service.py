"""CLI 服务层命令（DKWS-SPEC-001 §12/§10.8，Gate P8 G5）。

JSON 通则：request_id/status/data/errors[]/meta；字段 snake_case；不返回宿主绝对路径；
证据路径必须是工作区相对路径或逻辑 URI。
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from pathlib import Path

from .contract import parse_frontmatter
from .errors import NotFoundError, ValidationError
from .hashing import utcnow
from .projection import ProjectionBuilder
from .workspace import Workspace


@dataclass
class ServiceResponse:
    request_id: str
    status: str                # ok / error
    data: dict
    errors: list[dict] = field(default_factory=list)
    meta: dict = field(default_factory=dict)

    def as_dict(self, service_version: str, data_version: str) -> dict:
        return {
            "request_id": self.request_id,
            "status": self.status,
            "data": self.data,
            "errors": self.errors,
            "meta": {"service_version": service_version, "data_version": data_version,
                     "generated_at": utcnow()},
        }


class KnowledgeService:
    SERVICE_VERSION = "1.0"

    def __init__(self, ws: Workspace):
        self.ws = ws
        self.builder = ProjectionBuilder(ws)
        # 投影索引：{service_id: projection_dir}
        self._proj_cache: dict[str, Path] = {}

    # ------------------------------------------------------------- 数据读取（相对路径）
    def query(self, *, domain: str, version: str | None = None, entity_type: str | None = None,
              request_id: str | None = None) -> ServiceResponse:
        rid = request_id or _rid()
        core = self._core(domain, version)
        rows = []
        ent_dir = core / "entities"
        if ent_dir.is_dir():
            for p in sorted(ent_dir.glob("*.md")):
                data, _ = parse_frontmatter(p.read_text(encoding="utf-8"))
                if data.get("status") != "PUBLISHED":
                    continue
                if entity_type and data.get("entity_type") != entity_type:
                    continue
                rows.append({"entity_id": data.get("entity_id"), "name": data.get("name"),
                             "entity_type": data.get("entity_type"), "domain": data.get("domain"),
                             "status": data.get("status")})
        return ServiceResponse(rid, "ok", {"entity_count": len(rows), "entities": rows})

    # ------------------------------------------------------------- 检索
    def search(self, *, query: str, domain: str, version: str | None = None,
               request_id: str | None = None) -> ServiceResponse:
        rid = request_id or _rid()
        core = self._core(domain, version)
        q = query.lower()
        hits = []
        for kind in ("entities", "relations", "statements"):
            d = core / kind
            if not d.is_dir():
                continue
            for p in sorted(d.glob("*.md")):
                text = p.read_text(encoding="utf-8")
                if q in text.lower():
                    data, _ = parse_frontmatter(text)
                    hits.append({"kind": kind[:-1], "id": data.get(f"{kind[:-1]}_id"),
                                 "path": self.ws.rel_of(p)})
        hits = hits[:50]
        return ServiceResponse(rid, "ok", {"hit_count": len(hits), "hits": hits})

    # ------------------------------------------------------------- 规则执行
    def run_rule(self, *, rule_id: str, inputs: dict, domain: str, version: str | None = None,
                 request_id: str | None = None) -> ServiceResponse:
        rid = request_id or _rid()
        core = self._core(domain, version)
        rules_dir = core / "rules"
        rule_file = None
        if rules_dir.is_dir():
            for p in rules_dir.glob("*.md"):
                if p.stem.split("-")[-1] == rule_id or rule_id in p.stem:
                    rule_file = p
                    break
        if rule_file is None or not rule_file.exists():
            return ServiceResponse(rid, "error", {}, [{"code": "RULE_NOT_FOUND",
                                                       "message": f"规则不存在: {rule_id}",
                                                       "field": None, "retryable": False}])
        data, _ = parse_frontmatter(rule_file.read_text(encoding="utf-8"))
        outcome = _eval_rule(data, inputs)
        return ServiceResponse(rid, "ok", {"rule_id": rule_id, "outcome": outcome,
                                           "evaluated_by": data.get("name")})

    # ------------------------------------------------------------- 投影 / CURRENT
    def build_projection(self, *, service_id: str, domain: str, version: str,
                         request_id: str | None = None) -> ServiceResponse:
        rid = request_id or _rid()
        try:
            proj_id = self.builder.build(service_id, domain=domain, source_version=version)
            return ServiceResponse(rid, "ok", {"projection_id": proj_id,
                                               "service_id": service_id,
                                               "version": version})
        except (ValidationError, NotFoundError) as exc:
            return ServiceResponse(rid, "error", {}, [{"code": getattr(exc, "code",
                                                                       "BUILD_ERROR"),
                                                       "message": exc.message
                                                       if hasattr(exc, "message") else str(exc),
                                                       "field": None, "retryable": False}])

    # ------------------------------------------------------------- helper
    def _core(self, domain: str, version: str | None) -> Path:
        base = self.ws.resolve(f"03_core/{domain}")
        if version is None:
            current = base / "CURRENT.md"
            if not current.exists():
                raise ValidationError(f"领域 {domain} 尚未发布")
            data, _ = parse_frontmatter(current.read_text(encoding="utf-8"))
            version = data["target_version"]
        core = base / f"version={version}"
        if not core.is_dir():
            raise ValidationError(f"版本目录不存在: {version}")
        return core


def _rid() -> str:
    return f"req-{uuid.uuid4().hex[:16]}"


def _eval_rule(data: dict, inputs: dict) -> dict:
    """基于 when/then 的受限规则执行。when 为 list DSL：['all', cond...] 等。"""
    when = data.get("when", [])
    satisfied = _eval_when(when, inputs)
    then = data.get("then", {})
    action = then.get("action") if isinstance(then, dict) else None
    result = {
        "rule_type": data.get("rule_type"),
        "execution_mode": data.get("execution_mode"),
        "fired": bool(satisfied),
    }
    if satisfied:
        result["action"] = action
        if isinstance(then, dict):
            result["set"] = then.get("set", {})
            result["message"] = then.get("message")
    return result


def _eval_when(node, inputs: dict) -> bool:
    if isinstance(node, list):
        if not node:
            return True
        op = node[0]
        args = node[1:]
        if op == "all":
            return all(_eval_when(a, inputs) for a in args)
        if op == "any":
            return any(_eval_when(a, inputs) for a in args)
        if op == "not":
            return not _eval_when(args[0], inputs) if args else True
        if op in ("eq", "ne", "gt", "gte", "lt", "lte"):
            if len(args) != 2:
                return False
            left = _resolv(args[0], inputs)
            right = _resolv(args[1], inputs)
            return _cmp(op, left, right)
        if op == "in":
            return _resolv(args[0], inputs) in (_resolv(args[1], inputs) or [])
        if op == "is_null":
            return _resolv(args[0], inputs) is None
        if op == "exists":
            k = args[0] if isinstance(args[0], str) else None
            return k in inputs if k else False
        return False
    if isinstance(node, str):
        return bool(_resolv(node, inputs))
    return bool(node)


def _resolv(x, inputs):
    if isinstance(x, str) and x.startswith("input."):
        key = x.split(".", 1)[1]
        return inputs.get(key)
    return x


def _cmp(op, a, b):
    try:
        if op == "eq":
            return a == b
        if op == "ne":
            return a != b
        ops = {"gt": lambda x, y: x > y, "gte": lambda x, y: x >= y,
               "lt": lambda x, y: x < y, "lte": lambda x, y: x <= y}
        if op not in ops:
            return False
        try:
            return ops[op](float(a), float(b))
        except (TypeError, ValueError):
            # 数值比较失败时按字符串相等回退
            return ops[op](str(a), str(b))
    except (TypeError, ValueError):
        return False