# GK6-simulation-factory｜Next Session Baton

| 字段 | 值 |
|---|---|
| **Updated** | `2026-09-10T15:25:00Z` |
| **holder** | `independent_qa` |
| **packet** | `GK6-simulation-factory` |
| **wave** | `W0` |
| **do_not_start** | REAL_E2E_PASS、BUSINESS_SIGNED |

短提示词：你是 `independent_qa`（独立 QA，禁止 implementation actor 自签）。6 个 implementation gate 已全部 PASS（见 `EVIDENCE.json`），请独立复核并在 `EVIDENCE.json.independent_qa` 记录 QA_PASS（含 actor、session、evidence_file、evidence_sha256）。

## 待办

1. 独立运行（worktree 根 cwd）：
   - `make check`（合同基线未改，应 PASS）
   - `python3 tools/gk-ke-simulation/build_simulation.py`（确定性重写，应无 diff）
   - `python3 tools/gk-ke-simulation/validate_package.py`（117/117 PASS）
   - `python3 -m unittest tests.tooling.test_gk_ke_simulation -v`（11 项）
   - `make security-check`
2. 复核 T30–T33：
   - T30：12/24/6/30/144/288/720/12/12/18 计数；C001 日均 2,983,333.33 CNY；借贷同币相等反向；closing=opening+ΣsignedAmount；次日 opening=前日 closing。
   - T31：manifest 哈希一致；schema 正/负例；oracle 隔离。
   - T32：`tools/gk-ke-simulation/guards.py` + 负例测试（生产写动作、自批、陈旧版本、预测当事实、客户端注入授权均被拒）。
   - T33：simulationOnly=true、SIM- 前缀、oracle 不进 graph/documents 语料。
3. 红线复核：未改 `specs/`、`generated/`；无模型/网络/真实 DB；无真实客户/机构/凭据。
4. QA 通过后更新 STATE.status=qa_passed 并交棒 Tech Lead 关闭 Loop；不通过则写 FAILURES.md 退回 gk6-pilot。
