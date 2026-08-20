"""可选 HTTP API（DKWS-SPEC-001 §12 可选，Gate P8）。

依赖 fastapi/pydantic 仅在调用 create_app / 运行 api 服务时才加载；不强制。
不返回宿主绝对路径；字段 snake_case；带 request_id/status/data/errors[]/meta。
"""

from __future__ import annotations

from pathlib import Path

from .service import KnowledgeService
from .workspace import Workspace


class RuleRequest:  # 等价 pydantic 模型（schema 仅用于类型提示）
    def __init__(self, rule_id: str, domain: str, inputs: dict | None = None,
                 version: str | None = None):
        self.rule_id = rule_id
        self.domain = domain
        self.inputs = inputs or {}
        self.version = version


def create_app(ws_root: Path, meta: dict | None = None):
    """创建 FastAPI 应用。需要 fastapi。
    若环境未安装 fastapi，抛出明确的 RuntimeError（HTML-HTTP 为可选能力）。
    """
    try:
        from fastapi import FastAPI, HTTPException, Query
        import pydantic  # noqa: F401
    except ImportError as exc:  # pragma: no cover - 取决于环境
        raise RuntimeError(
            "HTTP API 需要可选依赖 fastapi+pydantic，当前未安装。"
            "请 `pip install 'dkws[http]'` 或在 pyproject 启用 http 可选组后运行。"
        ) from exc

    ws = Workspace.open(ws_root)
    svc = KnowledgeService(ws)
    meta = meta or ws.load_meta()

    app = FastAPI(title="DKWS 服务 API", version="0.1.0")

    @app.get("/health")
    def health():
        return {"status": "ok", "mode": meta.get("mode")}

    @app.get("/api/v1/query")
    def api_query(domain: str, version: str | None = None, entity_type: str | None = None,
                  request_id: str | None = None):
        resp = svc.query(domain=domain, version=version, entity_type=entity_type,
                         request_id=request_id)
        return resp.as_dict("http", version or "current")

    @app.get("/api/v1/search")
    def api_search(query: str, domain: str = "knowledge", version: str | None = None,
                   request_id: str | None = None):
        resp = svc.search(query=query, domain=domain, version=version, request_id=request_id)
        return resp.as_dict("http", version or "current")

    @app.post("/api/v1/rule")
    def api_rule(req: RuleRequest):
        resp = svc.run_rule(rule_id=req.rule_id, inputs=req.inputs, domain=req.domain,
                            version=req.version)
        return resp.as_dict("http", req.version or "current")

    @app.post("/api/v1/projection")
    def api_projection(req: "ProjectionRequest"):
        resp = svc.build_projection(service_id=req.service_id, domain=req.domain,
                                    version=req.version)
        return resp.as_dict("http", req.version)

    return app