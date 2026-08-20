"""dkws 命令行入口。

子命令：
    init / inspect                    工作区（P0）
    ingest / docs register|slice      接入与文档（P2/P4）
    knowledge candidate|conflict|decide（P5）
    publish / rollback                发布（P6）
    projection build                  投影（P7）
    service query|search|rule         服务（P8）
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import click

from . import __version__
from .docs import DocumentPipeline
from .ingest import IngestionService
from .knowledge import KnowledgeService
from .publish import Publisher
from .service import KnowledgeService as Service
from .workspace import Workspace

_smuggled_ctx = {}


def _ws(ctx: click.Context) -> Workspace:
    root = Path(ctx.obj.get("root", "."))
    return Workspace.open(root)


@click.group()
@click.version_option(__version__)
@click.option("--root", default=".", show_default=True, help="工作区根目录")
@click.pass_context
def dkws(ctx: click.Context, root: str):
    ctx.ensure_object(dict)
    ctx.obj["root"] = root


# ---------------------------------------------------------------- P0 工作区
@dkws.command()
@click.argument("root", type=click.Path(path_type=Path))
def init(root: Path):
    """初始化五层工作区。"""
    ws = Workspace.init(root)
    click.echo(f"已初始化工作区: {ws.root}")


@dkws.command()
@click.pass_context
def inspect(ctx: click.Context):
    """检视工作区结构与元数据。"""
    ws = _ws(ctx)
    info = ws.inspect()
    click.echo(json.dumps({"root": info["root"], "schema": info["schema"]},
                          ensure_ascii=False, indent=2))


# ---------------------------------------------------------------- P2 接入
@dkws.command()
@click.pass_context
@click.option("--source", "source_", required=True, type=click.Path(path_type=Path, exists=True))
@click.option("--domain", required=True, type=click.Choice(["nodes", "payroll", "knowledge"]))
@click.option("--idempotency-key", required=True)
def ingest(ctx: click.Context, source_: Path, domain: str, idempotency_key: str):
    """接入 raw 文件/目录批次。"""
    svc = IngestionService(_ws(ctx))
    result = svc.ingest(source_, domain=domain, idempotency_key=idempotency_key)
    click.echo(json.dumps({"batch_id": result.batch_id, "domain": result.domain,
                           "manifest": result.manifest_path,
                           "content_sha256": result.content_sha256},
                          ensure_ascii=False, indent=2))


# ---------------------------------------------------------------- P4 文档
@dkws.command("docs")
@click.pass_context
@click.argument("doc_id")
@click.option("--source", "source_", required=True, type=click.Path(path_type=Path, exists=True))
@click.option("--domain", required=True, type=click.Choice(["nodes", "payroll", "knowledge"]))
@click.option("--name", default="演示文档")
@click.option("--classification", default="INTERNAL")
@click.option("--owner", default="demo")
def docs(ctx: click.Context, doc_id: str, source_: Path, domain: str, name: str,
         classification: str, owner: str):
    """登记文档并规范化切片。"""
    pipe = DocumentPipeline(_ws(ctx))
    text = source_.read_text(encoding="utf-8")
    pipe.register(doc_id, name=name, source_file=source_.name, domain=domain,
                  classification=classification, owner=owner)
    outcome = pipe.normalize_and_slice(doc_id, domain, text)
    click.echo(json.dumps({"document_id": outcome.document_id,
                           "normalized_id": outcome.normalized_id,
                           "segments": outcome.segment_count},
                          ensure_ascii=False, indent=2))


# ---------------------------------------------------------------- P5 知识
@dkws.command("knowledge.candidate")
@click.pass_context
@click.option("--domain", required=True, type=click.Choice(["nodes", "payroll", "knowledge"]))
def knowledge_candidate(ctx: click.Context, domain: str):
    """从已切片文档生成知识候选。"""
    svc = KnowledgeService(_ws(ctx))
    # 查找最新切片文档
    u_dir = _ws(ctx).root / "02_work" / "U"
    docs = [p.name for p in u_dir.iterdir() if (u_dir / p.name / "segments").is_dir()]
    doc = docs[0] if docs else "DOC-DEMO"
    # 实体必须是关系的目标（关系引用完整性）
    svc.register_entity_candidate(
        entity_id=f"{domain}-corp", entity_type="CORPORATE_ENTITY", name="示例公司",
        aliases=["demo"], domain=domain, source_document_ids=[doc])
    svc.register_entity_candidate(
        entity_id=f"{domain}-asset", entity_type="ASSET", name="示例资产",
        aliases=["asset"], domain=domain, source_document_ids=[doc])
    svc.register_statement_candidate(
        statement_id=f"{domain}-net", subject_id=f"{domain}-corp", predicate="net_worth",
        object_value="1000000", value_type="NUMBER", source_document_ids=[doc])
    svc.register_relation_candidate(
        relation_id=f"{domain}-owns", source_id=f"{domain}-corp", target_id=f"{domain}-asset",
        relation_type="OWNS", direction="DIRECTED", statement_id=f"{domain}-net",
        source_document_ids=[doc])
    click.echo(json.dumps({"registered": ["entity", "entity", "statement", "relation"]},
                          ensure_ascii=False, indent=2))


@dkws.command("knowledge.conflict")
@click.pass_context
def knowledge_conflict(ctx: click.Context):
    """检测知识候选冲突。"""
    svc = KnowledgeService(_ws(ctx))
    n = svc.detect_conflicts()
    click.echo(json.dumps({"conflicts": n}, ensure_ascii=False, indent=2))


@dkws.command("knowledge.decide")
@click.pass_context
@click.option("--decision-id", required=True)
@click.option("--object-ref", "object_refs", multiple=True, required=True)
@click.option("--decision", required=True,
              type=click.Choice(["APPROVE", "REJECT", "REQUEST_CHANGES", "WAIVE"]))
@click.option("--decided-by", required=True)
@click.option("--role", required=True)
def knowledge_decide(ctx: click.Context, decision_id: str, object_refs, decision: str,
                     decided_by: str, role: str):
    """记录审核决定并应用。"""
    svc = KnowledgeService(_ws(ctx))
    rel = svc.record_decision(decision_id=decision_id, object_refs=list(object_refs),
                              decision=decision, decided_by=decided_by, role=role,
                              reason="manual decision")
    click.echo(json.dumps({"decision": rel}, ensure_ascii=False, indent=2))


# ---------------------------------------------------------------- P6 发布
@dkws.command()
@click.pass_context
@click.option("--domain", required=True, type=click.Choice(["nodes", "payroll", "knowledge"]))
@click.option("--approval", "approvals", multiple=True)
def publish(ctx: click.Context, domain: str, approvals):
    """发布 CURRENT 版本（需审核决定）。"""
    pub = Publisher(_ws(ctx))
    out = pub.publish(domain, approved_decision_ids=list(approvals))
    click.echo(json.dumps({"release_id": out.release_id, "version": out.version,
                           "manifest_sha256": out.manifest_sha256},
                          ensure_ascii=False, indent=2))


@dkws.command()
@click.pass_context
@click.option("--domain", required=True, type=click.Choice(["nodes", "payroll", "knowledge"]))
@click.option("--version", required=True)
def rollback(ctx: click.Context, domain: str, version: str):
    """回滚 CURRENT 到指定版本。"""
    pub = Publisher(_ws(ctx))
    click.echo(pub.rollback(domain, version))


# ---------------------------------------------------------------- P7 投影
@dkws.command("projection.build")
@click.pass_context
@click.option("--service", required=True)
@click.option("--domain", required=True, type=click.Choice(["nodes", "payroll", "knowledge"]))
@click.option("--version", required=True)
def projection_build(ctx: click.Context, service: str, domain: str, version: str):
    """构建服务投影。"""
    svc = Service(_ws(ctx))
    resp = svc.build_projection(service_id=service, domain=domain, version=version)
    click.echo(json.dumps(resp.as_dict("cli", version), ensure_ascii=False, indent=2))


# ---------------------------------------------------------------- P8 服务
@dkws.command("service.query")
@click.pass_context
@click.option("--domain", required=True, type=click.Choice(["nodes", "payroll", "knowledge"]))
@click.option("--version", default=None)
@click.option("--entity-type", default=None)
def service_query(ctx: click.Context, domain: str, version: str, entity_type: str):
    svc = Service(_ws(ctx))
    resp = svc.query(domain=domain, version=version, entity_type=entity_type)
    click.echo(json.dumps(resp.as_dict("cli", version or "current"), ensure_ascii=False, indent=2))


@dkws.command("service.search")
@click.pass_context
@click.option("--query", required=True)
@click.option("--domain", required=True, type=click.Choice(["nodes", "payroll", "knowledge"]))
def service_search(ctx: click.Context, query: str, domain: str):
    svc = Service(_ws(ctx))
    resp = svc.search(query=query, domain=domain)
    click.echo(json.dumps(resp.as_dict("cli", "current"), ensure_ascii=False, indent=2))


@dkws.command("service.rule")
@click.pass_context
@click.option("--rule-id", required=True)
@click.option("--domain", required=True, type=click.Choice(["nodes", "payroll", "knowledge"]))
@click.option("--input", "inputs", multiple=True, help="key=value")
def service_rule(ctx: click.Context, rule_id: str, domain: str, inputs):
    svc = Service(_ws(ctx))
    kv = {}
    for item in inputs:
        k, _, v = item.partition("=")
        kv[k] = v
    resp = svc.run_rule(rule_id=rule_id, inputs=kv, domain=domain)
    click.echo(json.dumps(resp.as_dict("cli", "current"), ensure_ascii=False, indent=2))


def main():
    dkws()


if __name__ == "__main__":
    main()