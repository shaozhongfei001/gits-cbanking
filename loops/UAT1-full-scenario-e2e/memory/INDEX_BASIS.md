# UAT1-full-scenario-e2e｜INDEX_BASIS（代码事实索引使用登记）

## 索引新鲜度声明

- **索引状态：INDEX_FRESH**（收工实测 `make index-status` → PASS，nodes=4492，drift=0，kert_drift=0）。
- **但本轮结论未依赖索引**：本轮问题是**运行时行为**判定（浏览器可见性、接口状态码、降级文案），
  索引不含函数级调用边与运行时信息；所有结论一律**回源到源码行 + 运行时实测**：
  - `frontend/src/router/index.ts:6-366`（59 条路由清单回源）
  - `frontend/src/api/engagement.ts:455-470`（修复前 `fetchReport` 占位伪造，F-UAT1-06）
  - `frontend/src/views/MeetingCaptureView.vue:73`（修复前 journeyId 冒充 interactionId，F-UAT1-07）
  - `frontend/src/api/v11.ts:319-322`（`/recording-consents/latest/{interactionId}` 契约）
  - `apps/api/src/main/java/com/gien/gits/api/controller/RecordingConsentController.java:39-43`（404 语义）
  - `apps/api/src/main/java/com/gien/gits/api/controller/EngagementJourneyController.java:114`（报告端点，合同未登记 F-UAT1-09）
  - `Leibniz-KERT/src/kert/api/server.py:403,1047`（ANALYTICS_UNAVAILABLE 根因，F-UAT1-01）
- 未把任何索引输出写入 `evidence/`、未用于 Gate 判定（索引为 DERIVED，不得升格）。
