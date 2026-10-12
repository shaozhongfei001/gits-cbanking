# 交接单 · independent_qa（AN0-ccrm-analytics-landing）

| 项 | 值 |
|---|---|
| 角色 | independent_qa |
| Loop | AN0-ccrm-analytics-landing |
| Baton | `independent_qa`（复核期）→ 复核毕交回 `owner_review` |
| 入口 | `evidence/INDEPENDENT_QA_PACKAGE-AN0.md` |
| 期望产出 | `evidence/INDEPENDENT_QA-AN0-<session>.md` + 判定（通过则以 QA 角色记 `QA_PASS`） |
| 禁止 | 改代码/文档、复用 TL 结论、以 mock 代替真实链路、代签 Owner 决策、恢复认证 |

## 复核要点速览

1. 6 门禁独立复跑（命令见 `LOOP.yaml`），比对 QA 包 §1.1 证据 sha256；
2. 变异 M1~M5 反证断言非空转（尤其 `frontend_typecheck` 空日志须由 M4 证明非假绿）；
3. 口径 Q4/Q5、隔离 Q6、注入 Q7、并发 Q8；
4. 界面 Q9/Q10/Q11 与 Owner 五项决策 Q12。

## 上下文

- 交付说明：`docs/dispatch/CCRM-经营分析菜单登记-V1.0.md`（GITS）、`../Leibniz-KERT/docs/integration/CCRM_ANALYTICS_LANDING.md`（KERT）
- 已知自愈记录（复核时判断是否真正修好）：`FAILURES.md` 7 条
- 运行前置与复现命令：QA 包 §2

## 交接说明

TL 不代签 `QA_PASS`。QA 判定若为 FAIL，请将缺陷写入 `FAILURES.md` 并交回 TL 修复；修复后由 QA 重跑对应门禁。
