# A3 包收口回执表（T-4 C5~C7）

| 项 | 结果 |
|---|---|
| **冻结哈希（composite）** | `a6b81ce2d790ace89baf1e5667356710d4521a665e61f2c099cfe05eba6e50e1` |
| 输入件 | `scripts/onto1_namespace_collision_check.py`=b14c5236346f · `scripts/onto1_reference_alignment_check.py`=ac7ced83f466 · `scripts/onto1_w15_acceptance.py`=e7ac80a3b6b4 · `specs/semantic/gits-core.owl.ttl`=705578d6324a · `loops/ONTO1-ontology-split/evidence/namespace-known-defects.json`=3ea485d4db49 · `loops/ONTO1-ontology-split/evidence/non-gate-log-allowlist.json`=85044fb1bf6a |
| C5 计数口径 | **全部一致** |
| C6 M12 夹具 | **确认在位**：`['M12 受控钉值载体无独立冻结记录 ⇒ C-4_PIN_FILE_UNFROZEN FAIL', 'M12 对照：记录落在扫描根内 ⇒ PASS（restore ⇒ PASS）', 'M12b 冻结记录写在扫描根之外（Loop 根 EVIDENCE.md 形态）⇒ 仍 FAIL（复现 F-3）']` |
| C7 日志自证 | `a3fix-after-wi_a4_namespace_collision-gate.log`（exit=3，首行 `# artifact=`=True） · `a3fix-after-wi_a4_namespace_collision-selftest.log`（exit=0，首行 `# artifact=`=True） · `a3fix-after-wi_a3_reference_alignment-gate.log`（exit=0，首行 `# artifact=`=True） · `a3fix-after-wi_a3_reference_alignment-selftest.log`（exit=0，首行 `# artifact=`=True） |

## 计数口径明细（实测 vs 声明）

| 门禁 | 声明 | 实测 | 一致 | 声明出处 |
|---|---|---|---|---|
| `wi_a4_namespace_collision_selftest` | 26 | 26 | 是 | memory/NEXT_SESSION.md T-4（26 条用例） |
| `wi_a3_reference_alignment_selftest` | 16 | 16 | 是 | memory/NEXT_SESSION.md T-4（selftest 16/16） |
| `wi_w15_a3_acceptance` | 8 | 8 | 是 | memory/NEXT_SESSION.md T-4（仪器 8/8） |
| `wi_d2_relation_resolution` | 11 | 11 | 是 | 本 Loop EVIDENCE.md（D2 分流 11/11） |
| `wi_d2_relation_resolution_selftest` | 10 | 10 | 是 | 本 Loop EVIDENCE.md（反例 10/10） |
| `wi_a2_disposition` | 9 | 9 | 是 | 本 Loop EVIDENCE.md（A-1 处置闭环 9/9：QA-W3R2 后新增 A9 独立键复核） |
| `wi_c2_consumer_scan` | 7 | 7 | 是 | 本 Loop EVIDENCE.md（C-2 消费者扫描 7/7） |

## 边界声明

- `wi_a4_namespace_collision` 仍为 **`INCOMPLETE`（exit 3）**：`C-1b` 待 D3 签署根域，**未提升**；
- 本次**未改**任何被检制品（两处脚本仅新增判据；基线 T-Box 未动）；
- 旧日志已按 `D-14` **先备份后重出**（备份目录 `/tmp/a3closeout-backup`）。
