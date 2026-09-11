# GITS-KERT 架构委员会复审整改答复（AC-01 ~ AC-04）V1.0

> 提交角色：GK-KE 交付 Tech Lead
> 日期：2026-09-11
> 针对：架构委员会复审报告（PASS_WITH_REQUIRED_CHANGES，三项必改 + 一项 MINOR）

---

## 一、整改结论

架构委员会复审提出的 **AC-01 / AC-02 / AC-03 三项必改项已全部整改完成**，AC-04（计数口径）已同步修正。封版 V1.0.1 已生成，形成唯一证据链。

| 整改项 | 状态 |
|---|---|
| AC-01 制品封版 | ✅ 完成（MANIFEST 覆盖全部受控文件 + 自校验） |
| AC-02 补充脚本交付 | ✅ 完成（脚本 vendor 进包 + 20/40 可复现） |
| AC-03 Git-QA 一一对应 | ✅ 完成（唯一 HEAD/tree/ZIP 证据链） |
| AC-04 计数口径 | ✅ 完成（统一表述） |

---

## 二、AC-01 制品封版（已完成）

### 问题
目录 120 文件，MANIFEST 只登记 117；总契约和后补负例未纳入控制；重生成后自检 125/0 → 应 126/0。

### 整改

| 动作 | 结果 |
|---|---|
| MANIFEST 重新生成 | 覆盖 **144 受控文件**（自排除 MANIFEST.json 自身），逐项 path/bytes/sha256 |
| 总契约纳入 | `GITS-KERT_..._项目总契约_V1.0.md` 已入 MANIFEST |
| 负例纳入 | `simulation/oracles/negative_cases.json` 已入 MANIFEST + dataset_manifest.json |
| validate_package.py 增加 MANIFEST 自校验 | 新增 `manifest-paths-unique` / `manifest-covers-all-files` / `manifest-no-missing-paths` / `manifest-bytes-sha256` 四项 |
| 版本号 | packageId 统一为 `GK-KE-CONTRACT-V1.0.1` |

### 自检结果变化

| 项 | 整改前 | 整改后 |
|---|---|---|
| MANIFEST 文件数 | 117 | **144** |
| 目录文件数 | 120 | **145**（144 + MANIFEST 自身） |
| 自检通过数 | 125 | **148**（+ MANIFEST 自校验 4 项 + negative_cases 登记 + 6 schema 相关） |

> 说明：架构委员会预估"126/0"，实际因 AC-02 同步 6 schema（+ 6 正例 12 负例 = +18 检查）而达到 148/0。126 的预估基于"仅补总契约+负例 2 文件"，未计入 AC-02 的 schema 同步。

---

## 三、AC-02 补充脚本交付（已完成）

### 问题
`gk_ke_contract_examples.py`、`verify_simulation.py` 不在 ZIP 中；ZIP 只提供 14 正例 / 28 负例，无法复核所称 20/40。

### 根因（TL 定位）
交付包 `docs/dd/gk-ke-contract/` 是 V1.0 时期的评审快照（14 schema），而 Feature Pilot 新增的 6 个 schema 落在权威源 `specs/gk-ke/v1/`（20 schema），两者**分叉**。

### 整改

| 动作 | 结果 |
|---|---|
| 同步 6 个新增 schema | `specs/gk-ke/v1` → 交付包（SourceVersion/Capability/QueryDefinition/Release/LegacyRagHit/MetricDefinition.full），**byte-identical** |
| 同步 6 正例 + 12 负例 | 交付包 examples 达 20 正例 / 40 负例 |
| vendor 补充脚本进包 | `tools/gk_ke_contract_examples.py` + `tools/verify_simulation.py`（路径改为包内相对，可独立运行） |
| validate_package.py 负例机制统一 | 从过时 `schema_cases.json`（28 条）改为 `negative/*.json` glob（40 个），与 gk_ke_contract_examples.py 一致 |
| 废弃历史生成器 | `build_contract_examples.py`（仅覆盖 14 schema）从 README 再生成流程移除 |
| CONTRACT_INDEX.json | 登记 6 新 schema 到 C02/C04/C05 |

### 可复现结果（包内独立运行）

| 脚本 | 结果 |
|---|---|
| `tools/gk_ke_contract_examples.py` | **20 正例 / 40 负例**（与 specs 一致，不再是 14/28） |
| `tools/verify_simulation.py` | PASS（C001 = 2,983,333.33 CNY） |
| `tools/validate_package.py` | 148 passed / 0 failed |

---

