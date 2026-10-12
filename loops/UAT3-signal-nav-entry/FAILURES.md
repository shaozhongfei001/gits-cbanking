# UAT3-signal-nav-entry｜Failures（append-only）

失败必须在修改实现之前由 `scripts/record_gate.py`追加。每项至少包含时间、Gate、命令、退出码、证据文件、初步分类和下一动作；修复后追加根因、变更SHA与原命令重跑结果，不覆盖原记录。

## 2026-09-26T03:55Z｜D-4 根因判定（TL/Feature Pilot 记录，修复前）

- 现象：`SignalsView.spec.ts` 的 `p08-open-engagements` / `p08-open-journey` / `signals-tab-*` 取不到元素。
- 回源：
  - `git show HEAD:frontend/src/views/SignalsView.vue` **含**两个跨页入口（131/134 行），
    当前工作区 diff 显示它们**被在途未提交改动删除**（同时删除 `.related-link` 样式）；
  - `signals-tab-p08/p10/p11` 由 `components/shell/SignalsDomainTabs.vue:26/33/40` 提供，
    且 `SignalsView.vue:129` **仍在使用**该组件 —— 故 Tab 未缺失，是测试所在层级取不到（先被入口断言打断）。
- 定性（可达性为据，不是"测试说了算"）：
  - 侧栏 `navConfig.ts` **无 `/engagements` 菜单项**（仅有域映射，无入口）；
  - 删除跨页入口后，P10 互动对象主页（有效路由 `router/index.ts:116`）**没有任何 UI 入口**，只能 URL 直达 ⇒ **真实可达性退化**。
- 处置：恢复两个 router-link 与样式；`it.fails` 改回正向断言。
