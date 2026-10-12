# GK6-l3-1-factory-candidate｜Failures（append-only）

## FAIL-2026-09-12-10: L3-1 断言误把「18 文档」等同于「18 个 sourceId」

- **时间**：2026-09-12（Wave C2，Feature Pilot）
- **Gate**：`l3_1_factory_tests`
- **命令**：`python3 scripts/gk_ke_l3_1_factory_tests.py`
- **退出码**：1
- **分类**：**MINOR**（断言口径错误，非实现缺陷）
- **现象**：`[chain] expected 18 documents, got 17`
- **根因**：C08 L3-1 要求「**18 文档**全可回链」，C07 §3 定义 18 份 = 6 产品说明 + 4 产业研究
  + 4 客户互动纪要 + 2 模拟制度 + **同一产品的新旧版本补充说明 2 份**。
  最后两份是**同一 sourceId（SIM-P001-SUPPLEMENT）的两个版本**（0.9.0 与 1.0.0）。
  故**文档数 = 18**，而**唯一 sourceId 数 = 17**。断言错用了 sourceId 去重计数。
- **合规影响**：这是**口径**问题而非缺陷；但它暴露了一个有益事实——
  版本对（旧/新）的存在正是 C07 §3「产品旧/新版包含时间与条件差异，不能直接选数值更宽松的一版」的**载体**，
  必须在回链校验中作为**两条独立文档版本**处理，不能被去重抹掉。
- **下一动作**：改为按 (sourceId, sourceVersion) 计数并断言 18；同时**新增断言**
  要求存在至少一对「同 sourceId 不同 version」的文档（版本对未被误合并）。

### 修复记录（第 1 轮，已闭环）

- **修复**：`gk_ke_l3_1_factory_tests.py` 改为按 `(sourceId, sourceVersion)` 计数；
  新增 `version-pair-present` 断言，确认同 sourceId 存在 ≥2 个版本。
- **验证**：`documents_backlinked=18/18`；版本对检测通过；P01–P06 全部阻断条件被负例覆盖（14 个负例）。
- **状态**：CLOSED（1 轮）。

---

## FAIL-2026-09-12-11: L3-1 回链校验断言无触发路径（独立 QA 变异测试发现）

- **时间**：2026-09-12（Wave C2，Independent QA 审计）
- **Gate**：`l3_1_factory_tests`
- **命令**：变异测试 —— 禁用 `frag_id not in frag_by_id` 断链检查后重跑
- **退出码**：0（**期望非 0**）
- **分类**：**MAJOR**（C08 L3-1 核心退出标准「18 文档全可回链」未被真实验证）
- **现象**：禁用断链检查后测试**仍 PASS**。
- **根因**：正常夹具中**所有**断言的 `evidenceSpan.fragmentId` **都**能解析，
  故断链分支**从未进入**；断言**恒真（noop）**。
  「全可回链」这一结论因而**没有被真正检验** —— 若未来出现断链，
  该断言不会报警。
- **合规影响**：C08 L3-1 退出标准原文第一条即「**18 文档全可回链**」。
  空转断言意味着该标准的形式化验证缺失。
- **下一动作**：加入**故意断链**的负例夹具（引用不存在 fragmentId），
  使回链检查具备真实触发路径；并把「必须存在可被拒的断链样例」写成 fail-closed 断言。

### 修复记录（第 1 轮，已闭环）

- **修复**：
  1. 新增 `specs/knowledge-architecture/factory/negative_fixtures/dangling_evidence_span.json`：
     一条断言引用不存在的 `FRAG-DOES-NOT-EXIST`。
  2. 测试新增对该夹具的执行：**必须**被回链检查拒绝；
     同时保留对正常夹具「0 断链」的正向断言。
- **验证（变异必须失败）**：再次禁用断链检查 → 测试 **FAIL**（断链夹具未被拒）。
- **验证（恢复必须通过）**：恢复 → 测试 **PASS**。
- **状态**：CLOSED（1 轮）。
