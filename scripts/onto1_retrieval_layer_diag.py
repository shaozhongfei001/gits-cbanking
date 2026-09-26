#!/usr/bin/env python3
"""ONTO1 检索层诊断仪（跨仓**只读**诊断；**不登记门禁**）。

目的：把「LightRAG 是否真生效」从口头判断变成机器可复核断言，并给
「检索层启用三前提」（真实模型 / simulationOnly 派生 / 端点进合同）留下可复算留痕。

边界（硬）：
  · KERT **零写入**：只 read_text / 只读 /proc，绝不写任何 KERT 路径；
  · 只做只读调用（health + 检索查询），**不** publish / retract / 不建索引 / 不删文档；
  · **不登记为门禁**（gateCandidate=false）：它读跨仓实现细节，登记会变成
    「拿别仓实现细节当本仓通过条件」，与 P3「跨仓零直读」精神相左。仅作诊断与留痕。

用法：
    python3 scripts/onto1_retrieval_layer_diag.py --scan          # 打印
    python3 scripts/onto1_retrieval_layer_diag.py --scan --json   # 另写制品
"""
from __future__ import annotations

import argparse
import ast
import json
import pathlib
import subprocess
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
KERT = pathlib.Path("/home/szf/dev/Leibniz-KERT")
SERVER_PY = KERT / "src" / "kert" / "api" / "server.py"
EXP_CFG = ROOT / "specs" / "knowledge-architecture" / "lightrag" / "experiment_config.json"
L6_LOCK = ROOT / "evidence" / "L6" / "DEPLOYMENT.lock.json"
CONTRACT_HINT = "retrieval/query"
OUT = ROOT / "loops" / "ONTO1-ontology-split" / "evidence" / "prep" / "retrieval-layer-diag.json"
LR_HEALTH = "http://127.0.0.1:9621/health"
KERT_EP = "http://127.0.0.1:8107/v1/retrieval/query"


def probe_simulation_only() -> dict:
    """D1：端点响应里 simulationOnly 是字面量还是派生（AST）。"""
    if not SERVER_PY.is_file():
        return {"id": "D1", "verdict": "SKIP", "detail": "KERT server.py 不可达"}
    try:
        tree = ast.parse(SERVER_PY.read_text(encoding="utf-8"))
    except SyntaxError as exc:
        return {"id": "D1", "verdict": "SKIP", "detail": f"server.py 解析失败: {exc}"}
    for fn in ast.walk(tree):
        if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)) and fn.name == "retrieval_query":
            for node in ast.walk(fn):
                if not isinstance(node, ast.Dict):
                    continue
                for key, val in zip(node.keys, node.values):
                    if isinstance(key, ast.Constant) and key.value == "simulationOnly":
                        if isinstance(val, ast.Constant):
                            return {"id": "D1", "verdict": "DEFECT", "value": val.value,
                                    "line": val.lineno,
                                    "detail": "端点响应把 simulationOnly 写成字面量（非派生）⇒ 与权威配置可相反"}
                        return {"id": "D1", "verdict": "OK", "line": val.lineno,
                                "detail": "simulationOnly 为表达式（派生）"}
    return {"id": "D1", "verdict": "SKIP", "detail": "未找到 retrieval_query 或其响应 dict"}


def _get(url: str, timeout: int = 5) -> tuple:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            return resp.status, resp.read().decode("utf-8", "ignore")
    except Exception as exc:  # noqa: BLE001
        return None, str(exc)


def _post(url: str, payload: dict, timeout: int = 60) -> tuple:
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=body,
                                 headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read().decode("utf-8", "ignore")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", "ignore")
    except Exception as exc:  # noqa: BLE001
        return None, str(exc)


def probe_service() -> dict:
    """D2：LightRAG 实例健康。"""
    status, body = _get(LR_HEALTH)
    if status is None:
        return {"id": "D2", "verdict": "UNREACHABLE", "detail": body[:160]}
    try:
        doc = json.loads(body)
    except Exception:  # noqa: BLE001
        doc = {}
    ok = doc.get("status") == "healthy"
    return {"id": "D2", "verdict": "OK" if ok else "DEFECT",
            "http": status, "core_version": doc.get("core_version"),
            "workspace_available": doc.get("workspace_available"),
            "pipeline_busy": doc.get("pipeline_busy"),
            "detail": "实例健康" if ok else "实例响应非 healthy"}


def probe_endpoint() -> dict:
    """D3：派生检索端点可达 + 出处字段（只读查询）。"""
    status, body = _post(KERT_EP, {"request_id": "diag-onto1-ro", "query": "产品解读", "mode": "hybrid"})
    if status is None:
        return {"id": "D3", "verdict": "UNREACHABLE", "detail": body[:160]}
    if status != 200:
        return {"id": "D3", "verdict": "DEFECT", "http": status, "detail": body[:200]}
    try:
        doc = json.loads(body)
    except Exception:  # noqa: BLE001
        return {"id": "D3", "verdict": "SKIP", "detail": "响应非 JSON"}
    data = doc.get("data", doc)
    cites = data.get("citations") or []
    return {"id": "D3", "verdict": "OK", "http": status,
            "evidenceClass": data.get("evidenceClass"),
            "response_simulationOnly": data.get("simulationOnly"),
            "entities": len(data.get("entities") or []),
            "relations": len(data.get("relations") or []),
            "citations": len(cites),
            "first_citation_doc": (cites[0].get("docId") if cites and isinstance(cites[0], dict) else None),
            "detail": "派生检索端点可召回（含可回译出处）"}


