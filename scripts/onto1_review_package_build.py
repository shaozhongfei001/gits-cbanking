#!/usr/bin/env python3
"""ONTO1 独立复核源码包（Owner 复核项 三）

**锚点原则**：以**实际提交**为锚（HEAD/tree SHA/status），**未提交改动单列**，不混入 HEAD 快照。
**零写入证明**：KERT 侧用「指定基准提交 → 当前 HEAD 与工作区」的 **diff** 证明，**不用"近 3 小时无变更"**。

产出目录：`docs/review/ONTO1-PREP-INDEPENDENT-REVIEW-20260921/`
产出压缩包：同名 `.tar.gz` + `.tar.gz.sha256`（**不合并/发布/改正式基线**）

用法：`--build`（默认）/ `--gate` / `--selftest`
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import shutil
import subprocess
import sys
import tarfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
PKG_NAME = "ONTO1-PREP-INDEPENDENT-REVIEW-20260921-R4"   # R4：更正说明文字 + P7 JSON 全字段一致性；v1/R2/R3 冻结留档
PREV_PKG_SHAS = {"v1": "700e2b373eaa393b4141cfe836fea3c5dc7356e4619b2e956db18a4abccf5071",
                 "R2": "83a3c08a3586116c57ba7888b7b6984c4d3680cc712e153bacb22b510169d995",
                 "R3": "d3c43e770387e26f771d46f5316d31f84c57f8e313b4a3249c31ca9bd3c6d1a5"}
PREV_PKG_SHA = PREV_PKG_SHAS["R3"]   # 上一冻结版（本包增量基准）
PKG = ROOT / "docs/review" / PKG_NAME
TARBALL = ROOT / "docs/review" / f"{PKG_NAME}.tar.gz"
KERT = ROOT.parent / "Leibniz-KERT"
KERT_BASELINE = "64f6f873"          # 指定基准提交（见下文 BASELINE_NOTE）
BASELINE_NOTE = ("指定基准：本 Loop 索引依据中记录的 KERT 提交 `64f6f873`（PKG-A1 开工声明所载索引基准；"
                 "GITS 侧对应 `71169042`）。")
EXCLUDE_PATTERNS = ("*.pem", "*.key", "*.p12", "*.jks", ".env", "*.env", ".env.*", ".envrc",
                    "id_rsa", "id_ed25519",
                    "*.password", "*secret*.txt", "*credential*", "node_modules", "__pycache__",
                    ".venv", "venv", ".tox", ".mypy_cache", ".pytest_cache", "*.pyc", "target/",
                    "*.class", "*.jar", "dist/", "build/")

DELIVERABLES = [
    "loops/ONTO1-ontology-split/evidence/prep/contract-split-candidates.json",
    "loops/ONTO1-ontology-split/evidence/prep/ONTO1-CONTRACT-SPLIT-CANDIDATES-DRAFT.md",
    "loops/ONTO1-ontology-split/evidence/prep/construction-plan.json",
    "loops/ONTO1-ontology-split/evidence/prep/ONTO1-CONSTRUCTION-PLAN-DRAFT.md",
    "loops/ONTO1-ontology-split/evidence/prep/32-classes-target-mapping.json",
    "loops/ONTO1-ontology-split/evidence/prep/32-CLASSES-TARGET-MAPPING.md",
    "loops/ONTO1-ontology-split/evidence/prep/l1-skeleton/README.md",
    "loops/ONTO1-ontology-split/evidence/prep/l1-skeleton/LAYOUT.md",
    "loops/ONTO1-ontology-split/evidence/prep/l1-skeleton/l1-term-inventory.json",
    "loops/ONTO1-ontology-split/evidence/prep/l1-skeleton/l1-namespace.json",
    "loops/ONTO1-ontology-split/evidence/prep/L2L3-ADAPTATION-CANDIDATES.md",
    "loops/ONTO1-ontology-split/evidence/prep/consumer-migration-coverage.json",
    "loops/ONTO1-ontology-split/evidence/prep/kert-change-proposal.json",
    "loops/ONTO1-ontology-split/evidence/prep/KERT-CHANGE-PREP.md",
    "loops/ONTO1-ontology-split/evidence/prep/PSO-ICO-INTERIM-AND-CLAUSE-CHECK.md",
    "loops/ONTO1-ontology-split/evidence/prep/WI-A2-CLAUSE-SCOPE-AND-DISPOSAL-TIMING.md",
]
SOURCES = [
    "scripts/onto1_construction_plan.py",
    "scripts/onto1_l1_prep.py",
    "scripts/onto1_class_reconciliation.py",
    "scripts/onto1_review_package_build.py",
    "scripts/onto1_c2_fix_verify.py",
    "scripts/onto1_c2_generator_check.py",
    "scripts/onto1_sim_projection.py",
    "scripts/onto1_log_hygiene.py",
    "scripts/onto1_consumer_scan.py",
    "scripts/onto1_consumer_scan_tests.py",
    "scripts/gk17_prodcard_to_rdf.py",
    "specs/knowledge-architecture/instances/product/projection-config.json",
]
EVIDENCE_FILES = [
    "loops/ONTO1-ontology-split/evidence/obligation-triage.csv",
    "loops/ONTO1-ontology-split/evidence/attribution-45-v2.csv",
    "loops/ONTO1-ontology-split/evidence/consumer-scan-summary.csv",
    "loops/ONTO1-ontology-split/evidence/consumer-scan-hits.jsonl",
    "loops/ONTO1-ontology-split/evidence/product-alias-resolution.json",
    "loops/ONTO1-ontology-split/evidence/board-summary.json",
    "loops/ONTO1-ontology-split/evidence/log-incident-W15TL-16.json",
    "loops/ONTO1-ontology-split/EVIDENCE.json",
    "loops/ONTO1-ontology-split/LOOP.yaml",
    "loops/ONTO1-ontology-split/FAILURES.md",
    "loops/ONTO1-ontology-split/memory/ROLE_BOARD.yaml",
    "loops/ONTO1-ontology-split/memory/TL-DECISIONS-W-1.md",
    "docs/review/ARCH-ONTO-2026-001-rereview-package/04-基线32项映射表.md",
    "docs/architecture/ONTOLOGY-SPLIT-DESIGN-V2.0-REVIEW.md",
    "docs/dispatch/ONTO-SPLIT-本体四层落地执行计划-V2.0.md",
]
GATE_LOGS = ["wi_construction_plan", "wi_construction_plan_selftest", "wi_l1_prep", "wi_l1_prep_selftest",
             "wi_class_reconciliation", "wi_class_reconciliation_selftest",
             "wi_prep_package_build", "wi_prep_package_build_selftest",
             "wi_c2_generator_check", "wi_c2_fix_verify", "wi_d2_sim_projection", "wi_log_hygiene",
             "wi_a4_namespace_collision"]


def sha256(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def git(repo: pathlib.Path, *args: str) -> str:
    try:
        r = subprocess.run(["git", *args], cwd=repo, text=True, capture_output=True, timeout=90)
        return (r.stdout or r.stderr).strip()
    except Exception as exc:  # noqa: BLE001
        return f"<git error: {exc}>"


def anchors() -> dict:
    out: dict = {}
    for name, path in (("gits", ROOT), ("kert", KERT)):
        if not (path / ".git").exists():
            out[name] = {"repo_path": str(path), "exists": False}
            continue
        out[name] = {
            "repo_path": str(path), "exists": True,
            "repo_name": path.name,
            "branch": git(path, "rev-parse", "--abbrev-ref", "HEAD"),
            "head_full": git(path, "rev-parse", "HEAD"),
            "head_short": git(path, "rev-parse", "--short", "HEAD"),
            "tree_sha": git(path, "rev-parse", "HEAD^{tree}"),
            "status_porcelain": git(path, "status", "--porcelain").splitlines(),
        }
    # KERT 零写入证明（基准 → HEAD 与工作区的差异）
    k = out["kert"]
    k["baseline_commit"] = KERT_BASELINE
    k["baseline_note"] = BASELINE_NOTE
    k["diff_baseline_to_head_stat"] = git(KERT, "diff", "--stat", f"{KERT_BASELINE}..HEAD")
    k["diff_baseline_to_worktree_stat"] = git(KERT, "diff", "--stat", KERT_BASELINE)
    k["diff_baseline_to_head_nameonly"] = git(KERT, "diff", "--name-only", f"{KERT_BASELINE}..HEAD").splitlines()
    k["status_short_summary"] = _status_summary(k["status_porcelain"])
    # 独立仓存在性
    out["l1_independent_repo"] = {"exists": False,
                                  "statement": "**不存在**（L1 独立语义契约库尚未建立；仅有候选骨架 `evidence/prep/l1-skeleton/`）"}
    out["integration_contract_repo"] = {"exists": False,
                                        "statement": "**不存在**（L4 集成契约注册表仅登记为候选 `CTR-SEM-005`）"}
    return out


def _status_summary(porcelain: list[str]) -> dict:
    import collections

    return dict(collections.Counter((ln[:2].strip() or "??") for ln in porcelain))


def change_list(anchor: dict) -> dict:
    """本轮交付（**未提交**，工作区）单列；HEAD 快照不含本轮改动。"""
    committed_since_anchor = git(ROOT, "log", "--oneline", "--no-decorate", "-5")
    return {
        "anchor": {"head": anchor["gits"]["head_full"], "head_short": anchor["gits"]["head_short"],
                   "note": "本轮**未产生新提交**；HEAD 快照不含本轮交付。"},
        "uncommitted_this_round": {"files": DELIVERABLES + SOURCES,
                                   "note": "以上为本轮交付件，均**位于工作区（未提交）**，已逐件进 MANIFEST 并附 SHA-256。"},
        "committed_view_last5": committed_since_anchor.splitlines(),
        "separation": "HEAD 快照（旧）与本轮交付（工作区，新）**分开列出**，评审人可据此区分。",
    }


def kert_zero_write_proof(anchor: dict) -> dict:
    """KERT 差异观察（**归因未核实**）：精确同名相对路径比对 + 绝对路径归属检查。"""
    k = anchor["kert"]
    mine = sorted(set(DELIVERABLES + SOURCES + EVIDENCE_FILES))
    head_names = set(k.get("diff_baseline_to_head_nameonly", []))
    worktree_names = {ln[3:].strip() for ln in k.get("status_porcelain", []) if len(ln) > 3}
    same_relpath = sorted(set(mine) & (head_names | worktree_names))
    under_kert = [rel for rel in mine if str((ROOT / rel).resolve()).startswith(str(KERT.resolve()))]
    return {
        "title": "**KERT 差异观察（归因未核实）**",
        "claim": "本轮**未对 KERT 侧执行写操作**（**声明**）；下列差异的归属**未核实**",
        "proof_type": "指定基准提交 → 当前 HEAD 与工作区（`git diff` + `git status`）；**不作时间推断**",
        "baseline_commit": KERT_BASELINE, "baseline_note": BASELINE_NOTE,
        "diff_baseline_to_head": k.get("diff_baseline_to_head_stat") or "（空 = 无差异）",
        "diff_baseline_to_worktree": k.get("diff_baseline_to_worktree_stat") or "（空 = 无差异）",
        "changed_file_counts": {"baseline_to_head": len(head_names), "worktree_status_entries": len(k.get("status_porcelain", []))},
        "status_summary": k.get("status_short_summary", {}),
        "attribution_argument": [
            "本轮全部写操作目标的**绝对路径均在 GITS 仓**（`" + str(ROOT) + "`）之下，**无一条**落在 KERT 仓（`" + str(KERT) + "`）之下；",
            f"本轮产出路径与 KERT 变更清单的**精确同名相对路径交集**：`{same_relpath or '空'}`；",
            "KERT 现有差异（含工作区）为**既有状态**，其归属由 KERT 维护方判定，本包**不作归因断言**。",
        ],
        "overlap_exact_relpath": same_relpath,
        "my_paths_under_kert": under_kert,
        "honest_limit": ("需**本轮开始时的 KERT 工作区哈希快照**或其他可核对操作记录才能闭合归因；本包**不掌握**该快照。"
                         "注：前一版曾以‘路径前缀’比较（会把 KERT 仓内同名目录误判为重叠），本版改为**精确同名**比对。"),
        "reviewer_finding_ref": "F-05：原名『零写入证明』过强；空交集原先只比 HEAD 差异文件名与特定前缀。",
    }


def write_text(path: pathlib.Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build() -> dict:
    if PKG.exists():
        shutil.rmtree(PKG)
    anchor = anchors()
    for rel in DELIVERABLES:
        src = ROOT / rel
        if src.is_file():
            dst = PKG / "DELIVERABLES" / pathlib.Path(rel).name
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
    for rel in SOURCES:
        src = ROOT / rel
        if src.is_file():
            dst = PKG / "SOURCE" / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
    for rel in EVIDENCE_FILES:
        src = ROOT / rel
        if src.is_file():
            dst = PKG / "EVIDENCE" / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
    # 门禁原始日志
    ev = ROOT / "loops/ONTO1-ontology-split/evidence"
    d = json.loads((ROOT / "loops/ONTO1-ontology-split/EVIDENCE.json").read_text(encoding="utf-8"))
    copied_logs = []
    for g in GATE_LOGS:
        f = d["gates"].get(g, {}).get("evidence_file")
        if f and (ROOT / f).is_file():
            dst = PKG / "EVIDENCE/gate-logs" / pathlib.Path(f).name
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / f, dst)
            copied_logs.append({"gate": g, "file": pathlib.Path(f).name, "sha256": sha256(ROOT / f),
                                "status": d["gates"][g]["status"], "exit_code": d["gates"][g]["exit_code"]})

    write_text(PKG / "ANCHORS.json", json.dumps(anchor, ensure_ascii=False, indent=2) + "\n")
    cl = change_list(anchor)
    write_text(PKG / "CHANGE-LIST.json", json.dumps(cl, ensure_ascii=False, indent=2) + "\n")
    zw = kert_zero_write_proof(anchor)
    write_text(PKG / "KERT-DIFF-OBSERVATION.json", json.dumps(zw, ensure_ascii=False, indent=2) + "\n")
    write_text(PKG / "EXCLUSIONS.md", "# 排除项\n\n" + "\n".join(f"- `{p}`" for p in EXCLUDE_PATTERNS) +
               "\n\n说明：源码包保留必要目录结构；**排除**密钥、真实银行客户数据、虚拟环境与缓存。\n"
               "本仓库未包含真实客户数据文件（该判断由文件名与目录模式筛查得出，非内容级扫描）。\n")
    write_text(PKG / "ANCHORS.md", _anchors_md(anchor, cl, zw))
    write_text(PKG / "RESULTS.md", _results_md(d))
    write_text(PKG / "GATE-DELTA.md", _gate_delta_md(d))
    write_text(PKG / "REVIEW-RESPONSE-R4.md", _review_response_md())
    write_text(PKG / "MUTATION-RECORDS.md", _mutation_records_md())
    write_text(PKG / "README-REPRO.md", _readme_repro(anchor, cl, zw, copied_logs))

    # MANIFEST（逐文件 SHA-256）
    lines = []
    for p in sorted(PKG.rglob("*")):
        if p.is_file():
            lines.append(f"{sha256(p)}  {p.relative_to(PKG).as_posix()}")
    write_text(PKG / "MANIFEST.sha256", "\n".join(lines) + "\n")

    with tarfile.open(TARBALL, "w:gz") as tf:
        tf.add(PKG, arcname=PKG_NAME)
    digest = sha256(TARBALL)
    (TARBALL.parent / f"{TARBALL.name}.sha256").write_text(f"{digest}  {TARBALL.name}\n", encoding="utf-8")
    print(f"包目录：{PKG.relative_to(ROOT)}（{len(lines)} 个文件）")
    print(f"压缩包：{TARBALL.relative_to(ROOT)}")
    print(f"包 SHA-256：{digest}")
    return {"files": len(lines), "tarball": str(TARBALL), "sha256": digest}


def _anchors_md(a: dict, cl: dict, zw: dict) -> str:
    g, k = a["gits"], a["kert"]
    L = ["# 锚点（实际提交）", "",
         "## GITS", f"- 仓库：`{g['repo_name']}`（`{g['repo_path']}`）",
         f"- 分支：`{g['branch']}`｜HEAD：`{g['head_full']}`", f"- tree SHA：`{g['tree_sha']}`",
         f"- `git status --porcelain` 条目：**{len(g['status_porcelain'])}**（分类 {dict(_status_summary(g['status_porcelain']))}）",
         "", "## KERT", f"- 仓库：`{k['repo_name']}`（`{k['repo_path']}`）",
         f"- 分支：`{k['branch']}`｜HEAD：`{k['head_full']}`", f"- tree SHA：`{k['tree_sha']}`",
         f"- `git status --porcelain` 条目：**{len(k['status_porcelain'])}**", "",
         "## 独立仓存在性",
         f"- L1 独立语义契约库：{a['l1_independent_repo']['statement']}",
         f"- 集成契约仓：{a['integration_contract_repo']['statement']}", "",
         "## KERT 零写入证明（基准 → HEAD 与工作区）", f"- 基准提交：`{zw['baseline_commit']}`",
         f"- 基准 → HEAD：{zw['diff_baseline_to_head'] or '（空）'}",
         f"- 基准 → 工作区：{zw['diff_baseline_to_worktree'] or '（空）'}",
         f"- 与本轮产出路径交集：`{zw['overlap_exact_relpath'] or '空'}`", "",
         "## 变更归属", f"- {cl['anchor']['note']}",
         f"- 本轮交付：{len(cl['uncommitted_this_round']['files'])} 件（**工作区未提交**，见 `CHANGE-LIST.json`）"]
    return "\n".join(L) + "\n"


def _results_md(d: dict) -> str:
    b = d["board_expression"]
    return f"""# 结果口径（三项分开陈述）

