# NEXT_SESSION — DEMO-HARDENING

| 项 | 值 |
|----|----|
| **holder** | `tech_lead` |
| **next_holder** | `owner_review` |
| **索引新鲜度** | `INDEX_ABSENT`（`.ua/knowledge-graph.json` 缺失；`make index-status` = WARN，退出码 0） |
| **本批次** | 2026-11-14 演示就绪三件事；2026-11-15 P15 会中工作区修复；2026-11-15 全站页头一行化 |

> 保持与 `STATE.json`（`status=qa_pass`, `baton.holder=tech_lead`, `next_holder=owner_review`）一致；
> 本批次未回退、未改写任何已完成 Gate 状态。

## 已完成（本批次）

1. GITS 全量 Playwright E2E：180 passed / 0 failed / 0 flaky / 2 个历史 `test.skip`；连续 3 轮全绿。
   58 条演示路由逐场景截图 + 58 份 sidecar 清单，19 张主验收截图，3 张 PC1 宽度截图，PNG 校验 0 损坏。
2. KERT `tests/e2e` pytest：69 passed / 0 failed / 0 skipped（`E2E_REQUIRE_SERVICES=1`）。
3. 两仓 `main` 与 `github/main` 同步、工作区干净（本批次代码已入库）。
4. 启停固化：固定 `logs/demo/`、PID 文件精确停止、`restart` 语义、`status` 输出 `READY` / `NOT READY`；
   `DEMO-FREEZE.md` §3 / §8 / §9 已按实际补全。
5. P15 会中工作区：修复 5s 轮询驱动全页四态切换导致的刷屏（浏览器实证 13s 内 3 轮循环 → 仅首载一次，
   输入节点与内容保留）；「录音」四组文案改为「解读」，会议记录页签预生成 10 轮客户经理 ↔ 客户演示对话。
6. 全站页头一行化：盘点 51 页（34 直接 + 17 间接）共用 `ObjectHeader.vue`，删除 30px 大号标题的视觉呈现
   （`sr-only h1` 保留语义与文本契约），小标题 + 当前状态 + 返回按钮同一行，标题区 99px → 37px；
   同步修 `EngagementWorkspace.vue` 双 h1，`DESIGN.md` 与 `ObjectHeader.spec.ts` 同步约定。
7. 本批次改动已按 Owner 指示提交并推送，两仓 `main` 与 `github/main` 同步（commit 以 `git log` 为准）。

## 下一位（owner_review）待办

- 演示前执行 `bash scripts/demo-startup.sh status`，确认末行 `READY`；结束执行 `down`。
- 裁决遗留问题清单：S14 KYC 404、`theme-toggle` 未实现导致的 2 个历史 `test.skip`、
  KERT 全量 pytest 的示例工作区知识地图缺口、本 Loop 缺失的受控证据文件、
  `INDEX_ABSENT` 是否按 GOV-CFI-001 SOP 建索引。
- 裁决是否彻底删除 `object-header` 内 `sr-only` 标题文字（需同步改 9 处测试/巡检断言），
  以及 8 处自建页内大标题（登录页品牌、`ProductHero`、Analytics* 等）是否一并降级。
- 确认 `frontend/scripts/w9a-escort.spec.ts` 的 P01 `titleContains:'我的客户经营'` 与实现不一致（既有问题）。
- 详细回源结论见 `memory/INDEX_BASIS.md`。
