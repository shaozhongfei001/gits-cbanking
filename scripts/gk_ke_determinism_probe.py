#!/usr/bin/env python3
"""确定性实验（**依预注册协议执行**，协议见
docs/architecture/GK-KE-确定性实验协议与阻塞登记-V1.0.md §2）。

问题：下游能力能否被固定到确定性？
  可达 → 反事实对比成立 → 可证明"真的消费"
  不可达 → 只能走运行时 trace，且只能证到"传递级"

预注册判据（**不得事后修改**）：
  确定性可达    : 5 次输出排除 generatedAt 后完全一致
  确定性不可达  : 存在任意两次不一致
  实验无效      : 实际 temperature ≠ 0 / 未取到 seed / 服务端未回读参数 / 任一次为空或报错

假阳性防护：复用 requestId 会命中幂等缓存而伪装成确定性 →
  每次用**唯一** requestId；并另做一次"改动无关字符"的对照，确认输出**确实会变**。
"""
from __future__ import annotations

import json
import time
import urllib.error
import urllib.request

BASE = "http://127.0.0.1:8100"
SKILL = "bank-front-kyc-gap-check"
K = 5
TEMP = 0.0
SEED = 20260913

# 固定输入：含**具体** ruleId（非占位符），并使触发源存在
INPUT = {
    "customerId": "HZB0000001234",
    "upstreamStatus": "SUCCESS",
    "conflicts": [
        {"id": "CFL-001", "issue": "用电量同比+30%，但近半年营收同比-5%",
         "ruleId": "RUL-FRONT-001-003"},
    ],
    "optional": {"customerName": "杭州智造精密齿轮有限公司"},
}


def call(payload: dict, req_temp, req_seed, tag: str) -> tuple[dict, dict]:
    rid = f"det-{tag}-{SKILL}-{int(time.time()*1000)}-{time.perf_counter_ns()%100000}"
    body = {"skillId": SKILL, "requestId": rid,
            "request": {"input": payload, "temperature": req_temp, "seed": req_seed}}
    req = urllib.request.Request(
        BASE + "/api/skill/execute",
        data=json.dumps(body, ensure_ascii=False).encode(),
        method="POST", headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode())
        except Exception:
            return e.code, {"status": "http_error"}


def norm(obj) -> str:
    """排除允许字段后的规范化文本。"""
    def strip(o):
        if isinstance(o, dict):
            return {k: strip(v) for k, v in o.items()
                    if k not in ("generatedAt",)}
        if isinstance(o, list):
            return [strip(v) for v in o]
        return o
    return json.dumps(strip(obj), ensure_ascii=False, sort_keys=True)


def main() -> int:
    runs: list[dict] = []
    print(f"gk-ke-determinism-probe  skill={SKILL}  k={K}  "
          f"要求 temperature={TEMP} seed={SEED}")
    for i in range(1, K + 1):
        code, resp = call(INPUT, TEMP, SEED, f"r{i}")
        if code != 200 or resp.get("status") != "ok":
            print(f"  第{i}次 **失败** code={code} status={resp.get('status')} "
                  f"errors={str(resp.get('errors'))[:120]}")
            print("  → 依预注册判据：任一次为空/报错 ⇒ **实验无效**，中止")
            return 1
        data = (resp.get("data") or {})
        # modelCalls 位于**响应顶层**（不在 data 内）——
        # 曾因假设它在 data 里而误判"服务端未回读"（实为找错位置）。
        mcs = resp.get("modelCalls") or []
        mc = mcs[0] if mcs else {}
        if not mc:
            print(f"  第{i}次 ok 但响应未含 modelCalls —— 依判据实验无效")
            return 1
        runs.append({"i": i, "data": data, "modelCall": mc})
        print(f"  第{i}次 ok  model={mc.get('model')} "
              f"生效temperature={mc.get('temperature')} 生效seed={mc.get('seed')}")

    # ---- 记录要求 1：实际生效参数（服务端回读）----
    eff = [(r["modelCall"].get("temperature"), r["modelCall"].get("seed"))
           for r in runs]
    print(f"\n[记录] 生效参数(服务端回读): {eff}")
    if any(t != TEMP for t, _ in eff):
        print(f"FAIL: 实际 temperature ≠ {TEMP} ⇒ **实验无效**")
        return 1
    if any(s != SEED for _, s in eff):
        print(f"FAIL: 未按请求取得 seed ⇒ **实验无效**")
        return 1
    print("  ✅ 生效参数与请求一致（满足预注册的有效性前提）")

    # ---- 预注册判据：k 次是否完全一致 ----
    norms = [norm(r["data"].get("result")) for r in runs]
    same = len(set(norms)) == 1
    print(f"\n[判定] 排除 generatedAt 后，{K} 次输出"
          f"{'**完全一致** ⇒ 确定性可达' if same else '**存在不一致** ⇒ 确定性不可达'}")
    if not same:
        print(f"  不一致组数: {len(set(norms))}/{K}")
        for i, n in enumerate(norms, 1):
            print(f"    第{i}次 规范化长度={len(n)} 前80={n[:80]}")
        print("\n  → 依预注册判据：确定性**不可达**。"
              "测量面只能走运行时 trace，且**只能证到传递级**。")
        return 0

    # ---- 假阳性防护：改动无关字符，输出应变化 ----
    alt = json.loads(json.dumps(INPUT, ensure_ascii=False))
    alt["conflicts"][0]["issue"] = alt["conflicts"][0]["issue"].replace("5%", "6%")
    code, resp = call(alt, TEMP, SEED, "alt")
    if code != 200 or resp.get("status") != "ok":
        print("  假阳性对照调用失败 —— 无法排除幂等缓存，结论降级为**不确定**")
        return 1
    alt_norm = norm((resp.get("data") or {}).get("result"))
    changed = alt_norm != norms[0]
    print(f"\n[假阳性对照] 改动输入中的一个字符后输出"
          f"{'**发生变化** ⇒ 非幂等缓存造成' if changed else '**未变化** ⇒ 疑似幂等缓存，确定性结论不可信'}")
    if not changed:
        print("  → 结论**不可信**，须排查幂等缓存后重跑")
        return 1

    print("\n结论：确定性**可达**（且已排除幂等缓存假阳性）"
          " ⇒ 测量面可走方案 C（受控确定性 + 反事实对比），可证明\"真的消费\"。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
