# P24-DKWS-Platform 交接

| 字段 | 值 |
|---|---|
| **Updated** | `2026-08-21T11:41:00Z` |
| **holder** | `independent_qa` |
| **packet** | `P24-dkws-platform` |
| **wave** | `W0` |
| **do_not_start** | REAL_E2E_PASS、BUSINESS_SIGNED、QA_PASS_BY_IMPLEMENTATION |

短提示词：你是 `independent_qa`。feature_pilot 已补齐证据板（`EVIDENCE.json` + 共享记忆）。禁止 feature_pilot/tech_lead 代签。复跑 `PYTHONPATH=src:tests:scripts python3 -m unittest discover -s tests -v`（在 scenario/dkws-platform）与 `make evidence-check LOOP=P24-dkws-platform` 后用 `scripts/qa_attest.py` 写入 `independent_qa`。不要调用 `--llm real`。

## feature_pilot 证据板（2026-08-21）

LOOP 门禁已改为可执行 unittest/CLI；十个 gate 均经 `scripts/record_gate.py` 实跑 PASS。baseline_commit=`2e1118d251ff065d3793e6d771d28a306dd5a1af`。未把独立 QA 旧日志哈希填到 P0–P9。

上一轮 IQA REJECT 证据仍保留：`evidence/independent_qa_20260821T094459Z.log`

## 独立 QA 应复跑

1. `make evidence-check LOOP=P24-dkws-platform`
2. `cd scenario/dkws-platform && PYTHONPATH=src:tests:scripts python3 -m unittest discover -s tests -v`
3. 可选 CLI：`cd scenario/dkws-platform && PYTHONPATH=src python3 -m dkws --help`（禁止 `--llm real`）
4. 通过则 `python3 scripts/qa_attest.py --loop P24-dkws-platform --actor independent_qa --session iqa-p24-<ts> --decision pass --evidence <log>`
5. 失败则 `--decision reject` 并追加 FAILURES.md

## 禁止

- 开发角色不得自签 `QA_PASS`
- 不得声称 `REAL_E2E_PASS` 或生产冻结

## 架构委员会决议后续任务（2026-08-23，ARCH-REVIEW-2026-08-23-001 §7 决议 3）

- [ ] **CI diagram 生成步骤**：`diagrams/architecture.png` 已随 P24 架构变更删除（旧图含已移除的 knowledge-filesystem 节点，保留即误导）。当前 `.github/workflows/ci.yml` 无任何 diagram 生成步骤。须在 CI 增加 playwright 环境的 `diagrams/gen_arch.py` PNG 生成步骤（或登记独立任务跟踪），完成后恢复 `diagrams/ARCHITECTURE.md` 第 3 行的 PNG 引用标注。
