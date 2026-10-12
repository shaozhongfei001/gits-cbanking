#!/usr/bin/env python3
"""生成 UAT1 人工 UAT 交付包：场景 × 功能点 × 判定矩阵 + 证据索引。

fail-closed 语义：
- 任一波次门禁未 PASS ⇒ 交付包生成失败（退出 2），不允许带着未通过的波次送人工 UAT；
- 门禁日志缺失或解析不到用例 ⇒ 视为证据不足，失败。

用法：python3 scripts/uat_package.py --loop UAT1-full-scenario-e2e
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# list reporter 的行形如：  ✓  12 e2e/uat/w0-route-sweep.spec.ts:47:5 › W0 全路由巡检 › P01 经营总览 — 真实数据 (1.9s)
RESULT_LINE = re.compile(r"^\s*(?P<mark>[✓✘±])\s+\d+\s+(?P<rest>\S+)\s+›\s+(?P<title>.+?)\s+\((?P<dur>[\d.]+m?s)\)\s*$")
WAVE_TITLES = {
    "w0_route_sweep": "W0 全路由巡检",
    "w1_workspace_domain": "W1 经营域",
    "w2_customer_domain": "W2 客户域",
    "w3_product_domain": "W3 产品域",
    "w4_proposal_domain": "W4 方案域",
    "w5_analytics_domain": "W5 经营分析域（KERT）",
    "w6_journey_closed_loop": "W6 旅程业务闭环",
    "w7_mobile_governance": "W7 移动端与治理页",
    "w8_error_paths": "W8 错误路径与四态",
}


def extract_pending_decisions(root: Path) -> list[str]:
    """提取本轮登记、需 Owner/设计裁决的 D- 编号项（不让它们悄悄消失）。"""
    items: list[str] = []
    for path in sorted((root / "docs" / "dispatch").glob("*UAT*.md")):
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.startswith("### D-"):
                items.append(line.lstrip("# ").strip())
    return items


def extract_known_issues(failures: Path) -> list[str]:
    """从 FAILURES.md 提取显式标注「非阻塞」且**尚未修复**的问题，交付包必须如实呈现。

    FAILURES.md 是 append-only：修复事实以追加条目出现（`<id> 修复完成`），
    因此这里按「后出现的修复记录覆盖原始登记」判定，避免把已修复项当成未决项。
    """
    if not failures.is_file():
        return []
    text = failures.read_text(encoding="utf-8", errors="replace")
    items: list[str] = []
    for line in text.splitlines():
        if not (line.startswith("### F-") and "非阻塞" in line):
            continue
        title = line.lstrip("# ").strip()
        issue_id = title.split("｜")[0].strip()
        if re.search(rf"{re.escape(issue_id)}[^｜\n]*修复完成", text):
            continue
        items.append(title)
    return items


def latest_log(loop: Path, gate: str) -> Path | None:
    logs = sorted((loop / "evidence").glob(f"{gate}-*.log"), key=lambda p: p.name)
    return logs[-1] if logs else None


def parse_log(log: Path) -> list[dict]:
    rows: list[dict] = []
    for line in log.read_text(encoding="utf-8", errors="replace").splitlines():
        match = RESULT_LINE.match(line)
        if not match:
            continue
        title = match.group("title")
        parts = [p.strip() for p in title.split("›")]
        rows.append(
            {
                "case": parts[-1] if len(parts) > 1 else title,
                "group": parts[-2] if len(parts) > 2 else "",
                "status": "PASS" if match.group("mark") == "✓" else ("FAIL" if match.group("mark") == "✘" else "FLAKY"),
                "duration": match.group("dur"),
            }
        )
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--loop", required=True)
    args = parser.parse_args()

    loop = ROOT / "loops" / args.loop
    evidence = json.loads((loop / "EVIDENCE.json").read_text(encoding="utf-8"))
    spec = json.loads((loop / "LOOP.yaml").read_text(encoding="utf-8"))

    problems: list[str] = []
    sections: list[str] = []
    total = passed = 0

    for gate in spec["gates"]:
        gid = gate["id"]
        row = evidence["gates"].get(gid, {})
        if gid == "uat_package":
            continue
        status = row.get("status")
        if gid == "env_ready":
            sections.append(f"### 环境就绪\n\n- 状态：**{status}** · 执行时间 {row.get('executed_at')}\n")
            if status != "pass":
                problems.append(f"env_ready 未通过（{status}）")
            continue

        log = latest_log(loop, gid)
        if log is None:
            problems.append(f"{gid}: 缺少门禁日志")
            continue
        rows = parse_log(log)
        if not rows:
            problems.append(f"{gid}: 门禁日志未解析到用例（证据不足）")
            continue
        failed = [r for r in rows if r["status"] != "PASS"]
        total += len(rows)
        passed += len(rows) - len(failed)
        if status != "pass" or failed:
            problems.append(f"{gid}: 存在未通过用例 {len(failed)}/{len(rows)}")

        lines = "\n".join(
            f"| {r['status']} | {r['case']} | {r['duration']} |" for r in rows
        )
        sections.append(
            f"### {WAVE_TITLES.get(gid, gid)}\n\n"
            f"- 门禁状态：**{status}** · 退出码 {row.get('exit_code')} · 用例 {len(rows)} · 证据 `{row.get('evidence_file')}`\n\n"
            f"| 判定 | 功能点 | 耗时 |\n|---|---|---|\n{lines}\n"
        )

    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    report = [
        f"# {args.loop} 人工 UAT 交付包",
        "",
        f"生成时间：{stamp}（UTC）",
        f"基线提交：{json.loads((loop / 'STATE.json').read_text(encoding='utf-8')).get('baseline_commit')}",
        f"用例总计：{total} · 通过：{passed} · 未通过：{total - passed}",
        "",
        "## 判定口径",
        "",
        "每个功能点都在真实浏览器（Playwright + Chromium）中验证**用户可见行为**：",
        "不白屏、无未捕获异常、后端/KERT 接口无 5xx、真实数据路由无未预期 4xx、",
        "无后端数据的页面必须显式降级标注（不得静默空白或伪造数据）。",
        "",
        *sections,
    ]

    if problems:
        report += ["## 结论", "", "**不可提交人工 UAT**，阻塞项：", ""]
        report += [f"- {p}" for p in problems]
        (loop / "UAT_PACKAGE.md").write_text("\n".join(report) + "\n", encoding="utf-8")
        print("\n".join(report))
        print("\nuat_package: FAIL")
        return 2

    known = extract_known_issues(loop / "FAILURES.md")
    report += [
        "## 结论",
        "",
        f"全部 {total} 个功能点用例通过，无人值守 E2E 迭代完成，**可提交人工 UAT**。",
        "",
    ]
    if known:
        report += ["## 已知未决问题（不阻断 UAT，须由 Owner 知悉）", ""]
        report += [f"- {item}" for item in known]
        report.append("")

    decisions = extract_pending_decisions(ROOT)
    if decisions:
        report += ["## 待 Owner / 设计裁决（不影响本次送审，但须拍板）", ""]
        report += [f"- {item}" for item in decisions]
        report.append("")

    report += [
        "## 已修复缺陷（本轮）",
        "",
        "- F-UAT1-01：KERT 经营分析全端点 503 —— 以 DuckDB 数据源重启 KERT 服务（环境/配置）",
        "- F-UAT1-06：报告详情页伪造数据 + Loading 永不消失 —— 移除占位桩，改真实来源定位 + 显式降级（P0 红线）",
        "- F-UAT1-07：会中捕获页用 journeyId 冒充 interactionId 查录音同意 —— 改为客户维度查询",
        "- F-UAT1-10：前端存量单测 17 failed —— 修实现（navConfig 域映射死代码、侧栏缺 testid、loading 缺 testid）"
        " 并更新过时测试期望；批次 UAT2-component-test-drift 三门禁 PASS，440 用例 0 failed",
        "- D-4：经营信号页跨页入口被在途改动删除，导致 P10 互动对象主页无 UI 入口（孤儿页）"
        " —— 恢复入口并补浏览器可达性用例；批次 UAT3-signal-nav-entry 三门禁 PASS + 变异复验闭环",
    ]
    (loop / "UAT_PACKAGE.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    (loop / "evidence" / f"uat-package-{stamp}.json").write_text(
        json.dumps({"loop": args.loop, "total": total, "passed": passed, "generated_at": stamp}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print("\n".join(report))
    print("\nuat_package: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