## 1. 作者自检通过（author self-check passed）
- 门禁（作者运行）：**PASS={b['PASS']} · FAIL={b['FAIL']} · PENDING_EXTERNAL_AUTHORITY={b['PENDING_EXTERNAL_AUTHORITY']}**（共 {b['total']}）
{_tool_rows_md(d)}
- **声明**：以上均为**作者自检**，不构成独立复核结论。

## 2. 独立复核待做（independent review pending）
- `independent_qa` = **{d['independent_qa']['status']}** / actor = **{d['independent_qa']['actor']}**（**无人代签**）。
- 本包用途：供**项目 Owner 的架构顾问**独立复核两项疑点（L1 32/8 类、条款作用域）与证据可复现性。
- 未做：未由第三方复跑脚本、未由委员会签署、未做 QA_PASS。

## 3. 正式分仓未完成（formal split NOT done）
- **拆分施工执行量 = 0 / 691**（真义务 691：W2_SPLIT 291 · W3_CONSUMER_SWITCH 381 · W3_KERT_ASSETS 19）。
- `wave_0..3` 仍 `BLOCKED`；`PRODUCTION_ACTIVATION` = **BLOCKED**；C-2 = CLOSED（仅命名空间兼容项）。
- 已完成者仅为 **Wave -1 就绪**（清单/门禁/候选/骨架/扫描）与 **SIM 范围整改**。
- **门禁通过数 ≠ 实施完成度**：请勿以 PASS 数替代上述完成度判断。

