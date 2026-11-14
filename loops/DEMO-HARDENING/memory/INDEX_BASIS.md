# INDEX_BASIS — 演示就绪批次（2026-11-14）

## 索引新鲜度

- 开工：`INDEX_ABSENT @ make index-status` → `WARN: F1 索引产物缺失：.ua/knowledge-graph.json`、`WARN: F2 merge-meta 未记录 kertCommit`。
- 收工：`INDEX_ABSENT`，`ua_index_gate: WARN (nodes=None)`；本机未建立两仓合并图。
- 因索引未覆盖，本批次全部按 **L4 回源** 定位；以下只记「候选影响面 + 回源结论」，索引本身为 DERIVED，不作 Gate / ADR 依据。

## 候选影响面（索引缺席，改由文件清单给出，非索引产物）

- `scripts/demo-startup.sh`、`scripts/demo-smoke.sh`、`DEMO-FREEZE.md`、`.gitignore`
- `frontend/playwright.config.ts`、`frontend/e2e/uat/*`、`frontend/e2e/qa-e2e-acceptance.spec.ts`
- `frontend/src/api/productCenter.ts`、`frontend/src/components/product-center/ProductChapterStack.vue`
- `frontend/src/assets/styles/theme.css`（只读回源，未修改）
- KERT：`src/kert/application/skills.py`、`src/kert/application/product_recommendation/eligibility.py`

## 回源结论（文件:行，全部指向 2026-11-14 本批次落盘版本）

| 结论 | 回源 |
|---|---|
| E2E 原指向 5173、代理默认 8080，与演示链路不一致 | `frontend/playwright.config.ts:3,35,46`（现统一 15173 并注入 18080/8107） |
| 截图证据沿用 `QA_EVIDENCE_DIR` 单一约定，未另造目录 | `frontend/e2e/uat/_harness.ts:8,9,202-205`；`.gitignore:45`（`test-results/`） |
| Playwright 每轮清空 `outputDir`，证据须与之隔离 | `frontend/playwright.config.ts:21` |
| 单后端并发导致时序红灯，收敛到 4 worker | `frontend/playwright.config.ts:15` |
| PRICING 章节有 `pricingItems` 却无渲染分支 ⇒ 空壳 | `frontend/src/components/product-center/ProductChapterStack.vue`（本批次新增 06 分支，字段对齐 `specs/product-center/product-center-api.openapi.json` 的 `PkcPricingItem`） |
| V9 设计令牌（白侧栏 / 17 项菜单 / Inter 字体栈）与 V8.1 遗留断言漂移 | `frontend/src/assets/styles/theme.css`（`--v8-sidebar-bg:#FFFFFF`、`--font-sans` 含 Inter）；`frontend/src/layouts/navConfig.ts`（5+4+2+2+4=17） |
| KERT 示意型 output-schema 的嵌套键被误当顶层必含键 | `Leibniz-KERT/src/kert/application/skills.py:69,298` |
| 产品卡 `minRating: BB` 不在 `_RATING_ORDER` 内致 `tuple.index` 抛错 | `Leibniz-KERT/src/kert/application/product_recommendation/eligibility.py:80` |
| 日志固定为 `logs/demo/`，PID 文件 `logs/demo/pids/`，`stop_stack` 不再用 `pkill -f` | `scripts/demo-startup.sh:40,41,80,93,188` |
| `status` 的 READY = 4 端口 200 + 冒烟 0 FAIL | `scripts/demo-startup.sh:326`；`scripts/demo-smoke.sh` 末行 `exit "$FAIL"` |
| `up` 与 `restart` 同一分支，`restart` 必先 `stop_stack` | `scripts/demo-startup.sh:389` |

## 校验现状

- `make index-status` → WARN（索引缺失），退出码 0。
- `make memory-check LOOP=DEMO-HARDENING` / `make evidence-check LOOP=DEMO-HARDENING` → FAIL：
  缺 `EVIDENCE.json` / `EVIDENCE.md` / `FAILURES.md` / `HANDOFF.md`，以及共享记忆 5 件套
  （`SHARED_MEMORY.md`、`memory/PROTOCOL.md`、`ROLE_BOARD.yaml`、`ORCHESTRATOR.md`）。
  这些文件自 2026-10-28 该 Loop 建立即缺失，且 `STATE.json` 已冻结 `qa_pass`；
  本批次**不补造历史证据**，登记为遗留问题。
