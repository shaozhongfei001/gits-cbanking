# UAT2-component-test-drift｜Failures（append-only）

失败必须在修改实现之前由 `scripts/record_gate.py`追加。每项至少包含时间、Gate、命令、退出码、证据文件、初步分类和下一动作；修复后追加根因、变更SHA与原命令重跑结果，不覆盖原记录。

## 20260926T033949Z｜e2e_regression

- Command: `bash scripts/uat_wave.sh uat2_regression e2e/uat/w0-route-sweep.spec.ts e2e/uat/w1-workspace-domain.spec.ts e2e/uat/w2-customer-domain.spec.ts`
- Exit: `1`
- Evidence: `loops/UAT2-component-test-drift/evidence/e2e_regression-20260926T033949Z.log`
- Classification: `PENDING_ROOT_CAUSE`
- Next: diagnose, record root cause, fix, rerun the original gate.

## 2026-09-26T03:35Z｜e2e_regression｜根因与处置（Feature Pilot 追加）

### F-UAT2-01｜W1 P11 用例依赖「旅程列表第一条」，被同批次的「启动旅程」用例污染
- 现象：`W1 经营域 › P11 互动工作区` 断言页面文本含 `华东精工|装备|CUST-CORP-0001` 失败，
  实际渲染的是另一客户（或无客户上下文）的工作区。
- 根因（回源）：`w1-workspace-domain.spec.ts:29` 用 `firstId('/api/v1/engagement/journey','journeyId')` 取**列表第一条**；
  而同批次 `P45 启动旅程` 用例（`w1-workspace-domain.spec.ts:47-63`）会真实调用启动旅程接口**写入新旅程**，
  列表首条随之漂移 ⇒ 用例间存在**数据耦合**，首轮通过纯属偶然。
- 分类：`GATE_DEFECT`（我的 E2E 用例不具幂等性），非产品缺陷。
- 处置：新增 `_harness.pickJourneyId(customerId)` —— 按 customerId 精确挑选种子旅程（取不到才回退首条），
  W1 与 W6 统一改用该选择方式，消除跨用例数据耦合。
