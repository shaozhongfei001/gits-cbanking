# P24 回滚计划

> **编号**：P24-ROLLBACK-PLAN
> **创建日期**：2026-08-24
> **审计基线**：`origin/main@d3142c9`

---

## 1. 回滚策略

P24 变更分为两类，回滚策略不同：

| 变更类型 | 回滚方式 | 数据风险 | 说明 |
|----------|----------|----------|------|
| 安全修复 (P0) | **禁止回滚** | N/A | 回滚会重新引入安全漏洞 |
| 功能开发 (DKWS) | `git revert` | 低 | 新增端点/表，无破坏性变更 |

## 2. 回滚步骤

### 2.1 DKWS 功能回滚（如需）

```bash
# 1. 确认回滚范围
git log --oneline feature/P24-dkws-supplychain --not origin/main

# 2. 逐提交 revert（从最新到最旧）
git revert --no-commit <commit-hash>
# ... 重复

# 3. 验证
mvn -pl apps/api -am test -Denforcer.skip=true
cd frontend && npm run build

# 4. 提交
git commit -m "revert(dkws): 回滚 P24 DKWS 功能开发"
```

### 2.2 安全修复回滚（禁止）

以下修复**禁止回滚**，因为回滚会重新引入 BLOCKER 级安全漏洞：

- REM-P0-02: 证据链可审计性
- REM-P0-03: CI 门禁
- REM-P0-04: 生产配置安全默认值
- REM-P0-05: 权威状态 SSOT
- REM-P0-06: 许可证风险评估

## 3. 数据库回滚

P24 新增了数据库表和字段。Flyway 迁移脚本不可逆（按项目规范），但可通过新增迁移脚本回退：

| 迁移脚本 | 回退方式 |
|----------|----------|
| 新增表 | 新增 `V{N+1}__drop_xxx_table.sql` |
| 新增列 | 新增 `V{N+1}__drop_xxx_column.sql` |

**注意**：生产环境需先备份数据。

## 4. 前端回滚

```bash
# 前端构建产物不在 git 中（.gitignore 排除）
# 回滚代码后重新构建即可
cd frontend && npm run build
```

## 5. 回滚验证清单

- [ ] 后端测试通过：`mvn -pl apps/api -am test`
- [ ] 前端构建通过：`cd frontend && npm run build`
- [ ] 前端类型检查：`cd frontend && npx vue-tsc --noEmit`
- [ ] 合同一致性：`make check`
- [ ] 无密钥泄露：secret scan

## 6. 变更记录

| 日期 | 变更 | 角色 |
|------|------|------|
| 2026-08-24 | 初始创建 | Feature Pilot (P24) |