## 4. 计数单位与重叠性（供评审人复算）

| 计数 | 单位 | 说明 |
|---|---|---|
| **691** | 义务**条数**（`obligation-triage.csv` 中 `disposition=TRUE_OBLIGATION`） | 每条含 `repo,path,tier,signal,rationale,evidence` |
| **499** | **唯一 (repo, path) 文件数** | 由 691 条义务**去重文件**得到 ⇒ 691 是"条"口径，499 是"文件"口径 |
| **364** | 引用**项**数（`RESOLVES_LOCAL_OR_PROVISIONAL_CURIE 332` + `…_IRI 32`） | 单位 = **「文件 × 去重后的引用形式」对**，跨文件累加；**不是唯一 IRI 数** |
| **125** | 同上（`KNOWN_EXTERNAL_CURIE 89` + `KNOWN_EXTERNAL_IRI 36`） | 通用词汇，不需迁移 |
| **64** | 同上（`OTHER_PREFIX_CURIE`） | 未知前缀；**含非 RDF 语境误匹配**，需逐条真伪判定 |
| **34** | 同上（`UNMAPPED_APP_IRI`） | 未映射应用 IRI，迁移期逐条裁决 |
| **325** | **导入语句条数**（`CODE_IMPORT_ONTOLOGY_PKG`） | Java `import com.gien.gits.ontology.*`；**非包名去重** |

