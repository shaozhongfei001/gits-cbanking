#!/usr/bin/env python3
"""生成 GK-KE L1-1 公共语义正负例（C08 L1-1）。

12 个最小类型 = C01 §3 的 9 个公共核心类型 + 3 个域扩展类型。
依据：C01 §3「最小共享类型：Customer、LegalEntity、Organization、Account、Product、
Transaction、Money、TimeInterval、ExternalIdentifier」+ C08 L1-1「12 个最小类型/关系与域扩展」。
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POS = ROOT / "specs" / "gk-ke" / "v1" / "examples" / "l1-1" / "positive"
NEG = ROOT / "specs" / "gk-ke" / "v1" / "examples" / "l1-1" / "negative"

# C01 §3 的 9 个公共核心类型
CORE_TYPES = [
    ("core.Customer", "银行客户（法人或自然人）", "customerId 稳定且不可由名称替代", ["customerId", "custName", "certNo"], ["customerId"], "TEMPORAL", "CONFIDENTIAL"),
    ("core.LegalEntity", "法律主体，唯一可被工商登记识别的实体", "legalEntityId", ["legalEntityId", "registeredName", "registrationNo"], ["legalEntityId"], "TEMPORAL", "INTERNAL"),
    ("core.Organization", "银行内部组织单元（机构/部门）", "orgId", ["orgId", "orgName", "parentOrgId"], ["orgId"], "TEMPORAL", "INTERNAL"),
    ("core.Account", "账户，余额为存量", "accountId", ["accountId", "customerId", "currency", "balance"], ["accountId", "currency"], "TEMPORAL", "CONFIDENTIAL"),
    ("core.Product", "产品定义，代码由银行源权威", "productId", ["productId", "productVersion", "productName"], ["productId", "productVersion"], "TEMPORAL", "INTERNAL"),
    ("core.Transaction", "交易流水，金额为流量", "transactionId", ["transactionId", "accountId", "amount", "occurredAt"], ["transactionId", "amount"], "TEMPORAL", "CONFIDENTIAL"),
    ("core.Money", "金额值对象，十进制字符串或整数分，强制 currency 与 unit", "value+currency", ["value", "currency", "unit"], ["value", "currency", "unit"], "NON_TEMPORAL", "INTERNAL"),
    ("core.TimeInterval", "时间间隔，统一左闭右开 [from,to)", "from+to", ["from", "to"], ["from", "to"], "NON_TEMPORAL", "PUBLIC"),
    ("core.ExternalIdentifier", "外部标识，指向外部登记体系的稳定 ID", "scheme+value", ["scheme", "value", "issuedBy"], ["scheme", "value"], "TEMPORAL", "INTERNAL"),
]

# C08 L1-1 要求的 3 个域扩展类型
DOMAIN_TYPES = [
    ("domain.MetricDefinition", "指标定义（域扩展），由指标 Owner 定义，FULLY_ADDITIVE 等口径属性", "metricId+version", ["metricId", "metricVersion", "additivity", "currencyPolicy"], ["metricId", "metricVersion"], "TEMPORAL", "INTERNAL"),
    ("domain.OperatingTask", "GITS 经营任务（域扩展）", "taskId", ["taskId", "taskType", "customerId", "asOf"], ["taskId", "taskType"], "TEMPORAL", "CONFIDENTIAL"),
    ("domain.Recommendation", "候选建议（域扩展），须有来源与有效范围", "recommendationId", ["recommendationId", "subjectRef", "evidenceRefs"], ["recommendationId", "evidenceRefs"], "TEMPORAL", "INTERNAL"),
]


def build_types() -> list[dict]:
    out = []
    for origin, items in (("CORE", CORE_TYPES), ("DOMAIN", DOMAIN_TYPES)):
        for type_id, definition, identity, attrs, required, temporal, sensitive in items:
            out.append({
                "typeId": type_id,
                "definition": definition,
                "identityRule": identity,
                "origin": origin,
                "attributeTypes": attrs,
                "requiredAttributes": required,
                "relations": [],
                "temporal": temporal,
                "sensitive": sensitive,
            })
    return out


def base_positive() -> dict:
    return {
        "contractVersion": "gk-ke/v1",
        "simulationOnly": True,
        "packageId": "SIM-CORE",
        "version": "1.0.0",
        "coreVersion": "1.0.0",
        "ownerSystem": "CORE",
        "idConvention": {
            "scheme": "STABLE_OPAQUE",
            "immutable": True,
            "nameSubstitutionForbidden": True,
            "namespacePattern": "^SIM-[A-Z0-9-]+$",
        },
        "timeConvention": {
            "intervalNotation": "LEFT_CLOSED_RIGHT_OPEN",
            "businessDateZone": "Asia/Shanghai",
            "recordedAtFormat": "RFC3339_UTC_WITH_OFFSET",
        },
        "moneyConvention": {
            "representation": "DECIMAL_STRING",
            "decimalPattern": "^-?\\d+(\\.\\d+)?$",
            "currencyRequired": True,
            "unitRequired": True,
            "stockVsFlow": "STOCK",
            "fxShape": {
                "base": "USD",
                "quote": "CNY",
                "rate": "7.1234",
                "rateDate": "2026-09-01",
                "sourceRef": "SIM-FX-SRC-001",
            },
        },
        "types": build_types(),
        "imports": [
            {"id": "SIM-CORE", "version": "1.0.0", "packageKind": "CORE"},
            {"id": "SIM-SEM-DOMAIN-CORP", "version": "0.1.0", "packageKind": "DOMAIN"},
        ],
    }


def write(path: Path, doc: dict, rule: str | None = None, reason: str | None = None) -> None:
    payload = {}
    if rule:
        payload["expect_rule"] = rule
        payload["reason"] = reason
    payload.update(doc)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    base = base_positive()

    # ---- 正例 ----
    write(POS / "SemanticPackage.json", base)
    # 域包正例：通过 imports 引用核心，不复制改义
    # 域包同样须满足 12 项最小类型；此处以「引用核心 + 域扩展」视图表达，
    # 核心类型仍标 origin=CORE（表示引用而非重定义），故不触发 SHARED_TYPE_NOT_FORKED。
    domain = copy.deepcopy(base)
    domain["packageId"] = "SIM-SEM-DOMAIN-CORP"
    domain["version"] = "0.1.0"
    domain["ownerSystem"] = "CORE"
    domain["imports"] = [
        {"id": "SIM-CORE", "version": "1.0.0", "hash": "a" * 64, "packageKind": "CORE"},
    ]
    write(POS / "SemanticPackage_domain_package.json", domain)

    # ---- 负例 ----
    d = copy.deepcopy(base); d["types"] = d["types"][:11]
    write(NEG / "SemanticPackage_too_few_types.json", d, "MIN_12_TYPES", "只有 11 个类型，不足 12")

    d = copy.deepcopy(base)
    for t in d["types"]:
        t.pop("origin", None); t.pop("temporal", None); t.pop("sensitive", None)
    write(NEG / "SemanticPackage_type_missing_markers.json", d, "TYPE_MARKERS_REQUIRED", "类型缺 origin/temporal/sensitive 标记")

    d = copy.deepcopy(base)
    d["types"].append({
        "typeId": "core.Customer",
        "definition": "与首个 core.Customer 定义冲突的同名异义类型",
        "identityRule": "custNo",
        "origin": "DOMAIN",
        "attributeTypes": ["custNo"],
        "requiredAttributes": ["custNo"],
        "relations": [],
        "temporal": "TEMPORAL",
        "sensitive": "INTERNAL",
    })
    write(NEG / "SemanticPackage_homonym.json", d, "HOMONYM_CONFLICT", "同 typeId 重复登记且定义不同（同名异义）")

    d = copy.deepcopy(base)
    # 破坏变更：域包复制核心类型后改义（以 DOMAIN origin 重新定义 core.Customer）
    d["packageId"] = "SIM-SEM-DOMAIN-CORP"
    for t in d["types"]:
        if t["typeId"] == "core.Customer":
            t["origin"] = "DOMAIN"
            t["definition"] = "复制后改义：本地重新定义 Customer"
    write(NEG / "SemanticPackage_semantic_fork.json", d, "SHARED_TYPE_FORKED", "共享类型被复制后改义（破坏变更）")

    d = copy.deepcopy(base)
    d["idConvention"]["nameSubstitutionForbidden"] = False
    write(NEG / "SemanticPackage_identity_merge.json", d, "IDENTITY_MERGE_BY_NAME", "允许按名称自动 sameAs（身份误并）")

    d = copy.deepcopy(base); d.pop("coreVersion", None)
    write(NEG / "SemanticPackage_missing_core_version.json", d, "DUAL_VERSION_REQUIRED", "缺 coreVersion（双版本引用不完整）")

    d = copy.deepcopy(base); d.pop("idConvention", None)
    write(NEG / "SemanticPackage_missing_id_convention.json", d, "ID_CONVENTION_REQUIRED", "缺 ID 规范")

    d = copy.deepcopy(base); d["timeConvention"]["intervalNotation"] = "CLOSED_CLOSED"
    write(NEG / "SemanticPackage_bad_time_interval.json", d, "TIME_INTERVAL_CONVENTION", "时间间隔非左闭右开")

    d = copy.deepcopy(base); d["moneyConvention"]["representation"] = "FLOAT64"
    write(NEG / "SemanticPackage_bad_money_representation.json", d, "MONEY_REPRESENTATION", "金额表示非法")

    d = copy.deepcopy(base)
    d["moneyConvention"]["representation"] = "FLOAT64"
    d["moneyConvention"]["decimalPattern"] = None
    d["moneyConvention"].pop("decimalPattern", None)
    write(NEG / "SemanticPackage_money_as_float.json", d, "MONEY_FLOAT_FORBIDDEN", "金额以浮点表示（禁止）")

    print("L1-1 examples generated")
    print("  positive:", len(list(POS.glob('*.json'))))
    print("  negative:", len(list(NEG.glob('*.json'))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
