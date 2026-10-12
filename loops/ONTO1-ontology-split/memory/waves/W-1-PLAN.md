# W-1（Wave -1）｜Plan

> 本文件是 **Wave -1（只读分析）** 的 PLAN；W0 及以后的 PLAN 在 G-1 通过后另起。
> 门禁命令唯一来源：`LOOP.yaml.gates`（禁止复制后漂移）。

## Goal

在 `RETURN_TO_HLD` 仍有效的前提下，完成委员会 §7/复审意见 §7 **明确允许**的全部只读工作，使 `G-1` 的三个非外部条件（WI-A2 / WI-A4 / WI-A6）达成，并把外部卡点（复审结论、角色任命、D1~D4）显式登记。

**不越界**：不改权威本体、不改合同登记、不切消费入口、不重钉、不标 `DESIGN_APPROVED`。

## Gates（11 项，均已在 `EVIDENCE.json` 记账）

| 组 | Gate | 断言要点 |
|---|---|---|
| WI-A1 | `wi_a1_baseline` | 基线哈希 + 32/34/1；45 资产 = 39/1/5；层归属 8/12/19；基线覆盖 100%；无占位根域 |
| WI-A1 | `wi_a1_attribution_selftest` | 删映射行 / 改制品牌径 / 占位根域 ⇒ FAIL；对照 ⇒ PASS |
| WI-A2 | `wi_a2_consumer_scan` | 期望命中 14/14；处置 100% 且无 `PENDING_TRIAGE`；净义务锚点 8/8 |
| WI-A2 | `wi_a2_scan_mutation` | 19 用例（含 fail-closed 与锚定有牙齿） |
| WI-A5 | `wi_a5_product_refs` | 产品卡可发现；三字段已声明；悬空引用非零且落盘；零实例关系显式声明 |
| WI-A5 | `wi_a5_product_refs_selftest` | 已解析 / 悬空 / 跨词表三形态区分；无卡片 ⇒ FAIL |
| WI-A6 | `wi_a6_cq_fixtures` | 六 CQ 六要素齐备；设计阶段无 `PASS`；D2/D4 阻塞项 `NOT_EVALUATED` |
| WI-A6 | `wi_a6_cq_fixtures_selftest` | CQ3 标 PASS / 删变异 / 删夹具 ⇒ FAIL |
| 锚定 | `contract_check` | `make check` 只读锚定（不含 wave -1 的 generate） |
| 锚定 | `security_check` | 密钥/权限/隔离资产 |
| 索引 | `index_status` | 索引红线门禁（drift 0） |

## Plan 与决策（为什么这样切）

1. **先固基线再谈影响面**：WI-A1 的哈希与计数是所有后续判断的锚，任何"改一处再比"都必须以它为参照。
2. **WI-A2 用"期望值锚定"而非"计数下限"**：把复审包 09 号初版清单的逐条锚点写成期望值，扫描检不到即失败——这是本轮唯一能防"0 命中即绿"的手段，并实际揪出 `CTR-` 模式缺失。
3. **处置表必须"100% 处置且零 PENDING"**：否则 Wave 2/3 的门禁会被"表存在但没填完"绕过。
4. **接受词法扫描的精度限制并显式抽样**：不假装 26690 命中都是义务；以抽样回源证伪同名，把"未确认"如实留给 Wave 2。
5. **把"40 处悬空引用"从口头数字变成清单**：D2 请求函没有清单就无法裁决，故补产品引用探针。
6. **索引新鲜度如实降级**：KERT 漂移 144 提交，声明 `INDEX_STALE(144)`，全部 KERT 结论回源到 `文件:行`，不声称掌握全局设计。

## Iteration 记录

实际 attempt 与证据哈希见 `memory/waves/W0-ITER.md`（由 `record_gate.py` 自动追加；文件名为模板沿用，内容含 W-1 全部 attempt）。
本轮 3 次自愈（先记后修）见 `FAILURES.md`：

- FAIL-2026-09-20-01（期望值形态错位 + A6 合并缺陷 + **真实缺口 `CTR-`**）
- FAIL-2026-09-20-02（处置表 184 处未分类）
- FAIL-2026-09-20-03（WI-A1 种子读取类型错误）

## Wave -1 完成定义（本 Loop 层）

- [x] 基线 v2 固定与四层归属矩阵重导（WI-A1）
- [x] 消费者全量扫描 S1~S5 + 变异复验（WI-A2）
- [x] 命名空间 ADR 草案（未预填根域）（WI-A4）
- [x] D2/D4 请求函 + SIM 临时权威声明草案（WI-A5）
- [x] 六 CQ 夹具设计（机读）（WI-A6）
- [x] WBS 重估（WI-A7）
- [x] 角色缺口与外部依赖登记（`memory/OWNER_REQUESTS.md`）
- [ ] WI-A3：D1 标准文本到手后完成条款适用性矩阵（**外部阻塞，非本 Loop 可控**）
- [ ] G-1：书面复审结论（**外部**）+ D3 签署（**外部**）
