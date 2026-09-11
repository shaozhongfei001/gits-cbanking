# FAILURES.md

## FAIL-2026-09-11-02: 封版 V1.0.1 证据链两处硬错误 + SemanticPackage schema 分叉

**发现日期**: 2026-09-11
**发现角色**: Tech Lead（对架构委员会 PASS_WITH_REQUIRED_CHANGES 整改的独立机器核验）
**严重程度**: BLOCKER（阻断独立 QA 二次复核与 D 阶段门禁提升）

### 现象

TL 对整改答复（`GITS-KERT_架构委员会整改答复_AC01-04_V1.0.md`）声称的"唯一证据链"做独立机器核验，发现三处不实：

1. **受控目录 tree hash 笔误**（已修正）：整改答复 + 独立QA提示词 + STATE.json 三处写 `daa9b511...`，真实值 `git rev-parse HEAD:docs/dd/gk-ke-contract` = `8de275b722f7d65186f3f0691973f28f3c51b8b3`。已由 TL 勘误修正为真实值。

2. **SemanticPackage.schema.json 权威源与交付包分叉**（未修复，需 Feature Pilot）：
   权威源 `specs/gk-ke/v1/schemas/SemanticPackage.schema.json` 含 `writeOwner`/`writeEntry`/`authorityScope` 三字段（WP-R4-1 任务6 补的 F03 权威矩阵整改），
   但交付包 `docs/dd/gk-ke-contract/schemas/SemanticPackage.schema.json` 仍是旧版（缺这三字段）。
   其正例 `examples/positive/SemanticPackage.json` 同样分叉。
   其余 19 schema + 59 example 均 byte-identical，分叉仅 SemanticPackage 一处。

3. **整改答复 AC-03 声称"byte-identical 0 差异"不成立**：见上，SemanticPackage 分叉直接推翻该声明。

### 影响

- 封版 V1.0.1 交付包缺少 F03（权威矩阵）整改的核心成果（writeOwner/writeEntry/authorityScope）。
- 独立 QA 按提示词执行会发现 tree hash 不符（已修正）与 schema 分叉，无法给出 QA_PASS。
- AC-03「Git-QA 一一对应」实际未关闭，整改答复的"AC-01/02/03 全部完成"声明不成立。

### 处理

- [x] tree hash 笔误：TL 已勘误 3 处（整改答复、QA提示词、STATE.json）。
- [x] SemanticPackage schema 分叉：Feature Pilot 已重新同步权威源 → 交付包（byte-identical，diff -r 0 差异），重跑 validate_package.py（148/0）、gk_ke_contract_examples.py（20/40）、verify_simulation.py（PASS），重新封包 V1.0.2。新三值锚点：HEAD `886f7104f47bc3fa7ed1de1c95b91e3aa1cda13e`、tree `4c5f5373c83386d27ea996293a49ee7f3b9f10ce`、ZIP `GK-KE-CONTRACT-V1.0.2_REVIEW.zip` SHA-256 `b21638abef8eb0e271c2190303c8f5dfaa1609a5c82269db2c20f451d97a5ad0`（145/145 逐文件一致，0 差异）。整改答复/STATE/QA提示词证据链锚点已同步更新。

---

## FAIL-2026-09-10-01: S4 建议书草稿各章内容完全相同 — KERT 未接真实 LLM

**发现日期**: 2026-09-08（修复），2026-09-10 复测确认
**发现角色**: E2E Owner
**严重程度**: MAJOR（草稿无业务价值，不影响链路连通性）

### 现象

`POST /api/v14/proposals`（SP-20）返回 SUCCESS，但 CH01~CH10 每章正文逐字相同，
均为「CUST-CORP-0001为制造业客户，经营基本正常，存在金融需求（确定性样例…）」。

### 根因（非数据样本、非 LLM 质量，而是根本没调 LLM）

1. `Leibniz-KERT/src/kert/infrastructure/adapters/llm.py` `create_llm_adapter()`
   仅当 `KERT_LLM_BASE_URL` + `KERT_LLM_API_KEY` + `KERT_LLM_MODEL` 三者齐备才用真实适配器，
   否则静默退化为 `DeterministicLlmAdapter`。启动时只设了 `DEEPSEEK_API_KEY`，三个 `KERT_LLM_*` 缺失。
2. `DeterministicLlmAdapter` 的 proposal 分支对所有章节用同一段硬编码模板，
   只替换 chapterId/chapterName/industry，丢弃全部 chapterContext 真实企业数据。