**重叠性**：单一引用按判定顺序**只落一类**（EXTERNAL → LOCAL → UNMAPPED；CURIE: local → external → other）⇒ 六类**互不重叠**。
唯一例外：**Java 导入**与 CURIE/IRI 是**不同维度**，同一文件可同时计数（报告时请分开看）。
复算命令：`python3 scripts/onto1_l1_prep.py --migration`（输出 `evidence/prep/consumer-migration-coverage.json`）。
"""


def _readme_repro(a: dict, cl: dict, zw: dict, logs: list[dict]) -> str:
    g, k = a["gits"], a["kert"]
    log_rows = "\n".join(f"| `{x['gate']}` | {x['status']} | {x['exit_code']} | `{x['file']}` |" for x in logs)
    return f"""# README-REPRO —— 独立复核指南

**目标**：没有本地仓库的评审人，也能核对本轮**关键结论**。

## 0. 包内结构
```
{PKG_NAME}/
├── README-REPRO.md            # 本文件
├── ANCHORS.md / ANCHORS.json  # 仓库锚点（分支/HEAD/tree SHA/status）+ 零写入证明
├── CHANGE-LIST.json           # 锚点 → 本轮交付；未提交改动**单列**
├── KERT-DIFF-OBSERVATION.json # 基准提交 → HEAD 与工作区的 diff 证据
├── RESULTS.md                 # 结果口径三项 + 计数单位与重叠性
├── EXCLUSIONS.md              # 排除项
├── DELIVERABLES/              # 本轮五项交付（含逐类核清、条款核清）
├── SOURCE/                    # 生成脚本与配置（可直接运行）
├── EVIDENCE/                  # 原始证据文件 + gate-logs/（门禁原始日志）
└── MANIFEST.sha256            # 逐文件 SHA-256
```

