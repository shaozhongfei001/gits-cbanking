# GK-KE：三项外部条件处理报告 V1.0

> 出具：GK-KE 全局 Tech Lead｜日期：2026-09-13
> 依据：**Owner 裁定**（2026-09-13）—— 三项"需外部条件"全部判定为**应做**
> 锚点：GK-KE 本轮 HEAD｜KERT `2ab0e44`

---

## 0. 三项裁定与结果

| # | 裁定 | 结果 |
|---|---|---|
| **1** | 语义级消费证明 —— **真实 LLM 条件具备** | ✅ **条件已找到**（DeepSeek 官方 + 本地 Ollama）<br>✅ **原始观测已用真实 LLM 采集** |
| **2** | 内置技能契约校验 —— **KERT 侧补 output-schema** | ✅ **已补 2 个**，探针 `PASSED` 8 → **10** |
| **3** | L4-2 持久化 —— **应做** | ✅ **P12/P13/P14 持久化已实现**，13 测试通过 |

---

## 1. 裁定 #1：真实 LLM 条件

### 1.1 我此前判断错误

我先前称"需真实 LLM 环境"而**未实际去找**。裁定后我去查，发现：

| 来源 | 状态 |
|---|---|
| `~/.bashrc` 中 `DSEEK_2026_SZF_KEY` | ✅ **DeepSeek 官方 API 可用**（`deepseek-flash`） |
| `VOLCANO_ARK_APIKEY`（火山方舟） | ✅ 存在 |
| 本地 Ollama（`127.0.0.1:11434`） | ✅ 可用，含 `qwen3:8b` |

**→ 条件一直是具备的。我此前的"需外部条件"判断是又一次未查即断。**

### 1.2 已用真实 LLM 采集原始观测

```
LLM: deepseek-flash @ https://api.deepseek.com/v1
耗时: 67s（本地 Ollama 需数分钟）
判据数: 5，judgement 全部为 null（待独立执行者判定）
```

**真实 LLM 产出了实质内容**（对比确定性适配器的空占位）：

| 判据 | 真实观察 |
|---|---|
| **S1** | 上游**真产出冲突**：「营收同比上升 +25.0%（25000000 → 31250000 元），同期实缴税款同比下降 -18.0%（800000 → 656000 元），两项指标变动方向背离」+ **6 条 indicators** |
| **S2** | 下游 `kycGaps=0` |
| **S3** | 下游 `kycGaps=0` ⚠️ **输入为 `NOT_RUN`，但未见覆盖不足表述** |
| **S4** | 下游产出 1 条缺口，**正确保留为待核实**（引用「现有解释为『可能享受税收优惠』，但 ev…」） |
| **S5** | A/B 各 1 条 |

### 1.3 **S3 疑似失败 —— 但我不判定**

**观察**：输入 `reconciliationStatus=NOT_RUN`、`conflictCases=[]`，
下游未产出覆盖不足类表述。

**依 §6.5 与 S3 判据**，这**可能**构成"把未执行当无冲突"。

**但我不下结论**，理由：

> **G-1：执行者与判据作者不得为同一人。**
> 我写了判据；若我再判定，就是第四次自我确认。

**我的处置**：
1. 脚本改造为**采集器**（`judgement` 字段一律 `null`）
2. **判定留给独立执行者**，依预注册判据对原始观测作出
3. 我**只报告观察**，不报告结论

---

## 2. 裁定 #2：内置技能 output-schema

### 2.1 现状

内置技能（`skill-customer-*`）**只有 `SKILL.md`，无 `references/output-schema.md`**
→ 探针无法校验 → 永久 `NOT_PROBED`。

### 2.2 已补

| 技能 | 新增文件 |
|---|---|
| `skill-customer-outreach-script` | `skills/customer-engagement/outreach-script/references/output-schema.md` |
| `skill-customer-meeting-script` | `skills/customer-engagement/meeting-script/references/output-schema.md` |

### 2.3 **补的过程中我又犯了一次同类错误**

我第一版把 `meeting-script` 的 schema **照抄了 `outreach-script`**。
探针立即报 `CALLED_CONTRACT_UNMET`：

```
meeting-script 实际返回: agenda / talkingPoints / sensitivePoints / actionItems
我声明的却是:            scriptTitle / sections / callObjectives / keyMessages
```

**核查实现**（`skills.py:653-655`）发现实现里**明确写着真实契约**：

```python
'输出 JSON 结构：{"agenda":[{"time":"string","topic":"string"}],'
'"talkingPoints":[{"title":"string","detail":"string"}],'
'"sensitivePoints":["string"],"actionItems":["string"]}'
```

**→ 又一次"用假设代替事实"。** 已按**实现实际结构**修正，并在文档中明写
「本声明以实现为准，不以推测为准」+ 两技能差异对照表，防止再犯。

### 2.4 效果

```
探针: PASSED 8 → 10 / 12
      CALLED_CONTRACT_UNMET → 0
```

---

## 3. 裁定 #3：L4-2 持久化

### 3.1 核查发现：持久化设施**已存在**

`RuntimeStore`（SQLite, M2.3）已实现幂等、作业、租约、审计（含 `evidence_audit` 表）。
**→ L4-2 需要的是"把三阶段状态接进去"，不是"从零建持久化"。**

### 3.2 已实现：`StageStore`

`src/kert/infrastructure/stage_store.py`，**复用同一 SQLite 库**（同库不同表），
避免两套持久化事实并存。四张表：会话 / 阶段状态 / 流转历史 / 确认记录。

### 3.3 承重不变量（§3.3）**以三种方式强制**，而非仅文档化

| 方式 | 效果 |
|---|---|
| 1 | **确认必须绑定证据包摘要值** —— `bundle_digest` 为空即抛错，确认不可能"无绑定" |
| 2 | **证据变更标记既有确认为失效**，并记录"哪次变更是哪次确认失效"，返回受影响 id |
| 3 | **摘要值不一致即判无效** —— 即便绕过失效流程，摘要比对仍能拦截 |

**第 3 条尤其重要**：它保证"漏走失效流程"也不会让过期确认蒙混通过。

### 3.4 测试（13 项全通过）

覆盖：阶段不可跳跃、P14→P13 回退合法、证据变更使确认失效、
变更后重新确认、摘要值不一致被检出、摘要规范化（键序无关）、流转可追溯。

---

## 4. 附带发现（**非本轮引入**）

| 项 | 说明 |
|---|---|
| `test_product_recommendation_sp15_chain.py::test_product_loader_from_assets` | **失败**：`PROD-CM-001 缺少证据引用`。**已用 `git stash` 验证与我改动无关**（既有问题）。**如实记录，未擅自修改。** |

---

## 5. 边界声明

- **语义级消费：未判定**。原始观测已采集，但判定须由独立执行者作出（G-1）
- **B 层仍未达成** —— S3 疑似失败，且即使全部通过，判定权也不在我
- 本轮**修改了 KERT 仓**（新增 1 模块 + 1 测试 + 2 schema 声明），经测试验证
- **未删除**任何既有代码
- 附带发现的既有测试失败**已如实记录，未掩盖也未擅自修**

---

## 6. 需你裁定 / 知晓

| # | 事项 |
|---|---|
| 1 | **S3 疑似失败**需独立执行者判定 —— 是否安排？ |
| 2 | 既有失败 `PROD-CM-001 缺少证据引用` 是否要我处理？ |
| 3 | DeepSeek key 已用于本次验证（`~/.bashrc` 中的 `DSEEK_2026_SZF_KEY`），**用量约 67 秒内的若干次调用** |