def probe_llm_binding() -> dict:
    """D4：底层 LLM 是否 mock（只读 /proc）。"""
    res = subprocess.run(["pgrep", "-f", "lightrag-server"], capture_output=True, text=True)
    pids = [x for x in res.stdout.split() if x.strip()]
    if not pids:
        return {"id": "D4", "verdict": "SKIP", "detail": "lightrag-server 进程不存在"}
    env_path = pathlib.Path("/proc") / pids[0] / "environ"
    if not env_path.is_file():
        return {"id": "D4", "verdict": "SKIP", "detail": "无法读取进程环境"}
    raw = env_path.read_text(encoding="utf-8", errors="ignore")
    env = dict(item.split("=", 1) for item in raw.split("\0") if "=" in item)
    model, host = env.get("LLM_MODEL"), env.get("LLM_BINDING_HOST")
    mock = (model == "mock") or bool(host and "9630" in host)
    return {"id": "D4", "verdict": "DEFECT" if mock else "OK",
            "llm_model": model, "llm_host": host,
            "detail": "底层 LLM 为 mock（CI 假模型）⇒ 抽取层非真实模型" if mock else "LLM 绑定非 mock"}


def probe_wording() -> dict:
    """D5：配置/验收口径与运行态是否矛盾（只读）。"""
    cfg = None
    if EXP_CFG.is_file():
        try:
            cfg = json.loads(EXP_CFG.read_text(encoding="utf-8")).get("simulationOnly")
        except Exception:  # noqa: BLE001
            cfg = "PARSE_ERROR"
    lock = None
    if L6_LOCK.is_file():
        try:
            lock = json.loads(L6_LOCK.read_text(encoding="utf-8")).get("lightragEnabled")
        except Exception:  # noqa: BLE001
            lock = "PARSE_ERROR"
    return {"id": "D5", "verdict": "CONTRADICTION" if lock is False else "OK",
            "experiment_config_simulationOnly": cfg, "l6_lightragEnabled": lock,
            "detail": "验收口径 lightragEnabled=false（未启用），与运行中的实例/端点并存 ⇒ 须披露，不得称已启用"}


def probe_deployment_staleness(d1: dict, d3: dict) -> dict:
    """D7：**源码已派生但运行实例未重启** ⇒ 陈旧部署（消费方最易误判的一种状态）。"""
    if d1.get("verdict") != "OK":
        return {"id": "D7", "verdict": "SKIP", "detail": "源码尚未派生，无需比对部署时效"}
    live = d3.get("response_simulationOnly")
    if live is None:
        return {"id": "D7", "verdict": "SKIP", "detail": "运行态不可达，无法比对部署时效"}
    if live is False:
        return {"id": "D7", "verdict": "STALE_DEPLOYMENT", "response_simulationOnly": live,
                "detail": "源码已派生（D1=OK）但运行实例仍返回 False ⇒ 需**重启服务**方生效"}
    return {"id": "D7", "verdict": "OK", "response_simulationOnly": live,
            "detail": "运行态已反映派生值"}


def probe_contract() -> dict:
    """D6：新端点是否进合同（只读 specs/ 文本检索）。"""
    hits = []
    specs = ROOT / "specs"
    if specs.is_dir():
        for path in specs.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in (".yaml", ".yml", ".json", ".md", ".ttl"):
                continue
            try:
                if CONTRACT_HINT in path.read_text(encoding="utf-8", errors="ignore"):
                    hits.append(str(path.relative_to(ROOT)))
            except Exception:  # noqa: BLE001
                continue
    return {"id": "D6", "verdict": "OK" if hits else "DEFECT",
            "hits": hits[:5], "hit_count": len(hits),
            "detail": "新端点已进合同" if hits else "specs/ 内零命中 ⇒ 端点未进合同（contract_check 应 FAIL）"}


def main() -> int:
    ap = argparse.ArgumentParser(description="ONTO1 检索层诊断仪（只读跨仓）")
    ap.add_argument("--scan", action="store_true", help="执行诊断")
    ap.add_argument("--json", action="store_true", help="另写制品")
    args = ap.parse_args()
    if not args.scan:
        ap.print_help()
        return 2

    d1 = probe_simulation_only()
    d3 = probe_endpoint()
    findings = [d1, probe_service(), probe_llm_binding(), d3,
                probe_contract(), probe_wording(), probe_deployment_staleness(d1, d3)]
    counts: dict = {}
    for item in findings:
        counts[item["verdict"]] = counts.get(item["verdict"], 0) + 1
    doc = {
        "schema": "ONTO1-RETRIEVAL-LAYER-DIAG/1.0",
        "generatedBy": "scripts/onto1_retrieval_layer_diag.py",
        "gateCandidate": False,
        "gateCandidateReason": "跨仓只读实现细节；登记门禁会以别仓实现当本仓通过条件（P3 精神）",
        "crossRepoWrites": "none:KERT-untouched",
        "findings": findings,
        "summary": {"counts": counts,
                    "defects": [f["id"] for f in findings if f["verdict"] in ("DEFECT", "CONTRADICTION")]},
    }

    print("ONTO1 检索层诊断（只读；KERT 零写入）")
    for item in findings:
        print(f"  [{item['verdict']:<13}] {item['id']} {item['detail'][:78]}")
    print(f"  小结: {counts}")

    (ROOT / "loops" / "ONTO1-ontology-split" / "evidence" / "prep").mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"  制品: {OUT.relative_to(ROOT)} (gateCandidate=False)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
