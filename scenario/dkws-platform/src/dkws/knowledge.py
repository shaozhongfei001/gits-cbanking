"""知识候选 + 冲突检测 + 审核决定（DKWS-SPEC-001 §9.5-9.8/§9.19/§11.2，Gate P5 G2）。

- 候选生成：从片段/声明生成 实体/关系/声明/规则 候选；
- 冲突检测：冲突/一致判定（conflict_status）；
- 审核决定：Review Decision，系统不得自动为 OWNER/INDEPENDENT_QA 生成批准决定。
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from .errors import ConflictError, ValidationError
from .hashing import utcnow
from .mdio import dump_contract
from .state import ASSET_SM
from .workspace import Workspace

_PREDICATE_RE = re.compile(r"^[a-z_][a-z0-9_]*$")


@dataclass
class Candidate:
    kind: str            # entity/relation/statement/rule
    ref: str             # 候选稳定 ID
    values: dict


class KnowledgeService:
    def __init__(self, ws: Workspace):
        self.ws = ws

    # ------------------------------------------------------------- 候选生成
    def register_entity_candidate(self, *, entity_id: str, entity_type: str, name: str,
                                  aliases: list[str], domain: str, source_document_ids: list[str],
                                  recorded_by: str = "candidate-extractor",
                                  description: str | None = None,
                                  attributes: dict | None = None) -> Candidate:
        values = {
            "schema": "entity/v1", "entity_id": entity_id, "entity_type": entity_type,
            "name": name, "aliases": aliases,
            "description": description or name, "domain": domain,
            "canonical_id": entity_id, "attributes": attributes or {},
            "source_document_ids": source_document_ids, "first_seen_at": utcnow(),
            "validation_status": "CANDIDATE", "conflict_status": "NONE",
            "effective_from": None, "effective_to": None, "recorded_at": utcnow(),
            "status": "ACTIVE", "version": "1.0", "source_segment_ids": [],
        }
        return self._write_candidate("entity", f"ENT-{entity_id}", values)

    def register_relation_candidate(self, *, relation_id: str, source_id: str, target_id: str,
                                    relation_type: str, direction: str, statement_id: str,
                                    source_document_ids: list[str]) -> Candidate:
        self._ensure_entity(source_id)
        self._ensure_entity(target_id)
        values = {
            "schema": "relation/v1", "relation_id": relation_id, "source_id": source_id,
            "target_id": target_id, "relation_type": relation_type,
            "direction": direction, "statement_id": statement_id, "aliases": [],
            "validated": True, "source_entity_type": None, "target_entity_type": None,
            "source_document_ids": source_document_ids, "first_seen_at": utcnow(),
            "validation_status": "CANDIDATE", "conflict_status": "NONE",
            "effective_from": None, "effective_to": None, "recorded_at": utcnow(),
            "status": "ACTIVE", "version": "1.0",
        }
        return self._write_candidate("relation", f"REL-{relation_id}", values)

    def register_statement_candidate(self, *, statement_id: str, subject_id: str, predicate: str,
                                     object_value: str, value_type: str, polarity: str = "AFFIRMED",
                                     derived: str = "NATIVE", source_document_ids: list[str]) -> Candidate:
        if not _PREDICATE_RE.match(predicate):
            raise ValidationError(f"谓词非法（应匹配 {_PREDICATE_RE.pattern}）: {predicate}")
        values = {
            "schema": "statement/v1", "statement_id": statement_id, "subject_id": subject_id,
            "predicate": predicate, "object_value": object_value,
            "value_type": value_type, "object_entity_id": None, "object_unit": None,
            "derived": derived, "derivation_rule_id": None, "confidence": None,
            "polarity": polarity, "validation_status": "CANDIDATE", "conflict_status": "NONE",
            "effective_from": None, "effective_to": None, "recorded_at": utcnow(),
            "status": "ACTIVE", "version": "1.0",
            "source_document_ids": source_document_ids, "source_segment_ids": [],
        }
        return self._write_candidate("statement", f"STMT-{statement_id}", values)

    def register_rule_candidate(self, *, rule_id: str, name: str, rule_type: str, priority: int,
                                execution_mode: str, when: dict, then: dict, required_inputs: list[str],
                                test_case_ids: list[str], source_document_id: str | None = None) -> Candidate:
        if not (0 <= priority <= 1000):
            raise ValidationError("rule.priority 必须在 0..1000")
        if len(test_case_ids) < 2:
            raise ValidationError("rule.test_case_ids 至少需正向、反向各一个")
        values = {
            "schema": "rule/v1", "rule_id": rule_id, "name": name,
            "rule_type": rule_type, "priority": priority, "execution_mode": execution_mode,
            "when": when, "then": then, "else": None, "required_inputs": required_inputs,
            "source_document_id": source_document_id, "source_segment_id": None,
            "test_case_ids": test_case_ids, "validation_status": "CANDIDATE",
            "status": "ACTIVE", "effective_from": None, "effective_to": None,
            "version": "1.0",
        }
        return self._write_candidate("rule", f"RUL-{rule_id}", values)

    def _write_candidate(self, kind: str, ref: str, values: dict) -> Candidate:
        # 候选暂存于 02_work/C/<kind>/ 下，供后续审核后提升到 03_core
        rel_dir = f"02_work/C/{kind}"
        (self.ws.root / rel_dir).mkdir(parents=True, exist_ok=True)
        candidate_path = self.ws.root / rel_dir / f"{ref}.md"
        dump_contract(candidate_path, values, _candidate_body(kind, values))
        return Candidate(kind=kind, ref=ref, values=values)

    # ------------------------------------------------------------- 冲突检测
    def detect_conflicts(self, emit: str = "none") -> int:
        """对同一主语+谓词的多个候选做冲突检测。返回冲突数。

        emit: 未经处理的冲突不做自动发布。此处仅登记 conflict_status 供审核。
        """
        stmts = self._load_candidates("statement")
        by_key: dict[tuple, list[dict]] = {}
        for s in stmts:
            key = (s["values"].get("subject_id"), s["values"].get("predicate"))
            by_key.setdefault(key, []).append(s)
        conflicts = 0
        for (subj, pred), group in by_key.items():
            if len(group) < 2:
                continue
            bases = {st["values"].get("object_value") for st in group}
            if len(bases) > 1:
                conflicts += 1
                for st in group:
                    st["values"]["conflict_status"] = "CONFIRMED"
                    self._rewrite_candidate(st)
        return conflicts

    # ------------------------------------------------------------- 审核决定
    def record_decision(self, *, decision_id: str, object_refs: list[str], decision: str,
                        decided_by: str, role: str, reason: str, conditions: list[str] | None = None) -> str:
        if decision not in ("APPROVE", "REJECT", "REQUEST_CHANGES", "WAIVE"):
            raise ValidationError(f"非法 decision: {decision}")
        if role in ("OWNER", "INDEPENDENT_QA") and decided_by == "_system_auto":
            raise ConflictError("§9.19: 系统禁止自动生成 OWNER/INDEPENDENT_QA 批准决定",
                                code="AUTO_DECISION")
        values = {
            "schema": "review_decision/v1", "decision_id": decision_id,
            "object_refs": object_refs, "decision": decision, "decided_by": decided_by,
            "role": role, "decided_at": utcnow(), "reason": reason,
            "conditions": conditions or [], "evidence_refs": [], "status": "ACTIVE",
            "version": "1.0",
        }
        rel = f"90_control/decisions/{decision_id}.md"
        dump_contract(self.ws.root / rel, values,
                      "# 审核决定\n\n## 决定描述\n{}\n\n## 条件\n- \n\n## 依据\n{}\n\n## 变更记录\n- v1.0\n".format(decision, reason))
        # 应用决策到候选（升级到 APPROVED / IN_REVIEW / REJECTED）
        self._apply_decision(object_refs, decision, role, decided_by)
        return rel

    def _apply_decision(self, object_refs: list[str], decision: str, role: str, decided_by: str) -> None:
        for ref in object_refs:
            cand = self._find_candidate(ref)
            if cand is None:
                continue
            cur = cand["values"].get("validation_status", "CANDIDATE")
            if decision == "APPROVE":
                if role not in ("OWNER", "INDEPENDENT_QA", "TECH_LEAD", "DATA_OWNER"):
                    # 非权威角色不能批准，转 IN_REVIEW
                    new = "IN_REVIEW"
                else:
                    # 候选直接批准：CANDIDATE -> APPROVED 需经 IN_REVIEW（合规状态机）
                    new = cur
                    if cur == "CANDIDATE":
                        new = ASSET_SM.transition(cur, "IN_REVIEW")
                    new = ASSET_SM.transition(new, "APPROVED")
            elif decision == "REJECT":
                new = "REJECTED" if cur in ("IN_REVIEW", "CANDIDATE") else cur
                if cur != "REJECTED":
                    ASSET_SM.transition(cur, new)
            elif decision == "REQUEST_CHANGES":
                new = "CANDIDATE"
                if cur != "CANDIDATE":
                    ASSET_SM.transition(cur, new)
            else:  # WAIVE
                new = cur
            cand["values"]["validation_status"] = new
            self._rewrite_candidate(cand)

    # ------------------------------------------------------------- helper
    def _load_candidates(self, kind: str) -> list:
        from .contract import parse_frontmatter, resolve_by_contract
        rel_dir = f"02_work/C/{kind}"
        d = self.ws.root / rel_dir
        if not d.is_dir():
            return []
        out = []
        for p in sorted(d.glob("*.md")):
            text = p.read_text(encoding="utf-8")
            try:
                data, _ = parse_frontmatter(text)
                out.append({"ref": p.stem, "values": data, "path": p, "kind": kind})
            except Exception:  # noqa: BLE001
                continue
        return out

    def _find_candidate(self, ref: str):
        for kind in ("entity", "relation", "statement", "rule"):
            for c in self._load_candidates(kind):
                if c["ref"] == ref:
                    return c
        return None

    def _rewrite_candidate(self, cand) -> None:
        # 审核后基于最新 values 重新渲染正文，避免保留旧模板占位
        kind = cand["kind"]
        dump_contract(cand["path"], cand["values"], _candidate_body(kind, cand["values"]))

    def _ensure_entity(self, entity_id: str) -> None:
        if self._find_candidate(f"ENT-{entity_id}"):
            return
        raise ConflictError(f"关系引用的实体候选不存在: {entity_id}", code="REFERENTIAL")


def _candidate_body(kind: str, values: dict) -> str:
    """按 values 真实渲染正文（非模板占位）。让生成物正文承载实际语义，而非仅 frontmatter。"""

    def _bullet(items):
        if not items:
            return "-（无）"
        return "\n".join(f"- {i}" for i in items)

    if kind == "entity":
        return (
            f"# 实体\n\n"
            f"## 描述\n{values.get('description') or values.get('name', '')}\n\n"
            f"## 来源证据\n{_bullet(values.get('source_document_ids', []))}\n\n"
            f"## 冲突与限定\n冲突状态: {values.get('conflict_status', 'NONE')}；"
            f"校验状态: {values.get('validation_status', '')}。\n\n"
            f"## 审核说明\n实体类型 {values.get('entity_type', '')}，"
            f"状态 {values.get('status', '')}。\n"
        )
    if kind == "relation":
        return (
            f"# 关系\n\n"
            f"## 描述\n{values.get('relation_type', '')}："
            f"{values.get('source_id', '')} → {values.get('target_id', '')}"
            f"（方向 {values.get('direction', '')}）\n\n"
            f"## 来源证据\n{_bullet(values.get('source_document_ids', []))}\n\n"
            f"## 冲突与限定\n冲突状态: {values.get('conflict_status', 'NONE')}；"
            f"校验状态: {values.get('validation_status', '')}。\n\n"
            f"## 审核说明\n绑定声明: {values.get('statement_id', '')}，"
            f"状态 {values.get('status', '')}。\n"
        )
    if kind == "statement":
        return (
            f"# 声明\n\n"
            f"## 规范表达\n{values.get('subject_id', '')} —"
            f"{values.get('predicate', '')}— {values.get('object_value', '')}"
            f"（{values.get('value_type', '')}, {values.get('polarity', '')}）\n\n"
            f"## 来源证据\n{_bullet(values.get('source_document_ids', []))}\n\n"
            f"## 冲突与限定\n冲突状态: {values.get('conflict_status', 'NONE')}；"
            f"校验状态: {values.get('validation_status', '')}。\n\n"
            f"## 审核说明\n派生: {values.get('derived', 'NATIVE')}，"
            f"状态 {values.get('status', '')}。\n"
        )
    if kind == "rule":
        w = values.get("when", {})
        t = values.get("then", {})
        return (
            f"# 规则\n\n"
            f"## 业务解释\n规则 {values.get('rule_id', '')} — {values.get('name', '')}\n\n"
            f"## 输入与输出\n输入: {_bullet(values.get('required_inputs', []))}\n\n"
            f"## 证据\n条件(when): `{w}`\n执行(then): `{t}`\n\n"
            f"## 人工责任边界\n执行模式: {values.get('execution_mode', '')}；"
            f"规则类型: {values.get('rule_type', '')}。\n\n"
            f"## 测试说明\n{_bullet(values.get('test_case_ids', []))}\n"
        )
    return ""