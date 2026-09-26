#!/usr/bin/env python3
"""Q8 独立复现：≥12 路并发混合请求 8 类端点，0 个 5xx/400。

QA 自研；用真实 HTTP 打 8107（非 TestClient），验证 DuckDB 连接串行化修复。
"""
from __future__ import annotations

import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from concurrent.futures import ThreadPoolExecutor

BASE = "http://127.0.0.1:8107"
PERIOD = "201112"
ORG = "350000"
WORKS = 16          # 并发路数 ≥12
ROUNDS = 7          # 每路轮转 8 类端点 ⇒ 16*7=112 请求

GET_PATHS = [
    "/v1/analytics/dimensions",
    "/v1/analytics/orgs",
    "/v1/analytics/periods",
    "/v1/analytics/screens",
    "/v1/analytics/params",
    f"/v1/analytics/metrics?screen=operating-customer&dim=INDUSTRY&orgId={ORG}&period={PERIOD}",
    ("/v1/analytics/metrics?screen=monitor-balance&dim=CUST_TYPE&orgId=" + ORG
     + "&period=" + PERIOD),
    ("/v1/analytics/trend?screen=monitor-ldr&dim=INDUSTRY&dimValue="
     + urllib.parse.quote("制造业") + f"&orgId={ORG}&metric=ldr&months=12"),
]
POST_PATH = "/v1/analytics/combo-query"
POST_BODY = json.dumps({
    "filters": {"period": PERIOD, "orgId": ORG,
                "amountRules": [{"metric": "depBal", "op": ">=", "value": 5000}]},
    "pageNumber": 0, "pageSize": 20,
}).encode()


def call(i: int) -> tuple[str, int, str]:
    if i % 2 == 1:  # 交替打 POST，保证 8 类端点均被覆盖
        req = urllib.request.Request(BASE + POST_PATH, data=POST_BODY,
                                     headers={"Content-Type": "application/json"},
                                     method="POST")
        kind = "POST combo-query"
    else:
        path = GET_PATHS[(i // 2) % len(GET_PATHS)]
        req = urllib.request.Request(BASE + path)
        kind = path.split("?")[0]
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            payload = resp.read()
            code = resp.status
    except urllib.error.HTTPError as exc:
        payload = exc.read()
        code = exc.code
    except Exception as exc:  # noqa: BLE001
        return kind, -1, repr(exc)
    ok = b'"status":"OK"' in payload or b'"status": "OK"' in payload
    return kind, code, "OK" if ok else payload[:120].decode("utf-8", "replace")


results = []
with ThreadPoolExecutor(max_workers=WORKS) as pool:
    futures = [pool.submit(call, i) for i in range(WORKS * ROUNDS)]
    results = [f.result() for f in futures]

codes = Counter(c for _, c, _ in results)
per_kind = Counter(k for k, _, _ in results)
env_ok = sum(1 for _, c, body in results if c == 200 and body == "OK")
bad = [(k, c, b) for k, c, b in results if c != 200 or b != "OK"]

print(f"总请求={len(results)} 并发={WORKS} 轮数={ROUNDS}")
print("HTTP 码分布=", dict(sorted(codes.items())))
print("端点覆盖=", dict(per_kind))
print(f"200 且信封 status=OK: {env_ok}/{len(results)}")
if bad:
    print("异常样例(前 10):")
    for row in bad[:10]:
        print("   ", row)
print("Q8 结论:", "PASS" if not bad else f"FAIL 异常 {len(bad)} 条")
sys.exit(0 if not bad else 1)