## 1. 锚点（{PKG_NAME}）
- GITS `{g['repo_name']}`：分支 `{g['branch']}`｜HEAD `{g['head_full']}`｜tree `{g['tree_sha']}`
- KERT `{k['repo_name']}`：分支 `{k['branch']}`｜HEAD `{k['head_full']}`｜tree `{k['tree_sha']}`
- **本轮未产生新提交**：交付件均为工作区文件，已逐件进 `MANIFEST.sha256`。

## 2. 复核两项疑点（无需本地仓库）

### 疑点一：L1 是 8 类还是 32 类
1. 打开 `DELIVERABLES/32-classes-target-mapping.json`：
   - `classes_32` = 基线**来源盘点**（32 行，逐行含 `existing_iri / target_layer / action / tbox_owner / mapping_45_item`）；
   - `l1_candidate_model` = **L1 候选 8 类**（每类含 `design_source / baseline_successor_of / mapping_type`）。
2. 打开 `EVIDENCE/docs/architecture/ONTOLOGY-SPLIT-DESIGN-V2.0-REVIEW.md` §4.2，逐项比对 8 类名单。
3. 结论成立条件：`l1_candidate_model` 的**集合等于**设计 §4.2 的 8 类（脚本 `--gate` 的 R3 断言）。
4. 另见 `DELIVERABLES/l1-term-inventory.json` 的 `artifact_role = SOURCE_INVENTORY`：**来源盘点 ≠ L1 候选**。

### 疑点二：条款作用域
1. 打开 `DELIVERABLES/WI-A2-CLAUSE-SCOPE-AND-DISPOSAL-TIMING.md`：含**原文出处**（执行计划 §1 WI-A2 行与 §0 阶段表）与逐动作判定表。
2. 打开 `EVIDENCE/loops/ONTO1-ontology-split/evidence/consumer-scan-summary.csv`：
   `disposition` 分布含 `FOLLOW_MIGRATION` / `HOMONYM_REQUIRES_SOURCE_CHECK` / `CONTROL_PLANE_REQUIRED`
   ⇒ 处置表**未达 100%**（推翻"处置率 100%"的说法，该说法已在 FAILURES `W15TL-17` 记为我方口径错误）。
3. 结论：条款约束 **Wave 2/3 开工**；**不约束** 需求分析 / SIM 开发。

