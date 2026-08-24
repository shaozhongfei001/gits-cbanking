# Knowledge Architecture Adapter 实现状态

> 本文档记录 `specs/knowledge-architecture/assets/` 中声明的 `activation.adapter` 的实现状态。
> 最后更新：2026-08-24

## 适配器实现状态

| adapter | 声明位置 | 实现状态 | 替代/说明 |
|---------|----------|----------|-----------|
| `skill-runtime-adapter` | `assets/process-tools/sp02,sp05,sp07,sp10,sp15` | **PLANNED** | PROCESS_TOOL 执行适配器，待 Owner 选型后实现。当前 PROCESS_TOOL 的执行由 `scenario/execute/` 模拟（MOCK_ONLY） |
| `mock-rag-adapter` | `assets/knowledge-rules/product-cards`, `assets/foundational-data/external-event` | **PLANNED** | 知识检索适配器，待真实 RAG 平台选型后实现。当前知识读取由 `scenario/dkws-platform/` 模拟平台提供 stub（MOCK_ONLY） |
| `knowledge-filesystem` | ~~已移除~~ | **REMOVED** | REPLACED_BY=`scenario/dkws-platform/`。P24 DKWS 重构中移除，原 `InMemoryKnowledgeStore`+`KnowledgeSnapshotLoader`+5 `InMemory*Reader`+`FailClosedJsonReader`+6 `Filesystem*Reader` 已删除 |

## 状态定义

| 状态 | 含义 |
|------|------|
| `IMPLEMENTED` | 已实现并通过测试，可在生产环境使用 |
| `MOCK_ONLY` | 仅有模拟/stub 实现，不可用于生产 |
| `PLANNED` | 已在 specs 中声明合同意图，尚未实现 |
| `DEPRECATED` | 已实现但标记为废弃，将在后续版本移除 |
| `REMOVED` | 已从代码中删除 |
| `REPLACED_BY=<adapter>` | 已被指定适配器替代 |

## knowledge-filesystem 移除验证

> P24 REM-P0-01 / REM-P1-07 要求：删除 `knowledge-filesystem` 前必须证明替代实现功能等价。

| 验证项 | 状态 | 证据 |
|--------|------|------|
| 替代实现功能等价 | ⚠️ 部分等价 | DKWS 模拟平台提供 stub 知识供给，但 fail-closed 语义需 E2E 验证 |
| API 能正常启动 | ✅ | `apps/api` 编译通过，Spring Context 启动成功 |
| 资产加载不倒退 | ⚠️ 待验证 | DKWS stub 加载演示数据，非全量知识资产 |
| fail-closed 语义不倒退 | ⚠️ 待验证 | 原 `FailClosedJsonReader` 语义需在 DKWS 适配器中复现 |
| E2E 全绿 | ⚠️ 待验证 | 需 Playwright E2E 执行 |
| 回退方案可执行 | ✅ | `git revert` 可恢复 `knowledge-filesystem` |

## 注意事项

- specs 中的 `activation.adapter` 是**合同声明**（SSOT），表示"预期由哪个适配器激活"
- "未实现"不等于"声明错误"——这些是待实现的合同意图
- 实现适配器时需先更新 `specs/CONTRACT_INDEX.yaml` 注册新合同，再 `make generate` → `make check` → 写实现
- 删除适配器前必须证明替代实现功能等价，并在 EVIDENCE 中记录
