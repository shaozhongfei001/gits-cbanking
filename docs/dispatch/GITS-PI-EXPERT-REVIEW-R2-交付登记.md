# GITS PI 外部专家审阅包 R2 — 交付登记

```text
交付人：tech_lead（AI/LLM 角色）｜ 交付时间：2026-09-22
包名：GITS-PI-EXPERT-REVIEW-20260922-R2.zip
位置：/home/szf/deliverables/GITS-PI-EXPERT-REVIEW-20260922-R2.zip（+ .sha256）
依据：~/deliverables/GITS-PI-EXPERT-REVIEW-R1-CODEX-意见-20260922.md（审阅状态 INSUFFICIENT_EVIDENCE）
R1 原包：保留未覆盖（sha256 f680d1f181d9e1e4d8dfdd5761a64fc8ac711bb804d88f235419f7ab43aded2f）
状态：SUBMITTED_FOR_OWNER_AND_INDEPENDENT_QA（作者自检；不含 QA_PASS）
```

## 1. 回执

| 项 | 值 |
|---|---|
| 大小 / SHA-256 | **3,386,793 bytes**（3.23 MiB）｜ `747a5b4a679605a30b2cf899a2df1b0019aac5d4de318c048d987abe16f85665` |
| 包内校验 | `SHA256SUMS.txt` **75/75 通过**（0 FAILED）｜88 条目（75 文件 + 13 目录） |
| 仓库 / 分支 / HEAD | `gits-cbanking` ｜ `recover/PI-ARCH-product-catalog` ｜ 本件提交前 HEAD `2d3534d` |

## 2. 规定文件（9 项 + MANIFEST + SHA256SUMS）

`00_修订说明及逐缺陷响应.md` · `01_权威输入与签批清单.md` · `02_O1-O3_Owner决策单.md` ·
`03_十二章四维映射.csv` · `04_95项差异矩阵_R2.csv` · `05_合同端点与版本快照映射.md` ·
`06_同产品同条件走查.md` · `07_DEMO与路径风险处置.md` · `08_逐项测试追踪表.csv` · `MANIFEST.md` · `SHA256SUMS.txt`

## 3. 核心修订

| 项 | R1 | R2 |
|---|---|---|
| `PI-FR-069` | `CONFLICT` | **`NEW_CAPABILITY`**（撤回冲突；同业另案） |
| 统计 | `CONFLICT 1` / `NEW_CAPABILITY 43` | `CONFLICT 0` / `NEW_CAPABILITY 44` |
| `EVIDENCE=N/A` | 30 行 | **0 行** |
| 章节表述 | "1+8+2=12"、"9 章降级/遗漏" | **降级 1 + 结构缺失 8 + 部分 2 + 被替代 1 = 12**（四维 CSV） |
| 契约消费 | 混用"已消费解读契约" | 两条链分列（`/cards/{id}` = `CTR-API-001`；`/{productId}/interpretation` = `CTR-PK-INT-001`） |
| P38 风险 | 仅登记 | **隔离已执行留证** + 候选补丁（未应用）+ DEMO 徽标字段提案（待合同 Owner） |
| 走查 | 入口不等价、"11 次展开" | 同入口/同产品/同版本；P38 实为 **2 次展开**；点击与"找到正确内容"分列；无用时结论 |

## 4. 新增的实测证据（R2）

| 证据 | 结果 |
|---|---|
| 用途白名单阻断 | `purpose=RECOMMENDATION` → **422 `PURPOSE_NOT_ALLOWED`** |
| 视图白名单 | `view=FOO` → **400** |
| 未发布产品 | `PROD-CM-003` → **404** |
| 访问隔离控制 | `gits.product-knowledge.enabled=false` → 链①② **404**；新版端点 **200** |
| 修复前/隔离后对照（脚本客观断言） | 绝对路径 `true→false`；DEMO 数值 `true→false`；"有证据支撑/新鲜可用" `true→false` |
| 复跑测试 | 后端 **29/0**；前端 **24/24**（4 文件）；合同 **check PASS + self-test PASS** |

## 5. 未关闭项

`P-2` 绝对路径（待 Owner 批准解冻范围后应用候选补丁）；`P-3` DEMO 徽标（待合同 Owner 批准字段）；
`U-1` 通用合同路径前缀重复；`U-2` 版本/快照字段语义；`U-3` KERT 侧 `EVSNAP` 生成落点；`U-4` `stale→409` 未构造复现；
`C-2` 40 条悬空产品引用（产品 Owner）；`C-3` 同业来源启用需产品+合规确认。

## 6. 边界声明

未改 P38 代码、KERT 制品、`specs/` 受控源；候选补丁与合同提案均为**待批件**；本包为**作者自检**，
`evidence/test-results/r2-*.log` 系同一作者在同一环境复跑，**不构成独立环境复现**；不含 `QA_PASS`/验收/冻结/生产可用结论。