## 3. 复现命令（在有仓库的环境中）
```bash
python3 scripts/onto1_class_reconciliation.py --gate      # 32 类 / L1 八类 / 计数算术
python3 scripts/onto1_construction_plan.py --gate         # 691 项批次计划
python3 scripts/onto1_l1_prep.py --gate                   # L1 骨架不变式
python3 scripts/onto1_l1_prep.py --migration              # 迁移覆盖率（499/364/125/64/34/325）
python3 scripts/onto1_c2_generator_check.py --gate        # 生成器根因（C-2）
python3 scripts/onto1_review_package_build.py --gate      # 本包自检
```
每条命令的**期望输出**见 `RESULTS.md` 与 `EVIDENCE/gate-logs/` 中的原始日志。

## 4. 原始证据与自检结果
| 门禁 | 状态 | exit | 原始日志 |
|---|---|---|---|
{log_rows}

## 5. KERT 差异观察（**归因未核实**）
- 基准提交：`{zw['baseline_commit']}`（{zw['baseline_note']}）
- 基准 → HEAD：{zw['diff_baseline_to_head'] or '（空）'}
- 基准 → 工作区：{zw['diff_baseline_to_worktree'] or '（空）'}
- 与本轮产出路径**交集**：`{zw['overlap_exact_relpath'] or '空'}`
- **诚实限度**：{zw['honest_limit']}

## 6. 独立仓存在性
- L1 独立语义契约库：{a['l1_independent_repo']['statement']}
- 集成契约仓：{a['integration_contract_repo']['statement']}

