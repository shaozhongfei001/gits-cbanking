# P38-oracle-deprecation｜Next Session Baton

| 字段 | 值 |
|---|---|
| **Updated** | `2026-09-13T00:00:00+00:00` |
| **holder** | `feature_pilot` |
| **packet** | `P38-oracle-deprecation` |
| **wave** | `W0` |
| **do_not_start** | QA_PASS、REAL_E2E_PASS、BUSINESS_SIGNED |

---

# P38-oracle-deprecation — 下一会话交接

## Baton

当前 holder：**无（Loop 有意阻塞）**

下一 holder：`tech_lead`（仅在外部依赖满足后接手）

## 禁止事项（先读这里）

1. **不要启动本 Loop 的删除动作。** 状态为 `blocked`，`precondition_kert_landed` 未过。
2. **不要从 GITS 会话写 Leibniz-KERT 仓库**，反之亦然（`Leibniz-KERT/AGENTS.md` §3 Rule 1 禁止修改 GITS）。
3. **不要物理删除** `specs/data/*` 与 `generated/data/*`；只标记 `migration_status`。
4. **不要删除** `docs/architecture/ADR-0007-oracle-readonly-enablement.md`。
5. **不要改动** `loops/P1-oracle-readonly/`、`loops/P13/`、`loops/P15/`（均 CLOSED）。
6. **不要在 KERT 侧能力交付前移除** `tools/quarantine/oracle/` 与 `scripts/oracle_*.py`（属迁移资产）。

## 解锁条件

Leibniz-KERT 侧 Loop `KERT-M7.x-oracle-data-understanding` 交付：

- Oracle 数据理解 Skill 已注册；
- Python Core OpenAPI v1 新增端点，GITS 可通过公共 HTTP 调用；
- 隔离资产、采集脚本、`specs/data` 输入已完成移交；
- KERT 侧独立 QA 通过；
- Owner 确认交接完成。

满足后：将 `STATE.json` 的 `blocked` 置 `false`、`status` 置 `in_progress`，并在 `EVIDENCE.md` 记录 KERT 侧提交哈希。

## KERT 侧应先做什么

在 **Leibniz-KERT 工作区新开会话**，让 agent 读取：

```
/home/szf/dev/gits-cbanking/docs/architecture/ORACLE_UNDERSTANDING_MIGRATION_PLAN.md
```

该文档含完整落点设计（`01_raw` / `02_work` / `03_core` / `04_serve` 分层、C-08 处理、G0–G6 Gate 定义、技术风险点）。

短提示词示例：

```text
你是 DKWS Tech Lead。读 /home/szf/dev/gits-cbanking/docs/architecture/ORACLE_UNDERSTANDING_MIGRATION_PLAN.md
与本仓 ADR.md 的 IMP-ADR-011、DKWS_DOCUMENT_CONFLICT_REGISTER.md 的 C-08，
在本仓建立 Loop KERT-M7.x-oracle-data-understanding 并先出 G0 ADR。
严禁修改 GITS 仓库。完成 G0 后 STOP。
```

## Owner 决策已确认项（无待确认）

- **KERT 侧 Oracle 只读授权签署方：Owner 兼任数据 owner，2026-08-31 已 GRANTED。**
  授权边界沿用 ADR-0007（只读 fail-closed、禁写、仅数据字典视图、不落客户行数据、凭据外置）。
  KERT 侧仍须在其 G0 ADR 中**显式登记**该授权——未落盘视为不存在。
- DBA / SECURITY_OWNER 书面确认为 KERT 侧 Loop 收尾条件，**不阻塞**只读验证。

本 Loop 当前唯一阻塞项是 KERT 侧能力交付（G5），**不是授权问题**。

## 上下文速查

- 影响面：`OracleSourcePort` 零业务消费者，删除低风险。
- 外部编目库：`/home/szf/dev/data/tzbank/data/metadata/oracle_metadata_catalog.sqlite`（22MB，仓库外，采集器缺失）。
- 凭据：仓库外 `~/.local_database.env` 的 `GITS_ORACLE_*`，绝不入仓。