### 修复

1. 主修复：启动 8107 注入 `KERT_LLM_BASE_URL=https://api.deepseek.com/v1`、
   `KERT_LLM_API_KEY`、`KERT_LLM_MODEL=deepseek-chat`、`KERT_LLM_TIMEOUT=180`。
2. 兜底加固：`DeterministicLlmAdapter` 新增 `_sample_proposal()`，按 chapterId 分化
   10 章叙述焦点并引用 chapterContext 真实字段，缺失字段进 unknowns 而非编造；
   `KERT_LLM_TIMEOUT` 改为可配（原硬编码 60s）。
3. 回归防护：`frontend/e2e/p24-s4-wizard.live.spec.ts` 断言各章正文互不相同
   （`new Set(bodies).size === bodies.length`），并禁止出现「确定性样例」。

### 复测结果（2026-09-10）

```
[s4] 200 in 31.6s status=SUCCESS draftLen=14145 citations=111 unknowns=53
[s4] headings=36 bodies=34 uniqueBodies=34 renderedLen=14145
1 passed (37.7s)
```

修复前：1085 字 / 10 章全同 / 16 引用 / model=deterministic_fallback。
修复后：14145 字 / 34 章正文全部唯一 / 111 引用 / model=deepseek-chat。

---

## Mapper XML Record 适配修复 — E2E 验证失败记录

**验证日期**: 2026-08-12
**验证角色**: E2E Owner
**分支**: feature/v11-frontend-depth-remediation

---

### F-1: FactReconciliationCaseMapper.xml 引用不存在的内部类 [BLOCKER]

**严重程度**: BLOCKER — 阻断所有集成测试

**文件**: `adapters/persistence-relational/src/main/resources/mapper/foundation/ontology/FactReconciliationCaseMapper.xml`

**行号**: 21

**现状**:
```xml
<arg column="status" javaType="com.gien.gits.ontology.FactReconciliationCase$ReconciliationStatus"/>
```

**期望**:
```xml
<arg column="status" javaType="com.gien.gits.ontology.ReconciliationStatus"/>
```

**原因**: `ReconciliationStatus` 是顶级枚举类 (`com.gien.gits.ontology.ReconciliationStatus`)，不是 `FactReconciliationCase` 的内部类。

**影响**: MyBatis 解析 Mapper XML 失败 → SqlSessionFactory 创建失败 → 所有 43 个集成测试 ERROR。

---

### F-2: 6 个 Mapper XML 的 INSERT 语句中 Instant 字段缺少 InstantTypeHandler [MINOR]

**严重程度**: MINOR — H2 兼容模式下可能不阻塞，但与项目规范不一致

**规范要求**: 所有 `java.time.Instant` 字段在 INSERT/UPDATE 中必须指定 `typeHandler=com.gien.gits.adapter.persistence.common.typehandler.InstantTypeHandler`

| 文件 | 缺失字段 |
|------|----------|
| `RelationshipReportMapper.xml` | `createdAt`, `updatedAt` |
| `ProductKnowledgeCardMapper.xml` | `createdAt` |
| `BankRelationshipSnapshotMapper.xml` | `createdAt` |
| `FactReconciliationCaseMapper.xml` | `createdAt`, `updatedAt` |
| `CreditFacilityMapper.xml` | `createdAt`, `updatedAt` |
| `TransactionRecordMapper.xml` | `createdAt` |
| `GroupRelationshipMapper.xml` | `createdAt` |

**注意**: `OpportunityMapper.xml` 的 `expectedCloseDate` 是 `String` 类型，不需要 InstantTypeHandler（已排除）。

---

## 验证通过项

| 检查项 | 结果 |
|--------|------|
| 编译 + 单元测试 (persistence-relational -am) | ✅ 19 tests, 0 failures |
| 所有 33 个 Mapper XML 使用 `<constructor>` 模式 | ✅ 无残留 `<result property=...>` |
| PrevisitReportContentMapper productSchemes typeHandler 一致性 | ✅ resultMap 和 INSERT 均使用 ProductSchemeListTypeHandler |
| 其他 `$` 内部类引用 (17 处) | ✅ 全部为真实内部类/枚举 |
| 已有 INSERT 中 InstantTypeHandler 覆盖 | ✅ 大部分 Mapper 已正确添加 |

---

## 退回建议

退回至 Feature Pilot 修复 F-1 (BLOCKER) 和 F-2 (MINOR) 后重新验证。
