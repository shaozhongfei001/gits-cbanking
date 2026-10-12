# L10 证据台账

- Loop: `L10-demo-authoritative-chain`
- 计划: `PI-ARCH-IMPLEMENTATION-01` · 阶段 B
- 角色: CodeBuddy Tech Lead（W1 合同 / W2-W3 登记 / W4 管道 / W5 证据）
- 日期: 2026-09-06
- 授权: Owner 决议 **DECISION-20260906-01**（演示路径 C；L10–L13 授权启动）
- 状态: `DEV_SELF_CHECK_PASS`（dev 侧最高，QA_PASS 需独立 QA）

---

## 1. 门禁总览

```
python3 specs/product-knowledge/check_all.py
  PI-0 基线合同                14/14
  L02/L03 候选合同              41/41
  不变式执行测试                99/99（49 条，正反例各 1）
  CTR-PR 增补兼容               30/30
  解读 API 契约测试             26/26
  KERT 源登记一致性             67/67  ← L10 扩展（+21）
  KERT legacy card 台账         76/76
  KERT L10 源版本/片段          48/48  ← L10 新增
  ─────────────────────────────────────
  8/8 PASS · 401 项
```

L03 收工基线为 7/7 · 326 项（46 条不变式）；本 Loop 后 8/8 · 401 项。

后端回归：`./mvnw -q -pl apps/api -am test -DskipITs`（见 §5）。

---

## 2. W1 · DEMO 语义入合同（合同先行）

**为什么必须改合同**：红线要求 DEMO 源标 `provenance_state: DEMO`，
而 V023 的 `pk_sv_prov_ck` 枚举只允许 `VERIFIED / UNVERIFIED / CONFLICTING_EVIDENCE`。
不改合同就实现，等于实现层发明枚举值。故先改合同再实现。

| 变更 | 文件 | 内容 |
|---|---|---|
| 枚举 | `migration-candidates/_tables.tpl` → `h2/` + `mysql/V023__product_knowledge_objects.sql` | `provenance_state` 增 `'DEMO'`，双方言由 `_render.py` 渲染同步 |
| 不变式 | `specs/product-knowledge/evidence-span.schema.json` `x-invariants` | 增 `INV-EVS-09/10/11` |
| 执行 | `invariants.py` + `check_invariants.py` | 3 条谓词 + 正反例，反例必须被拒 |

```
不变式执行测试：99/99 PASS（覆盖 49 条不变式，正反例各 1）   ← 原 93/93 · 46 条
```

三条不变式语义：

| ID | 约束 |
|---|---|
| INV-EVS-09 | DEMO 源证据**不得**支撑 `RECOMMENDATION_READY` |
| INV-EVS-10 | DEMO 证据所在 Release 必须标 `provenanceState=DEMO`，方可进入 `INTERPRETATION_READY` |
| INV-EVS-11 | DEMO 与 VERIFIED 证据**不得**混合支撑同一字段断言（禁止用演示材料补真实缺口） |

---

## 3. W2 + W3 · 演示文本生成与登记

**产物**（KERT `01_raw/_authoritative/`）：

| source_id | 条款数 | 字节 | bytes_sha256 前 16 |
|---|---|---|---|
| SRC-CM-001 | 19 | 4280 | `5879e81430538f75` |
| SRC-CM-002 | 17 | 3509 | `984fe6cde0c2b17b` |
| SRC-CM-003 | 15 | 3422 | `b4599dd141caa7d1` |

**防冒充三道闸**：

1. **物理隔离**：文件名固定 `SRC-CM-00x.DEMO.md`；真实制度上传时落 `SRC-CM-00x.pdf/.md`，
   门禁校验"真实制度文件尚未上传（DEMO 不冒充真实）"。
2. **front matter**：`provenance_state: DEMO` + `institution: DEMO-BANK` + `demo_notice`；
   门禁**只**解析 YAML front matter（见 F-L10-02 假安全修复）。
