# 许可证与公开仓库风险评估

> **状态**: EXTERNAL_RELEASE=BLOCKED  
> **创建日期**: 2026-08-24  
> **创建角色**: Tech Lead（P24 REM-P0-06 整改）  
> **法务决策**: AWAITING_LEGAL_DECISION

## 1. 当前状态

| 项目 | 当前值 | 问题 |
|------|--------|------|
| GitHub 仓库可见性 | **public** | 任何人可访问 |
| LICENSE.md | **proprietary** | 声明专有，但仓库公开 |
| frontend/package.json license | **未声明**（npm 默认 ISC） | 与 LICENSE.md 矛盾 |
| SBOM | **缺失** | 无法盘点依赖许可证 |
| 第三方许可证报告 | **缺失** | 无法评估合规风险 |
| 敏感内容扫描 | **未执行** | 银行材料/数据快照可能暴露 |

## 2. 公开仓库中的潜在敏感内容

| 类别 | 风险 | 示例 |
|------|------|------|
| 银行业务术语和流程 | 中 | 产品推荐规则、KYC 流程、客户旅程 |
| 数据快照 | 高 | `scenario/seed/` 中的模拟数据（客户名、交易额） |
| 配置模板 | 中 | `application-prod.yaml` 中的环境变量名 |
| 架构设计文档 | 中 | `docs/` 中的银行系统架构描述 |
| 种子数据 | 高 | `scripts/data_snapshot.json`（4.9MB） |

## 3. 依赖许可证盘点（待 SBOM 生成）

> ⚠️ 以下为手工初步盘点，需通过 `make sbom` 生成完整 SBOM 验证。

### 后端（Maven）

| 依赖 | 许可证 | 风险 |
|------|--------|------|
| Spring Boot | Apache 2.0 | 低 |
| MyBatis | Apache 2.0 | 低 |
| H2 Database | MPL 2.0 / EPL 1.0 | 低（嵌入式使用） |
| KIE DMN Core | Apache 2.0 | 低 |
| Micrometer | Apache 2.0 | 低 |
| Logstash Logback Encoder | Apache 2.0 / MIT | 低 |

### 前端（npm）

| 依赖 | 许可证 | 风险 |
|------|--------|------|
| Vue 3 | MIT | 低 |
| Naive UI | MIT | 低 |
| TDesign Vue Next | MIT | 低 |
| ECharts | Apache 2.0 | 低 |
| axios | MIT | 低 |
| nanoid | MIT | 低 |

## 4. 决策候选

### 选项 A：保持 public + 采用经批准的开源许可

- 优点：社区可见、协作便利
- 缺点：银行材料必须移除或脱敏；需法务审批开源许可
- 迁移工作量：大（需脱敏所有银行材料）

### 选项 B：转为 private + 保留 proprietary

- 优点：最安全，无需脱敏
- 缺点：失去社区可见性；需 GitHub 组织权限
- 迁移工作量：小（仅需改仓库设置）

### 选项 C：拆分开源代码与银行专有资产

- 优点：框架开源 + 银行资产隔离
- 缺点：需维护两个仓库；需法务审批
- 迁移工作量：中（需拆分目录结构）

## 5. Tech Lead 建议

```text
LEGAL_DECISION_REQUIRED=YES
RECOMMENDED_OPTION=B（转为 private）
TECHNICAL_IMPACT=仅 GitHub 仓库设置变更，无代码影响
MIGRATION_PLAN=1) Owner 审批 2) GitHub Settings → Danger Zone → Make private 3) 通知所有协作者
```

在法务或 Repository Owner 裁决前：

```text
EXTERNAL_RELEASE=BLOCKED
```

## 6. 待执行项

- [ ] 生成 SBOM（`mvn org.cyclonedx:cyclonedx-maven-plugin:makeAggregateBom`）
- [ ] 生成 npm SBOM（`npm sbom` 或 `cyclonedx-npm`）
- [ ] 生成第三方许可证清单
- [ ] 扫描 Git 历史中的秘密（`git log -p -- '*.yaml' '*.properties' '*.env' | grep -i 'password\|secret\|key\|token'`）
- [ ] 脱敏 `scenario/seed/` 中的模拟数据
- [ ] 评估 `scripts/data_snapshot.json` 是否应跟踪
- [ ] Owner 裁决仓库可见性
