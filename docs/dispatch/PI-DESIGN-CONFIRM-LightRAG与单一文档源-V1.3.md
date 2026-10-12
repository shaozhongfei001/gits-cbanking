# 设计确认 V1.3（撤回 V1.2 的变更申请；PC8 走既有 DEMO 轨）

```text
提交人：tech_lead（TL）｜ 时间：2026-09-22
本件性质：**技术自查后的自我更正**（V1.2 的 CR-1/CR-2/CR-3 撤回）
依据：Owner 2026-09-22「技术问题请你先做建议」⇒ 以下为 TL 决策（可被 Owner 否决）
```

## 0. 结论：造数机制**早已存在**，V1.2 的"第三轨"是重复建设，予以撤回

| 我 V1.2 提的 | 事实（已实测） |
|---|---|
| `CR-1` 新增 `usage: SIMULATED` 第三轨 + `CR-2` 改门禁 + `CR-3` 三区 | ❌ **撤回**。造数轨已被 Owner 决议建好：`source-registry.md` **§5.8「DEMO 演示轨登记（`_authoritative/` · `provenance_state: DEMO`）」**，依据 **Owner 决议 `DECISION-20260906-01`（演示路径 C）**；3 份 DEMO 源已登记 `AVAILABLE (DEMO)`，含字节数 + SHA-256 + 抽取片段数 |
| 需要新门禁 | ❌ 撤回。既有阻断判据齐备且为**源级**：`INV-EVS-09/10/11`（DEMO 不得支撑 `RECOMMENDATION_READY`；所在 Release 必须标 DEMO；DEMO 与 VERIFIED 不得混用）+ `INV-RLS-09` |
| 需要新登记表 | ❌ 撤回。`02_work/source-versions/manifest.json`（3 个 `SV-*`）+ `04_serve/releases/RLS-2026.09.06.1.json`（`provenanceState=DEMO`、`interpretationReady=true`、`recommendationReady=false`）**已存在** |
| 新路径 `_sim/` | ❌ 撤回（已 `git revert`：`54f93e8`）。该路径不在 `sourcePath` pattern 内 ⇒ 落进去反而不可被引用；且与 §5.8 形成**两套 DEMO 语义分叉**（违反"判据单点、不分叉"） |

**KERT 侧既有门禁实测**：`tools/check_registry_consistency.py` = **67/67 PASS**
（含「DEMO 登记字节数 == 实测」「DEMO 登记 SHA-256 == 实测」「DEMO 文件命名含 `.DEMO.md`」
「front matter 声明 `provenance_state: DEMO`」「DEMO 不冒充真实」）。

## 1. 更正 `F-KERT-01` 的定性（我上一轮登记过重）

| 我 V1.2 的说法 | 更正后 |
|---|---|
| 「3 份 DEMO 源坐在 `_authoritative/`，一旦被引用即可把产品卡推向 ACTIVE，**有风险**」 | ⚠ **定性过重**：这是 §5.8 的**有意设计**——"演示文本固定带 `.DEMO.md` 后缀；真实制度上传时落 `SRC-CM-00X.pdf/.md`"，阻断靠 `provenance_state` 而**不是**路径 |
| 保留的**真实**判据缝 | `gateRule`（产品卡转 `ACTIVE` 的前提）只写 `usage=AUTHORITATIVE` + `sourcePath` 落 `_authoritative/`，**未含 `provenanceState`**；而 DEMO 源正在 `_authoritative/` ⇒ `usage=AUTHORITATIVE` ⇒ 单看 `gateRule` **可转 `ACTIVE`**。是否补字句由**合同 Owner** 定，本件只登记 |

## 2. TL 决策（三项，可被 Owner 否决）

| # | 决策 | 理由 |
|---|---|---|
| `T-1` | **撤回 `CR-1`/`CR-2`/`CR-3`**；不新增 `usage: SIMULATED`、不建第三区 | 既有 §5.8 DEMO 轨已满足全部需求，且已被机器校验（67/67） |
| `T-2` | **PC8 只保留一个代码变更 `CR-5`**：新增检索 HTTP 出口（把既有 `retrieve_via_lightrag` 暴露；纯新增，响应带可回译 `filePath` + `chunkId` + `evidenceClass`/`provenanceState`） | 实测 `retrieve_via_lightrag` 仅在 service 层（`services.py:554`），`server.py` 无 lightrag 端点 ⇒ 这是**唯一真实缺口** |
| `T-3` | **`CR-4` 不动**（`EGRESS_ROOTS` 保持 `03_core`/`04_serve`） | 索引内容取自既有可发布产物，不扩 Owner 已批准的出口边界 |

