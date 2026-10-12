# GK5-l2-1-semantic-query｜Failures（append-only）

## FAIL-2026-09-12-08: L2-1 跨币种拒绝路径存在逻辑漏洞（8 条错误路径只触发 7 条）

- **时间**：2026-09-12（Wave C1，Feature Pilot）
- **Gate**：`l2_1_semantic_query_tests`
- **命令**：`python3 scripts/gk_ke_l2_1_semantic_query_tests.py`
- **退出码**：1
- **分类**：**MAJOR**（C04 §7 的 8 条失败行为之一未被触发 → 存在 noop 风险）
- **现象**：
  ```
  [X] cross_currency: NOT rejected (expected CURRENCY_POLICY_REQUIRED)
  [X] error paths never triggered (noop risk): ['CURRENCY_POLICY_REQUIRED']
  ```
- **根因**：跨币种分支的判定顺序错误。
  原实现先判 `request.get("currency") not in {None, "CNY"}` ——
  当请求 `currency=None` 时该条件为 **False**，直接**穿透**；
  随后的 `other_ccy and currency is None` 分支依赖账户侧数据，
  在当前夹具（SIM-C001 全为 CNY 账户）下 `other_ccy` 为空，故**从未触发**。
  → `CURRENCY_POLICY_REQUIRED` 这条 C04 明确的错误路径**恒不触发**。
- **合规影响**：C04 §7 列出 8 条失败行为，其中「CURRENCY_POLICY_REQUIRED / FX_MISSING —
  不输出混合金额」是防跨币种误加的关键防线（呼应 C07 §6 的跨币种负例）。未触发即未验证。
- **下一动作**：修正判定顺序 —— 指标声明 `currencyPolicy=CNY_ONLY`，
  故请求币种**必须显式等于 CNY**，否则一律拒绝；保留账户侧 `other_ccy` 检查作为二次防线。重跑。

### 修复记录（第 1 轮，已闭环）

- **修复**：`gk_ke_l2_1_semantic_query_tests.py` 的 `compile_and_run`：
  改为 `if requested_ccy != "CNY": return CURRENCY_POLICY_REQUIRED`，
  使「未指定币种」与「非 CNY 币种」**都**被拒；账户侧检查保留。
- **验证**：8 条错误路径**全部触发**（`error paths covered (8)`）；
  C001 仍 = 2,983,333.33；正例结果最小返回字段齐备。
- **状态**：CLOSED（1 轮）。

---

## FAIL-2026-09-12-09: L2-1 白名单编译断言存在冗余路径掩盖（独立 QA 变异测试发现）

- **时间**：2026-09-12（Wave C1，Independent QA 审计）
- **Gate**：`l2_1_semantic_query_tests`
- **命令**：变异测试 —— 禁用 `FORBIDDEN_FIELDS` 显式检查后重跑
- **退出码**：0（**期望非 0**）
- **分类**：**MAJOR**（C04 §6「禁止 rawSql、Cypher、SPARQL 字段」的主防线未被独立验证）
- **现象**：禁用显式禁字段检查后测试**仍 PASS**。
- **根因**：存在**两条**拒绝路径 ——（a）显式 `FORBIDDEN_FIELDS` 检查；（b）
  未知字段检查 `set(request) - ALLOWED_REQUEST_FIELDS`。
  `rawSql`/`sparql`/`cypher` 恰好**都不在** `ALLOWED_REQUEST_FIELDS` 中，
  故 (b) **完全遮蔽**了 (a)。禁用 (a) 后 (b) 仍返回 `RAW_QUERY_FORBIDDEN`，断言看不出差异。
- **合规影响**：C04 §6 明令「请求**只允许** metricId/version、已定义参数和业务用途；
  禁止 rawSql、Cypher、SPARQL 字段」。虽然当前行为正确，但**主防线未被验证**，
  一旦未来有人把某禁字段误加入 `ALLOWED_REQUEST_FIELDS`，(b) 也会失效而测试无感。
- **下一动作**：为显式禁字段路径建立**独立可观测信号**，使两条防线可分别验证。

### 修复记录（第 1 轮，已闭环）

- **修复**：显式禁字段命中时返回**不同错误码** `RAW_QUERY_FIELD_DENIED`
  （仍属拒绝，但可与未知字段路径区分）；测试新增对 `rawSql`/`sparql`/`cypher`
  断言 **`RAW_QUERY_FIELD_DENIED`**，未知字段仍断言 `RAW_QUERY_FORBIDDEN`。
- **验证（变异必须失败）**：再次禁用显式禁字段检查 → 测试 **FAIL**
  （`raw_sql: error 'RAW_QUERY_FORBIDDEN' != expected 'RAW_QUERY_FIELD_DENIED'`）。
- **验证（恢复必须通过）**：恢复 → 测试 **PASS**，9 条错误路径全部触发。
- **状态**：CLOSED（1 轮）。
