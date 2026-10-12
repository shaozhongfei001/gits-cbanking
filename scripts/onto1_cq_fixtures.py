#!/usr/bin/env python3
"""ONTO1 WI-A6｜六类 CQ 夹具设计（机读）与门禁校验。

依据：复审包 `08-CQ语义验收矩阵.md`（每 CQ 绑定：查询 / 正例 / 负例 / 预期 / 责任 Owner / 变异）、
      `06-验证状态模型与状态跃迁表.md`（五态：PASS/FAIL/NOT_EVALUATED/DESIGN_ONLY/WAIVED_FOR_DEVELOPMENT）。

本脚本只产出**设计基线**（夹具执行属 Wave 4）。它的价值在于把"设计"约束成可机检结构：
    Q1 六个 CQ 齐备，缺一即 FAIL（fail-closed）
    Q2 每个 CQ 必须具备 query/positive/negative/expected/mutation/owner 六要素，缺一即 FAIL
    Q3 **任何 CQ 在设计阶段不得为 `PASS`**（`PASS` 只能由独立 QA 在执行后记录）
    Q4 D2/D4 未签期间，CQ1/CQ2/CQ3 必须是 `NOT_EVALUATED`（不得降级为 DESIGN_ONLY 蒙混）
    Q5 每个 CQ 至少 1 个否定式断言（负例 + 变异），防止"只测正例"的空转
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "loops/ONTO1-ontology-split/evidence/cq-fixtures"

REQUIRED_KEYS = ["id", "question", "validates", "query", "positive", "negative",
                 "expected", "mutation", "owner", "status", "gate"]
FORBIDDEN_STATUS_NOW = {"PASS"}
# D2（产品 Owner）/ D4（数据 Owner）未签期间，这三类必须保持 NOT_EVALUATED
BLOCKED_BY_EXTERNAL = {"CQ1": "D4", "CQ2": "D4", "CQ3": "D2"}

CQ_DEFINITIONS = [
    {
        "id": "CQ1",
        "question": "某法人何时、依据哪个源系统成为客户？",
        "validates": "CustomerRole + SourceIdentifier（L1）",
        "query": "按 LegalEntity 查 CustomerRole 及其 SourceIdentifier（sourceSystem/objectType/originalId/validFrom）",
        "positive": "法人 LE-001 经 SourceIdentifier{EDWCRM, Customer, C001, 2026-01-05} 关联 CustomerRole CR-001",
        "negative": "CustomerRole 无 SourceIdentifier ⇒ 摄取拒绝（fail-closed）",
        "expected": "正例返回（成为客户的时点 2026-01-05 + 来源 EDWCRM）；负例具名拒绝 `MISSING_SOURCE_IDENTIFIER`",
        "mutation": "删除 SourceIdentifier 的 sourceSystem ⇒ 必须 FAIL",
        "owner": "公共语义 Owner（待任命）",
        "status": "NOT_EVALUATED",
        "gate": "Wave 4 · 需 D4 签署后放行",
    },
    {
        "id": "CQ2",
        "question": "某集团成员关系在指定业务日是否有效，来源是什么？",
        "validates": "GroupMembership（validFrom/validTo + 来源）",
        "query": "按（fromEntity, toEntity, 业务日 D）查有效 GroupMembership 及来源",
        "positive": "M-001（2025-06-01~2026-12-31，来源=集团登记系统），D=2026-09-20 ⇒ 有效",
        "negative": "同一对实体在 D=2027-01-01 查询 ⇒ 无效（过期不得返回有效）",
        "expected": "正例返回有效+来源；负例返回无效且不带「有效」标记",
        "mutation": "把 validTo 改到查询日之后 ⇒ 负例翻正必须被检测为变更",
        "owner": "公共语义 Owner（待任命）",
        "status": "NOT_EVALUATED",
        "gate": "Wave 4 · 需 D4 签署后放行",
    },
    {
        "id": "CQ3",
        "question": "某产品知识卡描述的是哪个产品版本，是否在查询时点有效？",
        "validates": "ProductKnowledgeCard —describesProduct→ ProductOffering；ProductKnowledgeVersion 有效期",
        "query": "按卡 ID 查 describesProduct 目标 + 当前有效版本",
        "positive": "卡 PROD-CB-001 → ProductOffering PROD-CB-001，有效版本 v3（查询日在有效期内）",
        "negative": "卡指向已退役版本 / 悬空 product_id（40 处悬空引用样本）⇒ 具名提示 `DANGLING_PRODUCT_REF`",
        "expected": "正例返回产品身份+版本；负例具名拒绝或标记，**不得静默通过**",
        "mutation": "将 describesProduct 改指不存在的产品 ⇒ 必须 FAIL",
        "owner": "Knowledge Owner（KERT 维护方）",
        "status": "NOT_EVALUATED",
        "gate": "Wave 4 · **受 D2 硬阻塞**（40 处悬空引用未分类前不得标 PASS）",
    },
    {
        "id": "CQ4",
        "question": "某 GITS 建议使用了哪一版地图、规则、产品知识和数据快照？",
        "validates": "ActivationPlan（planHash + 版本子块：KM/AC/本体/数据快照）",
        "query": "按建议 ID 取 ActivationPlan，重算 planHash 并核对版本子块（API + 哈希重算脚本）",
        "positive": "建议 S-001 的 planHash 重算一致，版本子块含 KM@v、AC@v、ontology@sha256:…、snapshot@v",
        "negative": "版本子块缺 ontology 字段 ⇒ 拒绝执行（fail-closed，沿袭 ADR-0016）",
        "expected": "正例可完整回答「哪一版」；负例具名拒绝 `PLAN_VERSION_INCOMPLETE`",
        "mutation": "篡改版本子块任一字段 ⇒ planHash 必须不一致 ⇒ FAIL",
        "owner": "Integration Contract Owner（待任命）",
        "status": "DESIGN_ONLY",
        "gate": "Wave 4 · 实施后执行",
    },
    {
        "id": "CQ5",
        "question": "某能力可见但不可执行时，原因是未发布、无端点、无授权还是版本不兼容？",
        "validates": "CapabilityPublication + EndpointBinding + ConsumerBinding + ContractVersion（L4）",
        "query": "按能力 ID 取四对象状态，判定原因类别",
        "positive": "四态各一：① status=DRAFT ② 无 EndpointBinding ③ ConsumerBinding 缺失/过期 ④ 版本 ∉ 兼容集",
        "negative": "四种原因混报为单一「不可用」⇒ FAIL",
        "expected": "每种场景返回可区分原因码 `NOT_PUBLISHED`/`NO_ENDPOINT`/`UNAUTHORIZED`/`VERSION_INCOMPATIBLE`",
        "mutation": "删除 EndpointBinding ⇒ 原因必须从 OK 变为 NO_ENDPOINT",
        "owner": "Integration Contract Owner（待任命）",
        "status": "DESIGN_ONLY",
        "gate": "Wave 4 · 实施后执行",
    },
    {
        "id": "CQ6",
        "question": "某动作由谁确认，产生了什么回执，能否复算当时使用的知识与数据？",
        "validates": "Action / Receipt / HumanConfirmation（L3）+ planHash 复算",
        "query": "按 action_id 查确认人、回执、关联 plan 并重算",
        "positive": "Action A-001 ← HumanConfirmation{actor=RM-007, decision=APPROVE} → Receipt{status=SUCCESS}，planHash 复算一致",
        "negative": "无 HumanConfirmation 的 Action ⇒ FAIL（违反「AI 候选未经人工确认不得执行」）",
        "expected": "正例完整回答确认人/回执/可复算；负例具名失败 `ACTION_WITHOUT_CONFIRMATION`",
        "mutation": "删除 HumanConfirmation 记录 ⇒ 必须 FAIL",
        "owner": "GITS Owner",
        "status": "DESIGN_ONLY",
        "gate": "Wave 4 · 实施后执行",
    },
]


def write_fixtures(out_dir: Path | None = None) -> list[Path]:
    target = out_dir or OUT_DIR
    target.mkdir(parents=True, exist_ok=True)
    written = []
    for definition in CQ_DEFINITIONS:
        path = target / f"{definition['id']}.json"
        payload = dict(definition)
        payload["external_blocker"] = BLOCKED_BY_EXTERNAL.get(definition["id"])
        payload["schema"] = "onto1_cq_fixture/v1"
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        written.append(path)
    return written


def validate(target: Path) -> list[str]:
    failures: list[str] = []
    expected_ids = [item["id"] for item in CQ_DEFINITIONS]
    missing_files = [cid for cid in expected_ids if not (target / f"{cid}.json").is_file()]
    if missing_files:
        failures.append(f"Q1 missing fixture files: {missing_files}")
        return failures

    for cid in expected_ids:
        payload = json.loads((target / f"{cid}.json").read_text(encoding="utf-8"))
        # Q2 六要素齐备
        for key in REQUIRED_KEYS:
            value = payload.get(key)
            if value in (None, "", [], {}):
                failures.append(f"Q2 {cid} missing/empty field: {key}")
        # Q3 设计阶段不得 PASS
        if payload.get("status") in FORBIDDEN_STATUS_NOW:
            failures.append(f"Q3 {cid} must not claim PASS during design phase")
        # Q4 外部阻塞项必须 NOT_EVALUATED
        if cid in BLOCKED_BY_EXTERNAL and payload.get("status") != "NOT_EVALUATED":
            failures.append(f"Q4 {cid} is blocked by {BLOCKED_BY_EXTERNAL[cid]} "
                            f"⇒ status must be NOT_EVALUATED, got {payload.get('status')}")
        # Q5 否定式断言
        if not str(payload.get("negative", "")).strip():
            failures.append(f"Q5 {cid} lacks negative assertion")
        if not str(payload.get("mutation", "")).strip():
            failures.append(f"Q5 {cid} lacks mutation assertion")
    return failures


def gate(out_dir: Path | None = None, write: bool = False) -> int:
    """**只读盘上夹具并校验**（QA-W3R3 S-2 修复）。

    原实现 `if write: write_fixtures(target)` 先按常量重生成 6 份夹具、再校验自己刚写出的内容
    ⇒ Q1~Q5 五条失败路径**永不可达**，且会把盘上破坏**写回**。
    现：默认 `write=False`；重生成是**独立动作**（`--build`），不得混入门禁。
    """
    target = out_dir or OUT_DIR
    if write:
        write_fixtures(target)
    failures = validate(target)
    files = sorted(path.name for path in target.glob("CQ*.json"))
    print(f"[Q1] fixtures={len(files)} {files}")
    statuses = {cid: json.loads((target / f"{cid}.json").read_text(encoding="utf-8")).get("status")
                for cid in [item["id"] for item in CQ_DEFINITIONS] if (target / f"{cid}.json").is_file()}
    print(f"[Q3/Q4] statuses={statuses} blocked={BLOCKED_BY_EXTERNAL}")
    if failures:
        for item in failures:
            print(f"onto1-cq-fixtures: FAIL: {item}", file=sys.stderr)
        return 2
    print("onto1-cq-fixtures: PASS")
    return 0


def selftest() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="onto1-cq-selftest-"))
    failures: list[str] = []
    try:
        write_fixtures(tmp)
        # M1 把 CQ3 标 PASS ⇒ Q3/Q4 必须 FAIL
        path = tmp / "CQ3.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["status"] = "PASS"
        path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        problems = validate(tmp)
        ok1 = any("Q3" in item for item in problems) and any("Q4" in item for item in problems)
        print(f"{'PASS' if ok1 else 'FAIL'}  M1 CQ3 标 PASS（D2 未签）⇒ 被拦下  {problems[:2]}")
        if not ok1:
            failures.append("M1")

        # 恢复后再制造 M2：删掉 CQ4 的 mutation
        write_fixtures(tmp)
        path = tmp / "CQ4.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["mutation"] = ""
        path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        problems = validate(tmp)
        ok2 = any("Q2" in item and "mutation" in item for item in problems) or \
            any("Q5" in item for item in problems)
        print(f"{'PASS' if ok2 else 'FAIL'}  M2 删除 CQ4 变异断言 ⇒ 被拦下  {problems[:2]}")
        if not ok2:
            failures.append("M2")

        # M3 删掉一个夹具文件 ⇒ Q1 FAIL
        (tmp / "CQ6.json").unlink()
        problems = validate(tmp)
        ok3 = any("Q1" in item for item in problems)
        print(f"{'PASS' if ok3 else 'FAIL'}  M3 删除 CQ6 夹具 ⇒ 被拦下  {problems[:1]}")
        if not ok3:
            failures.append("M3")

        # M6（QA-W3R4 B-i5）：`Q5 negative 空缺`这条拒绝点此前**唯一未被自检踩到** ⇒ 补反例。
        neg_dir = Path(tempfile.mkdtemp(prefix="onto1-cq-neg-"))
        try:
            for f in OUT_DIR.glob("CQ*.json"):
                shutil.copy(f, neg_dir / f.name)
            np_ = neg_dir / "CQ1.json"
            payload = json.loads(np_.read_text(encoding="utf-8"))
            payload["negative"] = ""
            np_.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
            probs = validate(neg_dir)
            ok6 = any("Q5" in item and "negative" in item for item in probs)
            print(f"{'PASS' if ok6 else 'FAIL'}  M6 清空 CQ1.negative ⇒ Q5 拒因拦下  {probs[:1]}")
            if not ok6:
                failures.append("M6")
        finally:
            shutil.rmtree(neg_dir, ignore_errors=True)

        # M4 盘上篡改（不动仓内制品：在 tmp 复制后改）⇒ gate(write=False) 必须 FAIL
        tamper = Path(tempfile.mkdtemp(prefix="onto1-cq-tamper-"))
        try:
            for f in OUT_DIR.glob("CQ*.json"):
                shutil.copy(f, tamper / f.name)
            tp = tamper / "CQ2.json"
            payload = json.loads(tp.read_text(encoding="utf-8"))
            payload["status"] = "PASS"
            tp.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
            code_t = gate(tamper, write=False)
            ok4 = code_t == 2
            print(f"{'PASS' if ok4 else 'FAIL'}  M4 盘上篡改 CQ2 状态 ⇒ gate 必须 FAIL（真读盘）  exit={code_t}")
            if not ok4:
                failures.append("M4")
            # 且 gate 不得把篡改改回去（证明不写盘）
            after = json.loads(tp.read_text(encoding="utf-8")).get("status")
            ok5 = after == "PASS"
            print(f"{'PASS' if ok5 else 'FAIL'}  M5 gate 不得写回（篡改内容保持原样）  status={after}")
            if not ok5:
                failures.append("M5")
        finally:
            shutil.rmtree(tamper, ignore_errors=True)

        code = gate(OUT_DIR, write=False)
        print(f"{'PASS' if code == 0 else 'FAIL'}  M0 对照：正式夹具 ⇒ PASS  exit={code}")
        if code != 0:
            failures.append("M0")

        if failures:
            print(f"onto1-cq-fixtures-selftest: FAIL {failures}", file=sys.stderr)
            return 2
        print("onto1-cq-fixtures-selftest: PASS")
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gate", action="store_true")
    parser.add_argument("--selftest", action="store_true")
    parser.add_argument("--build", action="store_true",
                        help="显式重生成 6 份夹具（**独立动作**；gate 不再代写，见 QA-W3R3 S-2）")
    args = parser.parse_args()
    if args.build:
        write_fixtures(OUT_DIR)
        print(f"已显式重生成 6 份夹具 → {OUT_DIR}（与 gate 分离；QA-W3R3 S-2）")
        return 0
    if args.selftest:
        return selftest()
    return gate(OUT_DIR, write=False)


if __name__ == "__main__":
    raise SystemExit(main())
