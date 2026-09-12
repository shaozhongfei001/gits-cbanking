#!/usr/bin/env python3
"""GK-KE 人工验收台（只读，SIM 数据）—— OC-03 / OC-04 / OC-05 可操作验证。

设计约束（LOOP.yaml §design_decisions）：
  D-1 只读：不写入任何权威源
  D-2 独立应用：置于 tools/gk-ke-console/，不改动 frontend/
  D-3 合同绑定：每区块标注 /gk-ke/v1 operationId 与合同条款
  D-4 拒绝可操作：可注入违规并展示真实拒绝码
  D-5 SIM 标识：全程 simulationOnly + 非生产水印
  D-6 零外部依赖：仅 stdlib

用法：
  python3 scripts/gk_ke_console_server.py --port 8765
  然后浏览器打开 http://localhost:8765/

注意：本服务**只读**，不修改任何仓库文件；「注入违规」只在内存中求值。
"""
from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]

# ---------------------------------------------------------------- 数据加载

def load_json(rel: str):
    path = ROOT / rel
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


DATA = {
    "release": "specs/knowledge-architecture/release/release_manifest.json",
    "decisions": "specs/knowledge-architecture/release/review_decisions.json",
    "release_negatives": "specs/knowledge-architecture/release/negatives.json",
    "map_spec": "specs/knowledge-architecture/activation/map_spec.json",
    "plan": "specs/knowledge-architecture/activation/activation_plan.json",
    "route_policy": "specs/knowledge-architecture/activation/route_policy.json",
    "task_template": "specs/knowledge-architecture/activation/task_template.json",
    "activation_violations": "specs/knowledge-architecture/activation/violations.json",
    "closed_loop": "specs/knowledge-architecture/closed-loop/closed_loop_run.json",
    "closed_loop_violations": "specs/knowledge-architecture/closed-loop/violations.json",
    "factory_review": "specs/knowledge-architecture/factory/review_package.json",
    "graph": "specs/knowledge-architecture/graph/graph_manifest.json",
    "openapi": "specs/openapi/gk-ke-v1.openapi.json",
}


def snapshot() -> dict:
    out = {}
    for key, rel in DATA.items():
        out[key] = load_json(rel)
    return out


# ------------------------------------------------- 拒绝判定（与门禁同构）

ALLOWED_ACTIONS = {"CREATE_FOLLOWUP_TASK", "RECORD_CONTACT_OUTCOME"}
FORBIDDEN_ACTIONS = {"TRANSFER_FUNDS", "DISBURSE_LOAN", "APPROVE_CREDIT",
                     "EXECUTE_WIRE", "CREATE_LOAN_CONTRACT", "SUBMIT_CREDIT_APPLICATION"}


def eval_release(doc: dict) -> dict:
    """OC-03 发布判定（C03 §5 Publishable + §6 回滚/撤销）。"""
    v = {
        "ValidSchema": bool(doc.get("schemaValid")),
        "RefClosure": bool(doc.get("refClosure")),
        "SourceUsable": bool(doc.get("sourceUsable")),
        "IdentityResolved": bool(doc.get("identityResolved")),
        "NoBlockingConflict": not doc.get("blockingConflict"),
        "ApprovedHash": doc.get("targetHash") == doc.get("currentHash"),
        "RequiredCapabilitiesReady": bool(doc.get("requiredCapabilitiesReady")),
        "QualityGate": bool(doc.get("qualityGatePassed")),
    }
    rejections: list[dict] = []
    if doc.get("targetHash") != doc.get("currentHash") and doc.get("published"):
        rejections.append({"code": "CONTENT_CHANGED_AFTER_APPROVAL", "http": 409,
                           "clause": "C03 §5 审批绑定 hash"})
    for d in doc.get("decisions", []):
        if d.get("reviewerPrincipal") == d.get("authorPrincipal") and d.get("decision") == "APPROVED":
            rejections.append({"code": "SELF_APPROVAL", "http": 403, "clause": "C03 §4 双维审核"})
        if d.get("expired") and d.get("countedInRelease"):
            rejections.append({"code": "EXPIRED_APPROVAL_COUNTED", "http": 409, "clause": "C03 §5"})
    for p in doc.get("projections", []):
        if p.get("published") and not p.get("ready"):
            rejections.append({"code": "HALF_PUBLISH", "http": 409, "clause": "C03 §6 原子发布"})
    for it in doc.get("runtimeStates", []):
        if it.get("state") == "REVOKED" and it.get("stillSearchable"):
            rejections.append({"code": "REVOKED_STILL_SEARCHABLE", "http": 409, "clause": "C03 §5 运行有效性"})
    for rb in doc.get("rollbacks", []):
        if rb.get("toReleaseRevoked") and rb.get("performed"):
            rejections.append({"code": "ROLLBACK_TO_REVOKED", "http": 409, "clause": "C03 §6.6"})
    for pf in doc.get("purposeFlags", []):
        if pf.get("from") == "RESEARCH" and pf.get("to") == "RECOMMENDATION" and pf.get("silentlyUpgraded"):
            rejections.append({"code": "PURPOSE_FLAG_SILENT_UPGRADE", "http": 422, "clause": "C03 §4"})
    return {"publishable": v, "allPass": all(v.values()), "rejections": rejections}


