---
schema: rule/v1
rule_id: RUL-002
name: evil
rule_type: ALERT
priority: 10
execution_mode: AUTOMATIC
when: [all]
then: {action: "$(rm -rf /)"}
required_inputs: [x]
test_case_ids: [a, b]
validation_status: CANDIDATE
status: ACTIVE
version: 1.0
---
# 规则

## 业务解释

## 输入与输出

## 证据

## 人工责任边界

## 测试说明