**连带关闭**：`D-2`（共享文档集的"版本 + sha256 清单"）**不需要新造** ——
registry §5.8 的 `bytes_sha256` 台账 + `02_work/source-versions/manifest.json` 即该清单（且已有门禁校验一致性）。

## 3. PC8 真实工作量：把 DEMO 覆盖从 3 产品扩到 13 产品

**现状**（实测）：13 张产品卡 / 6 族；DEMO 源**只覆盖 CASH_MANAGEMENT 3 张**
（`SRC-CM-001/002/003.DEMO.md` → `PROD-CM-001/002/003`）；其余族**全部缺源**。

**造数清单（14 份，按杠杆排序）**：

| 批次 | 源 | 覆盖产品 | 族 |
|---|---|---|---|
| **B1 跨族通用（杠杆最高）** | `SRC-XFAM-001` 准入与评级 · `SRC-XFAM-002` 产品定价 · `SRC-XFAM-003` 销售适当性 | **全部 13 张** | 跨族 |
| B2 融资 | `SRC-FIN-001` 流贷办法 · `SRC-FIN-003` 供应链操作规程 · `SRC-FIN-005` 流贷风险指引 | `PROD-FIN-001/002/003` | FINANCING |
| B3 结算 | `SRC-SET-001` 单位结算账户细则 · `SRC-SET-002` 国内保理办法 | `PROD-SET-001/002` | SETTLEMENT |
| B4 贸易金融 | `SRC-TF-001` 银承办法 · `SRC-TF-002` 国内信用证规程 · `SRC-TF-003` 贸易背景审查 | `PROD-TF-001/002` | TRADE_FINANCE |
| B5 跨境 | `SRC-CB-001` 跨境人民币办法 · `SRC-CB-002` 内保外贷办法 | `PROD-CB-001/002` | CROSS_BORDER |
| B6 投行 | `SRC-IB-001` 并购贷款办法 | `PROD-IB-001` | INVESTMENT_BANKING |

> `SRC-FIN-002/004` 为 `SRC-XFAM-001/002` 的**别名**（registry §5.6 明载），**不重复造数**。
> `REG-*` 监管法规（12 份）**不造数** —— 虚构监管法规冒充真实法规的风险不可接受；其缺口按"未上传"诚实呈现。

**每份造数必须满足（对齐既有 `SRC-CM-00X.DEMO.md`）**：

1. front matter：`source_id` / `source_title`（…（演示文本））/ `institution: DEMO-BANK` /
   `provenance_state: DEMO` / `zone: _authoritative` / `authority_level: INTERNAL_POLICY` /
   `allowed_claim_types` / `registry_status: AVAILABLE` / `version: 1.0-demo` /
   `effective_date` / `demo_notice`（逐字沿用既有声明口径）；
2. 正文首部 **DEMO 声明块**（不得删除改写）；
3. 章条体（`第N条`）与 registry 登记的 `clause` 指向一致；
4. **不得**照抄真实机构制度；机构名恒为 `DEMO-BANK`。

## 4. PC8 施工步序（修正后）

```text
8-1 造数：B1→B6 共 14 份 DEMO 源（源本体；**不手写** SV-/Release —— 那是 pipeline 产物）
8-2 登记：registry §5.8 表 + 入库记录（bytes/SHA-256/片段数）+ source-versions/manifest
8-3 结构化：跑既有 pipeline（ingest → 抽取 → 候选卡 → Release），产出 02_work/03_core/04_serve
8-4 灌入：既有受控通道发布 03_core/04_serve（EGRESS_ROOTS 不动）
8-5 检索出口：CR-5 端点 + 出处回译（filePath/chunkId 入解读）
8-6 索引重建：沿用 ADR-017 判据（清空 ⇒ 同文档集重灌 ⇒ 覆盖与出处一致）
```

**纪律**（不因造数放宽）：`02_work/source-versions/*.json` 与 `04_serve/releases/*.json`
**必须由 pipeline 生成**，禁止手写（手写即伪造抽取与发布记录）。

## 5. 未落 / 下一步

| 项 | 状态 |
|---|---|
| `git revert` `_sim/` 骨架（KERT `54f93e8`） | ✅ 已做 |
| gits 本件（V1.3 撤回与更正） | ✅ 本件 |
| 造数 B1（跨族 3 份，覆盖 13 产品） | ▶ 下一步开工 |
| `CR-5` 检索出口 | ⏸ 待 B1–B6 与 pipeline 打通后做（有检索对象才有意义） |
| `gateRule` 是否补 `provenanceState` 字句 | ⏸ 合同 Owner 裁决 |

## 6. 边界

未改 gits 受控合同（撤回变更申请）；未改 KERT 既有文件；未灌入任何文档到 LightRAG；
本件不构成验收、激活或生产可用结论。
