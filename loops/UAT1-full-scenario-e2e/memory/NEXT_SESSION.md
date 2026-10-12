# UAT1-full-scenario-e2e｜Next Session Baton

| 字段 | 值 |
|---|---|
| **Updated** | `2026-09-26T05:14:35.289381+00:00` |
| **holder** | `e2e_owner` |
| **packet** | `UAT1-full-scenario-e2e` |
| **wave** | `W0–W8 全绿，待独立 QA` |
| **index_basis** | `INDEX_ABSENT`（本轮以源码回源 + 运行时实测为准，未使用 `.ua` 派生索引） |
| **do_not_start** | QA_PASS、REAL_E2E_PASS、BUSINESS_SIGNED |

## 本轮已完成（e2e_owner）

- 11 个门禁全 PASS，115 个功能点用例全通过；交付包 `UAT_PACKAGE.md` 已生成。
- 修复：F-UAT1-01（KERT DuckDB 未注入 → 分析全端点 503）、F-UAT1-06（报告页伪造数据，P0 红线）、
  F-UAT1-07（录音同意参数语义）、F-UAT1-08（W8 门禁自身 glob 误伤 + 注入生效未校验）。
- 变异复验：真实停掉 KERT 8107 → W5 5 failed / 1 passed → 恢复后 6/6 PASS（断言非空转）。

## 下一棒（independent_qa）要做的事

1. 独立复跑至少两个波次（建议 `w0_route_sweep` 与 `w6_journey_closed_loop`），确认非偶发绿；
2. 复核 `FAILURES.md` 中 F-UAT1-02/03（门禁判定放宽）是否放水：13 个降级壳页与合成 ID 路由的
   放宽是否有据（依据：页面显式降级标注，符合诚实性红线 E1/E2）；
3. 复核 F-UAT1-09 合同缺口是否需补登记（`/engagement/journey/{journeyId}/reports` 未入 OpenAPI）；
4. 通过后写入 `EVIDENCE.json.independent_qa`，交 Owner 做人工 UAT。

短提示词：你是 `independent_qa`。复核 UAT1 全部波次与 FAILURES 判定，独立复跑后再签 QA_PASS；不许沿用 implementation 的自述结论。
