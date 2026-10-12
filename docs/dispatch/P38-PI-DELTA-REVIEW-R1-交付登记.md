# P38 ↔ 新版 基线核对包 R1 — 交付登记

```text
交付人：tech_lead ｜ 交付时间：2026-09-22
包名：P38-PI-NEW-DELTA-REVIEW-20260922-R1.zip
位置：/home/szf/deliverables/P38-PI-NEW-DELTA-REVIEW-20260922-R1.zip
      /home/szf/deliverables/P38-PI-NEW-DELTA-REVIEW-20260922-R1.zip.sha256
工作目录（未打包全量）：/home/szf/deliverables/P38-PI-NEW-DELTA-REVIEW-20260922-R1/
状态：SUBMITTED_FOR_INDEPENDENT_REVIEW（TL 自检 PASS，非 QA_PASS）
```

## 1. 五项回执

| # | 回执项 | 值 |
|---|---|---|
| 1 | 文件名 / 大小 / SHA-256 | `P38-PI-NEW-DELTA-REVIEW-20260922-R1.zip` ｜ **3,125,536 bytes**（2.98 MiB）｜ `d5b7fd2910a973ef1207c6d0ec8d5a19998c16a45345a39bb7d6a6fe2563bc6e`（78 条目：68 文件 + 10 目录；`SHA256SUMS.txt` 67/67 校验通过） |
| 2 | 仓库 / 分支 / HEAD / 工作区 | `gits-cbanking` ｜ `recover/PI-ARCH-product-catalog` ｜ `0ab85ff3a11bc729af51b496f1359d2763521a1d` ｜ **406 未跟踪 / 28 修改 / 2 删除**（他人在飞，本次未触碰）；关联 `Leibniz-KERT` @ `922a674d3385a803704bc900d4f8ca21523276ed` |
| 3 | P38 正式需求 / KERT 权威来源 | **P38 正式需求（单文件）：NOT_FOUND → UNKNOWN**（检索范围与命令见包内 `evidence/command-logs/recon-commands.md` §2；未据截图补写）。代之以：需求变更方案 V1.0（**待批准**）+ SDD 契约 + 页面实现。**KERT 权威来源：已找到** —— 13 张产品卡、`04_serve/interpretation/PROD-CM-001.json`、`04_serve/releases/RLS-2026.09.06.1.json`（哈希见包内 `input-hashes.txt`） |
| 4 | 差异矩阵统计（95 项） | `P38_ALREADY_HAS 14` · `P38_NEEDS_ENHANCEMENT 18` · `NEW_CAPABILITY 43` · `PRESENTATION_ONLY 3` · `POTENTIAL_REGRESSION 7` · `CONFLICT 1` · `UNKNOWN 9`（**未默认 NEW_CAPABILITY**） |
| 5 | 推荐方案 / 最高等级缺陷 / 门禁建议 | 方案：**保留 P38（冻结）+ 新版增量 `I1–I6`**，不主张替换；最高等级缺陷：`F-1` 未承接 Release 三视图、`F-2` 9 章降级/遗漏、`F-3` 首屏摘要事实性倒退（均 **MAJOR**）；门禁：**`DEV_SELF_CHECK_PASS`**（`QA_PASS` 须由智能体 QA 独立签发，TL 不代签） |

## 2. 关键结论（一句话）

以 P38 为基线，**新版当前不构成功能升级**：12 类产品卡章节中 **9 章降级或遗漏**（含 Owner 点名的 C6 前置/互斥/替代/配套、C9 风险与人工复核、C11 不可变版本语义）；P38 的「现金池制度解读（Release + 三视图 + 依据原文）」**运行态真实可用但新版未承接**（`PROD-CM-001` 在新版与 `PROD-CM-003` 表现相同）。

**对 TL 自身历史结论的更正**：此前把"本机未配置 `snapshot-dir` 导致的 503"判定为 P38 能力缺失 —— 该结论**不成立**，已记账 `PC1-ANA-01` 并在包内更正。

## 3. 包内自证与可复算入口

```bash
cd <解压目录>
sha256sum -c SHA256SUMS.txt                       # 67/67
sed -n '1,40p' 00_README_AND_MANIFEST.md
sed -n '1,40p' 05_CHAPTER_AND_PRODUCT_PARITY.md   # 章节映射 + 同产品/现金池专项
sed -n '1,30p' 09_OPEN_ISSUES_AND_DECISIONS.md    # O-1/O-2/O-3 待 Owner 裁决
cat 04_REQUIREMENT_DELTA_MATRIX.csv | head -5
ls evidence/screenshots/p38 evidence/screenshots/new evidence/api-or-data-samples
```

## 4. 只读声明

本次交付为**只读盘点 + 运行观察 + 差异分析**：未按 95 项需求重写页面；未修改 P38 代码、KERT 制品、`specs/` 受控源；未签署任何 `QA_PASS`/`UAT_PASS`/冻结结论。