def eval_activation(doc: dict, policy: dict, route_task: str | None = None) -> dict:
    """OC-04 路由与计划判定（C06 §2）。"""
    rejections: list[dict] = []
    routing = None
    if route_task is not None:
        rules = [r for r in (policy or {}).get("rules", []) if r.get("taskType") == route_task]
        if not rules:
            routing = {"task": route_task, "decision": "REJECT", "reason": "no matching rule",
                       "clause": "OWNER-003 §4.2 无匹配"}
            rejections.append({"code": "NO_MATCH_REJECT", "http": 409, "clause": "OWNER-003 §4.2"})
        else:
            best = min(r.get("priority", 999) for r in rules)
            winners = [r for r in rules if r.get("priority", 999) == best]
            if len(winners) > 1:
                routing = {"task": route_task, "decision": "ROUTE_AMBIGUOUS",
                           "candidates": sorted(str(r.get("ruleId")) for r in winners),
                           "clause": "C06 §2 同优先级歧义"}
                rejections.append({"code": "ROUTE_AMBIGUOUS", "http": 409, "clause": "C06 §2"})
            else:
                routing = {"task": route_task, "decision": "ROUTED",
                           "rule": winners[0].get("ruleId"), "mode": winners[0].get("mode")}

    steps = doc.get("steps", [])
    for s in steps:
        ref = str(s.get("executorRef", "")).upper()
        if any(a in ref for a in FORBIDDEN_ACTIONS):
            rejections.append({"code": "GITS_WRITEBACK_IN_KERT_PLAN", "http": 422, "clause": "C06 §2"})
        if s.get("sideEffect") not in {"NONE", "READ_ONLY", "PROPOSE_ONLY"}:
            rejections.append({"code": "UNEXPECTED_SIDE_EFFECT", "http": 422, "clause": "C06 §2"})

    graph = {s["stepId"]: list(s.get("dependencyStepIds", [])) for s in steps}
    seen: set[str] = set()
    stack: set[str] = set()

    def cyclic(n: str) -> bool:
        if n in seen:
            return False
        if n in stack:
            return True
        stack.add(n)
        for d in graph.get(n, []):
            if d in graph and cyclic(d):
                return True
        stack.discard(n)
        seen.add(n)
        return False

    if any(cyclic(n) for n in graph):
        rejections.append({"code": "DEPENDENCY_CYCLE", "http": 409, "clause": "C08 L4-1"})

    missing = [c for c in doc.get("requiredCapabilityRefs", [])
               if c not in {r.get("id") for r in doc.get("capabilityRefs", [])}]
    if missing:
        rejections.append({"code": "REQUIRED_CAPABILITY_MISSING", "http": 409,
                           "detail": missing, "clause": "C08 L4-1"})

    return {"routing": routing, "rejections": rejections}


def eval_closed_loop(doc: dict) -> dict:
    """OC-05 闭环判定（C06 §3 / C03 §8）。"""
    rejections: list[dict] = []
    stmt = doc.get("interpretation", {}).get("statement3000W", {})
    if stmt:
        if stmt.get("modality") != "CUSTOMER_STATEMENT" or stmt.get("treatedAsRealLoanDemand") \
                or stmt.get("treatedAsApprovedAmount") or stmt.get("treatedAsDrawableAmount"):
            rejections.append({"code": "STATEMENT_AS_FACT_REJECTED", "http": 422, "clause": "C03 §8"})
    hc = doc.get("healthCheck", {})
    if hc.get("purposeKnown") is False:
        if hc.get("result") != "UNKNOWN" or not hc.get("followUpQuestions") \
                or hc.get("passedAdmissionBasedOnGraphRelation"):
            rejections.append({"code": "UNKNOWN_PURPOSE_NOT_ADMITTED", "http": 422, "clause": "C03 §8"})
    follow = doc.get("simulatedFollowUp", {})
    if follow.get("attempted") is True:
        if follow.get("actionType") in FORBIDDEN_ACTIONS:
            rejections.append({"code": "FORBIDDEN_ACTION_REJECTED", "http": 422, "clause": "OWNER-003 §6.1"})
        if not follow.get("confirmationRef"):
            rejections.append({"code": "MISSING_CONFIRMATION_REJECTED", "http": 403, "clause": "C06 §1"})
    for bad in doc.get("invalidVersionAttempts", []):
        if bad.get("attempted") and bad.get("accepted"):
            rejections.append({"code": "STALE_TARGET_VERSION_REJECTED", "http": 409, "clause": "C06 §2"})
    to = doc.get("timeoutReconciliation", {})
    if to.get("timedOut"):
        if to.get("status") != "RESULT_UNKNOWN" or not to.get("queriedTargetReceipt") \
                or to.get("declaredFailureImmediately"):
            rejections.append({"code": "TIMEOUT_RESULT_UNKNOWN", "http": 200, "clause": "C06 §3"})
    return {"rejections": rejections}


