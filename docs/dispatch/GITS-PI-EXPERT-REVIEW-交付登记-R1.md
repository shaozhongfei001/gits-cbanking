# GITS PI 外部专家审阅包 — 交付登记 R1

```text
交付人：tech_lead（AI/LLM 角色）｜ 交付时间：2026-09-22
包名：GITS-PI-EXPERT-REVIEW-20260922-R1.zip
位置：/home/szf/deliverables/GITS-PI-EXPERT-REVIEW-20260922-R1.zip
      /home/szf/deliverables/GITS-PI-EXPERT-REVIEW-20260922-R1.zip.sha256
状态：SUBMITTED_FOR_EXTERNAL_REVIEW（不含任何验收结论；QA_PASS 未申请）
用途：交外部专家独立审阅"新版是否真的优于 P38"及最小施工方案
```

## 1. 交付回执

| 项 | 值 |
|---|---|
| 大小 | **5,858,747 bytes**（5.59 MiB）；**202 条目**（145 文件 + 57 目录） |
| SHA-256 | `f680d1f181d9e1e4d8dfdd5761a64fc8ac711bb804d88f235419f7ab43aded2f` |
| 包内校验 | `SHA256SUMS.txt` **143/143 通过**（0 FAILED；不含 MANIFEST 与自身） |
| 目录 | `/home/szf/deliverables/GITS-PI-EXPERT-REVIEW-20260922-R1/`（未压缩全量） |

## 2. 包内结构与内容

```text
00_EXPERT_REVIEW_BRIEF.md      审阅提示（约 1,100 字；含产物性质声明、三条核心结论、三处自曝错误、7 条质疑清单）
01_EXECUTIVE_SUMMARY.md        全部生成物总结（8 阶段时间线 + 关键数字 + 结论强度分级）
02_REVIEW_CHECKLIST.md         可执行核查清单（B1–B9 可复算项 / C1–C6 待判断 / D 反向判否条件 / E 越界红线）
03_DECISIONS_PENDING.md        待裁决（阻断 3：O-1/O-2/O-3；默认 7：O-4–O-10；专家判断 5：X-1–X-5）
10_generated_documents/        本次会话 7 份分析文档原样副本
                               （需求准入与影响分析 / 业务调研与价值论证 / 角色与决策权登记 /
                                 台阶1议题清单 / P38→新版差异表 / 数据来源与可信度清单 / R1 交付登记）
20_pc1_implementation/         PC1+PC1.5 实现：source 31 文件（后端 12 / 前端 19，含改动过的 navConfig 与 router）
                               + loop_PC1（EVIDENCE / FAILURES / STATE / memory）+ screenshots（1680/1440/1280）
30_R1_delta_review_package/    基线核对包 R1 全量（11 份规定文件 + evidence 六类）
40_inputs_reference/           Owner 提供的输入：新版需求包 8 文件 + 截图（含重复判定说明）
MANIFEST.md / SHA256SUMS.txt   清单与哈希
```

## 3. 关键结论（与包内一致）

1. **新版当前不构成功能升级**：P38 的 12 类产品卡章节中 **9 章降级或遗漏**（含"前置/互斥/替代/配套""风险与人工复核""不可变版本语义"被比较表/版本徽章替代）；
2. **P38 现金池制度解读真实可用、新版未承接**：配置快照目录后 `200`（`RLS-2026.09.06.1`，准入视图可见 `SRC-CM-001 第十条`）；新版 `PROD-CM-001` 与 `PROD-CM-003` 表现相同；
3. **95 项需求不应作为"从零新建"施工指令**：`ALREADY_HAS 14 + NEEDS_ENHANCEMENT 18 + POTENTIAL_REGRESSION 7`，真实新增 43 项中多数未实现。

## 4. 生成者自曝问题（包内已同步）

| 编号 | 内容 |
|---|---|
| `PC1-ANA-01` | 曾把"未配置 `snapshot-dir` 的 503"判定为 P38 能力缺失 → 已更正并记账 |
| `PC1-GOV-01` | 曾以 TL 身份未声明角色切换即写实现 → 已记账，后续强制切 `feature_pilot` |
| `E-2` | 曾用 DEMO 数值论证业务价值 → 已撤回，全篇标注数据可信级别 |
| `C-01`/`C-02` | 采集侧自伤缺陷（截图命名、`sed` 缺 `p`）→ 已修并记录于 R1 包内 |

## 5. 边界声明

本次为**只读盘点 + 运行观察 + 差异分析 + 已交付的 PC1/PC1.5 实现**；未修改 P38 代码、KERT 制品、`specs/` 受控源；**未**签署 `QA_PASS`/`UAT_PASS`/冻结结论；**未做用户测试**，不宣称任何用时结论。
