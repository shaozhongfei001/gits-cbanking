# PC-i1-chapter-inheritance｜Next Session Baton

| 字段 | 值 |
|---|---|
| **Updated** | `2026-09-22T07:30:00+00:00` |
| **holder** | `tech_lead` |
| **packet** | `PC-i1-chapter-inheritance` |
| **wave** | `W0（已定义 scope/gates/exit criteria，未开始实现）` |
| **do_not_start** | 实现前必须先声明 `[角色切换] tech_lead → feature_pilot`（单独上下文）；不得改 P38 冻结文件与 `specs/` 受控源；不得自签 QA_PASS |

## 本 Loop 要做什么（依 Owner 2026-09-22 已批 O-1/O-2 范围）

把 P38 的 **12 类产品卡章节**在新版逐一落位：

```text
C1  产品概览与客户价值        → 首屏摘要 + 指向附录原文（当前：降级，需补来源/状态）
C2  适用客户与适用场景        → 「适用边界」章（当前：章节位缺失）
C3  产品能力                  → 能力标签 + 指向原文（当前：部分）
C4  准入条件                  → 「适用边界」章（缺失）
C5  排除条件与禁止用途        → 「适用边界」章（缺失）
C6  前置/互斥/替代/配套产品   → **独立区块，必须可见**（缺失；不得被比较表替代）
C7  流程与材料                → 「办理流程」「申请材料」章（缺失）
C8  价格边界                  → 「价格与协议」章（缺失）
C9  风险提示与人工复核        → **独立区块，必须可见**（缺失）
C10 销售边界                  → 首屏/边界区（当前仅通用 2 条，产品级缺失）
C11 不可变版本语义            → 版本区承载节语义（当前：被徽章替代）
C12 EvidenceRef（源文件与条款定位）→ 证据位（缺失；3 张 FIN 卡有该节）
```

**DoD**：未实现章节必须**原样呈现该章原文 + 相对来源标识 + 有效状态**（不得空占位/示意内容）；
同产品对照满足 **事实不丢 + 来源可达 + 阅读更快**（`R2 06` §6）。

## 准入与门禁

- 门禁命令见 `LOOP.yaml`（`make generate` / `make check` / `make security-check` / 前端类型检查 / 前端单测 / e2e 对照）。
- 证据必须落在 `loops/PC-i1-chapter-inheritance/evidence/`，并由 `scripts/record_gate.py` 登记。
- **独立 QA 未指定前不得宣布通过**（`independent_qa` 状态 pending）。

## 依赖与阻断

| 项 | 状态 |
|---|---|
| O-1 过渡安排（Owner 批） | ✅ 已解锁本 Loop |
| O-2 ①② 分别建模（Owner 批） | ✅ 已解锁（C6 独立区块） |
| O-3 合同字段（`published_version_id`/`evidence_snapshot_id`） | ⏳ 合同 Owner 待签 ⇒ **不阻断本 Loop**（I1 不依赖） |
| DEMO 徽标字段（合同提案 1） | ⏳ 合同 Owner 待签 ⇒ 不阻断 |
| 身份/权限服务 | 缺失 ⇒ 权限过滤不在本 Loop |

## 下一会话第一步

```text
1) 声明 [角色切换] tech_lead → feature_pilot（单独上下文）
2) 读 loops/PC-i1-chapter-inheritance/LOOP.yaml 的 scope（严格不越界）
3) 先写测试（12 章落位断言 + 原文可见断言 + C6/C9 独立区块断言），再写实现
4) 每完成一门禁：scripts/record_gate.py 登记 + 更新 STATE.json
```
