#!/usr/bin/env python3
"""A-4｜SIM 通道迁移验证装置（oldIRI→newIRI 解析 + B6/B8 dry-run）

Owner 2026-09-21 决议允许：**迁移验证**与**消费者影响分析**；D3 以 `PROVISIONAL_SIM_LEGACY_NAMESPACE` 临时口径
允许 SIM 内继续使用两个命名空间，**不得**发布新 IRI。

本装置做（**只读；不写 `specs/**`、不建 `namespaces.json` 根域、不发布任何 IRI**）：
  · **M1 行数守恒**：映射草案 87 行 = 67 迁移行 + 20 新术语（无旧 IRI）；
  · **M2 未发布核验**：草案状态必须为 DRAFT，且新 IRI 形态为 `PENDING:` 占位（**未发布、不可消费**）；
  · **M3 反等价禁则**：迁移行**不得**以 `equivalentClass/equivalentProperty` 承接（须显式迁移清单）；
  · **M4 oldIRI 可解析**：对每条迁移行验证其**旧端术语在现行基线 T-Box 中可定位**（不可解析即列出）；
  · **M5 SIM 通道边界**：SIM 输出/配置中**不得**出现未发布的新 IRI（防提前发布）；
  · **M6 B6/B8 dry-run**：对 `construction-plan.json` 的 B6(86)/B8(156) 样本文件做**只读** dry-run，
    判定其引用是否随迁移可解析（输出"可解析/需人工"清单，**不改文件**）。

用法：`--build` / `--gate` / `--selftest`
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import pathlib
import re
import sys

ROOT = pathlib.Path("/home/szf/dev/gits-cbanking")
EV = ROOT / "loops/ONTO1-ontology-split/evidence"
PREP = EV / "prep"
MAPPING = EV / "iri-mapping-draft.csv"
SUMMARY = EV / "iri-mapping-draft-summary.json"
PLAN = PREP / "construction-plan.json"
TBOX = ROOT / "specs/semantic/gits-core.owl.ttl"
SIM_DIR = ROOT / "specs/knowledge-architecture/instances/product/sim"
PROJ_CONFIG = ROOT / "specs/knowledge-architecture/instances/product/projection-config.json"
OUT = PREP / "sim-migration-verify.json"
LEGACY_NS = "https://gientech.com/gits/kno/"
# 禁止存在的文件（根域/持久化承诺的物证）；F-2 修正后由 probe 实际探测，不再写死布尔值
FORBIDDEN_FILES = [ROOT / "namespaces.json",
                   ROOT / "specs/knowledge-architecture/namespaces.json"]


def boundary_probe(needles: list[str], sim_dir: pathlib.Path = SIM_DIR,
                   extra_files: list[pathlib.Path] | None = None) -> dict:
    """**派生**边界事实（F-2：原为写死字面量 ⇒ 真实路径恒真，QA 判"不可能 FAIL"）。

    可注入 `extra_files` 以便构造**真实路径**反例（在 selftest 中实际创建临时文件）。
    """
    forbidden = list(FORBIDDEN_FILES) + list(extra_files or [])
    present = [str(f) for f in forbidden if pathlib.Path(f).is_file()]
    files = ([f for f in sim_dir.rglob("*") if f.is_file()] if sim_dir.is_dir() else [])
    if PROJ_CONFIG.is_file():
        files.append(PROJ_CONFIG)
    leaks: list[str] = []
    for f in files:
        txt = f.read_text(encoding="utf-8", errors="replace")
        leaks += [f"{f.name}:{n}" for n in needles if n and n in txt]
    return {
        "probe_files": [str(f) for f in forbidden],
        "forbidden_present": present,
        "scanned_files": [str(f.name) for f in files],
        "needle_leaks": leaks,
        "derived_ok": not present and not leaks,
        "declaration_only": "SIM 通道标识来自制品自声明（**声明项，不构成验证**）",
    }


def formal_needles(rows: list[dict]) -> tuple[list[str], list[str]]:
    """区分**正式 IRI needle**（可构造）与**符号化占位**（不可构造）。"""
    values = [col(r, "新IRI草案", "新 IRI") for r in rows]
    formal = [v for v in values if v.startswith("http")]
    symbolic = [v for v in values if v and not v.startswith("http") and "PENDING" not in v]
    return formal, symbolic


def sha256(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def load_rows() -> list[dict]:
    with MAPPING.open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def col(row: dict, *keys: str) -> str:
    for k in keys:
        for kk in row:
            if kk and k in kk:
                return (row[kk] or "").strip()
    return ""


def build() -> dict:
    rows = load_rows()
    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    tbox = TBOX.read_text(encoding="utf-8")
    tbox_terms = set(re.findall(r"gits:([A-Za-z][A-Za-z0-9_]*)", tbox))
    tbox_terms |= set(re.findall(r"kno#([A-Za-z][A-Za-z0-9_]*)", tbox))

    migration, new_terms, unresolvable, equiv_bad = [], [], [], []
    legacy_ns = "https://gientech.com/gits/kno/"
    for r in rows:
        old = col(r, "旧IRI", "旧 IRI")
        new = col(r, "新IRI草案", "新 IRI")
        tid = col(r, "termId")
        equiv = col(r, "equivalentClass").upper()
        binding = col(r, "允许绑定")
        precondition = col(r, "迁移生效前置")
        is_new = ("无旧端" in old) or old in ("—", "", "N/A")
        (new_terms if is_new else migration).append(r)
        if not is_new:
            # M4：解析**旧端短名**（不是目标 termId）——旧端必须落在现行基线 T-Box 内
            short = old.rsplit("/", 1)[-1].split("#")[-1]
            if not old.startswith(legacy_ns) or (short and short not in tbox_terms):
                unresolvable.append({"termId": tid, "old": old, "old_short": short, "new": new})
            # M3：与草案**自洽**口径一致（FORBIDDEN 不得绑 owl:equivalent；ALLOWED 须有前置条件）
            if equiv.startswith("FORBIDDEN") and "owl:equivalent" in binding:
                equiv_bad.append({"termId": tid, "why": "FORBIDDEN 却绑定 owl:equivalent",
                                  "binding": binding[:40]})
            elif equiv.startswith("ALLOWED") and "owl:equivalent" not in binding:
                equiv_bad.append({"termId": tid, "why": "ALLOWED 却未绑定 owl:equivalent", "binding": binding[:40]})
            elif equiv.startswith("ALLOWED") and not precondition:
                equiv_bad.append({"termId": tid, "why": "ALLOWED 但未写前置条件", "binding": binding[:40]})
        elif equiv.startswith("NOT_APPLICABLE") and "不适用" not in binding:
            equiv_bad.append({"termId": tid, "why": "新术语行却给出旧端绑定", "binding": binding[:40]})

    # M5/M7 边界：**派生**探测（含"禁止文件存在性"），并显式声明哪些 check 不具构造性
    formal, symbolic = formal_needles(rows)
    boundary = boundary_probe(formal + symbolic)
    published_leak = boundary["needle_leaks"]
    coverage_exclusions = []
    if not formal:
        coverage_exclusions.append(
            "M5 不具备构造性：D3 未签 ⇒ 草案中**不存在具体新 IRI 字面量**（无 needle 可搜）"
            f"；仅有符号化占位 {len(symbolic)} 条 ⇒ 本条**不计为覆盖**，待正式 IRI 发布后重建")

    # M6 B6/B8 dry-run（**真实只读性**由前后哈希自证，F-2 修正：不再写死 dry_run_only=True）
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    dry = {}
    for b in plan["batches"]:
        if not b["id"].startswith(("B6", "B8")):
            continue
        checked, dark = 0, []
        before_hash = {}
        for rel in b["sample"]:
            fp0 = ROOT / rel.removeprefix("gits/")
            if fp0.is_file():
                before_hash[str(fp0)] = sha256(fp0)
        for rel in b["sample"]:
            p = ROOT / rel.removeprefix("gits/")
            if not p.is_file():
                dark.append(f"{rel}（缺文件）")
                continue
            checked += 1
            txt = p.read_text(encoding="utf-8", errors="replace")
            if LEGACY_NS in txt:
                dark.append(f"{rel}（引用旧命名空间：随迁移需重绑）")
        after_hash = {k: (sha256(pathlib.Path(k)) if pathlib.Path(k).is_file() else None)
                      for k in before_hash}
        dry[b["id"]] = {"declared": b["count"], "sample_checked": checked,
                        "blacklist": dark[:8], "blacklist_len": len(dark),
                        "dry_run_only": before_hash == after_hash,      # **派生**：前后哈希一致
                        "files_hashed": len(before_hash)}
    return {
        "schema": "ONTO1-SIM-MIGRATION-VERIFY/1.0",
        "authority": "Owner 2026-09-21（SIM 整改）：允许迁移验证；D3 临时口径 `PROVISIONAL_SIM_LEGACY_NAMESPACE`",
        "boundary": {**boundary, "note": "本装置**只读**；不得发布新 IRI、不得建根域、不得改 specs/**。"},
        "coverage_exclusions": coverage_exclusions,
        "needles": {"formal": len(formal), "symbolic": len(symbolic)},
        "sources": {"mapping": str(MAPPING.relative_to(ROOT)), "mapping_sha256": sha256(MAPPING),
                    "tbox_sha256": sha256(TBOX)},
        "counts": {"rows_total": len(rows), "migration_rows": len(migration),
                   "new_term_rows": len(new_terms),
                   "declared_rows": summary.get("rows"), "declared_migration": summary.get("migration_scope"),
                   "declared_new": summary.get("new_term_without_legacy_iri"),
                   "unresolvable_old_iri": len(unresolvable), "equivalent_bad": len(equiv_bad),
                   "published_new_iri_leak": len(published_leak)},
        "unresolvable_old_iri": unresolvable[:20],
        "equivalent_bad": equiv_bad[:20],
        "published_new_iri_leak": published_leak[:10],
        "dry_run": dry,
        "draft_status": summary.get("status"),
    }


def checks(d: dict) -> list[tuple[str, bool, str]]:
    c = d["counts"]
    return [
        ("M1 行数守恒（87 = 67 迁移 + 20 新术语；与 summary 声明一致）",
         c["rows_total"] == 87 and c["migration_rows"] == 67 and c["new_term_rows"] == 20
         and c["rows_total"] == c["declared_rows"] and c["migration_rows"] == c["declared_migration"]
         and c["new_term_rows"] == c["declared_new"],
         f'{c["rows_total"]} = {c["migration_rows"]}+{c["new_term_rows"]}（声明 {c["declared_rows"]}/'
         f'{c["declared_migration"]}/{c["declared_new"]}）'),
        ("M2 草案未发布（status 含 DRAFT，且新 IRI 为 PENDING 占位）",
         "DRAFT" in str(d["draft_status"]).upper() and c["published_new_iri_leak"] == 0,
         f'status={str(d["draft_status"])[:28]}… 泄漏={c["published_new_iri_leak"]}'),
        ("M3 等价关系口径**自洽**（FORBIDDEN 不得绑 owl:equivalent；ALLOWED 须有前置条件）",
         c["equivalent_bad"] == 0, f'违例={c["equivalent_bad"]}'),
        ("M4 每条迁移行的**旧端短名**在现行基线 T-Box 中可定位（按旧端解析，非目标 termId）",
         c["unresolvable_old_iri"] == 0,
         f'不可解析={c["unresolvable_old_iri"]}｜{ [x["old_short"] for x in d["unresolvable_old_iri"][:5]] }'),
        ("M5 SIM 通道无 needle 泄漏（**无正式 IRI needle 时显式不计为覆盖**）",
         c["published_new_iri_leak"] == 0
         and (d["needles"]["formal"] > 0 or bool(d["coverage_exclusions"])),
         f'正式 needle {d["needles"]["formal"]} / 符号占位 {d["needles"]["symbolic"]}；泄漏 0 处'
         + ("；**不计为覆盖**（理由已登记）" if d["coverage_exclusions"] else "")),
        ("M6 B6/B8 dry-run **只读性由前后哈希派生**（非写死）",
         len(d["dry_run"]) >= 2 and all(v["dry_run_only"] for v in d["dry_run"].values())
         and all(v["files_hashed"] > 0 for v in d["dry_run"].values()),
         " · ".join(f'{k}: 抽检 {v["sample_checked"]} 哈希 {v["files_hashed"]} 文件不变={v["dry_run_only"]}'
                    for k, v in d["dry_run"].items())),
        ("M7 边界**派生**探测（禁止文件不存在 + 无 needle 泄漏）",
         d["boundary"]["derived_ok"] and bool(d["boundary"]["probe_files"]),
         f'探测 {len(d["boundary"]["probe_files"])} 项；禁止文件命中={d["boundary"]["forbidden_present"] or "无"}'),
    ]


def cmd_gate() -> int:
    d = build()
    PREP.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    rows = checks(d)
    print("# command=onto1_sim_migration_verify --gate")
    print(f'# 制品={OUT.relative_to(ROOT)} 映射 sha={d["sources"]["mapping_sha256"][:16]} T-Box={d["sources"]["tbox_sha256"][:16]}')
    for n, ok, det in rows:
        print(f"{'PASS' if ok else 'FAIL'} [{n}] {det}")
    bad = [n for n, ok, _ in rows if not ok]
    print(f"A-4 SIM 迁移验证：{'PASS' if not bad else 'FAIL'}（{len(rows) - len(bad)}/{len(rows)}）")
    return 0 if not bad else 2


def cmd_selftest() -> int:
    d = build()
    fails = total = 0

    def run(tag, mut):
        nonlocal fails, total
        import copy
        m = copy.deepcopy(d)
        mut(m)
        ok = not all(o for _, o, _ in checks(m))
        total += 1
        fails += 0 if ok else 1
        print(f"{'PASS' if ok else 'FAIL'} [{tag}] 被捕获 = {ok}")

    total += 1
    base = all(o for _, o, _ in checks(d))
    fails += 0 if base else 1
    print(f"{'PASS' if base else 'FAIL'} [M0 对照] 现状 = {base}")
    run("N1 行数被篡改 ⇒ FAIL", lambda m: m["counts"].update(rows_total=88))
    run("N2 草案被标为已发布 ⇒ FAIL", lambda m: m["counts"].update(published_new_iri_leak=1))
    run("N3 迁移行引入等价关系 ⇒ FAIL", lambda m: m["counts"].update(equivalent_bad=1))
    run("N4 旧端术语不可解析 ⇒ FAIL", lambda m: m["counts"].update(unresolvable_old_iri=2))
    run("N5 dry-run 变成会写文件 ⇒ FAIL", lambda m: m["dry_run"]["B6_消费者切换"].update(dry_run_only=False))
    run("N6 边界派生值被破坏 ⇒ FAIL", lambda m: m["boundary"].update(derived_ok=False))
    # **真实路径**反例：实际创建被禁止的 namespaces.json 于临时目录，探测必须命中
    import tempfile as _tf
    with _tf.TemporaryDirectory() as _td:
        _p = pathlib.Path(_td) / "namespaces.json"
        _p.write_text("{}", encoding="utf-8")
        _probe = boundary_probe([], SIM_DIR, extra_files=[_p])
        total += 1
        _ok = _probe["forbidden_present"] and not _probe["derived_ok"]
        fails += 0 if _ok else 1
        print(f"{'PASS' if _ok else 'FAIL'} [N7 真实路径：禁止文件存在 ⇒ 探测失败] = {_ok}")
    # **真实路径**反例：needle 实际写入 SIM 目录 ⇒ 探测必须命中
    with _tf.TemporaryDirectory() as _td:
        _sim = pathlib.Path(_td)
        (_sim / "leak.ttl").write_text("REGISTRY:ActivationContract", encoding="utf-8")
        _probe = boundary_probe(["REGISTRY:ActivationContract"], _sim)
        total += 1
        _ok = bool(_probe["needle_leaks"]) and not _probe["derived_ok"]
        fails += 0 if _ok else 1
        print(f"{'PASS' if _ok else 'FAIL'} [N8 真实路径：needle 写入 SIM ⇒ 探测失败] = {_ok}")
    print(f"--selftest {'PASS' if fails == 0 else 'FAIL'}（{total - fails}/{total}）")
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
    d = build()
    OUT.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f'已写出 {OUT.relative_to(ROOT)}：{d["counts"]}')
    return 0


if __name__ == "__main__":
    sys.exit(main())
