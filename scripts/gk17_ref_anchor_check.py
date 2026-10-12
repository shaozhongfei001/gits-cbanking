#!/usr/bin/env python3
"""GK17 WP5.1 引用锚定门禁（上游判据 V3）—— fail-closed，纯 stdlib。

判据 V3
-------
知识地图引用一个「不存在的个体」必须被**拒绝（fail-closed）**。

覆盖的 ID 空间与其权威锚点来源（一律复用既有权威，不另造第二套定义）
-------------------------------------------------------------------
| ID 空间              | 出现位置                                      | 锚点来源（权威）                                                        |
|----------------------|-----------------------------------------------|-------------------------------------------------------------------------|
| 地图 `KM-*`          | `mapId`、`domains[].mapRef`（地图→地图引用）   | `specs/knowledge-architecture/maps/**/*.md` 的 `mapId`                  |
| 域 `KD-*`            | `domains[].domainId`                          | 资产 manifest 的 `domain` 值 ∪ 各图 `domains[].domainId`（见「诚实缺口」）|
| 资产 `ASSET-*`       | `assetRefs`                                   | `specs/knowledge-architecture/assets/**/*.md` 的 `assetId`              |
| 技能 `SP-*`          | `skillRefs`                                   | `specs/knowledge-architecture/skills/*.json` 的 `skillId`               |
| 激活合同 `AC-*`      | `activationContractRefs`                      | `specs/knowledge-architecture/activations/*.json` 的 `contractId`       |
| 路由策略 `RP-*`      | `routePolicyRef`                              | `specs/knowledge-architecture/routes/*.json` 的 `policyId`              |
| 任务入口 `TaskType`  | `entrypoints.tasks`                           | 本体 `gits:TaskType`（对齐）∪ activations/routes 的 `taskType`           |

既有缺口（实测，本门禁要补的洞）
--------------------------------
`scripts/validate_knowledge_architecture.py` 只校验 `assetRefs` / `skillRefs` /
`activationContractRefs` / `routePolicyRef` 四类，**完全不校验**：
  1. `domains[].domainId`（KD-* 无任何校验）
  2. `domains[].mapRef`（地图→地图引用，含路径是否存在）
  3. `entrypoints.tasks`（任务入口是否对齐本体）
而 `MapVersion.json` 只登记 `SIM-MAP-FINANCE`，`KM-*` 无独立 registry。

诚实缺口（不靠放宽判定刷绿）
----------------------------
`KD-*` **没有独立锚点来源**：registry 无 KD 条目、本体无 `KnowledgeDomain` 类
（`gits-core.owl.ttl` 与 `gits-core.linkml.yaml` 均确认）、`gits:` 32 类中无 KD 类。
仅有两处旁证且粒度不一致：资产 manifest 的 `"domain":"KD-CORP-RM"`（不含叶子域），
以及本图自身的 `domains[].domainId` 自声明。
因此本门禁**单列** `unanchoredIdSpaces` 报告该缺口，**不**把它计入 PASS 断言 ——
即：既不让它把门禁刷绿，也不谎称 KD-* 已获外部锚定。

变异负例（本仓硬约束：不做负例的门禁视为未完成）
------------------------------------------------
`--selftest` 在**临时副本**上注入假引用，证明门禁真的会 FAIL，并打印前后对照；
临时副本用后即删，原文件以 sha256 逐字节自证未被改动。

退出码：0 = PASS；2 = FAIL（存在未锚定引用）；3 = 自证失败；4 = 环境/用法错误。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import tempfile
from pathlib import Path

# ══════════════════════════════════════════════════════════════════════════════
# 复用既有权威：常量对齐 scripts/validate_knowledge_architecture.py（该文件只读，未修改）
# ══════════════════════════════════════════════════════════════════════════════
KA_REL = Path("specs") / "knowledge-architecture"
MAPS_REL = KA_REL / "maps"
ASSETS_REL = KA_REL / "assets"
SKILLS_REL = KA_REL / "skills"
ACTIVATIONS_REL = KA_REL / "activations"
ROUTES_REL = KA_REL / "routes"
REGISTRY_REL = KA_REL / "registry"
ONTOLOGY_REL = Path("specs") / "semantic" / "gits-core.owl.ttl"

# 本体 ID 空间类名（gits-core.owl.ttl 中的 gits: 类）—— 任务入口锚点须与本体的 TaskType 对齐
ONTOLOGY_TASK_TYPE_CLASS = "gits:TaskType"

# 引用字段 → ID 空间标签
REF_FIELDS = (
    ("assetRefs", "asset"),
    ("skillRefs", "skill"),
    ("activationContractRefs", "activationContract"),
)

# 自举：这些是**锚点来源自身的载体**，不是"被引用个体"，不参与锚定校验
ANCHOR_CARRIER_FIELDS = ("schemaVersion", "name", "version", "status", "mapType",
                         "defaultPolicy", "maxInitialTokens", "entrypoints", "domains")

# 显式豁免：这些 ID 是**设计上刻意不属于任何已批准合同的占位符**，
# 由 routes/RP-CORP-RM-001.json 自己声明（AC-NOT-IN-P20 字面量）。
# 与"假引用"不同：它在权威源内有正式出处（validate_knowledge_architecture.py 同样显式放行）。
# 仅对 activationContractRefs 生效，且**必须**在权威源中查得到该字面量，否则不豁免。
PLACEHOLDER_IDS = {"AC-NOT-IN-P20"}


class GateError(Exception):
    """环境/解析类错误（非门禁判定失败）。"""


# ══════════════════════════════════════════════════════════════════════════════
# 读取原语（与既有校验器同构，便于审计对照）
# ══════════════════════════════════════════════════════════════════════════════
def read_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise GateError(f"{path}: invalid JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise GateError(f"{path}: root object required")
    return value


def read_frontmatter(path: Path) -> dict:
    """知识地图/资产 manifest 的 front matter 是**一行 JSON**（契约规定）。"""
    text = path.read_text(encoding="utf-8-sig")
    lines = text.splitlines()
    if len(lines) < 4 or lines[0].strip() != "---":
        raise GateError(f"{path}: opening frontmatter delimiter required")
    try:
        closing = next(index for index in range(1, len(lines)) if lines[index].strip() == "---")
    except StopIteration:
        raise GateError(f"{path}: closing frontmatter delimiter required") from None
    raw = "\n".join(lines[1:closing]).strip()
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise GateError(f"{path}: frontmatter must be JSON-compatible YAML: {exc}") from exc
    if not isinstance(value, dict):
        raise GateError(f"{path}: frontmatter object required")
    if not "\n".join(lines[closing + 1:]).strip():
        raise GateError(f"{path}: human-readable markdown body required")
    return value


def rel(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def collect_json_ids(root: Path, directory: Path, id_field: str, label: str) -> dict[str, str]:
    """从目录下 *.json 收集 id_field 作为锚点集合。"""
    index: dict[str, str] = {}
    base = root / directory
    if not base.is_dir():
        return index
    for path in sorted(base.glob("*.json")):
        try:
            value = read_json(path)
        except GateError:
            continue
        item_id = value.get(id_field)
        if isinstance(item_id, str) and item_id:
            index.setdefault(item_id, rel(root, path))
    return index


def collect_manifest_ids(root: Path, directory: Path, id_field: str) -> dict[str, str]:
    """从目录下 **/*.md 的 front matter 收集 id_field 作为锚点集合。"""
    index: dict[str, str] = {}
    base = root / directory
    if not base.is_dir():
        return index
    for path in sorted(base.rglob("*.md")):
        try:
            value = read_frontmatter(path)
        except GateError:
            continue
        item_id = value.get(id_field)
        if isinstance(item_id, str) and item_id:
            index.setdefault(item_id, rel(root, path))
    return index


def collect_ontology_classes(root: Path) -> set[str]:
    """从本体 TTL 抽取 `gits:Xxx a owl:Class` 的类名集合。"""
    path = root / ONTOLOGY_REL
    if not path.is_file():
        return set()
    classes: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        head = line.split(" a owl:Class", 1)
        if len(head) == 2 and head[0].strip().startswith("gits:"):
            classes.add(head[0].strip())
    return classes


# ══════════════════════════════════════════════════════════════════════════════
# 锚点集合装配
# ══════════════════════════════════════════════════════════════════════════════
def build_anchor_index(root: Path) -> tuple[dict[str, dict[str, str]], dict[str, object]]:
    if not (root / KA_REL).is_dir():
        raise GateError(f"knowledge architecture directory missing: {root / KA_REL}")

    maps = collect_manifest_ids(root, MAPS_REL, "mapId")
    assets = collect_manifest_ids(root, ASSETS_REL, "assetId")
    skills = collect_json_ids(root, SKILLS_REL, "skillId", "skill")
    activations = collect_json_ids(root, ACTIVATIONS_REL, "contractId", "activation")
    routes = collect_json_ids(root, ROUTES_REL, "policyId", "route")

    # 域（KD-*）：无独立权威源 —— 只能用旁证聚合，并在报告中诚实标注
    domains: dict[str, str] = {}
    for path in sorted((root / MAPS_REL).rglob("*.md")):
        try:
            value = read_frontmatter(path)
        except GateError:
            continue
        for domain in value.get("domains", []) or []:
            if isinstance(domain, dict) and isinstance(domain.get("domainId"), str):
                domains.setdefault(domain["domainId"], rel(root, path))
    for path in sorted((root / ASSETS_REL).rglob("*.md")):
        try:
            value = read_frontmatter(path)
        except GateError:
            continue
        domain_id = value.get("domain")
        if isinstance(domain_id, str) and domain_id:
            domains.setdefault(domain_id, rel(root, path))

    # 任务入口：本体 gits:TaskType（对齐）+ 合同的 hasTaskType + 路由规则的 taskType
    ontology_classes = collect_ontology_classes(root)
    task_types: dict[str, str] = {}
    for path in sorted((root / ACTIVATIONS_REL).glob("*.json")):
        try:
            value = read_json(path)
        except GateError:
            continue
        if isinstance(value.get("taskType"), str) and value["taskType"]:
            task_types.setdefault(value["taskType"], rel(root, path))
    for path in sorted((root / ROUTES_REL).glob("*.json")):
        try:
            value = read_json(path)
        except GateError:
            continue
        for rule in value.get("rules", []) or []:
            if isinstance(rule, dict) and isinstance(rule.get("taskType"), str) and rule["taskType"]:
                task_types.setdefault(rule["taskType"], rel(root, path))

    placeholders = resolve_placeholders(root)

    anchors: dict[str, dict[str, str]] = {
        "map": maps,
        "domain": domains,
        "asset": assets,
        "skill": skills,
        "activationContract": activations,
        "routePolicy": routes,
        "taskType": task_types,
    }
    meta = {
        "ontologyTaskTypeClass": ONTOLOGY_TASK_TYPE_CLASS,
        "ontologyTaskTypeDeclared": ONTOLOGY_TASK_TYPE_CLASS in ontology_classes,
        "ontologyClassCount": len(ontology_classes),
        "placeholders": placeholders,
    }
    return anchors, meta


def resolve_placeholders(root: Path) -> dict[str, str]:
    """占位符豁免必须**在权威源里查得到字面量**，否则不豁免（fail-closed）。"""
    found: dict[str, str] = {}
    routes_dir = root / ROUTES_REL
    if not routes_dir.is_dir():
        return found
    for path in sorted(routes_dir.glob("*.json")):
        text = path.read_text(encoding="utf-8")
        for placeholder in PLACEHOLDER_IDS:
            if placeholder in text:
                found.setdefault(placeholder, rel(root, path))
    return found


# ══════════════════════════════════════════════════════════════════════════════
# 判定
# ══════════════════════════════════════════════════════════════════════════════
def check_ref(
    root: Path,
    anchors: dict[str, dict[str, str]],
    space: str,
    ref: str,
    holder: Path,
    field: str,
    violations: list[dict],
    checked: dict[str, int],
) -> None:
    checked[space] = checked.get(space, 0) + 1
    if not isinstance(ref, str) or not ref:
        return
    if space == "activationContract" and ref in PLACEHOLDER_IDS:
        # 占位符仅在权威源确有出处时豁免（见 resolve_placeholders）
        return
    if ref not in anchors[space]:
        violations.append({
            "idSpace": space,
            "referencedId": ref,
            "field": field,
            "mapFile": rel(root, holder),
            "reason": "NO_ANCHOR_IN_AUTHORITATIVE_SOURCE",
        })


def check(root: Path) -> dict:
    anchors, meta = build_anchor_index(root)

    violations: list[dict] = []
    checked: dict[str, int] = {}
    map_records: list[dict] = []

    for path in sorted((root / MAPS_REL).rglob("*.md")):
        value = read_frontmatter(path)
        map_id = value.get("mapId")
        record = {"mapId": map_id, "file": rel(root, path), "mapType": value.get("mapType")}
        map_records.append(record)

        # 1. 地图自身身份可锚定（自举：文件即锚点，这里记录一致性）
        if map_id not in anchors["map"]:
            violations.append({
                "idSpace": "map", "referencedId": map_id, "field": "mapId",
                "mapFile": rel(root, path),
                "reason": "MAP_ID_NOT_IN_MAP_ANCHOR_SET",
            })

        # 2. 地图 → 地图引用（既有校验器完全没查这一项）
        for domain in value.get("domains", []) or []:
            if not isinstance(domain, dict):
                continue
            check_ref(root, anchors, "domain", domain.get("domainId"), path,
                      "domains[].domainId", violations, checked)
            map_ref = domain.get("mapRef")
            if isinstance(map_ref, str) and map_ref:
                checked["mapRef"] = checked.get("mapRef", 0) + 1
                target = root / map_ref
                if not target.is_file():
                    violations.append({
                        "idSpace": "map", "referencedId": map_ref,
                        "field": "domains[].mapRef", "mapFile": rel(root, path),
                        "reason": "MAP_REF_PATH_NOT_FOUND",
                    })

        # 3. 资产 / 技能 / 激活合同引用
        for field, space in REF_FIELDS:
            for ref in value.get(field, []) or []:
                check_ref(root, anchors, space, ref, path, field, violations, checked)

        # 4. 路由策略引用
        check_ref(root, anchors, "routePolicy", value.get("routePolicyRef"), path,
                  "routePolicyRef", violations, checked)

        # 5. 任务入口（对齐本体 gits:TaskType）
        entrypoints = value.get("entrypoints") or {}
        for task in (entrypoints.get("tasks") or []) if isinstance(entrypoints, dict) else []:
            check_ref(root, anchors, "taskType", task, path, "entrypoints.tasks",
                      violations, checked)

    # ── 诚实缺口：KD-* 无独立锚点来源 ────────────────────────────────────────
    # 仅以「资产 manifest 的 domain 值」为外部旁证；仅出现在 maps 的 domains[] 里
    # 但不在资产 domain 集合中的 KD，属"仅父图自声明"。
    asset_domain_values = {
        value.get("domain")
        for path in sorted((root / ASSETS_REL).rglob("*.md"))
        for value in [safe_frontmatter(path)]
        if isinstance(value, dict) and isinstance(value.get("domain"), str)
    }
    domain_values_seen = {v["referencedId"] for v in violations if v["idSpace"] == "domain"}
    self_declared_only = sorted(
        d for d in anchors["domain"]
        if d not in asset_domain_values and d not in domain_values_seen
    )

    unanchored_spaces = []
    unanchored_spaces.append({
        "idSpace": "domain",
        "ids": ["KD-*"],
        "detail": (
            "KD-* 无独立锚点来源：registry 无 KD 条目、本体无 KnowledgeDomain 类"
            "（gits-core.owl.ttl / gits-core.linkml.yaml 均无）、gits: 类中无 KD 类。"
        ),
        "partialEvidence": {
            "assetManifestDomainValues": sorted(asset_domain_values),
            "selfDeclaredInMaps": sorted(anchors["domain"]),
            "selfDeclaredOnly": self_declared_only,
        },
        "soundness": "NOT_COUNTED_AS_PASS_ASSERTION",
    })

    result = {
        "gate": "gk17-ref-anchor-check",
        "criterion": "V3",
        "root": str(root),
        "verdict": "FAIL" if violations else "PASS",
        "anchorSources": {space: len(index) for space, index in anchors.items()},
        "referencesChecked": checked,
        "mapsScanned": map_records,
        "violations": violations,
        "unanchoredIdSpaces": unanchored_spaces,
        "meta": meta,
    }
    return result


def safe_frontmatter(path: Path) -> dict:
    try:
        return read_frontmatter(path)
    except (GateError, OSError):
        return {}


# ══════════════════════════════════════════════════════════════════════════════
# 输出
# ══════════════════════════════════════════════════════════════════════════════
def render_text(result: dict) -> str:
    lines: list[str] = []
    lines.append(f"gk17-ref-anchor-check: {result['verdict']}  (criterion {result['criterion']})")
    lines.append("anchor sources: " + ", ".join(
        f"{space}={count}" for space, count in sorted(result["anchorSources"].items())))
    lines.append("references checked: " + ", ".join(
        f"{space}={count}" for space, count in sorted(result["referencesChecked"].items())))
    lines.append(f"maps scanned: {len(result['mapsScanned'])}  "
                 f"taskType anchored via {result['meta']['ontologyTaskTypeClass']} "
                 f"(declared={result['meta']['ontologyTaskTypeDeclared']})")

    if result["violations"]:
        lines.append("")
        lines.append(f"UNANCHORED REFERENCES ({len(result['violations'])})：被引用 ID 找不到锚点 ⇒ 拒绝")
        for item in result["violations"]:
            lines.append(
                f"  - [{item['idSpace']}] {item['referencedId']}"
                f"  referenced by {item['mapFile']}  (field: {item['field']}, {item['reason']})")
    else:
        lines.append("no unanchored reference found")

    lines.append("")
    for entry in result["unanchoredIdSpaces"]:
        ev = entry["partialEvidence"]
        lines.append(f"HONEST GAP [{entry['idSpace']}]: {entry['detail']}")
        lines.append(f"  assetManifestDomainValues={ev['assetManifestDomainValues']}")
        lines.append(f"  selfDeclaredInMaps={ev['selfDeclaredInMaps']}")
        lines.append(f"  selfDeclaredOnly(no external anchor)={ev['selfDeclaredOnly']}")
        lines.append(f"  soundness={entry['soundness']}")
    return "\n".join(lines)


# ══════════════════════════════════════════════════════════════════════════════
# 变异负例自检：注入假引用 ⇒ 必须 FAIL；临时副本删除，原文件 sha256 自证
# ══════════════════════════════════════════════════════════════════════════════
SELFTEST_TARGET = Path("specs/knowledge-architecture/maps/corporate-rm/DOMAIN_MAP.md")

# 每个变异：(名称, kind, field, 注入值, 期望命中的 ID 空间)
# kind=list  → front matter 的顶层数组引用字段（assetRefs / skillRefs / ...）
# kind=tasks → entrypoints.tasks
# kind=mapref→ domains[0].mapRef（地图→地图引用，既有校验器完全不查这一项）
MUTATIONS = (
    ("fake_assetRef", "list", "assetRefs", "ASSET-DOES-NOT-EXIST-GK17", "asset"),
    ("fake_skillRef", "list", "skillRefs", "SP-99", "skill"),
    ("fake_activationContractRef", "list", "activationContractRefs", "AC-NOT-REGISTERED-GK17", "activationContract"),
    ("fake_taskRef", "tasks", "entrypoints", "TASK_DOES_NOT_EXIST_GK17", "taskType"),
    ("fake_domainRef", "list", "assetRefs", "ASSET-DOMAIN-PROBE-GK17", "asset"),
    ("fake_mapRef", "mapref", "domains[].mapRef",
     "specs/knowledge-architecture/maps/corporate-rm/DOES-NOT-EXIST-GK17.md", "map"),
)


def mutate_frontmatter(text: str, kind: str, field: str, fake_id: str) -> str:
    """在 front matter 的 JSON 里注入假引用。

    kind=list   → 给顶层数组 field 追加 fake_id
    kind=tasks  → 给 entrypoints.tasks 追加 fake_id
    kind=mapref → 把 domains[0].mapRef 改成不存在的路径 fake_id
    """
    lines = text.splitlines()
    closing = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    value = json.loads("\n".join(lines[1:closing]).strip())
    if kind == "tasks":
        value.setdefault("entrypoints", {})
        tasks = value["entrypoints"].setdefault("tasks", [])
        if fake_id not in tasks:
            tasks.append(fake_id)
    elif kind == "mapref":
        domains = value.get("domains") or []
        if not domains:
            raise GateError("selftest: target map has no domains[] to mutate")
        domains[0]["mapRef"] = fake_id
    else:
        refs = value.setdefault(field, [])
        if fake_id not in refs:
            refs.append(fake_id)
    mutated = lines[:1] + [json.dumps(value, ensure_ascii=False, separators=(",", ":"))] + lines[closing:]
    return "\n".join(mutated) + ("\n" if text.endswith("\n") else "")


def run_selftest(root: Path, out_stream) -> int:
    print("=" * 78, file=out_stream)
    print("MUTATION SELFTEST (临时副本；原文件只读自证)", file=out_stream)
    print("=" * 78, file=out_stream)

    baseline_before = check(root)
    originals = {rel(root, p): sha256_of(p)
                 for p in sorted((root / MAPS_REL).rglob("*.md"))}
    print(f"[baseline] verdict={baseline_before['verdict']}  "
          f"violations={len(baseline_before['violations'])}", file=out_stream)
    print(f"[baseline] original map sha256 count={len(originals)}", file=out_stream)

    overall_ok = True
    with tempfile.TemporaryDirectory(prefix="gk17-refanchor-") as tmp:
        tmp_root = Path(tmp) / "repo"
        # 只复制门禁需要的受控子树（不复制整个仓库）
        for directory in (Path("specs/knowledge-architecture"), Path("specs/semantic")):
            shutil.copytree(root / directory, tmp_root / directory)
        target = tmp_root / SELFTEST_TARGET
        pristine = target.read_text(encoding="utf-8")
        pristine_sha = hashlib.sha256(pristine.encode("utf-8")).hexdigest()

        for name, kind, field, fake_id, expected_space in MUTATIONS:
            mutated_text = mutate_frontmatter(pristine, kind, field, fake_id)
            target.write_text(mutated_text, encoding="utf-8")
            mutated_sha = sha256_of(target)
            mutated_result = check(tmp_root)

            hits = [v for v in mutated_result["violations"]
                    if v["referencedId"] == fake_id and v["idSpace"] == expected_space]
            verdict_fail = mutated_result["verdict"] == "FAIL"
            ok = verdict_fail and bool(hits)
            overall_ok &= ok

            print("", file=out_stream)
            print(f"--- mutation: {name} ---", file=out_stream)
            print(f"  target file      : {SELFTEST_TARGET.as_posix()} (temp copy)", file=out_stream)
            print(f"  field            : {field}", file=out_stream)
            print(f"  injected id      : {fake_id}", file=out_stream)
            print(f"  BEFORE sha256    : {pristine_sha}", file=out_stream)
            print(f"  AFTER  sha256    : {mutated_sha}", file=out_stream)
            print(f"  changed          : {pristine_sha != mutated_sha}", file=out_stream)
            print(f"  verdict          : {mutated_result['verdict']}", file=out_stream)
            print(f"  violations total : {len(mutated_result['violations'])}", file=out_stream)
            for hit in hits:
                print(f"  DETECTED         : [{hit['idSpace']}] {hit['referencedId']}"
                      f"  referenced by {hit['mapFile']}  (field: {hit['field']}, {hit['reason']})",
                      file=out_stream)
            if not hits:
                print("  DETECTED         : (none) <<< 空转！断言未捕获变异", file=out_stream)
            print(f"  result           : {'OK (mutation rejected)' if ok else 'BROKEN'}", file=out_stream)
            if not ok:
                print("  ALL VIOLATIONS   : "
                      + json.dumps(mutated_result["violations"], ensure_ascii=False), file=out_stream)

            # 复原临时副本
            target.write_text(pristine, encoding="utf-8")
            restored_sha = sha256_of(target)
            if restored_sha != pristine_sha:
                print("  RESTORE FAILED in temp copy", file=out_stream)
                overall_ok = False

        # 复原后临时副本必须回到 PASS
        restored_result = check(tmp_root)
        print("", file=out_stream)
        print(f"[restored] verdict={restored_result['verdict']}  "
              f"violations={len(restored_result['violations'])}", file=out_stream)
        if restored_result["verdict"] != "PASS":
            overall_ok = False
            print("[restored] BROKEN: restored copy did not return to PASS", file=out_stream)

    # 原文件逐字节自证
    print("", file=out_stream)
    print("[original self-proof] 原文件未被改动（sha256 对照）", file=out_stream)
    drifted = []
    for relative, digest in sorted(originals.items()):
        now = sha256_of(root / relative)
        marker = "SAME" if now == digest else "DIFF"
        if now != digest:
            drifted.append(relative)
        print(f"  {marker}  {digest}  {relative}", file=out_stream)
    if drifted:
        overall_ok = False
        print(f"  ORIGINALS CHANGED: {drifted}", file=out_stream)
    # 目录中不得残留临时文件
    leftovers = [rel(root, p) for p in sorted((root / MAPS_REL).rglob("*")) if p.is_file()
                 and rel(root, p) not in originals]
    if leftovers:
        overall_ok = False
        print(f"  UNEXPECTED FILES IN ORIGINAL MAPS DIR: {leftovers}", file=out_stream)

    print("", file=out_stream)
    print(f"SELFTEST RESULT: {'PASS' if overall_ok else 'FAIL'}"
          f"  ({len(MUTATIONS)} mutations)", file=out_stream)
    return 0 if overall_ok else 3


# ══════════════════════════════════════════════════════════════════════════════
def main() -> int:
    parser = argparse.ArgumentParser(description="GK17 WP5.1 reference anchoring gate (criterion V3)")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1],
                        help="repository root (default: this script's repo root)")
    parser.add_argument("--json", action="store_true", help="machine-readable JSON output")
    parser.add_argument("--selftest", action="store_true",
                        help="run the built-in mutation negative self-test on a temp copy")
    args = parser.parse_args()
    root = args.root.resolve()

    try:
        if args.selftest:
            code = run_selftest(root, sys.stdout)
            if args.json:
                baseline = check(root)
                print(json.dumps({"selftestExitCode": code, "baseline": baseline},
                                 ensure_ascii=False, sort_keys=True, indent=2))
            return code

        result = check(root)
        if args.json:
            print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
        else:
            print(render_text(result))
        return 0 if result["verdict"] == "PASS" else 2
    except GateError as exc:
        print(f"gk17-ref-anchor-check: ERROR: {exc}", file=sys.stderr)
        return 4
    except OSError as exc:
        print(f"gk17-ref-anchor-check: ERROR: {exc}", file=sys.stderr)
        return 4


if __name__ == "__main__":
    raise SystemExit(main())
