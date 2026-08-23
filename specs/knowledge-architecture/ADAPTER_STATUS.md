# Knowledge Architecture Adapter 实现状态

> 本文档记录 `specs/knowledge-architecture/assets/` 中声明的 `activation.adapter` 的实现状态。
> 最后更新：2026-08-23

## 适配器实现状态

| adapter | 声明位置 | 实现状态 | 说明 |
|---------|----------|----------|------|
| `skill-runtime-adapter` | `assets/process-tools/sp02,sp05,sp07,sp10,sp15` | **未实现** | PROCESS_TOOL 执行适配器，待 Owner 选型后实现。当前 PROCESS_TOOL 的执行由 `scenario/execute/` 模拟 |
| `mock-rag-adapter` | `assets/knowledge-rules/product-cards`, `assets/foundational-data/external-event` | **未实现** | 知识检索适配器，待真实 RAG 平台选型后实现。当前知识读取由 `scenario/dkws-platform/` 模拟平台提供 stub |
| `knowledge-filesystem` | ~~已移除~~ | **已移除** | P24 DKWS 重构中移除，由 `scenario/dkws-platform/` 替代 |

## 注意事项

- specs 中的 `activation.adapter` 是**合同声明**（SSOT），表示"预期由哪个适配器激活"
- "未实现"不等于"声明错误"——这些是待实现的合同意图
- 实现适配器时需先更新 `specs/CONTRACT_INDEX.yaml` 注册新合同，再 `make generate` → `make check` → 写实现