## 7. 非声明
本包**不构成**委员批准 / `QA_PASS` / 正式基线生效 / 生产可用；**未**合并、发布或改动正式基线；
C-2 关闭仅指**命名空间兼容项**，不代表分仓重构完成（见 `RESULTS.md` §3）。
"""


def cmd_gate() -> int:
    ok = True
    rows = []
    for name, cond in (
        ("P1 包目录与压缩包存在", PKG.is_dir() and TARBALL.is_file()),
        ("P2 MANIFEST 覆盖包内全部文件", _manifest_consistent()[0]),
        ("P3 无排除模式文件进入包", not _has_excluded()[1]),
        ("P4 KERT 差异观察：与本轮产出**精确同名**交集为空（归因未核实）",
         not kert_zero_write_proof(anchors())["overlap_exact_relpath"]
         and not kert_zero_write_proof(anchors())["my_paths_under_kert"]),
        ("P5 结果口径三项齐备", all(k in (PKG / "RESULTS.md").read_text(encoding="utf-8")
                                    for k in ("作者自检通过", "独立复核待做", "正式分仓未完成"))),
        ("P6 README-REPRO 存在且含复现命令", (PKG / "README-REPRO.md").is_file()
         and "onto1_class_reconciliation.py --gate" in (PKG / "README-REPRO.md").read_text(encoding="utf-8")),
    ):
        rows.append((name, cond))
        ok = ok and cond
    for n, c in rows:
        print(f"{'PASS' if c else 'FAIL'} [{n}]")
    print(f"复核包：{'PASS' if ok else 'FAIL'}（{sum(1 for _, c in rows if c)}/{len(rows)}）")
    return 0 if ok else 2


def _manifest_consistent() -> tuple[bool, list[str]]:
    bad = []
    for line in (PKG / "MANIFEST.sha256").read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        h, rel = line.split("  ", 1)
        p = PKG / rel
        if not p.is_file() or sha256(p) != h:
            bad.append(rel)
    return (not bad, bad)


def _has_excluded() -> tuple[bool, list[str]]:
    """排除项检查：文件名 glob（fnmatch）+ 目录名包含判定（D-14 口径：先判后动）。"""
    import fnmatch

    dir_pats = [p.strip("*/") for p in EXCLUDE_PATTERNS if p.startswith(("node_modules", "__pycache__",
                ".venv", "venv", ".tox", ".mypy_cache", ".pytest_cache", "target", "dist", "build"))]
    hits = []
    for p in PKG.rglob("*"):
        rel = p.relative_to(PKG).as_posix()
        if any(d and f"/{d}/" in f"/{rel}" for d in dir_pats):
            hits.append(rel); continue
        if any(fnmatch.fnmatch(p.name, pat) for pat in EXCLUDE_PATTERNS):
            hits.append(rel)
    return (bool(hits), hits)


def cmd_selftest() -> int:
    fails = 0
    # M1 注入一个"密钥"文件 ⇒ 排除检查必须发现
    fake = PKG / "SOURCE/.env"
    fake.write_text("SECRET=1", encoding="utf-8")
    hit = _has_excluded()[0]
    print(f"{'PASS' if hit else 'FAIL'} [M1 注入 .env ⇒ 应被排除检查发现] = {hit}")
    fails += 0 if hit else 1
    fake.unlink()
    # M2 篡改一个文件 ⇒ MANIFEST 校验必须失败
    victim = PKG / "RESULTS.md"
    orig = victim.read_text(encoding="utf-8")
    victim.write_text(orig + "\n篡改", encoding="utf-8")
    bad = _manifest_consistent()[1]
    ok2 = bool(bad)
    print(f"{'PASS' if ok2 else 'FAIL'} [M2 篡改文件 ⇒ MANIFEST 校验失败] = {ok2}")
    fails += 0 if ok2 else 1
    victim.write_text(orig, encoding="utf-8")
    ok3 = _manifest_consistent()[0]
    print(f"{'PASS' if ok3 else 'FAIL'} [M3 还原 ⇒ MANIFEST 一致] = {ok3}")
    fails += 0 if ok3 else 1
    print(f"--selftest {'PASS' if fails == 0 else 'FAIL'}（{3 - fails}/3）")
    return 0 if fails == 0 else 2


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--gate", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ns = ap.parse_args()
    if ns.selftest:
        return cmd_selftest()
    if ns.gate:
        return cmd_gate()
    build()
    return 0


def _tool_rows_md(d: dict) -> str:
    """逐工具读数**取自登记日志**（避免硬编码漂移）。"""
    import re as _re

    pairs = [("onto1_class_reconciliation", "wi_class_reconciliation", "wi_class_reconciliation_selftest"),
             ("onto1_construction_plan", "wi_construction_plan", "wi_construction_plan_selftest"),
             ("onto1_l1_prep", "wi_l1_prep", "wi_l1_prep_selftest"),
             ("onto1_c2_generator_check", "wi_c2_generator_check", "wi_c2_generator_check_selftest"),
             ("onto1_c2_fix_verify", "wi_c2_fix_verify", "wi_c2_fix_verify_selftest"),
             ("onto1_sim_projection", "wi_d2_sim_projection", "wi_d2_sim_projection_selftest"),
             ("onto1_log_hygiene", "wi_log_hygiene", "wi_log_hygiene_selftest"),
             ("onto1_review_package_build", "wi_prep_package_build", "wi_prep_package_build_selftest")]

    def num(gate: str) -> str:
        v = d["gates"].get(gate) or {}
        f = v.get("evidence_file")
        if not f or not (ROOT / f).is_file():
            return "（日志缺失）"
        txt = (ROOT / f).read_text(encoding="utf-8")
        hits = _re.findall(r"(\d+)/(\d+)", txt)
        if hits:
            return f"{hits[-1][0]}/{hits[-1][1]}"
        np_, nf_ = len(_re.findall(r"(?m)^PASS \[", txt)), len(_re.findall(r"(?m)^FAIL \[", txt))
        return f"{np_}/{np_ + nf_}" if (np_ + nf_) else "n/a（无分数式输出）"

    out = ["- 逐工具读数（**从登记日志提取**，非硬编码）："]
    for tool, g, s in pairs:
        out.append(f"  - `{tool}`：`--gate {num(g)}`（{d['gates'].get(g, {}).get('status', 'n/a')}）"
                   f" · `--selftest {num(s)}`（{d['gates'].get(s, {}).get('status', 'n/a')}）")
    out.append("  - **声明**：以上为**作者自检**；`independent_qa` 仍为 pending，**不得**表述为已独立复跑。")
    return "\n".join(out)


def _gate_delta_md(d: dict) -> str:
    import sys as _sys

    names = [g for g in ("wi_class_reconciliation", "wi_class_reconciliation_selftest",
                         "wi_construction_plan", "wi_construction_plan_selftest",
                         "wi_l1_prep", "wi_l1_prep_selftest",
                         "wi_prep_package_build", "wi_prep_package_build_selftest") if g in d["gates"]]
    L = ["# 门禁增量（自旧包以来，F-04）", "",
         f"- 上一冻结版：`ONTO1-PREP-INDEPENDENT-REVIEW-20260921-R3`（SHA-256 `{PREV_PKG_SHA}`，**冻结留档**）",
         f"- 更早版本（冻结留档）：v1 `{PREV_PKG_SHAS['v1'][:16]}…` · R2 `{PREV_PKG_SHAS['R2'][:16]}…`",
         f"- 本包（R4）与看板**同一快照**：PASS={d['board_expression']['PASS']} · FAIL={d['board_expression']['FAIL']} · "
         f"PENDING_EXTERNAL_AUTHORITY={d['board_expression']['PENDING_EXTERNAL_AUTHORITY']} · 共 {d['board_expression']['total']}",
         "", "| 新增门禁 | 状态 | exit | 原始日志 |", "|---|---|---|---|"]
    for g in names:
        v = d["gates"][g]
        L.append(f"| `{g}` | {v['status']} | {v['exit_code']} | `{pathlib.Path(v['evidence_file']).name}` |")
    L += ["", "## 本轮相对 R3 的变化（**无新增门禁**，仅精度与文字）", "",
          "| 项 | R3 | R4 |", "|---|---|---|",
          "| `onto1_construction_plan --gate` | 7/7 | 7/7（判定字段扩展：见下） |",
          "| `onto1_construction_plan --selftest` | 8/8 | **11/11**（新增 M6 分类篡改 / M7 occurrences 篡改 / M8 明细之和） |",
          "| `RESULTS.md` 逐工具读数 | 硬编码（施工计划写 6/6、自检 3/3） | **从登记日志提取**（实际 7/7、11/11） |",
          "| 说明文字 | 残留「R2 包/快照」 | 已更正为「R3 冻结版 / R4 本包」 |", "",
          f"**运行环境**：Python {_sys.version.split()[0]} · cwd `{ROOT}` · 运行者 tech_lead（**作者自检**）", "",
          "> 看板计数 48 PASS / 0 FAIL / 1 PENDING（共 49）与上一冻结版一致；本包按**同一快照**重出，不改变任何门禁结论。"]
    return "\n".join(L) + "\n"


def _review_response_md() -> str:
    return """# 独立架构复核处理回执（F-01~F-05）