## 四、AC-03 Git 与独立 QA 一一对应（已完成）

### 问题
材料同时出现 0034f22、3e0d741、a40de1b、91d5fed 等版本；最终 HEAD/受控 tree/ZIP hash/QA 受测版本不明确；包内仍记录 independentQa=NOT_PERFORMED。

### 整改：唯一证据链

| 证据 | 值 |
|---|---|
| **最终 HEAD** | `a65c3369b0f3fa43482f837cc2a975aa4f5424d3` |
| **受控目录 tree** | `daa9b5112853a6404f6e72dd29e6169cc14cbb99` |
| **ZIP 文件** | `docs/dd/GK-KE-CONTRACT-V1.0.1_REVIEW.zip` |
| **ZIP SHA-256** | `3bf136355fc0c7f6ecd55a2e38e0d0704ea5cf0f5690788a8c4f356b3a6118bf` |
| **ZIP 与 tree 一致性** | 145/145 文件逐文件 sha256 完全一致，0 差异 |
| **包版本** | `GK-KE-CONTRACT-V1.0.1` |
| **构建幂等** | build_simulation.py 重跑后工作树无差异 |

### 关于 QA 受测版本的诚实说明

| 版本 | QA 状态 | 说明 |
|---|---|---|
| `91d5fed` | ✅ QA_PASS（qa-gk0-formal-001） | WP-R4-1 六合同源变更（F03/F04/F06/F07/F08） |
| `a65c336` | ⏳ 待 QA 二次复核 | 封版 V1.0.1（AC-01/02/03 制品一致性变更） |

**关键澄清**：
1. 封版 `a65c336` 同步到交付包的 6 个 schema，**与 QA 已复核的 `91d5fed` 的 specs/gk-ke/v1 内容 byte-identical**（TL 逐文件核验 0 差异）。
2. 封版新增的变更（MANIFEST 封版、validate_package.py MANIFEST 自校验、脚本 vendor、CONTRACT_INDEX 登记）属**制品一致性工程**，非语义变更。
3. 但为满足 AC-03"QA 受测版本一一对应"，TL **不自行宣称封版已 QA_PASS**，已准备独立 QA 二次复核提示词（HEAD `a65c336`），由独立 QA 另行复核封版制品一致性。

### 关于 independentQa=NOT_PERFORMED 的说明

包内 `acceptance/package_self_check.json` 的 `independentQa=NOT_PERFORMED` 是**作者离线自检的如实标注**（该文件是作者 self-check 的结果快照），不代表"独立 QA 未做过"。独立 QA 的结论记录在 Loop 的 `EVIDENCE.json` 的 `independent_qa` 字段（非包内自检文件），二者是不同层级的证据。封版 V1.0.1 已通过 `validate_package.py` 的 MANIFEST 自校验确保包内容受控，独立 QA 结论通过 EVIDENCE.json 的 reviewed_head 绑定到具体 HEAD。

---

## 五、AC-04 计数口径（已完成）

统一表述如下：

| 口径 | 值 |
|---|---|
| MANIFEST 受控文件 | **144**（V1.0.1，自排除 MANIFEST.json 自身） |
| 目录磁盘文件 | **145**（144 + MANIFEST.json） |
| Schema 数量 | **20**（14 原始 + 6 新增） |
| 正例 / 负例 | **20 / 40** |
| 自检通过 | **148** |

历史口径（清单 B 的"100 文件 / json 8 / 12 类 / 18 事件"）已全部作废，以 V1.0.1 MANIFEST 为准。

---

## 六、提交链路（封版相关）

| 提交 | 内容 |
|---|---|
| `a65c336` | 封版 V1.0.1（AC-01/AC-02 制品一致性，33 文件） |
| `a5a825b` | WP-R4-1 六合同源变更 |
| `91d5fed` | Feature Pilot 交付（QA 已复核） |

---

## 七、TL 声明

AC-01/02/03/04 四项整改已完成。封版 V1.0.1 形成唯一证据链（HEAD `a65c336` + tree `daa9b511` + ZIP `3bf13635`），ZIP 与 git tree 逐文件一致，自检 148/0、正负例 20/40、独立复算 PASS。

封版制品一致性已由 TL 完成自检（DEV_SELF_CHECK_PASS），但**独立 QA 的二次复核（HEAD a65c336）尚未执行**——按角色隔离规范，TL 不自行宣称封版 QA_PASS。已准备二次复核提示词，待独立 QA 复核后，D 阶段门禁可提升为 `PASS_FOR_OWNER_REVIEW`。
