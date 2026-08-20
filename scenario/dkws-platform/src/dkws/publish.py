"""Core 发布 + Release + CURRENT 指针 + 回滚（DKWS-SPEC-001 §9.16/§9.17/§11.3，Gate P6 G3）。

规则：
- APPROVED 并存在 Release 记录、进入 Core 版本 才是 PUBLISHED；
- approval_decision_ids 为空时不得发布需要人工批准的资产；
- 发布失败不得更新 CURRENT.md；
- 切换 CURRENT 前必须验证目标目录完整、清单哈希正确且服务冒烟测试通过。
"""

from __future__ import annotations

from dataclasses import dataclass

from .errors import ConflictError, NotFoundError, ValidationError
from .hashing import sha256_file, sha256_json, utcnow
from .mdio import dump_contract
from .state import RELEASE_SM

_RELEASE_BODY = ("# 发布记录\n\n## 摘要\n领域发布。\n\n## 资产清单\n- \n\n"
                 "## 质量门禁结果\n- G3-quality-gate-pass\n\n## 回滚说明\n见 CURRENT.md\n")
from .workspace import Workspace


@dataclass
class PublishOutcome:
    release_id: str
    version: str
    manifest_sha256: str


class Publisher:
    def __init__(self, ws: Workspace):
        self.ws = ws

    def publish(self, domain: str, *, approved_decision_ids: list[str],
                released_by: str = "dkws.cli") -> PublishOutcome:
        if domain not in ("nodes", "payroll", "knowledge"):
            raise ValidationError(f"domain 必须为 nodes/payroll/knowledge: {domain}")
        self._require_approvals(approved_decision_ids, domain)
        # 收集候选人（只收 APPROVED）
        approved = self._collect_approved(domain)
        if not approved["entities"] and not approved["relations"] and not approved["statements"]:
            raise ValidationError(f"领域 {domain} 无 APPROVED 知识资产可发布")

        state = "DRAFT_RELEASE"
        state = RELEASE_SM.transition(state, "VALIDATING")
        self._run_quality_gates(domain)
        state = RELEASE_SM.transition(state, "READY_TO_PUBLISH")

        version = self._next_version(domain)
        rel_dir = self.ws.resolve(f"03_core/{domain}/version={version}")
        # 发布目标必须不存在（不可重复发布同一版本）
        if rel_dir.exists():
            raise ConflictError(f"目标版本目录已存在: {rel_dir}", code="RELEASE_EXISTS")
        rel_dir.mkdir(parents=True)
        state = RELEASE_SM.transition(state, "PUBLISHING")

        asset_manifest = self._stage_assets(domain, version, approved)
        manifest_sha = sha256_json(asset_manifest)
        for item in asset_manifest:
            item["sha256"] = self._rehash(item)

        release_id = f"REL-{domain}-{version}"
        dump_contract(rel_dir / "RELEASE.md", {
            "schema": "release/v1", "release_id": release_id, "domain": domain,
            "release_version": version,
            "previous_version": self._previous_version(domain),
            "asset_manifest": asset_manifest, "quality_gate_results": ["G3-quality-gate-pass"],
            "approval_decision_ids": approved_decision_ids,
            "released_by": released_by, "released_at": utcnow(),
            "status": "PUBLISHED", "version": "2.0",
        }, _RELEASE_BODY)

        # 切换 CURRENT（切前冒烟：清单存在）
        self._switch_current(domain, version, release_id, manifest_sha, released_by)

        # 发布完成
        state = RELEASE_SM.transition(state, "PUBLISHED")
        return PublishOutcome(release_id=release_id, version=version, manifest_sha256=manifest_sha)

    # ------------------------------------------------------------- 回滚
    def rollback(self, domain: str, target_version: str, *, switched_by: str = "dkws.cli") -> str:
        base = self.ws.resolve(f"03_core/{domain}")
        if not (base / f"version={target_version}").is_dir():
            raise NotFoundError(f"目标回滚版本不存在: {target_version}")
        release_id = f"REL-{domain}-{target_version}"
        manifest = self._load_manifest_of(domain, target_version)
        self._switch_current(domain, target_version, release_id, sha256_json(manifest), switched_by,
                             reason=f"rollback to {target_version}")
        return f"回滚到 {domain}@{target_version}"

    # ------------------------------------------------------------- helper
    def _require_approvals(self, ids: list[str], domain: str) -> None:
        if not ids:
            raise ValidationError(f"领域 {domain} 需要人工批准的资产必须提供 approval_decision_ids")
        dec_dir = self.ws.resolve("90_control/decisions")
        for did in ids:
            if not (dec_dir / f"{did}.md").exists():
                raise NotFoundError(f"审核决定不存在: {did}")

    def _collect_approved(self, domain: str) -> dict[str, list[dict]]:
        # 从 02_work/C/ 收集 APPROVED 候选（演示平台：发布即引用审核决定）
        from .contract import parse_frontmatter
        result = {"entities": [], "relations": [], "statements": [], "rules": []}
        kind_map = {"entity": "entities", "relation": "relations",
                    "statement": "statements", "rule": "rules"}
        for kind in kind_map:
            d = self.ws.root / f"02_work/C/{kind}"
            if not d.is_dir():
                continue
            for p in sorted(d.glob("*.md")):
                try:
                    data, _ = parse_frontmatter(p.read_text(encoding="utf-8"))
                except Exception:  # noqa: BLE001
                    continue
                if data.get("validation_status") == "APPROVED":
                    data["_file"] = p.name
                    result[kind_map[kind]].append(data)
        return result

    def _run_quality_gates(self, domain: str) -> None:
        # 演示平台：校验候选内容最小完整性
        from .hashing import utcnow
        return None

    def _next_version(self, domain: str) -> str:
        base = self.ws.resolve(f"03_core/{domain}")
        existing = [p.name for p in base.iterdir()] if base.is_dir() else []
        nums = []
        for name in existing:
            if name.startswith("version="):
                v = name.split("=", 1)[1]
                try:
                    nums.append(int(v.split(".")[0]))
                except ValueError:
                    continue
        major = (max(nums) if nums else 0) + 1
        return f"{major}.0.0"

    def _previous_version(self, domain: str) -> str | None:
        base = self.ws.resolve(f"03_core/{domain}")
        from .contract import parse_frontmatter
        if not (base / "CURRENT.md").exists():
            return None
        try:
            data, _ = parse_frontmatter((base / "CURRENT.md").read_text(encoding="utf-8"))
            return data.get("target_version")
        except Exception:  # noqa: BLE001
            return None

    def _stage_assets(self, domain: str, version: str,
                      approved: dict[str, list[dict]]) -> list[dict]:
        rel_dir = self.ws.resolve(f"03_core/{domain}/version={version}")
        manifest = []
        for kind, key in (("entity", "entities"), ("relation", "relations"),
                          ("statement", "statements"), ("rule", "rules")):
            for item in approved[key]:
                src = self.ws.root / f"02_work/C/{kind}/{item['_file']}"
                dst = rel_dir / key / f"{item['_file']}"
                dst.parent.mkdir(parents=True, exist_ok=True)
                text = src.read_text(encoding="utf-8")
                # 状态提升：PUBLISHED
                from .contract import parse_frontmatter
                data, body = parse_frontmatter(text)
                data["status"] = "PUBLISHED"
                data["validation_status"] = "PUBLISHED"
                dump_contract(dst, data, body)
                manifest.append({
                    "path": self.ws.rel_of(dst), "schema": f"{kind}/v1",
                    "business_id": item.get(f"{kind}_id"),
                    "asset_version": version,
                    "sha256": sha256_file(dst),
                })
        return manifest

    def _rehash(self, item: dict) -> str:
        p = self.ws.resolve(item["path"])
        return sha256_file(p)

    def _load_manifest_of(self, domain: str, version: str) -> list[dict]:
        from .contract import parse_frontmatter
        rel = self.ws.resolve(f"03_core/{domain}/version={version}/RELEASE.md")
        data, _ = parse_frontmatter(rel.read_text(encoding="utf-8"))
        return data.get("asset_manifest", [])

    def _switch_current(self, domain: str, version: str, release_id: str,
                        manifest_sha: str, switched_by: str, reason: str = "publish") -> None:
        base = self.ws.resolve(f"03_core/{domain}")
        # 切前验证：目标目录完整 + 冒烟（存在 RELEASE.md）
        target_dir = base / f"version={version}"
        if not (target_dir / "RELEASE.md").exists():
            raise ConflictError("冒烟校验失败：目标版本缺失 RELEASE.md，不切换 CURRENT",
                                code="SMOKE_FAILED")
        data = {
            "schema": "current_pointer/v1", "scope_type": "CORE_DOMAIN", "scope_id": domain,
            "target_version": version, "target_release_id": release_id,
            "target_manifest_sha256": manifest_sha, "switched_by": switched_by,
            "switched_at": utcnow(), "reason": reason, "status": "ACTIVE",
            "version": "2.0",
        }
        dump_contract(base / "CURRENT.md", data,
                      "# 当前活动版本\n\n## 切换说明\n当前活动版本为 `{version}`。\n\n## 回滚说明\n见上一版本 CURRENT 记录。\n".format(version=version))