复核来源：`docs/dd/ONTO1_准备包独立架构复核_20260921.md`（架构顾问复核，**不代替独立 QA**）。

| 发现 | 处理 | 证据 |
|---|---|---|
| **F-01** 制品保留「处置率 100%」 | ✅ 生成源改**数据驱动**（实测未闭环聚合行 **412** 内嵌禁止句）；新增 **P7**：未闭环非零却声称 100% ⇒ FAIL | `SOURCE/scripts/onto1_construction_plan.py` · `DELIVERABLES/ONTO1-CONSTRUCTION-PLAN-DRAFT.md` |
| **F-02** 自检只比脚本常量 | ✅ 改为**解析受控源文档**（设计 §4.2 / 映射表 / 归属矩阵）；候选由数据推导；**设计表/映射表/归属矩阵各一处真实变异**均被拦下（M1/M2/M3） | `SOURCE/scripts/onto1_class_reconciliation.py` · `DELIVERABLES/32-classes-target-mapping.json` |
| **F-03** 入口引 V1.2 且称 32 类为 L1 候选 | ✅ 改引 **V2.0 §4.2**；入口明示「来源盘点(32) ≠ L1 候选(8)」 | `DELIVERABLES/README.md` · `l1-term-inventory.json` |
| **F-04** 48 项 vs 封包 45 项 | ✅ 同快照重封（**R2 → R3 → 本 R4**，逐版冻结留档）；新增门禁逐条列名/日志/退出码/环境 | 本文件 · `GATE-DELTA.md` · `RESULTS.md` |
| **W-1**（R3 复核第 1 项）R3 说明文字与实测不符 | ✅ `RESULTS.md` 的逐工具读数改为**从登记日志提取**（施工计划实为 `--gate 7/7`、`--selftest 11/11`）；`GATE-DELTA.md` / 本回执 / 看板中的旧版字样已更正 | `RESULTS.md` · `GATE-DELTA.md` · `board-summary.json` |
| **W-2**（R3 复核第 2 项）P7 JSON 只比对两个字段 | ✅ 扩展为**全字段一致性**：三类未闭环明细、明细之和、`unclosed_occurrences`、`aggregated_rows`、`occurrences_total`（**不写死 412**）；新增必败反例 M6（总数不变但分类被篡改）/ M7（occurrences 篡改）/ M8（明细之和≠总数） | `SOURCE/scripts/onto1_construction_plan.py` · `MUTATION-RECORDS.md` |
| **F-05** 扫描与 KERT 归因不可独立确认 | ✅ 入包**原始** `consumer-scan-hits.jsonl` + 扫描脚本 + 双仓边界；「零写入证明」→ **KERT 差异观察（归因未核实）**，纳入工作区路径并声明归因限度 | `EVIDENCE/.../consumer-scan-hits.jsonl` · `KERT-DIFF-OBSERVATION.json` |

## 评审边界（F-05）
1. 入包原始扫描数据 `consumer-scan-hits.jsonl`（**26,690** 命中行）；**扫描覆盖率**与**逐条处置完整性**仍需在有双仓源码的环境复算。
2. KERT 归因**未核实**：需**本轮开始时的 KERT 工作区哈希快照**方可闭合；本包不作归因断言。

## 非声明
不构成 QA_PASS / 委员会批准 / 正式根域 / 生产激活；**Wave 2 仍禁止开工**（WI-A2 处置未达 100%）。
"""




def _mutation_records_md() -> str:
    """**真实运行**三个变异自检并嵌入原始输出（供独立复核人核对变异是否真被捕获）。"""
    import subprocess

    cases = [("L1/设计源变异", "scripts/onto1_class_reconciliation.py"),
             ("P7 处置口径变异", "scripts/onto1_construction_plan.py"),
             ("L1 骨架不变式变异", "scripts/onto1_l1_prep.py")]
    L = ["# 变异记录（真实运行输出，未人工誊写）", "",
         "> **命名提示**：脚本内的检查标签 `R1`~`R7`/`M1`~`M8` 与**包版本号**（R2/R3/R4）**无关**，避免误读。", "",
         "命令：`python3 <脚本> --selftest`（每条的首行即退出码）", ""]
    for title, script in cases:
        r = subprocess.run([sys.executable, script, "--selftest"], cwd=ROOT, text=True, capture_output=True)
        L += [f"## {title} —— `{script}`（exit={r.returncode}）", "", "```",
              (r.stdout or r.stderr).strip(), "```", ""]
    return "\n".join(L) + "\n"

if __name__ == "__main__":
    sys.exit(main())
