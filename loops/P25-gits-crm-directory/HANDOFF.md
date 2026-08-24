# P25-gits-crm-directory｜Handoff

| 项 | 状态 |
|---|---|
| 交付对象 | GITS CRM 客户目录（身份键 only） |
| 开发自检 | 单元/前端测试由 E2E Owner 复跑通过；未写 `DEV_SELF_CHECK_PASS` 门禁脚本 |
| 独立QA | `PENDING` |
| 生产就绪 | `NO` |

## 交付物

- `PUT /api/v1/engagement/customer/{customerId}` upsert CRM 主档
- `POST /api/v1/engagement/crm-customer-master/reload` 灌夹具
- 启动加载 `docs/dd/fixtures/gits-crm-customer-master.json`
- 工作台「刷新客户目录」：reload（404 忽略）+ GET list
- 身份键：`CUST-CORP-0001` / `RM-ZW-001`

E2E Owner 复跑（2026-08-22）：

- `./mvnw -pl apps/api -am -Dsurefire.failIfNoSpecifiedTests=false -Dtest=CrmCustomerMasterServiceTest,CustomerContextControllerTest test` → 14 passed
- `cd frontend && npx vitest run src/api/__tests__/engagement.spec.ts src/views/__tests__/EngagementWorkspace.spec.ts` → 50 passed

## 开放项与禁止声明

不得将上述复跑写成 QA、真实浏览器 E2E、客户验收或生产冻结。未写 `QA_PASS`。未碰 P24。未 commit。

下一批（非本 Loop）：外联/会面 Skill 切流；DKWS 按 customerId 落 KI。
