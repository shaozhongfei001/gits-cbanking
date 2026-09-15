# GK17-ontology-unified-map｜Failures（append-only）

失败必须在修改实现之前由 `scripts/record_gate.py`追加。每项至少包含时间、Gate、命令、退出码、证据文件、初步分类和下一动作；修复后追加根因、变更SHA与原命令重跑结果，不覆盖原记录。

## 20260915T002544Z｜frontend_test

- Command: `make frontend-test`
- Exit: `2`
- Evidence: `loops/GK17-ontology-unified-map/evidence/frontend_test-20260915T002544Z.log`
- Classification: `PENDING_ROOT_CAUSE`
- Next: diagnose, record root cause, fix, rerun the original gate.

### 根因（已定位，2026-09-15）

`make frontend-test` 的第一步是 `npm ci`（锁文件一致性安装），它会**清空并重建 `frontend/node_modules`**。
本环境的**沙箱批量删除守卫**拦截了该操作：

```
npm error [safe-delete][SAFE_DELETE_BULK_CONFIRM_REQUIRED]
  {"count":538,"threshold":500,"scope":"turn",
   "targets":["/home/szf/dev/gits-cbanking/frontend/node_modules/@css-render"],"targetCount":1}
```

- **分类**：`ENVIRONMENT_LIMITATION`（**非产品缺陷、非本 Loop 引入**）
- **证据**：`evidence/frontend_test-20260915T002544Z.log`（含完整 STDERR）
- **代码相关性**：W1 仅改动 `specs/semantic/` 与 `generated/semantic/`，**与前端无交集**；
  W0 基线已实测前端为绿（`npx vue-tsc --noEmit` = 0 错误；`npx vitest --run` = 63 文件 / 342 通过）

### 处置（**不擅自弱化门禁**）

1. **本条目保持 fail 状态**：`npm ci` 确实未执行成功 ⇒ **不得记为 pass**；
2. 不在本 Loop 内把 gate 命令改成"跳过 `npm ci` 的等价物" —— 那会移除门禁四项职责中的
   「锁文件安装」一项，属**门禁弱化**，须走治理决策而**非 TL 自行处置**；
3. 记录两个候选出路，**待 Owner/TL 治理裁定**：
   - **(a) 环境侧**：为本 Loop 的验证放行 `npm ci` 的删除额度（或改用 `npm install --prefer-offline` 等不触发阈值的等价安装）；
   - **(b) 门禁侧**：经批准后把 `frontend_test` 拆为「安装」与「类型+测试」两道，前者标注环境前置条件；
4. **对 W1 的影响**：**无**。W1 的 ACCEPT 判据为
   「`make generate` + `make check` + `MechanismE2eIT` + 新类进 SHACL」，全部已 pass；
5. **对 W8 的影响**：`LOOP.yaml.exit_criteria.dev` 要求"全部 implementation 门禁通过"，
   ⇒ 本条**阻塞 W8 收口**，须在 W8 之前裁定 (a)/(b)。
- Next: 记录根因（已完成）；等治理裁定 (a)/(b) 后按原命令重跑，并在本文件追加重跑结果（不覆盖本记录）。
