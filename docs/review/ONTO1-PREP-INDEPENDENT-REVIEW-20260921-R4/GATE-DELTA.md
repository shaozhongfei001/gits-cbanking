# 门禁增量（自旧包以来，F-04）

- 上一冻结版：`ONTO1-PREP-INDEPENDENT-REVIEW-20260921-R3`（SHA-256 `d3c43e770387e26f771d46f5316d31f84c57f8e313b4a3249c31ca9bd3c6d1a5`，**冻结留档**）
- 更早版本（冻结留档）：v1 `700e2b373eaa393b…` · R2 `83a3c08a3586116c…`
- 本包（R4）与看板**同一快照**：PASS=48 · FAIL=0 · PENDING_EXTERNAL_AUTHORITY=1 · 共 49

| 新增门禁 | 状态 | exit | 原始日志 |
|---|---|---|---|
| `wi_class_reconciliation` | pass | 0 | `wi_class_reconciliation-20260921T095056Z.log` |
| `wi_class_reconciliation_selftest` | pass | 0 | `wi_class_reconciliation_selftest-20260921T095056Z.log` |
| `wi_construction_plan` | pass | 0 | `wi_construction_plan-20260921T102852Z.log` |
| `wi_construction_plan_selftest` | pass | 0 | `wi_construction_plan_selftest-20260921T102852Z.log` |
| `wi_l1_prep` | pass | 0 | `wi_l1_prep-20260921T092921Z.log` |
| `wi_l1_prep_selftest` | pass | 0 | `wi_l1_prep_selftest-20260921T092921Z.log` |
| `wi_prep_package_build` | pass | 0 | `wi_prep_package_build-20260921T102927Z.log` |
| `wi_prep_package_build_selftest` | pass | 0 | `wi_prep_package_build_selftest-20260921T102927Z.log` |

## 本轮相对 R3 的变化（**无新增门禁**，仅精度与文字）

| 项 | R3 | R4 |
|---|---|---|
| `onto1_construction_plan --gate` | 7/7 | 7/7（判定字段扩展：见下） |
| `onto1_construction_plan --selftest` | 8/8 | **11/11**（新增 M6 分类篡改 / M7 occurrences 篡改 / M8 明细之和） |
| `RESULTS.md` 逐工具读数 | 硬编码（施工计划写 6/6、自检 3/3） | **从登记日志提取**（实际 7/7、11/11） |
| 说明文字 | 残留「R2 包/快照」 | 已更正为「R3 冻结版 / R4 本包」 |

**运行环境**：Python 3.10.12 · cwd `/home/szf/dev/gits-cbanking` · 运行者 tech_lead（**作者自检**）

> 看板计数 48 PASS / 0 FAIL / 1 PENDING（共 49）与上一冻结版一致；本包按**同一快照**重出，不改变任何门禁结论。
