"""演示：给定客户 ID，LLM「读知识地图」→ 组装数据 → 输出访前报告。

链路（对应 apps/api：KnowledgeWikiService + KnowledgeDrivenPrevisitReportGenerator）：
    客户ID + 访前任务
  → 读根知识地图 ROOT_KNOWLEDGE_MAP → 对公客户域地图 DOMAIN_MAP
  → 触发激活合同 AC-PREVISIT-001（客户画像/授信/互动历史/交易/外部信号/KYC/产品卡/SOP）
  → 模拟 LLM 按合同 sequence 逐个从 DKWS 已发布核心知识检索该客户数据
  → 按优先级组装知识上下文
  → 输出结构化访前报告（JSON + Markdown）

合成数据演示，不代表真实客户。
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from dkws import schemas  # noqa: E402,F401
from dkws.service import KnowledgeService as ServiceApi  # noqa: E402
from dkws.workspace import Workspace  # noqa: E402

SPECS = REPO_ROOT / "specs" / "knowledge-architecture"
ACTIVATION = SPECS / "activations" / "AC-PREVISIT-001.json"

VISIT_OBJECTIVES = {
    "P-VISIT-001": {
        "customerId": "CUST-001",
        "objective": "营销现金流管理+供应链金融，覆盖二期智能制造项目资金需求",
        "theme": "产业升级融资 + 现金管理配对",
        "rm": "P-RM-001",
    },
}

# 激活合同所需资产 → DKWS 服务检索的实体类型/谓词
ASSET_TO_KEY = {
    "ASSET-DATA-CUSTOMER-PROFILE": ("CUSTOMER", None),
    "ASSET-KNOW-CUSTOMER-ONTOLOGY": ("ONTOLOGY_OBJECT", None),
    "ASSET-DATA-CREDIT-FACILITY": ("CREDIT_FACILITY", None),
    "ASSET-DATA-INTERACTION-HISTORY": ("INTERACTION", None),
    "ASSET-KNOW-KYC-QUESTION-LIBRARY": ("KYC_QUESTION", None),
    "ASSET-KNOW-PRODUCT-CARDS": ("PRODUCT_RULE_VERSION", None),
    "ASSET-KNOW-VISIT-SOP": ("VISIT_SOP", None),
}


class MockLlm:
    """模拟 LLM：不真正调外部模型，用确定性的受控规则把已检索的 DKWS 数据组装成语义上下文。

    等价真实 LLM 读图行为：给定激活合同 + 已检索数据 → 生成结构化访前要点。
    """

    def compose(self, activation, retrieved: dict):
        sections = []
        for act in activation["activations"]:
            key = ASSET_TO_KEY.get(act["assetId"])
            matched = retrieved.get(act["assetId"], [])
            section = {
                "assetId": act["assetId"],
                "purpose": act["purpose"],
                "required": act["required"],
                "sequence": act["sequence"],
                "items": [m["name"] for m in matched],
            }
            sections.append(section)
        return sections


class PrevisitAssembler:
    def __init__(self, ws_root: Path, llm_mode: str = "mock"):
        self.ws = Workspace.open(ws_root)
        self.api = ServiceApi(self.ws)
        self.llm_mode = llm_mode
        if llm_mode == "real":
            from dkws.llm import RealLlm
            self.llm = RealLlm()   # 真实 DeepSeek 调用（凭据从环境加载）
            self._llm_note = "real-llm"
            self._max_tokens = 2048
        elif llm_mode == "mock":
            self.llm = MockLlm()
            self._llm_note = "mock-llm"
        else:
            raise ValueError(f"非法 --llm 模式: {llm_mode}（可选 real/mock）")

    def run(self, visit_id: str) -> dict:
        spec = VISIT_OBJECTIVES[visit_id]
        cid = spec["customerId"]

        # 1) 读根知识地图
        root_map = self._read_map(SPECS / "maps" / "ROOT_KNOWLEDGE_MAP.md")
        domain_ref = root_map["domainRef"]

        # 2) 读领域地图（对公持续经营）
        domain_map = self._read_map(SPECS / "maps" / domain_ref)
        # 3) 激活合同
        activation = json.loads(ACTIVATION.read_text(encoding="utf-8"))

        # 4) 模拟 LLM 按合同检索该客户在 DKWS 的已发布数据
        retrieved = self._retrieve(cid, activation)

        # 5) LLM 组装知识上下文（按 sequence/required 排序）
        sections = self.llm.compose(activation, retrieved)

        # 6) 生成访前报告
        report = self._render_report(spec, root_map, domain_map, activation, sections)
        report["llmMode"] = self._llm_note
        return report

    # --------------------------------------------------------- 地图读取
    def _read_map(self, path: Path) -> dict:
        text = path.read_text(encoding="utf-8")
        fm, body = _split_frontmatter(text)
        import re as _re
        m = _re.search(r"# \[对公客户持续经营\]\(([^)]+\.md)\)", body)
        domain_ref = m.group(1) if m else "corporate-rm/DOMAIN_MAP.md"
        fm["_body"] = body
        fm["domainRef"] = domain_ref
        return fm

    # --------------------------------------------------------- 数据检索
    def _retrieve(self, cid: str, activation: dict) -> dict:
        retrieved = {}
        for act in activation["activations"]:
            key = ASSET_TO_KEY.get(act["assetId"])
            if not key:
                retrieved[act["assetId"]] = []
                continue
            etype, _pred = key
            # 命中该客户
            hits = self._query_entities(etype)
            # CUSTOMER 只取该客户；其它取与客户同源/同 doc
            if etype == "CUSTOMER":
                hits = [h for h in hits if h["entity_id"] == cid]
            retrieved[act["assetId"]] = hits
        return retrieved

    def _query_entities(self, etype) -> list:
        """跨已发布版本聚合实体：激活合同需要的资产可能分布在多个 release 版本。
        直接遍历 03_core/knowledge/version=*/entities/*.md，收集指定类型的已发布实体。"""
        from dkws.contract import parse_frontmatter
        base = self.ws.root / "03_core" / "knowledge"
        if not base.is_dir():
            return []
        hits = []
        for vdir in sorted(base.glob("version=*")):
            ent_dir = vdir / "entities"
            if not ent_dir.is_dir():
                continue
            for p in sorted(ent_dir.glob("*.md")):
                try:
                    data, _ = parse_frontmatter(p.read_text(encoding="utf-8"))
                except Exception:  # noqa: BLE001
                    continue
                if data.get("status") != "PUBLISHED":
                    continue
                if etype and data.get("entity_type") != etype:
                    continue
                hits.append({"entity_id": data.get("entity_id"), "name": data.get("name"),
                             "entity_type": data.get("entity_type"), "domain": data.get("domain"),
                             "status": data.get("status")})
        return hits

    # --------------------------------------------------------- 报告
    def _render_report(self, spec, root_map, domain_map, activation, sections,
                       section_kwargs=None) -> dict:
        # 数据完整度：required 资产是否命中
        required_hits = {}
        missing = []
        for s in sections:
            if s["required"]:
                required_hits[s["assetId"]] = len(s["items"]) > 0
                if not s["items"]:
                    missing.append(s["assetId"])
        ready = not missing

        report = {
            "schema": "previsit_report/r1",
            "visitId": spec.get("visitId", "P-VISIT-001"),
            "customerId": spec["customerId"],
            "rm": spec["rm"],
            "objective": spec["objective"],
            "theme": spec["theme"],
            "knowledgePath": {
                "rootMap": f"{root_map.get('mapId')}@{root_map.get('version')}",
                "domainMap": domain_map.get("mapId", domain_map.get("_body", "")[:30]),
                "activationContract": activation["contractId"],
                "routeMode": activation["routeMode"],
            },
            "dataAssembly": {
                "activationSequenced": [
                    {"sequence": s["sequence"], "assetId": s["assetId"],
                     "purpose": s["purpose"], "required": s["required"],
                     "items": s["items"]}
                    for s in sections
                ],
                "missingRequiredAssets": missing,
                "readyToReport": ready,
            },
            "priorityOrder": activation["context"]["priorityOrder"],
            "humanGates": activation["humanGates"],
            "status": "READY" if ready else "GATED_BY_MISSING_ASSETS",
        }
        return report

    # --------------------------------------------------------- 便捷
    def render_markdown(self, report: dict) -> str:
        lines = ["# 访前报告（访前准备数据组装）",
                 "", f"**客户**: {report['customerId']}  |  **客户经理**: {report['rm']}  |  报告ID: {report['visitId']}",
                 "", f"**访问目标**: {report['objective']}",
                 "", f"**主题**: {report['theme']}", "",
                 "## 知识读图路径",
                 f"`{report['knowledgePath']['rootMap']}` → `{report['knowledgePath']['domainMap']}` → `{report['knowledgePath']['activationContract']}`（{report['knowledgePath']['routeMode']}）",
                 "", "## 数据组装清单（按激活合同 sequence）", ""]
        for s in report["dataAssembly"]["activationSequenced"]:
            need = "必需" if s["required"] else "可选"
            items = "、".join(s["items"]) if s["items"] else "—"
            lines.append(f"- **{s['sequence']}.** {s['assetId']}（{need}）`{s['purpose']}` → {items}")
        lines += ["", f"## 就绪度",
                  f"- 缺失必备资产: {report['dataAssembly']['missingRequiredAssets'] or '无'}",
                  f"- 是否可就绪输出: {'是' if report['dataAssembly']['readyToReport'] else '否（人工门禁）'}",
                  f"- 人工门禁: {', '.join(report['humanGates'])}",
                  f"- 状态: {report['status']}", ""]
        return "\n".join(lines)


def _split_frontmatter(text: str):
    if text.startswith("---"):
        head, _, body = text[3:].partition("---")
        return json.loads(head), body.lstrip("\n")
    return {}, text


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ws", default="/tmp/dkws-rm-demo", help="DKWS 工作区（需先跑 demo_rm_data_access.py）")
    ap.add_argument("--visit", default="P-VISIT-001", help="访前访问 ID")
    ap.add_argument("--md", action="store_true", help="同时输出 Markdown 版本")
    ap.add_argument("--llm", default="mock", choices=["real", "mock"],
                    help="real=真实 DeepSeek（需环境 DSEEK_2026_SZF_KEY）；mock=确定性模拟")
    ap.add_argument("--max-tokens", type=int, default=2048)
    args = ap.parse_args()
    a = PrevisitAssembler(Path(args.ws), llm_mode=args.llm)
    report = a.run(args.visit)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if args.md:
        print("\n" + a.render_markdown(report))


if __name__ == "__main__":
    main()