3. **统计隔离**：源登记表 §5.8 单列；真实权威区仍 28 条 / 缺口 **27/28**；
   **F-L00-07 未解除**，DEMO 不抵扣 Owner 上传义务。

**红测（W3）**：

```
注入：front matter 的 DEMO → VERIFIED
  FAIL | SRC-CM-001 front matter 声明 provenance_state: DEMO
  FAIL | SRC-CM-001 DEMO 登记字节数 == 实测（4280 vs 4284）
  FAIL | SRC-CM-001 DEMO 登记 SHA-256 == 实测
  → 65 及 64/67，退出码 1
还原：67/67 PASS，退出码 0
```

**内建已知冲突（演示数据）**：`SRC-CM-001` 第十条 50 万元 vs `SRC-CM-003` 第六条 100 万元
→ `VALUE_MISMATCH`，供 L12 冲突检测实证，已在登记表 §5.8 声明。

---

## 4. W4 · SourceVersion / Fragment

构建器：`tools/l10_build_source_versions.py`（确定性，`SOURCE_DATE_EPOCH` 支持）

```
run=RUN-20260906-c8bb9f1f · sources=3 · fragments=51
SV-SRCCM001-20260906-5879e814  fragments=19  provenanceState=DEMO
SV-SRCCM002-20260906-984fe6cd  fragments=17  provenanceState=DEMO
SV-SRCCM003-20260906-b4599dd1  fragments=15  provenanceState=DEMO
```

**确定性验证**（`SOURCE_DATE_EPOCH=1788667200`，对应 2026-09-06 12:00 +0800）：

```
两次运行 → diff 为空 · 7 个产出文件逐字节一致 · REPRODUCIBLE=YES
```

**字段真值来源**：`specs/product-knowledge/migration-candidates/V023` 的
`pk_source_version` / `pk_fragment` 表列。**未发明任何合同外字段**
（SourceVersion 额外带的 `zone / sourcePath / productFamily / allowedClaimTypes /
authorityLevel` 均取自 V023 的 `pk_source_document` 与 `pk_evidence_span` 既有列）。

**ID 规则**（来自 CTR-PK-EVS-002）：
`SV-{sourceId 去横线}-{YYYYMMDD}-{bytesHash 前 8 位}`、`FRG-{sourceId 去横线}-{4 位序号}`。

门禁 `tools/check_l10_sources.py` **48/48 PASS**，其中关键项：

- `bytesSha256 / byteSize` == 磁盘实测
- `contentSha256 == SHA-256(contentText)`
- **51 个 fragment 的 `contentText` 全部可在源文件原样定位**（INV-EVS-02 前置）
- 条款数 == 源登记表声明（19/17/15）
- DEMO 源数量 == 3 且 `provenanceState=DEMO`

---

## 5. 后端回归

```
./mvnw -q -pl apps/api -am test -DskipITs
→ tests=955  failures=0  errors=0  skipped=4  （129 surefire 报告）
→ 与 L00/L03 基线 955 完全一致：NO_REGRESSION
```

统计口径说明：以 surefire **XML** 汇总（含 `@Nested`/动态测试）为 955；
若按报告 **txt** 的摘要行汇总为 864，属口径差异，非测试缺失。
L10 未改动任何 Java 代码，回归属**守门性质**。

---

## 6. 本 Loop 不证明什么

- 不证明 DEMO 材料可支撑真实业务 —— 恰恰相反，门禁强制其不得进入 `RECOMMENDATION_READY`
- 不证明 F-L00-07 已解除 —— 真实权威材料缺口仍 **27/28**
- 不证明任何合同已冻结 —— V023 与 EVS-002 均为 `CANDIDATE`
- 不证明 Release 可用 —— 现存 Release 数仍为 0（L13 范畴）
- 不构成 QA 结论 —— 开发侧最高 `DEV_SELF_CHECK_PASS`
- `FROZEN=NO` · `PRODUCTION_READY=NO` · `REAL_E2E_PASS=NO`
- 未执行任何 git 提交
