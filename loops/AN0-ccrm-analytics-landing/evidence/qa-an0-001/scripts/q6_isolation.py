#!/usr/bin/env python3
"""Q6 独立复现：未配置 KERT_ANALYTICS_DUCKDB ⇒ 端点 503 且 Skill 注册表零扰动。

QA 自研（不复用 TL 测试代码），只依赖被测应用与真实造数库。
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

REPO = Path("/home/szf/dev/Leibniz-KERT")
sys.path.insert(0, str(REPO / "src"))

from starlette.testclient import TestClient  # noqa: E402

from kert.api.server import ANALYTICS_DUCKDB_ENV, create_app  # noqa: E402

DB = REPO / "examples" / "bank-front-analytics" / "cb_analytics.duckdb"
WS = Path("/tmp/kert-analytics-ws")
SKILLS = REPO / "examples" / "bank-front-skills"
ANALYTICS_IDS = ("bank-front-operating-metrics", "bank-front-customer-segment",
                 "bank-front-combo-query", "bank-front-metrics-monitor")

failures: list[str] = []


def check(label: str, ok: bool, detail: str) -> None:
    print(f"[{'PASS' if ok else 'FAIL'}] {label}: {detail}")
    if not ok:
        failures.append(label)


# ---- 1) 未配置：503 + 注册表不含分析 Skill ------------------------------------
os.environ.pop(ANALYTICS_DUCKDB_ENV, None)
plain = create_app(WS, skill_packages=SKILLS)
plain_ids = sorted(s.skill_id for s in plain.state.skill_service.registry())
c_plain = TestClient(plain)
r = c_plain.get("/v1/analytics/screens")
body = r.json()
check("未配置 /v1/analytics/screens", r.status_code == 503,
      f"HTTP={r.status_code} code={body.get('detail', {}).get('error', {}).get('code')}")
check("未配置 analytics_service is None", plain.state.analytics_service is None,
      f"analytics_service={plain.state.analytics_service!r}")
leaked = [i for i in plain_ids if i in ANALYTICS_IDS]
check("未配置 分析 Skill 未注册", not leaked, f"leaked={leaked}")
check("未配置 端点全 503", all(TestClient(plain).get(p).status_code == 503 for p in (
    "/v1/analytics/dimensions", "/v1/analytics/orgs", "/v1/analytics/periods",
    "/v1/analytics/params", "/v1/analytics/screens",
    "/v1/analytics/metrics?screen=operating-customer&dim=INDUSTRY&orgId=350000&period=201012",
    "/v1/analytics/trend?screen=monitor-ldr&dim=INDUSTRY&dimValue=%E5%88%B6%E9%80%A0%E4%B8%9A"
    "&orgId=350000&metric=ldr")),
      "7 个 GET 端点逐一核对")

# ---- 2) 已配置：503 消失 + 恰好多出 4 个分析 Skill ----------------------------
os.environ[ANALYTICS_DUCKDB_ENV] = str(DB)
on = create_app(WS, skill_packages=SKILLS)
on_ids = sorted(s.skill_id for s in on.state.skill_service.registry())
c_on = TestClient(on)
r2 = c_on.get("/v1/analytics/screens")
check("已配置 /v1/analytics/screens", r2.status_code == 200, f"HTTP={r2.status_code}")
added = sorted(set(on_ids) - set(plain_ids))
check("已配置 恰好多出 4 个分析 Skill", added == sorted(ANALYTICS_IDS), f"added={added}")
check("注册表纯增无删（零扰动）", set(plain_ids) <= set(on_ids),
      f"removed={sorted(set(plain_ids) - set(on_ids))}")
print(f"   注册表规模：未配置={len(plain_ids)} 已配置={len(on_ids)}")
print(f"   未配置注册表={plain_ids}")

print("\nQ6 结论:", "PASS" if not failures else f"FAIL {failures}")
sys.exit(0 if not failures else 1)