# --------------------------------------------------------------- 违规注入

INJECTIONS = {
    # OC-03
    "OC03_CONTENT_CHANGED": ("release", {"targetHash": None, "currentHash": None}),
    "OC03_SELF_APPROVAL": ("release", {"decisions": [{"reviewerPrincipal": "SIM-AUTHOR",
                                                      "authorPrincipal": "SIM-AUTHOR",
                                                      "decision": "APPROVED",
                                                      "countedInRelease": True}]}),
    "OC03_EXPIRED_APPROVAL": ("release", {"decisions": [{"reviewerPrincipal": "R",
                                                         "authorPrincipal": "A",
                                                         "decision": "APPROVED",
                                                         "expired": True,
                                                         "countedInRelease": True}]}),
    "OC03_HALF_PUBLISH": ("release", {"projections": [{"name": "graph", "ready": False, "published": True}]}),
    "OC03_REVOKED_SEARCHABLE": ("release", {"runtimeStates": [{"assetId": "X", "state": "REVOKED",
                                                               "stillSearchable": True}]}),
    "OC03_ROLLBACK_TO_REVOKED": ("release", {"rollbacks": [{"toReleaseRevoked": True, "performed": True,
                                                            "toReleaseId": "SIM-REL-BAD"}]}),
    "OC03_PURPOSE_UPGRADE": ("release", {"purposeFlags": [{"from": "RESEARCH", "to": "RECOMMENDATION",
                                                           "silentlyUpgraded": True}]}),
    # OC-04
    "OC04_ROUTE_AMBIGUOUS": ("activation", {"routeTask": "AMBIGUOUS_TASK"}),
    "OC04_NO_MATCH": ("activation", {"routeTask": "UNKNOWN_TASK"}),
    "OC04_GITS_WRITEBACK": ("activation", {"steps": [{"stepId": "SX", "executorRef": "TRANSFER_FUNDS",
                                                      "inputBindings": {}, "dependencyStepIds": [],
                                                      "evidenceRequirement": "E", "onFailure": "FAIL_CLOSED",
                                                      "sideEffect": "NONE"}]}),
    "OC04_DEPENDENCY_CYCLE": ("activation", {"steps": [
        {"stepId": "A", "executorRef": "SIM-CAP-INTERPRET", "inputBindings": {}, "dependencyStepIds": ["B"],
         "evidenceRequirement": "E", "onFailure": "FAIL_CLOSED", "sideEffect": "NONE"},
        {"stepId": "B", "executorRef": "SIM-CAP-INTERPRET", "inputBindings": {}, "dependencyStepIds": ["A"],
         "evidenceRequirement": "E", "onFailure": "FAIL_CLOSED", "sideEffect": "NONE"}]}),
    "OC04_MISSING_CAPABILITY": ("activation", {"requiredCapabilityRefs": ["SIM-CAP-NOT-REGISTERED"]}),
    # OC-05
    "OC05_FORBIDDEN_ACTION": ("closed_loop", {"simulatedFollowUp": {"actionType": "TRANSFER_FUNDS",
                                                                    "confirmationRef": "SIM-CONFIRM-001",
                                                                    "expectedTargetVersion": "1",
                                                                    "attempted": True}}),
    "OC05_STALE_VERSION": ("closed_loop", {"invalidVersionAttempts": [{"targetVersion": "0",
                                                                       "attempted": True, "accepted": True}]}),
    "OC05_MISSING_CONFIRMATION": ("closed_loop", {"simulatedFollowUp": {"actionType": "CREATE_FOLLOWUP_TASK",
                                                                        "confirmationRef": None,
                                                                        "expectedTargetVersion": "1",
                                                                        "attempted": True}}),
    "OC05_TIMEOUT_AS_FAILURE": ("closed_loop", {"timeoutReconciliation": {"timedOut": True, "status": "FAILED",
                                                                          "queriedTargetReceipt": False,
                                                                          "declaredFailureImmediately": True}}),
    "OC05_STATEMENT_AS_FACT": ("closed_loop", {"interpretation": {"statement3000W": {
        "modality": "FACT", "treatedAsRealLoanDemand": True, "treatedAsApprovedAmount": True,
        "treatedAsDrawableAmount": True, "sourceRef": "x"}}}),
    "OC05_UNKNOWN_ADMITTED": ("closed_loop", {"healthCheck": {"purposeKnown": False, "result": "PASSED",
                                                              "followUpQuestions": [],
                                                              "passedAdmissionBasedOnGraphRelation": True}}),
}


