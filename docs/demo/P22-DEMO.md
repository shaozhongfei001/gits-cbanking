# P22 LLM-WIKI 知识地图｜完整流程演示

```text
DEMO_ID=P22-DEMO-001
STATUS=DEMO（基于 QA_PASS 真实产物）
CREATED_AT=2026-08-19
HEAD=29e0c78（P22 已推送 origin/main）
```

> 本演示展示 P22 从权威规范到"大模型优先读图再执行"的完整链路，全部基于真实产物（非 mock）。

---

## 一、完整流程总览

```
《银行知识工程规范打样_fixed.xlsx》(最高权威)
  │  ① 资产化
  ▼
39 个知识要素 (KE) → specs/knowledge-architecture/elements/{KI}/KE-*.md
  │  ② 合同登记
  ▼
KnowledgeElement 合同 (CTR-KELEM-001) → CONTRACT_INDEX.yaml → make generate/check
  │  ③ 控制面（生产可用）
  ▼
InMemoryKnowledgeStore (启动加载内存快照) + 5 个 InMemory*Reader → apps/api
⚠️ 注：InMemoryKnowledgeStore/KnowledgeSnapshotLoader/InMemory*Reader 已在 P24 DKWS 重构中移除，由 scenario/dkws-platform/ 模拟平台替代
  │  ④ LLM 读图（方案 A）
  ▼
KnowledgeWikiPort.renderMap(scope) → 渲染受控知识地图 → LlmClient 注入
  │  ⑤ Shadow E2E
  ▼
两场景黄金比对 + LLM 读图导航 (formal_output_changed=false)
```

---

## 二、分步演示

### ① 知识资产化（G1）
39 个 KE 按 KI 分组存入 `specs/knowledge-architecture/elements/`，含 `source.authority`（受控权威标注）：

```text
KI-009（8 要素）: 客户全称/编号/所属行业/企业规模/年营收/注册地址/主要产品/合作年限 [K-Type-F]
KI-FRONT-001（3）: 上游供应商/下游客户/供应链位置解读 [F/E]
KI-FRONT-002（9）: 政策/市场/技术/供应链/区域/风险 六维研判 + 指数量化评分[M] + 竞争力评估[E] + 综合结论[E]
...
```

### ② 合同登记（G0）
新增 `KnowledgeElement` 合同（CTR-KELEM-001），要素类型 `K-Type-F/R/P/E/M`，`make check` 全绿。

### ③ 生产可用控制面（E1）
`KnowledgeSnapshotLoader` 启动时从 Git 权威源一次性加载 `InMemoryKnowledgeStore` 内存快照，运行时 5 个 `InMemory*Reader` 高频读内存（消除每请求扫盘）。

> ⚠️ **P24 DKWS 重构后**：`InMemoryKnowledgeStore`、`KnowledgeSnapshotLoader`、5 个 `InMemory*Reader` 已移除，由 `scenario/dkws-platform/` 模拟平台替代。本节描述的架构为 P22 交付时状态，仅作历史参考。

### ④ LLM 读图（G3，方案 A）
`KnowledgeWikiService` 执行任务前，`KnowledgeWikiPort.renderMap(scope)` 渲染受控知识地图（按场景决定 KI 范围），作为 systemPrompt 注入 `LlmClient`，体现"大模型优先读图再执行"。

### ⑤ Shadow E2E（G4）——实际输出
运行 `python3 scripts/run_p22_shadow_e2e.py --mode shadow --scenario PRE_VISIT_PREPARATION --scenario FACT_RECONCILIATION_30M`：

```
shadow-e2e: PASS
shadow-e2e: scenarios=['FACT_RECONCILIATION_30M','PRE_VISIT_PREPARATION'] formal_output_changed=False
```

**PRE_VISIT_PREPARATION 场景**：
- `planId`: `AP-PRE_VISIT_PREPARATION-CUST-001-SHADOW`
- `routeMode`: `ONTOLOGY_THEN_MAP`
- 选中资产：9 个（客户档案 / 客户本体 / 授信 / 交互历史 / 交易摘要 / 外部事件 / KYC问题库 / 产品卡 / 访前SOP）
- **LLM 读图导航**（大模型优先读取的知识地图）：

```markdown
# Knowledge Map (shadow) [AUTHORITATIVE]
- scenario: `PRE_VISIT_PREPARATION`
- **KI `KI-009`**
  - `KE-009-01` 客户全称 [K-Type-F] [AUTHORITATIVE]
  - `KE-009-02` 客户编号 [K-Type-F] [AUTHORITATIVE]
  - ...（共 8 个事实要素）
- **KI `KI-FRONT-001`**
  - `KE-FRONT-001-01` 上游供应商列表 [K-Type-F]
  - `KE-FRONT-001-03` 供应链位置解读 [K-Type-E]
- **KI `KI-FRONT-002`**（八维研判）
  - `KE-FRONT-002-07` 指数维度量化评分 [K-Type-M]
  - `KE-FRONT-002-08` 企业竞争力评估 [K-Type-E]
  - `KE-FRONT-002-09` 综合研判结论 [K-Type-E]
...
```

---

## 三、质量验证（G5）

| 维度 | 结果 |
|---|---|
| 合同一致性 | `make check` 全绿（7 schemas） |
| 后端回归 | apps/api 321 + worker 22 tests，覆盖率达标 |
| 前端 | vue-tsc + vitest + vite build 通过 |
| 依赖安全 | dependency-check 15 reports PASS |
| 受控证据 | 9/9 gates pass，`evidence-check` + `memory-check` 全绿 |
| 独立 QA | QA_PASS（session=qa-p22-formal-001） |

---

## 四、关键决策

| 决策 | 结论 |
|---|---|
| OpenWiki | 放弃引入（代码级评估：权限/内网CDN/非结构化三大硬伤） |
| 人机共读 | 保留目标；过渡期只读导航（GAP-5 后续） |
| Git 控制面 | 增强至生产可用（内存快照 + LLM 读图） |
| 真实平台 | 选型留空待 Owner（RAG/Graph/Metadata 评估见 `P22-REAL-PLATFORM-ASSESSMENT.md`） |
