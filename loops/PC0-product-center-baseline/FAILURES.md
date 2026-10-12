# PC0-product-center-baseline｜Failures（append-only）

失败必须在修改实现之前由 `scripts/record_gate.py`追加。每项至少包含时间、Gate、命令、退出码、证据文件、初步分类和下一动作；修复后追加根因、变更SHA与原命令重跑结果，不覆盖原记录。

## FAIL-2026-09-20-01 ｜ MINOR ｜ pkc-contract-tests 首跑红（检测器缺陷，非合同缺陷）

- 时间：2026-09-20T15:40+08:00
- Gate：pcc-contract-tests（T0-11，Loop 自建消费者测试）
- 命令：`python3 scripts/pkc_contract_tests.py --self-test`
- 退出码：1
- 现象：baseline 判红 52 项，全部为 "xxx must reference PkcError"
- 初步分类：检测器缺陷 —— 各 operation 的 4xx/5xx 响应写的是**响应级** `$ref: "#/components/responses/BadRequest"`，检测器只做了一层 `$ref` 字符串匹配，未把响应组件解析到 `PkcError`
- 下一动作：修复 `detect()` 的响应引用解析（支持 `#/components/responses/*` 一级解引），修复后原命令重跑，要求 baseline 干净 + 6 个变异全部被捕获
- 备注：红测先记账再修（record_before_fix）；此失败不涉及合同源语义变更

### FAIL-2026-09-20-01 ｜ 闭环记录（原命令重跑）

- 根因：`detect()` 对 4xx/5xx 响应只做一层 `$ref` 字符串匹配；本合同错误响应统一写成响应级 `$ref: "#/components/responses/*"`，需解引到 `PkcError`
- 修复：新增 `_error_response_refs()`（支持 `#/components/responses/*` 一级解引）；M1 变异改为整体替换响应对象（响应级 $ref 无 `content` 键，原变异写法 KeyError）
- 原命令重跑：`python3 scripts/pkc_contract_tests.py --self-test` → **PASS（6/6 变异被捕获）**；`python3 scripts/pkc_contract_tests.py` → **PASS**
- 结论：非空转断言成立；合同源未改