def apply_injection(kind: str, injection_id: str) -> dict:
    base = snapshot()
    if injection_id == "NONE":
        return base
    entry = INJECTIONS.get(injection_id)
    if not entry:
        return base
    target, patch = entry
    if target == "activation":
        patch = {k: v for k, v in patch.items()}
        if "routeTask" in patch:
            base["_route_task"] = patch.pop("routeTask")
        plan = dict(base["plan"] or {})
        plan.update(patch)
        base["plan"] = plan
    elif target == "closed_loop":
        # 违规注入：与正例**合并**（只覆盖被注入字段）
        doc = {}
        for k, v in (base["closed_loop"] or {}).items():
            doc[k] = v
        for k, v in patch.items():
            if isinstance(v, dict) and isinstance(doc.get(k), dict):
                merged = dict(doc[k]); merged.update(v); doc[k] = merged
            else:
                doc[k] = v
        base["closed_loop"] = doc
    elif target == "release":
        if "targetHash" in patch and patch["targetHash"] is None:
            doc = dict(base["release"] or {})
            doc["hash_variant"] = "changed"
            doc["currentHash"] = "b" * 64   # 与原 targetHash 不同
            base["release"] = doc
        else:
            doc = {}
            for k, v in (base["release"] or {}).items():
                doc[k] = v
            for k, v in patch.items():
                doc[k] = v
            base["release"] = doc
    return base


# ---------------------------------------------------------------- HTTP 服务

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):  # 保持安静
        pass

    def _send(self, code: int, body: bytes, ctype: str):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, obj, code: int = 200):
        self._send(code, json.dumps(obj, ensure_ascii=False, indent=2).encode("utf-8"),
                   "application/json; charset=utf-8")

    def do_POST(self):
        """唯一的写操作：把验收答复落盘到 evidence/ 目录（不碰任何权威源）。"""
        if urlparse(self.path).path != "/api/save":
            self._json({"error": "not found"}, 404)
            return
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length) if length else b"{}"
        try:
            payload = json.loads(raw.decode("utf-8"))
        except Exception as exc:
            self._json({"ok": False, "error": f"invalid json: {exc}"}, 400)
            return

        outdir = ROOT / "evidence" / "GK-KE-验收答复"
        outdir.mkdir(parents=True, exist_ok=True)
        stamp = __import__("datetime").datetime.now().strftime("%Y%m%d-%H%M%S")
        path = outdir / f"答复-{stamp}.json"
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        self._json({"ok": True, "saved": str(path.relative_to(ROOT))})

    def do_GET(self):
        path = urlparse(self.path).path
        if path in ("/", "/index.html"):
            html = (ROOT / "tools" / "gk-ke-console" / "index.html").read_bytes()
            self._send(200, html, "text/html; charset=utf-8")
            return
        if path == "/api/snapshot":
            self._json(snapshot())
            return
        if path == "/api/injections":
            self._json({"injections": sorted(INJECTIONS.keys()),
                        "descriptions": {k: f"{k}" for k in INJECTIONS}})
            return
        if path.startswith("/api/console"):
            from urllib.parse import parse_qs
            qs = parse_qs(urlparse(self.path).query)
            inj = (qs.get("inject") or ["NONE"])[0]
            state = apply_injection("console", inj)
            release = eval_release(state.get("release") or {})
            activation = eval_activation(state.get("plan") or {},
                                         state.get("route_policy") or {},
                                         state.get("_route_task"))
            loop = eval_closed_loop(state.get("closed_loop") or {})
            self._json({
                "simulationOnly": True,
                "productionReady": False,
                "injection": inj,
                "oc03": release,
                "oc04": activation,
                "oc05": loop,
                "data": state,
            })
            return
        self._json({"error": "not found", "path": path}, 404)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--host", default="127.0.0.1")
    args = ap.parse_args()

    console = ROOT / "tools" / "gk-ke-console" / "index.html"
    if not console.is_file():
        raise SystemExit(f"console missing: {console}")

    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print("=" * 72)
    print("GK-KE 人工验收台（只读 / SIM）")
    print("=" * 72)
    print(f"  打开: http://{args.host}:{args.port}/")
    print("  OC-03 审核发布 | OC-04 地图与计划 | OC-05 经营闭环")
    print("  所有数据为 SIM 夹具；注入违规不会修改任何文件")
    print("  Ctrl+C 停止")
    print("=" * 72)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n已停止")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
