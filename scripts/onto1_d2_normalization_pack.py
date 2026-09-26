#!/usr/bin/env python3
"""ONTO1 WI-A5 续 / P-4｜D2 悬空产品引用的「归一化决策包」生成器。

定位（**重要**）：
    本脚本是 **分析产物生成器 + 自检**，产出供**产品 Owner** 勾选的决策包；
    它 **不做裁定**，也不注册为 Loop 门禁（`LOOP.yaml.gates` / `EVIDENCE.json.gates` 未变）。

为什么需要它：
    D2 请求函 §4 的裁决表是**手写**的（12 行按取值聚合）。产品 Owner 若要逐条裁定，
    还需回答「这 40 处分别在哪张卡的哪个字段」，且候选映射缺**回源位置与证据强度**。
    本脚本把三件事变成可复现的机读产物：
      (1) 40 处引用的**逐卡片逐字段逐行**明细（含行号）；
      (2) 每个取值的**候选归一化映射 + 证据强度 + 回源位置**（回源位置逐条**机器校验**）；
      (3) 每个取值与**非产品词表**（capabilities / product_family / applicable_scenarios /
          required_materials / 账户关系位 / GITS 分类基线 / GITS PI-0 种子）的**碰撞**。

fail-closed 自检（--gate）：
    G1 计数：40 = 12 prerequisite + 28 complementary；唯一取值 12；卡 13 张。
    G2 mutex_product_ids 在 13 张卡**全部为空** ⇒ 零实例事实必须显式落盘。
    G3 12 个取值**每个都有候选行**（缺行 ⇒ FAIL，不得留空让 Owner 面对空白）。
    G4 **每条证据回源位置必须真实存在且行内容匹配**（写错行号 ⇒ FAIL）。
    G5 证据强度 ∈ {强,弱,无}；判「强」必须带回源；每条候选必须给出反证段。
    G6 候选映射若是 `PROD-*`，必须落在产品身份空间内（不得发明产品）。
    G7 三个关系场景**必须**全部为 `NOT_EVALUATED`；出现 `PASS` ⇒ FAIL。
    G8 决策包必须携带「不裁定」声明与 R-6 保留。

用法：
    python3 scripts/onto1_d2_normalization_pack.py --gate
    python3 scripts/onto1_d2_normalization_pack.py --selftest
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
KERT = WORKSPACE / "Leibniz-KERT"
CARD_GLOBS = ["examples/**/product-cards/PROD-*.md", "examples/**/PROD-*.md"]
PRODUCTS_TTL = ROOT / "specs/knowledge-architecture/instances/product/products.ttl"
TAXONOMY = ROOT / "specs/product-knowledge/product-taxonomy.yaml"
GITS_SEED = (ROOT / "adapters/persistence-relational/src/main/resources/db/migration/h2/"
             "V021__corporate_product_knowledge_seed.sql")
OUT_DIR = ROOT / "loops/ONTO1-ontology-split/evidence"

RELATION_FIELDS = {
    "prerequisite_product_ids": "requiresProduct",
    "mutex_product_ids": "mutuallyExclusiveWith",
    "complementary_products": "complementsProduct",
}
ACCOUNT_FIELD = "admission_criteria.requiredAccountRelationship"
NON_PRODUCT_FIELDS = (
    "name", "product_family", "product_family_name", "capabilities", "applicable_scenarios",
    "risk_notes", "required_materials", "prohibited_industries", "prohibited_regions",
    "prohibited_uses", "institutions", "admission_criteria.customerTypes",
    "admission_criteria.minScale", "admission_criteria.minRating",
)
PROSE_PATTERN = re.compile(r"^\s*-\s*(前置|互斥|替代|配套)产品：(.*)$")

CM = "examples/product-recommendation-assets/03_core/cash-management/version=2026.09.01.1/product-cards/"
CB = "examples/product-recommendation-assets/03_core/cross-border/version=2026.09.01.1/product-cards/"
FIN = "examples/product-recommendation-assets/03_core/financing/version=2026.08.31.1/product-cards/"
IB = "examples/product-recommendation-assets/03_core/investment-banking/version=2026.09.01.1/product-cards/"
SET = "examples/product-recommendation-assets/03_core/settlement/version=2026.09.01.1/product-cards/"
TF = "examples/product-recommendation-assets/03_core/trade-finance/version=2026.09.01.1/product-cards/"

SEED = ("adapters/persistence-relational/src/main/resources/db/migration/h2/"
        "V021__corporate_product_knowledge_seed.sql")

# ---------------------------------------------------------------------------
# 候选归一化映射表（**分析员候选**，非裁定；回源位置由 G4 逐条机器校验）
#   strength: 强 = 有决定性回源（名称或语义一一对应）
#             弱 = 名称近似 / 存在第二身份可能，需产品 Owner 定性
#             无 = 无 PROD-* 候选（本卡集未覆盖或性质非产品）
# ---------------------------------------------------------------------------
CANDIDATES = {
    "SETTLEMENT_ACCOUNT": {
        "nature": "跨槽位同名：既被当产品引用，又是账户准入字段取值",
        "suggested": "错误引用（账户关系被写入产品关系位）；账户关系位保留",
        "options": [
            "有效待补 → PROD-SET-001",
            "有效待补 → 需新增卡（对公结算账户）",
            "错误引用（非产品：账户关系）",
            "作废",
        ],
        "analyst_note": (
            "24 处产品位引用 = 12 prerequisite + 12 complementary；另有 **12 处账户关系位**"
            "（admission_criteria.requiredAccountRelationship，见 reference_slot）**不计入 40**。"
            "若判为非产品：24 处需从产品谓词移出，而「前置是账户」这一事实将**无谓词可承载** ⇒ "
            "是否新增关系类型属 TL + 语义架构（合同先行），不在本包范围。"
        ),
        "rows": [
            {
                "to": "（非产品）账户关系取值",
                "kind": "NON_PRODUCT_ACCOUNT_RELATION",
                "strength": "强",
                "evidence": [
                    {"repo": "kert", "ref": CM + "PROD-CM-001.md:26",
                     "expect": "requiredAccountRelationship: SETTLEMENT_ACCOUNT"},
                    {"repo": "kert", "ref": "src/kert/application/product_recommendation/eligibility.py:547",
                     "expect": "requiredAccountRelationship"},
                    {"repo": "kert", "ref": "src/kert/application/product_recommendation/eligibility.py:552",
                     "expect": "required_rel not in rels"},
                    {"repo": "kert", "ref": "scripts/product_recommendation_golden_benchmark.py:8",
                     "expect": "SETTLEMENT_ACCOUNT"},
                    {"repo": "kert", "ref": "tests/integration/test_sp15_contract_conformance.py:155",
                     "expect": "accountRelationships"},
                    {"repo": "gits", "ref": SEED + ":44", "expect": "SETTLEMENT_ACCOUNT"},
                ],
                "why": (
                    "同一 token 被 KERT 执行器当**客户账户关系事实**与产品卡准入要求比对"
                    "（eligibility.py:547-553），测试夹具 accountRelationships=[SETTLEMENT_ACCOUNT] 与之自洽；"
                    "GITS PI-0 种子里它还是「关键特性」取值（V021:44）⇒ 至少三个槽位同名。"
                ),
                "against": (
                    "该证据只证明「账户关系位」的读法；**不能**据此断言产品位的 24 处也必是账户关系"
                    "（同 token 不同位 ≠ 同义），故仍并列 PROD-SET-001 为候选。"
                ),
            },
            {
                "to": "PROD-SET-001",
                "kind": "PRODUCT_ID",
                "strength": "弱",
                "evidence": [
                    {"repo": "kert", "ref": SET + "PROD-SET-001.md:4", "expect": "单位结算账户"},
                    {"repo": "kert", "ref": CM + "PROD-CM-001.md:64", "expect": "对公结算账户"},
                    {"repo": "gits", "ref": "specs/knowledge-architecture/instances/product/products.ttl:58",
                     "expect": "单位结算账户"},
                    {"repo": "gits", "ref": SEED + ":42", "expect": "对公结算账户"},
                    {"repo": "gits", "ref":
                        "docs/architecture/GK17-产品卡引用空间裁定-V1.0.md:64", "expect": "PROD-SET-001"},
                ],
                "why": "KERT 卡名「单位结算账户」（SET-001:4）与 ttl label（products.ttl:58）逐字一致，族为 SETTLEMENT。",
                "against": (
                    "① 卡**正文**写的是「对公结算账户」（CM-001:64 等 12 处），与卡名「单位结算账户」**不完全一致**；"
                    "② GITS PI-0 种子另有名为「对公结算账户」的产品（V021:42）⇒ 存在**第二个身份候选**；"
                    "③ PROD-SET-001 自身 requiredAccountRelationship = null（SET-001:26），未自证该 token 是产品。"
                ),
            },
        ],
    },
    "CORPORATE_E_BANK": {
        "nature": "电子渠道（企业网银）——本卡集未覆盖，GITS 侧另有同名产品登记",
        "suggested": "错误引用（渠道非产品）或 有效待补（须先做跨仓身份对齐）",
        "options": [
            "有效待补 → 需新增卡（企业网银）",
            "有效待补 → GITS 侧既有产品身份（企业网上银行）",
            "错误引用（非产品：渠道）",
            "作废",
        ],
        "analyst_note": (
            "5 处引用与 5 张卡正文「配套产品：企业网银」**一一对应**（CM-001:65、CM-002:65、"
            "FIN-001:77、SET-001:65、SET-002:66），语义无歧义；争议只在**性质与身份**："
            "GITS 分类基线把「电子渠道」列为**品类**且 has_products=false（taxonomy:197-200），"
            "而 GITS PI-0 种子把它登记为**产品**（V021:51）⇒ 跨仓同一符号两种身份，须 Owner 定。"
        ),
        "rows": [
            {
                "to": "（非产品）渠道",
                "kind": "NON_PRODUCT_CHANNEL",
                "strength": "强",
                "evidence": [
                    {"repo": "kert", "ref": CM + "PROD-CM-001.md:65", "expect": "配套产品：企业网银"},
                    {"repo": "kert", "ref": SET + "PROD-SET-002.md:66", "expect": "配套产品：企业网银"},
                    {"repo": "gits", "ref": "specs/product-knowledge/product-taxonomy.yaml:197",
                     "expect": "SET_E_CHANNEL"},
                    {"repo": "gits", "ref": "specs/product-knowledge/product-taxonomy.yaml:198",
                     "expect": "电子渠道"},
                ],
                "why": "5/5 正文对应；GITS 分类基线把电子渠道列为品类（has_products=false）。",
                "against": (
                    "GITS PI-0 种子把「企业网上银行」登记为**产品**行（V021:51）⇒ 判「非产品」在 GITS 侧不成立，"
                    "须跨仓对齐后定。"
                ),
            },
            {
                "to": "PROD-*（无）",
                "kind": "NO_PRODUCT_CANDIDATE",
                "strength": "无",
                "evidence": [
                    {"repo": "gits", "ref": SEED + ":51", "expect": "企业网上银行"},
                ],
                "why": "13 张卡中无任何 PROD-* 的名称或族能对应「企业网银」。",
                "against": (
                    "GITS 侧存在名为「企业网上银行」的产品登记（V021:51），但**不在** PROD-* 身份空间内 ⇒ "
                    "本包**不**给出 PROD-* 映射（不发明产品身份）。"
                ),
            },
        ],
    },
    "CASH_MANAGEMENT": {
        "nature": "产品族编码（与 product_family 同码），非产品",
        "suggested": "错误引用（族名写入产品位）——若保留该语义需另立族级关系",
        "options": [
            "错误引用（族编码非产品）",
            "有效待补 → 具体 PROD-CM-00x（由 Owner 指定成员）",
            "作废",
        ],
        "analyst_note": (
            "唯一同时命中非产品词表的取值（2 处，均为产品位）。族 CASH_MANAGEMENT 有 **3 个成员**"
            "（PROD-CM-001/002/003）⇒ 任何指向单一 PROD-* 的映射都是**推测**，本包不提供。"
            "若「配套的是整个现金管理能力」确为业务事实，则需要的是**族级关系语义**，不是产品关系谓词。"
        ),
        "rows": [
            {
                "to": "（非产品）产品族 CASH_MANAGEMENT",
                "kind": "NON_PRODUCT_FAMILY",
                "strength": "强",
                "evidence": [
                    {"repo": "kert", "ref": CM + "PROD-CM-001.md:5",
                     "expect": "product_family: CASH_MANAGEMENT"},
                    {"repo": "kert", "ref": CM + "PROD-CM-001.md:6", "expect": "现金管理"},
                    {"repo": "kert", "ref": FIN + "PROD-FIN-001.md:77", "expect": "现金管理"},
                    {"repo": "kert", "ref": SET + "PROD-SET-001.md:65", "expect": "现金管理"},
                    {"repo": "gits", "ref": "specs/product-knowledge/product-taxonomy.yaml:68",
                     "expect": "CASH_MANAGEMENT"},
                    {"repo": "gits", "ref":
                        "docs/architecture/GK17-产品卡引用空间裁定-V1.0.md:76", "expect": "product_family"},
                ],
                "why": (
                    "token 与 product_family 编码**逐字相同**；族中文名「现金管理」（CM-001:6）"
                    "正是两处正文所写的配套名（FIN-001:77 / SET-001:65）。"
                ),
                "against": "无（该取值非产品的证据链完整）；但「族级配套」是否要进本体属语义架构问题。",
            },
        ],
    },
    "CASH_POOL": {
        "nature": "产品语义名（现金池）",
        "suggested": "有效待补 → PROD-CM-001",
        "options": ["有效待补 → PROD-CM-001", "有效待补 → 需新增卡", "错误引用", "作废"],
        "analyst_note": (
            "同卡集正文把「现金池」放在**配套产品**位（CM-002:65），与 PROD-CM-001 卡名逐字一致；"
            "GITS 分类基线另有**品类** CM_CASH_POOLING（名称「资金池」，taxonomy:167-168）——"
            "「资金池 / 现金池」一字之差，是本行唯一可能引起争议处，已并列列出。"
        ),
        "rows": [
            {
                "to": "PROD-CM-001",
                "kind": "PRODUCT_ID",
                "strength": "强",
                "evidence": [
                    {"repo": "kert", "ref": CM + "PROD-CM-002.md:65", "expect": "现金池"},
                    {"repo": "kert", "ref": CM + "PROD-CM-001.md:4", "expect": "现金池"},
                    {"repo": "gits", "ref": "specs/knowledge-architecture/instances/product/products.ttl:23",
                     "expect": "现金池"},
                    {"repo": "gits", "ref":
                        "docs/architecture/GK17-产品卡引用空间裁定-V1.0.md:65", "expect": "PROD-CM-001"},
                ],
                "why": "正文配套名（CM-002:65）= 卡名（CM-001:4）= ttl label（products.ttl:23），三处逐字一致。",
                "against": (
                    "GITS 品类 CM_CASH_POOLING 中文名「资金池」（taxonomy:168）与「现金池」仅一字之差；"
                    "若 Owner 认为应指品类，则本行改判为族/品类问题。"
                ),
            },
            {
                "to": "品类 CM_CASH_POOLING（非 PROD-*）",
                "kind": "NON_PRODUCT_CATEGORY",
                "strength": "弱",
                "evidence": [
                    {"repo": "gits", "ref": "specs/product-knowledge/product-taxonomy.yaml:167",
                     "expect": "CM_CASH_POOLING"},
                    {"repo": "gits", "ref": "specs/product-knowledge/product-taxonomy.yaml:168",
                     "expect": "资金池"},
                ],
                "why": "GITS 分类基线中确有该品类，名称近似。",
                "against": "名称是「资金池」而非「现金池」，且卡正文用的是「现金池」⇒ 语义证据指向 PROD-CM-001。",
            },
        ],
    },
    "WORKING_CAPITAL_LOAN": {
        "nature": "产品语义名（流动资金贷款）",
        "suggested": "有效待补 → PROD-FIN-001",
        "options": ["有效待补 → PROD-FIN-001", "有效待补 → 需新增卡", "错误引用", "作废"],
        "analyst_note": "正文（CM-003:65）写「配套产品：流动资金贷款」，与 PROD-FIN-001 卡名逐字一致。",
        "rows": [
            {
                "to": "PROD-FIN-001",
                "kind": "PRODUCT_ID",
                "strength": "强",
                "evidence": [
                    {"repo": "kert", "ref": CM + "PROD-CM-003.md:65", "expect": "流动资金贷款"},
                    {"repo": "kert", "ref": FIN + "PROD-FIN-001.md:4", "expect": "流动资金贷款"},
                    {"repo": "gits", "ref": "specs/knowledge-architecture/instances/product/products.ttl:38",
                     "expect": "流动资金贷款"},
                    {"repo": "gits", "ref":
                        "docs/architecture/GK17-产品卡引用空间裁定-V1.0.md:66", "expect": "PROD-FIN-001"},
                ],
                "why": "正文配套名 = 卡名 = ttl label，三处逐字一致。",
                "against": "无已知反证。",
            },
        ],
    },
    "CROSS_BORDER_RMB_SETTLEMENT": {
        "nature": "产品语义名（跨境人民币结算）",
        "suggested": "有效待补 → PROD-CB-001",
        "options": ["有效待补 → PROD-CB-001", "有效待补 → 需新增卡", "错误引用", "作废"],
        "analyst_note": "CB-002（内保外贷）正文写「配套产品：跨境人民币结算」（CB-002:65），与 PROD-CB-001 卡名逐字一致。",
        "rows": [
            {
                "to": "PROD-CB-001",
                "kind": "PRODUCT_ID",
                "strength": "强",
                "evidence": [
                    {"repo": "kert", "ref": CB + "PROD-CB-002.md:65", "expect": "跨境人民币结算"},
                    {"repo": "kert", "ref": CB + "PROD-CB-001.md:4", "expect": "跨境人民币结算"},
                    {"repo": "gits", "ref": "specs/knowledge-architecture/instances/product/products.ttl:13",
                     "expect": "跨境人民币结算"},
                    {"repo": "gits", "ref":
                        "docs/architecture/GK17-产品卡引用空间裁定-V1.0.md:67", "expect": "PROD-CB-001"},
                ],
                "why": "正文配套名 = 卡名 = ttl label，三处逐字一致。",
                "against": "无已知反证。",
            },
        ],
    },
    "BANK_ACCEPTANCE_DRAFT": {
        "nature": "产品语义名（银行承兑汇票）",
        "suggested": "有效待补 → PROD-TF-001",
        "options": ["有效待补 → PROD-TF-001", "有效待补 → 需新增卡", "错误引用", "作废"],
        "analyst_note": "TF-002（国内信用证）正文写「配套产品：银行承兑汇票」（TF-002:65），与 PROD-TF-001 卡名逐字一致。",
        "rows": [
            {
                "to": "PROD-TF-001",
                "kind": "PRODUCT_ID",
                "strength": "强",
                "evidence": [
                    {"repo": "kert", "ref": TF + "PROD-TF-002.md:65", "expect": "银行承兑汇票"},
                    {"repo": "kert", "ref": TF + "PROD-TF-001.md:4", "expect": "银行承兑汇票"},
                    {"repo": "gits", "ref": "specs/knowledge-architecture/instances/product/products.ttl:68",
                     "expect": "银行承兑汇票"},
                    {"repo": "gits", "ref":
                        "docs/architecture/GK17-产品卡引用空间裁定-V1.0.md:68", "expect": "PROD-TF-001"},
                ],
                "why": "正文配套名 = 卡名 = ttl label，三处逐字一致。",
                "against": "无已知反证。",
            },
        ],
    },
    "FX_FORWARD": {
        "nature": "产品语义名（远期结售汇）——本卡集未覆盖",
        "suggested": "有效待补（需新增卡）或 错误引用（若定性为非产品）",
        "options": ["有效待补 → 需新增卡", "有效待补 → GITS 侧既有产品身份", "错误引用", "作废"],
        "analyst_note": (
            "CB-001 正文写「配套产品：远期结售汇」（CB-001:66）。GITS 分类基线把「外汇服务」列为**品类**"
            "（CB_FX_SERVICE，has_products=false，taxonomy:229-232），GITS PI-0 种子另有"
            "「外汇避险（远期结售汇）」产品行（V021:108）——与本仓 PROD-* 空间均无交集。"
        ),
        "rows": [
            {
                "to": "PROD-*（无）",
                "kind": "NO_PRODUCT_CANDIDATE",
                "strength": "无",
                "evidence": [
                    {"repo": "kert", "ref": CB + "PROD-CB-001.md:66", "expect": "远期结售汇"},
                    {"repo": "gits", "ref": "specs/product-knowledge/product-taxonomy.yaml:229",
                     "expect": "CB_FX_SERVICE"},
                ],
                "why": "13 张卡中无对应产品身份，本包不发明映射。",
                "against": "语义明确指向「远期结售汇」（CB-001:66）⇒ 属「本卡集未覆盖」，不等于「不是产品」。",
            },
        ],
    },
    "DISCOUNT_SERVICE": {
        "nature": "产品/服务语义名（贴现服务）——本卡集未覆盖",
        "suggested": "有效待补（需新增卡或定性为服务）",
        "options": ["有效待补 → 需新增卡", "错误引用（若定性为服务非产品）", "作废"],
        "analyst_note": (
            "TF-001 正文写「配套产品：贴现服务」（TF-001:66）。GITS 分类基线有品类 TF_BILL_DISCOUNT"
            "（票据贴现，has_products=false，taxonomy:215-218）⇒ 与「服务 vs 产品」定性相关。"
        ),
        "rows": [
            {
                "to": "PROD-*（无）",
                "kind": "NO_PRODUCT_CANDIDATE",
                "strength": "无",
                "evidence": [
                    {"repo": "kert", "ref": TF + "PROD-TF-001.md:66", "expect": "贴现服务"},
                    {"repo": "gits", "ref": "specs/product-knowledge/product-taxonomy.yaml:215",
                     "expect": "TF_BILL_DISCOUNT"},
                ],
                "why": "13 张卡中无对应产品身份。",
                "against": "词尾为 SERVICE，是否为「产品」需 Owner 定性；本包不预设。",
            },
        ],
    },
    "FINANCIAL_ADVISORY": {
        "nature": "服务/产品待定性（财务顾问）——本卡集未覆盖",
        "suggested": "有效待补（须先定性产品 / 服务）",
        "options": ["有效待补 → 需新增卡", "错误引用（若定性为服务非产品）", "作废"],
        "analyst_note": (
            "IB-001（并购贷款）正文写「配套产品：财务顾问」（IB-001:66）。GITS 分类基线把「财务顾问」"
            "列为**品类** IB_ADVISORY（has_products=false，taxonomy:265-268）⇒ 性质须先定性。"
        ),
        "rows": [
            {
                "to": "PROD-*（无）",
                "kind": "NO_PRODUCT_CANDIDATE",
                "strength": "无",
                "evidence": [
                    {"repo": "kert", "ref": IB + "PROD-IB-001.md:66", "expect": "财务顾问"},
                    {"repo": "gits", "ref": "specs/product-knowledge/product-taxonomy.yaml:265",
                     "expect": "IB_ADVISORY"},
                ],
                "why": "13 张卡中无对应产品身份。",
                "against": "GITS 侧「财务顾问」是品类而非产品（taxonomy:265-268）⇒ 与「产品/服务」定性直接相关。",
            },
        ],
    },
    "RECEIVABLE_LEDGER_TOOL": {
        "nature": "工具（应收账款台账 / 确权工具）——非产品",
        "suggested": "错误引用（工具被写入产品关系位）",
        "options": ["错误引用（非产品：工具）", "有效待补 → 需新增卡", "作废"],
        "analyst_note": (
            "FIN-002 正文写「配套产品：对公结算账户、应收账款台账/确权工具」（FIN-002:75）；"
            "同卡前置位写的是「与买方的真实贸易合同、本行结算账户」（FIN-002:72）——**该字段本身就承载了"
            "合同 / 账户等非产品项**，是本取值被列为「错误引用」的主要环境证据。"
        ),
        "rows": [
            {
                "to": "（非产品）工具",
                "kind": "NON_PRODUCT_TOOL",
                "strength": "强",
                "evidence": [
                    {"repo": "kert", "ref": FIN + "PROD-FIN-002.md:75", "expect": "应收账款台账/确权工具"},
                    {"repo": "kert", "ref": FIN + "PROD-FIN-002.md:72", "expect": "本行结算账户"},
                    {"repo": "gits", "ref":
                        "docs/architecture/GK17-产品卡引用空间裁定-V1.0.md:82", "expect": "RECEIVABLE_LEDGER_TOOL"},
                ],
                "why": "正文自述为「工具」，且同一字段混入合同 / 账户 ⇒ 性质错配。",
                "against": "无 PROD-* 候选；若 Owner 认为应为其出卡，则本行改判「有效待补」。",
            },
        ],
    },
    "ORDER_RECEIVABLE_CLOSED_ACCOUNT": {
        "nature": "账户（订单回款封闭账户）——非产品",
        "suggested": "错误引用（账户被写入产品关系位）",
        "options": ["错误引用（非产品：账户）", "有效待补 → 需新增卡", "作废"],
        "analyst_note": (
            "FIN-003 正文写「配套产品：对公结算账户、订单回款封闭账户」（FIN-003:75）；"
            "「封闭账户」是**账户用途约束**，不是产品身份。"
        ),
        "rows": [
            {
                "to": "（非产品）账户",
                "kind": "NON_PRODUCT_ACCOUNT",
                "strength": "强",
                "evidence": [
                    {"repo": "kert", "ref": FIN + "PROD-FIN-003.md:75", "expect": "订单回款封闭账户"},
                    {"repo": "gits", "ref": "docs/architecture/GK17-产品卡引用空间裁定-V1.0.md:83",
                     "expect": "ORDER_RECEIVABLE_CLOSED_ACCOUNT"},
                ],
                "why": "正文自述为「账户」；账户在 GITS 侧无独立本体类（GK17 四项悬置 §3.2 指定 Transaction.accountId 承担）。",
                "against": "无 PROD-* 候选；若 Owner 认为应为其出卡，则本行改判「有效待补」。",
            },
        ],
    },
}

# ---------------------------------------------------------------------------
# 邻近 / 跨词表语义命中（**curated + 逐条机器校验**）
#   精确同形命中由脚本自动算（见 d2-cross-vocab.md 上半）；本表收录**非同形但同物/近物**的
#   词表命中（族名、品类名、账户关系位、GITS PI-0 种子），否则「交叉验证」会漏掉最难判的行。
# ---------------------------------------------------------------------------
SEMANTIC_HITS = {
    "SETTLEMENT_ACCOUNT": [
        {"source": "card.admission_criteria.requiredAccountRelationship",
         "ref": CM + "PROD-CM-001.md:26", "expect": "SETTLEMENT_ACCOUNT",
         "note": "同 token 出现在账户关系位（12 张卡），**不计入 40**"},
        {"source": "card.prose.§6", "ref": CM + "PROD-CM-001.md:64", "expect": "对公结算账户",
         "note": "正文主体中文名，与 PROD-SET-001 卡名「单位结算账户」不完全一致"},
        {"source": "gits.seed_key_feature", "ref": SEED + ":44", "expect": "SETTLEMENT_ACCOUNT",
         "note": "GITS PI-0 种子里是「关键特性」取值"},
    ],
    "CORPORATE_E_BANK": [
        {"source": "card.prose.§6", "ref": CM + "PROD-CM-001.md:65", "expect": "企业网银",
         "note": "5 张卡正文一一对应"},
        {"source": "gits.taxonomy_category", "ref": "specs/product-knowledge/product-taxonomy.yaml:197",
         "expect": "SET_E_CHANNEL", "note": "GITS 分类基线「电子渠道」品类，has_products=false"},
        {"source": "gits.seed_product_name", "ref": SEED + ":51", "expect": "企业网上银行",
         "note": "GITS PI-0 种子把同类事物登记为**产品** ⇒ 跨仓身份冲突"},
    ],
    "CASH_MANAGEMENT": [
        {"source": "card.product_family_name", "ref": CM + "PROD-CM-001.md:6", "expect": "现金管理",
         "note": "族中文名 = 两处正文所写配套名"},
        {"source": "gits.taxonomy_name_zh", "ref": "specs/product-knowledge/product-taxonomy.yaml:69",
         "expect": "现金管理", "note": "GITS 分类基线族中文名"},
        {"source": "gits.seed_product_category", "ref": SEED + ":61", "expect": "CASH_MANAGEMENT",
         "note": "GITS PI-0 种子的 category 列即产品族编码"},
    ],
    "CASH_POOL": [
        {"source": "card.prose.§6", "ref": CM + "PROD-CM-002.md:65", "expect": "现金池",
         "note": "正文配套名"},
        {"source": "gits.taxonomy_category", "ref": "specs/product-knowledge/product-taxonomy.yaml:167",
         "expect": "CM_CASH_POOLING", "note": "近名品类「资金池」（一字之差）"},
    ],
    "WORKING_CAPITAL_LOAN": [
        {"source": "card.prose.§6", "ref": CM + "PROD-CM-003.md:65", "expect": "流动资金贷款",
         "note": "正文配套名"},
        {"source": "gits.taxonomy_category", "ref": "specs/product-knowledge/product-taxonomy.yaml:239",
         "expect": "FIN_WORKING_CAPITAL", "note": "近名品类「流动资金」"},
    ],
    "CROSS_BORDER_RMB_SETTLEMENT": [
        {"source": "card.prose.§6", "ref": CB + "PROD-CB-002.md:65", "expect": "跨境人民币结算",
         "note": "正文配套名"},
        {"source": "gits.taxonomy_category", "ref": "specs/product-knowledge/product-taxonomy.yaml:221",
         "expect": "CB_CROSS_BORDER_SETTLEMENT", "note": "近名品类「跨境结算」"},
    ],
    "BANK_ACCEPTANCE_DRAFT": [
        {"source": "card.prose.§6", "ref": TF + "PROD-TF-002.md:65", "expect": "银行承兑汇票",
         "note": "正文配套名"},
        {"source": "gits.taxonomy_category", "ref": "specs/product-knowledge/product-taxonomy.yaml:203",
         "expect": "TF_ACCEPTANCE_INSTRUMENT", "note": "近名品类「承兑工具」"},
    ],
    "FX_FORWARD": [
        {"source": "card.prose.§6", "ref": CB + "PROD-CB-001.md:66", "expect": "远期结售汇",
         "note": "正文配套名"},
        {"source": "gits.taxonomy_category", "ref": "specs/product-knowledge/product-taxonomy.yaml:229",
         "expect": "CB_FX_SERVICE", "note": "GITS 品类「外汇服务」，has_products=false"},
        {"source": "gits.seed_product_name", "ref": SEED + ":108", "expect": "远期结售汇",
         "note": "GITS PI-0 种子有产品行，但不在 PROD-* 空间"},
    ],
    "DISCOUNT_SERVICE": [
        {"source": "card.prose.§6", "ref": TF + "PROD-TF-001.md:66", "expect": "贴现服务",
         "note": "正文配套名"},
        {"source": "gits.taxonomy_category", "ref": "specs/product-knowledge/product-taxonomy.yaml:215",
         "expect": "TF_BILL_DISCOUNT", "note": "GITS 品类「票据贴现」，has_products=false"},
    ],
    "FINANCIAL_ADVISORY": [
        {"source": "card.prose.§6", "ref": IB + "PROD-IB-001.md:66", "expect": "财务顾问",
         "note": "正文配套名"},
        {"source": "gits.taxonomy_category", "ref": "specs/product-knowledge/product-taxonomy.yaml:265",
         "expect": "IB_ADVISORY", "note": "GITS 品类「财务顾问」，has_products=false"},
    ],
    "RECEIVABLE_LEDGER_TOOL": [
        {"source": "card.prose.§6", "ref": FIN + "PROD-FIN-002.md:75", "expect": "应收账款台账/确权工具",
         "note": "正文自述为「工具」"},
        {"source": "gits.seed_required_material", "ref": SEED + ":27", "expect": "RECEIVABLE_LEDGER",
         "note": "**近形不同 token**（RECEIVABLE_LEDGER 是材料项）⇒ 不构成归一化依据"},
    ],
    "ORDER_RECEIVABLE_CLOSED_ACCOUNT": [
        {"source": "card.prose.§6", "ref": FIN + "PROD-FIN-003.md:75", "expect": "订单回款封闭账户",
         "note": "正文自述为「账户」"},
    ],
}

SCENARIOS = {
    "requiresProduct": "NOT_EVALUATED",
    "complementsProduct": "NOT_EVALUATED",
    "mutuallyExclusiveWith": "NOT_EVALUATED",
}


# ---------------------------------------------------------------------------
# 解析
# ---------------------------------------------------------------------------
def _rel(path, base):
    try:
        return Path(path).relative_to(base).as_posix()
    except ValueError:
        return str(path)


def sha256_of(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def find_cards(root):
    cards = set()
    for pattern in CARD_GLOBS:
        cards.update(path for path in Path(root).glob(pattern) if path.is_file())
    return sorted(cards)


def parse_front_matter(path):
    """返回 {字段: {'value': str, 'line': int}}；嵌套字段用 `父.子`。"""
    lines = Path(path).read_text(encoding="utf-8", errors="ignore").splitlines()
    if len(lines) < 3 or lines[0].strip() != "---":
        return {}
    fields = {}
    parent = ""
    for idx, line in enumerate(lines[1:], start=2):
        if line.strip() == "---":
            break
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        match = re.match(r"^(\s*)([A-Za-z_][A-Za-z0-9_]*)\s*:\s*(.*?)\s*$", line)
        if not match:
            continue
        indent, key, value = match.group(1), match.group(2), match.group(3)
        full = key if not indent else f"{parent}.{key}"
        if not indent:
            parent = key
        fields[full] = {"value": value, "line": idx}
    return fields


def parse_list(raw):
    raw = (raw or "").strip()
    if raw in ("", "null", "~", "[]"):
        return []
    raw = raw.strip("[]")
    return [item.strip().strip("'\"") for item in raw.split(",") if item.strip().strip("'\"")]


def product_id_space(cards, ttl):
    space = {}
    for card in cards:
        pid = parse_front_matter(card).get("product_id", {}).get("value", "").strip()
        if pid:
            space.setdefault(pid, []).append(_rel(card, KERT))
    ttl = Path(ttl)
    if ttl.is_file():
        for match in re.finditer(r"^gits:(prod_[a-z0-9_]+)", ttl.read_text(encoding="utf-8"), re.M):
            space.setdefault(match.group(1).upper().replace("_", "-"), []).append(
                f"{_rel(ttl, ROOT)}:label")
    return space


def collect_card_vocab(cards):
    vocab = {}
    for card in cards:
        fields = parse_front_matter(card)
        ref_base = _rel(card, KERT)
        for name in NON_PRODUCT_FIELDS:
            entry = fields.get(name)
            if not entry:
                continue
            for value in parse_list(entry["value"]):
                vocab.setdefault(name, {}).setdefault(value, []).append(
                    f"{ref_base}:{entry['line']}")
    return vocab


def collect_prose(cards):
    """卡片正文 §6 的（前置 / 互斥 / 替代 / 配套）产品叙述，带行号。"""
    out = {}
    for card in cards:
        text = Path(card).read_text(encoding="utf-8", errors="ignore")
        for idx, line in enumerate(text.splitlines(), start=1):
            match = PROSE_PATTERN.match(line)
            if match:
                out.setdefault(_rel(card, KERT), []).append(
                    {"line": idx, "slot": match.group(1), "text": match.group(2).strip()})
    return out


def collect_taxonomy(path):
    vocab = {"taxonomy_id": {}, "taxonomy_name_zh": {}}
    path = Path(path)
    if not path.is_file():
        return vocab
    for idx, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        ref = f"{_rel(path, ROOT)}:{idx}"
        match = re.match(r"^\s*-?\s*id:\s*([A-Za-z_][A-Za-z0-9_]*)\s*$", line)
        if match:
            vocab["taxonomy_id"].setdefault(match.group(1), []).append(ref)
        match = re.match(r"^\s*name_zh:\s*(.+?)\s*$", line)
        if match:
            vocab["taxonomy_name_zh"].setdefault(match.group(1), []).append(ref)
    return vocab


def collect_gits_seed(path):
    vocab = {"seed_product_name": {}, "seed_product_category": {}, "seed_key_feature": {}}
    path = Path(path)
    if not path.is_file():
        return vocab
    text = path.read_text(encoding="utf-8")
    def line_of(pos):
        return text.count("\n", 0, pos) + 1
    row = re.compile(r"^\('[0-9a-f-]+',\s*'[0-9a-f-]+',\s*\d+,\s*\n\s*'([^']*)',\s*'([^']*)',", re.M)
    for match in row.finditer(text):
        ref = f"{_rel(path, ROOT)}:{line_of(match.start()) + 1}"
        vocab["seed_product_name"].setdefault(match.group(1), []).append(ref)
        vocab["seed_product_category"].setdefault(match.group(2), []).append(ref)
    for match in re.finditer(r"'(\[[A-Z_0-9,\s\"]*\])'", text):
        ref = f"{_rel(path, ROOT)}:{line_of(match.start())}"
        for token in re.findall(r"[A-Z][A-Z0-9_]+", match.group(1)):
            vocab["seed_key_feature"].setdefault(token, []).append(ref)
    return vocab


# ---------------------------------------------------------------------------
# 回源校验
# ---------------------------------------------------------------------------
ANCHOR_DRIFT: list[str] = []   # 锚点位移记账（gate 内打印并计入说明；不允许静默）


def verify_ref(entry):
    # repo 缺省时按路径推断：KERT 侧引用一律以 examples/ 开头，GITS 侧以 specs|adapters|docs/ 开头。
    # （推断规则本身也被 M0 对照 + 真实卡集回归覆盖；写错路径 ⇒ missing file ⇒ FAIL。）
    repo = entry.get("repo")
    if repo is None:
        repo = "kert" if entry["ref"].startswith("examples/") else "gits"
    base = KERT if repo == "kert" else ROOT
    rel, _, line_no = entry["ref"].rpartition(":")
    path = base / rel
    if not path.is_file():
        return f"missing file: {entry['ref']}"
    lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    try:
        idx = int(line_no)
    except ValueError:
        return f"bad line number: {entry['ref']}"
    if idx < 1 or idx > len(lines):
        return f"line out of range: {entry['ref']}"
    # QA-W3R4 A-1 处置：**明示语义**（原先我的表述"0 命中/歧义一律 FAIL"与实现不符）。
    # 正确语义（锚点是**显式行钉定**，故 expect 允许在文件内非唯一）：
    #   · 精确行命中 ⇒ 通过（不追究他处是否还有同样字符串）；
    #   · 精确行未命中 ⇒ 进入位移容忍：**全局恰好唯一命中**才记为位移并记账；
    #     0 命中（内容丢失）或 ≥2 命中（无法确定落点）⇒ FAIL。
    # 反例覆盖：删内容 ⇒ content lost；追加副本使唯一性丧失 ⇒ ambiguous（QA-W3R4 A-1 实测已证）。
    if entry["expect"] in lines[idx - 1]:
        return None
    hits = [i + 1 for i, ln in enumerate(lines) if entry["expect"] in ln]
    if not hits:
        return f"line content lost: {entry['ref']} expected {entry['expect']!r}"
    if len(hits) > 1:
        return (f"ambiguous drift ({len(hits)} matches at {hits[:6]}) : {entry['ref']} "
                f"expected {entry['expect']!r}")
    ANCHOR_DRIFT.append(f"{entry['ref']} → :{hits[0]}（expect={entry['expect'][:24]!r}）")
    return None


def verify_all_refs(candidates, semantic_hits=None):
    problems = []
    for value, row in candidates.items():
        for cand in row["rows"]:
            for entry in cand["evidence"]:
                problem = verify_ref(entry)
                if problem:
                    problems.append(f"{value} / {cand['to']}: {problem}")
    for value, hits in (semantic_hits or {}).items():
        for entry in hits:
            problem = verify_ref(entry)
            if problem:
                problems.append(f"{value} / semantic:{entry.get('source')}: {problem}")
    return problems


# ---------------------------------------------------------------------------
# 组装
# ---------------------------------------------------------------------------
def _git_head(repo):
    try:
        return subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"],
                              capture_output=True, text=True, check=True).stdout.strip()
    except Exception:  # noqa: BLE001
        return None


def build_pack(card_root=KERT, ttl=PRODUCTS_TTL, taxonomy=TAXONOMY, seed=GITS_SEED):
    cards = find_cards(card_root)
    if not cards:
        raise RuntimeError(f"no product cards under {card_root}")
    space = product_id_space(cards, ttl)
    parsed = {card: parse_front_matter(card) for card in cards}
    card_vocab = collect_card_vocab(cards)
    external = {"taxonomy": collect_taxonomy(taxonomy), "gits_seed": collect_gits_seed(seed)}

    occurrences = []
    for card in cards:
        fields = parsed[card]
        for field, relation in RELATION_FIELDS.items():
            entry = fields.get(field)
            if not entry:
                continue
            for value in parse_list(entry["value"]):
                occurrences.append({
                    "card": card.name,
                    "card_path": _rel(card, KERT),
                    "line": entry["line"],
                    "field": field,
                    "relation": relation,
                    "value": value,
                })

    reference_slot = []
    for card in cards:
        entry = parsed[card].get(ACCOUNT_FIELD)
        if not entry:
            continue
        for value in parse_list(entry["value"]):
            reference_slot.append({"card": card.name, "line": entry["line"], "value": value})

    mutex_rows = []
    for card in cards:
        entry = parsed[card].get("mutex_product_ids")
        if entry is None:
            continue
        mutex_rows.append({"card": card.name, "line": entry["line"],
                           "raw": entry["value"].strip(), "parsed": parse_list(entry["value"])})

    prose = collect_prose(cards)

    values = {}
    for row in occurrences:
        values.setdefault(row["value"], []).append(row)

    value_rows = []
    for value in sorted(values, key=lambda item: (-len(values[item]), item)):
        rows = values[value]
        cross_hits = []
        for vocab_name, mapping in card_vocab.items():
            if value in mapping:
                cross_hits.append({"source": vocab_name, "refs": mapping[value]})
        for group in external.values():
            for vocab_name, mapping in group.items():
                if value in mapping:
                    cross_hits.append({"source": f"gits.{vocab_name}", "refs": mapping[value]})
        value_rows.append({
            "value": value,
            "occurrences": len(rows),
            "cards_hit": len({row["card"] for row in rows}),
            "fields": sorted({row["field"] for row in rows}),
            "per_card_detail": [{"card": row["card"], "card_path": row["card_path"],
                                 "line": row["line"], "field": row["field"],
                                 "relation": row["relation"]} for row in rows],
            "cross_vocab_hits": cross_hits,
            "cross_vocab_semantic": SEMANTIC_HITS.get(value, []),
            "candidates": CANDIDATES[value]["rows"],
            "nature": CANDIDATES[value]["nature"],
            "suggested_classification": CANDIDATES[value]["suggested"],
            "options": CANDIDATES[value]["options"],
            "analyst_note": CANDIDATES[value]["analyst_note"],
        })

    prose_mutex = [{"card": card, "line": item["line"], "text": item["text"]}
                   for card, items in prose.items() for item in items if item["slot"] == "互斥"]

    return {
        "schema": "onto1_d2_normalization_pack/v1",
        "role": "product-ref-normalization-analyst",
        "artifact_kind": "DECISION_INPUT_ONLY",
        "no_ruling_declaration": (
            "本包不含裁定：所有 candidates 与 suggested_classification 均为**分析员候选**，"
            "裁定权在产品 Owner。本包不改产品卡、不改 products.ttl、不改 specs/、"
            "不标三场景 PASS、不关闭 R-6 风险登记、不把 SIM 数据当企业权威。"
        ),
        "inputs": {
            "gits_commit": _git_head(ROOT),
            "kert_commit": _git_head(KERT),
            "cards": [{"file": _rel(card, KERT), "sha256": sha256_of(card),
                       "product_id": parsed[card].get("product_id", {}).get("value", ""),
                       "name": parsed[card].get("name", {}).get("value", "")} for card in cards],
            "products_ttl": {"file": _rel(ttl, ROOT),
                             "sha256": sha256_of(ttl) if Path(ttl).is_file() else None},
            "taxonomy": {"file": _rel(taxonomy, ROOT),
                         "sha256": sha256_of(taxonomy) if Path(taxonomy).is_file() else None},
            "gits_seed": {"file": _rel(seed, ROOT),
                          "sha256": sha256_of(seed) if Path(seed).is_file() else None},
            "read_only_guarantee": "KERT 侧仅读取；本脚本除 evidence/ 输出外无任何写操作",
        },
        "counts": {
            "cards": len(cards),
            "distinct_product_ids": len(space),
            "occurrences": len(occurrences),
            "by_field": {field: sum(1 for row in occurrences if row["field"] == field)
                         for field in RELATION_FIELDS},
            "distinct_values": len(values),
            "account_relationship_occurrences": len(reference_slot),
            "mutex_cards_empty": sum(1 for row in mutex_rows if not row["parsed"]),
        },
        "identity_space": sorted(space),
        "occurrences": occurrences,
        "values": value_rows,
        "reference_slot": {
            "field": ACCOUNT_FIELD,
            "note": "该字段**不是**产品关系字段；其 12 处不计入 40。列出用于证明 SETTLEMENT_ACCOUNT 跨槽位同名。",
            "occurrences": len(reference_slot),
            "distinct": sorted({row["value"] for row in reference_slot}),
            "per_card": reference_slot,
        },
        "zero_instance": {
            "field": "mutex_product_ids",
            "relation": "mutuallyExclusiveWith",
            "cards": len(mutex_rows),
            "cards_with_empty_list": sum(1 for row in mutex_rows if not row["parsed"]),
            "rows": mutex_rows,
            "prose_mentions": prose_mutex,
            "prose_note": (
                "正文里存在**叙述性**互斥描述（见 prose_mentions），但 front matter 的 "
                "mutex_product_ids 13/13 全空 ⇒ 零实例。不得用正文叙述充当实例，"
                "也不得用「0 目标 0 违规」包装为通过（设计 §6.2）。"
            ),
        },
        "scenario_status": dict(SCENARIOS),
        "shacl_scenario_matrix": [
            {"scenario": "requiresProduct", "expected_targets": "待 D2 裁定",
             "actual_targets": 0, "status": "NOT_EVALUATED",
             "blocker": "D2 未签（40 处悬空引用未分类）"},
            {"scenario": "complementsProduct", "expected_targets": "待 D2 裁定",
             "actual_targets": 0, "status": "NOT_EVALUATED",
             "blocker": "D2 未签（40 处悬空引用未分类）"},
            {"scenario": "mutuallyExclusiveWith", "expected_targets": 0,
             "actual_targets": 0, "status": "NOT_EVALUATED",
             "blocker": "零实例（13/13 空）；且 D2 未签",
             "must_not": "不得解释为业务覆盖已验证"},
        ],
        "prohibited_actions": [
            "以本包充当产品 Owner 裁定",
            "把 WAIVED_FOR_DEVELOPMENT 当激活依据",
            "修改产品卡 / products.ttl（KERT 只读）",
            "把 SIM / 种子数据静默升级为企业权威",
            "把三场景标 PASS",
            "关闭 R-6 风险登记",
        ],
        "open_questions_for_owner": [
            "SETTLEMENT_ACCOUNT：是「账户关系」（则 24 处产品位引用为错误引用），还是「结算账户产品」"
            "（则指 PROD-SET-001，还是 GITS 种子里的「对公结算账户」）？",
            "若判为账户关系：产品卡「前置是账户」这一事实当前无谓词可承载，是否需要新增关系类型"
            "（属 TL + 语义架构，合同先行）？",
            "CASH_MANAGEMENT：确认其为产品族编码 ⇒ 产品位引用作废 / 改判？如需保留「族级配套」语义，是否另立关系类型？",
            "CORPORATE_E_BANK：GITS 分类基线的「电子渠道」品类（has_products=false）与 GITS PI-0 种子的"
            "「企业网上银行」产品行冲突，以哪个为准（跨仓身份对齐）？",
            "5 个「名称逐字对应」取值（CASH_POOL / WORKING_CAPITAL_LOAN / CROSS_BORDER_RMB_SETTLEMENT / "
            "BANK_ACCEPTANCE_DRAFT；以及 SETTLEMENT_ACCOUNT 若判为产品）是否一次性确认？",
            "4 个「本卡集未覆盖」取值（CORPORATE_E_BANK / FX_FORWARD / DISCOUNT_SERVICE / FINANCIAL_ADVISORY）"
            "是否补卡，或判为非产品 / 服务后改用其他关系建模？",
        ],
    }


# ---------------------------------------------------------------------------
# 输出
# ---------------------------------------------------------------------------
def _checklist_table(pack):
    lines = [
        "| # | 取值 | 次数 | 命中卡片数 | 候选归一化映射 | 证据强度 | 建议分类（**非裁定**） | 产品 Owner 勾选 |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for idx, row in enumerate(pack["values"], start=1):
        mapping = "；".join(f"`{cand['to']}`" for cand in row["candidates"])
        options = " / ".join(f"☐ {opt}" for opt in row["options"])
        lines.append(
            f"| {idx} | `{row['value']}` | {row['occurrences']} | {row['cards_hit']} | {mapping} | "
            f"{'／'.join(cand['strength'] for cand in row['candidates'])} | "
            f"{row['suggested_classification']} | {options} |")
    lines.append(f"| | **合计** | **{pack['counts']['occurrences']}** | 13 张卡 | | | | |")
    return "\n".join(lines)


def _per_card_table(pack):
    lines = ["| 取值 | 卡片 | 字段 | 行号 | 关系 |", "|---|---|---|---|---|"]
    for row in pack["values"]:
        for detail in row["per_card_detail"]:
            lines.append(f"| `{row['value']}` | `{detail['card']}` | `{detail['field']}` | "
                         f"{detail['line']} | `{detail['relation']}` |")
    return "\n".join(lines)


def _cross_vocab_table(pack):
    lines = ["## A. 精确同形命中（脚本自动扫描非产品词表）", "",
             "| 取值 | 命中的非产品词表 | 回源位置 |", "|---|---|---|"]
    for row in pack["values"]:
        if not row["cross_vocab_hits"]:
            lines.append(f"| `{row['value']}` | （无） | — |")
            continue
        for hit in row["cross_vocab_hits"]:
            refs = "、".join(f"`{ref}`" for ref in hit["refs"][:6])
            more = "" if len(hit["refs"]) <= 6 else f"（另 {len(hit['refs']) - 6} 处）"
            lines.append(f"| `{row['value']}` | `{hit['source']}` | {refs}{more} |")
    lines += ["", "## B. 邻近 / 跨词表语义命中（人工收录 + 机器校验行内容）", "",
              "> 「同物不同形」的情况 A 段扫不到（族名 / 品类名 / 账户关系位 / GITS 种子 / 正文中文名），"
              "故单列，避免交叉验证留下最难判的那几行。", "",
              "| 取值 | 词表来源 | 回源位置 | 说明 |", "|---|---|---|---|"]
    for row in pack["values"]:
        for hit in row["cross_vocab_semantic"]:
            repo = hit.get("repo")
            if repo is None:
                repo = "kert" if hit["ref"].startswith("examples/") else "gits"
            base = "KERT" if repo == "kert" else "GITS"
            lines.append(f"| `{row['value']}` | `{hit['source']}` | {base} `{hit['ref']}` | {hit['note']} |")
        if not row["cross_vocab_semantic"]:
            lines.append(f"| `{row['value']}` | （无） | — | — |")
    return "\n".join(lines)


def write_pack(pack, out_dir=None):
    out = Path(out_dir) if out_dir is not None else OUT_DIR
    out.mkdir(parents=True, exist_ok=True)
    pack_path = out / "d2-normalization-pack.json"
    pack_path.write_text(json.dumps(pack, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out / "d2-checklist-table.md").write_text(_checklist_table(pack) + "\n", encoding="utf-8")
    (out / "d2-per-card-detail.md").write_text(_per_card_table(pack) + "\n", encoding="utf-8")
    (out / "d2-cross-vocab.md").write_text(_cross_vocab_table(pack) + "\n", encoding="utf-8")
    return {"pack": _rel(pack_path, ROOT), "sha256": sha256_of(pack_path), "out_dir": str(out)}


# ---------------------------------------------------------------------------
# 门禁
# ---------------------------------------------------------------------------
def gate(pack=None, out_dir=None):
    failures = []
    pack = pack or build_pack()
    written = write_pack(pack, out_dir)

    counts = pack["counts"]
    ok1 = (counts["occurrences"] == 40 and counts["by_field"]["prerequisite_product_ids"] == 12
           and counts["by_field"]["complementary_products"] == 28 and counts["distinct_values"] == 12
           and counts["cards"] == 13)
    print(f"[G1] occurrences={counts['occurrences']} by_field={counts['by_field']} "
          f"distinct={counts['distinct_values']} cards={counts['cards']} ⇒ {'PASS' if ok1 else 'FAIL'}")
    if not ok1:
        failures.append("G1 counting mismatch (must be 40 = 12 + 28, 12 values, 13 cards)")

    z = pack["zero_instance"]
    ok2 = z["cards_with_empty_list"] == z["cards"] == counts["cards"] and z["cards"] == 13
    print(f"[G2] mutex_product_ids empty {z['cards_with_empty_list']}/{z['cards']}，"
          f"正文互斥叙述 {len(z['prose_mentions'])} 处 ⇒ {'PASS' if ok2 else 'FAIL'}"
          f"（零实例 ⇒ NOT_EVALUATED，不得包装为通过）")
    if not ok2:
        failures.append("G2 mutex zero-instance fact not established")

    missing_rows = [row["value"] for row in pack["values"] if not row["candidates"]]
    print(f"[G3] 候选行齐备：{len(pack['values'])} 行，缺行 {missing_rows} ⇒ "
          f"{'PASS' if not missing_rows else 'FAIL'}")
    if missing_rows:
        failures.append(f"G3 values without candidate rows: {missing_rows}")

    total_refs = (sum(len(c["evidence"]) for r in CANDIDATES.values() for c in r["rows"])
                  + sum(len(h) for h in SEMANTIC_HITS.values()))
    ANCHOR_DRIFT.clear()
    ref_problems = verify_all_refs(CANDIDATES, SEMANTIC_HITS)
    print(f"[G4] 回源位置校验：{total_refs} 条（含语义命中），问题 {len(ref_problems)}，"
          f"**锚点位移 {len(ANCHOR_DRIFT)} 处**（语义：精确行命中即通过；仅位移时要求全局唯一命中；0 命中/歧义 ⇒ FAIL）⇒ "
          f"{'PASS' if not ref_problems else 'FAIL'}")
    for _d in ANCHOR_DRIFT:
        print(f"     ~ 位移已记账：{_d}")
    for problem in ref_problems:
        print(f"     - {problem}", file=sys.stderr)
    if ref_problems:
        failures.append(f"G4 evidence refs failed: {ref_problems[:3]}")

    strength_problems = []
    for value, row in CANDIDATES.items():
        for cand in row["rows"]:
            if cand["strength"] not in ("强", "弱", "无"):
                strength_problems.append(f"{value}/{cand['to']} bad strength {cand['strength']}")
            if cand["strength"] == "强" and not cand["evidence"]:
                strength_problems.append(f"{value}/{cand['to']} 强 without evidence")
            if not cand.get("against"):
                strength_problems.append(f"{value}/{cand['to']} missing counter-evidence note")
    print(f"[G5] 证据强度 / 反证齐备：问题 {len(strength_problems)} ⇒ "
          f"{'PASS' if not strength_problems else 'FAIL'}")
    if strength_problems:
        failures.append(f"G5 strength/counter-evidence problems: {strength_problems[:3]}")

    space = set(pack["identity_space"])
    invented = [cand["to"] for row in CANDIDATES.values() for cand in row["rows"]
                if cand["kind"] == "PRODUCT_ID" and cand["to"] not in space]
    print(f"[G6] PROD-* 候选落在身份空间（{len(space)} 个）：越界 {invented} ⇒ "
          f"{'PASS' if not invented else 'FAIL'}")
    if invented:
        failures.append(f"G6 invented product ids: {invented}")

    statuses = pack["scenario_status"]
    ok7 = all(state == "NOT_EVALUATED" for state in statuses.values()) and \
        all(entry["status"] == "NOT_EVALUATED" for entry in pack["shacl_scenario_matrix"])
    print(f"[G7] 三场景状态 {statuses} ⇒ {'PASS' if ok7 else 'FAIL'}")
    if not ok7:
        failures.append("G7 scenario status must all be NOT_EVALUATED")

    decl = pack.get("no_ruling_declaration") or ""
    acts = pack.get("prohibited_actions") or []
    ok8 = (isinstance(decl, str) and len(decl) >= 40 and "不含裁定" in decl
           and isinstance(acts, list) and len(acts) >= 5
           and any("R-6" in str(x) for x in acts))
    print(f"[G8] 非裁定声明（{len(decl)} 字）与 R-6 保留（prohibited_actions {len(acts)} 条，"
          f"含 R-6={any('R-6' in str(x) for x in acts)}）⇒ {'PASS' if ok8 else 'FAIL'}"
          f"（QA-W3R3 修复：原判据第 2 合取项为整包 JSON 子串 ⇒ 自指恒真）")
    if not ok8:
        failures.append("G8 missing no-ruling declaration / R-6 retention")

    print(f"[out] {written['pack']} sha256={written['sha256'][:16]}")
    print("      evidence/d2-checklist-table.md · d2-per-card-detail.md · d2-cross-vocab.md")

    if failures:
        for item in failures:
            print(f"onto1-d2-pack: FAIL: {item}", file=sys.stderr)
        return 2
    print("onto1-d2-pack: PASS")
    return 0


def selftest():
    """变异：证明 G3/G4/G5/G6/G7 不是空转。"""
    failures = []
    tmp = Path(tempfile.mkdtemp(prefix="onto1-d2-pack-selftest-"))
    try:
        code = gate(build_pack(), out_dir=tmp / "out-real")
        print(f"{'PASS' if code == 0 else 'FAIL'}  M0 真实产品卡 ⇒ 自检 PASS  exit={code}")
        if code != 0:
            failures.append("M0")

        saved = CANDIDATES["CASH_POOL"]["rows"][0]["evidence"][0]["expect"]
        CANDIDATES["CASH_POOL"]["rows"][0]["evidence"][0]["expect"] = "不存在的字样"
        saved_sem = SEMANTIC_HITS["CASH_POOL"][0]["ref"]
        SEMANTIC_HITS["CASH_POOL"][0]["ref"] = CM + "PROD-CM-002.md:9999"
        problems = verify_all_refs(CANDIDATES, SEMANTIC_HITS)
        print(f"{'PASS' if len(problems) == 2 else 'FAIL'}  M1 候选回源篡改 + 语义命中行号越界 ⇒ "
              f"被拦下（{len(problems)} 条：{problems}）")
        if len(problems) != 2:
            failures.append("M1")
        CANDIDATES["CASH_POOL"]["rows"][0]["evidence"][0]["expect"] = saved
        SEMANTIC_HITS["CASH_POOL"][0]["ref"] = saved_sem

        # M6（QA-W3R4 B-i4）：G5 的三条强度/反证判据在本轮前**从未被任何变异触发** ⇒ 补反例。
        # 去掉一条候选的 `against`（反证说明）⇒ G5 必须失败、整门 exit 2。
        saved_against = CANDIDATES["CASH_POOL"]["rows"][0].pop("against", None)
        code6 = gate(build_pack(), out_dir=tmp / "out-m6")
        print(f"{'PASS' if code6 == 2 else 'FAIL'}  M6 去掉候选 `against`（反证缺失）⇒ G5 拦下、整门 FAIL  exit={code6}")
        if code6 != 2:
            failures.append("M6")
        CANDIDATES["CASH_POOL"]["rows"][0]["against"] = saved_against

        # M7（QA-W3R4 B-i4 第二条）：`strength=强` 但证据为空 ⇒ G5 必须失败
        row0 = CANDIDATES["CASH_POOL"]["rows"][0]
        saved_strength, saved_ev = row0["strength"], row0["evidence"]
        row0["strength"] = "强"
        row0["evidence"] = []
        code7 = gate(build_pack(), out_dir=tmp / "out-m7")
        print(f"{'PASS' if code7 == 2 else 'FAIL'}  M7 `强`无证据 ⇒ G5 拦下、整门 FAIL  exit={code7}")
        if code7 != 2:
            failures.append("M7")
        row0["strength"], row0["evidence"] = saved_strength, saved_ev

        saved_rows = CANDIDATES["FX_FORWARD"]["rows"]
        CANDIDATES["FX_FORWARD"]["rows"] = []
        pack = build_pack()
        missing = [row["value"] for row in pack["values"] if not row["candidates"]]
        print(f"{'PASS' if missing == ['FX_FORWARD'] else 'FAIL'}  M2 删除候选行 ⇒ 被拦下 {missing}")
        if missing != ["FX_FORWARD"]:
            failures.append("M2")
        CANDIDATES["FX_FORWARD"]["rows"] = saved_rows

        CANDIDATES["CASH_POOL"]["rows"][0]["to"] = "PROD-NOPE-999"
        pack2 = build_pack()
        space = set(pack2["identity_space"])
        invented = [cand["to"] for r in CANDIDATES.values() for cand in r["rows"]
                    if cand["kind"] == "PRODUCT_ID" and cand["to"] not in space]
        print(f"{'PASS' if invented == ['PROD-NOPE-999'] else 'FAIL'}  M3 发明产品身份 ⇒ 被 G6 拦下 {invented}")
        if invented != ["PROD-NOPE-999"]:
            failures.append("M3")
        CANDIDATES["CASH_POOL"]["rows"][0]["to"] = "PROD-CM-001"

        card_root = tmp / "kert"
        cards = card_root / "examples" / "x" / "product-cards"
        cards.mkdir(parents=True, exist_ok=True)
        (cards / "PROD-XX-001.md").write_text(
            "---\nproduct_id: PROD-XX-001\nname: 测试产品\n"
            "prerequisite_product_ids: [SETTLEMENT_ACCOUNT]\nmutex_product_ids: []\n"
            "complementary_products: [CORPORATE_E_BANK]\n---\n", encoding="utf-8")
        ttl = tmp / "products.ttl"
        ttl.write_text('gits:prod_xx_001 a gits:Product ;\nrdfs:label "测试产品" .\n', encoding="utf-8")
        small = build_pack(card_root=card_root, ttl=ttl, taxonomy=tmp / "none.yaml",
                           seed=tmp / "none.sql")
        code4 = gate(small, out_dir=tmp / "out-small")
        print(f"{'PASS' if code4 == 2 else 'FAIL'}  M4 卡集不全（1 张卡 / 3 处引用）⇒ 门禁 FAIL  exit={code4}")
        if code4 != 2:
            failures.append("M4")

        saved_status = dict(SCENARIOS)
        SCENARIOS["requiresProduct"] = "PASS"
        code5 = gate(build_pack(), out_dir=tmp / "out-pass")
        print(f"{'PASS' if code5 == 2 else 'FAIL'}  M5 三场景标 PASS ⇒ 门禁 FAIL  exit={code5}")
        if code5 != 2:
            failures.append("M5")
        SCENARIOS.clear()
        SCENARIOS.update(saved_status)

        if failures:
            print(f"onto1-d2-pack-selftest: FAIL {failures}", file=sys.stderr)
            return 2
        print("onto1-d2-pack-selftest: PASS")
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--gate", action="store_true")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()
    if args.selftest:
        return selftest()
    if args.gate:
        return gate()
    print(json.dumps(build_pack()["counts"], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
