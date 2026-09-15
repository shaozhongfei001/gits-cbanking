# ADR-0007｜Oracle EDwCRM 只读访问启用

状态：`ACCEPTED_WITH_READ_ONLY_BOUNDARY`

> **2026-08-31 承载方变更提示**：本 ADR 的历史决策与授权记录保留不变。Owner 已于 2026-08-31 决定将「Oracle 数据集市数据理解能力」迁出 GITS，改由 Leibniz-KERT（DKWS）维护，见 `ADR-0018`。GITS 侧不再演进 Oracle 直连的数据理解实现；KERT 侧需自建独立 ADR 与数据所有者授权，本 ADR 的授权**不跨仓库自动生效**。

## 背景

`tools/quarantine/oracle/profile.json` 原要求 DATA_OWNER、DBA、SECURITY_OWNER 三方书面授权方可启用 Oracle 资产，默认 `enabled=false`。项目 owner 同时作为数据 owner，于 2026-08-02 显式授权「允许对 Oracle 的读操作、无需隔离」，并要求按治理流程落实：本 ADR + 数据 owner 授权记录 + 专用 loop。

Oracle 数据源：`oracle-vm:1521/ACRM`，账号 `edwcrm`（凭据存于仓库外 `~/.local_database.env` 的 `GITS_ORACLE_*`）。合同 `CTR-MAP-001`（`oracle_mapping_spike`，`spike_only`）是当前唯一与 Oracle 相关的受控合同。

## 决策

启用对 Oracle EDwCRM 的**只读**访问，用于元数据探查与语义映射 Spike：

- 连接后必须先执行 `SET TRANSACTION READ ONLY`；失败即关闭连接并终止（`tools/quarantine/oracle/readonly_guard.py` 强制）；
- 仅允许读取与元数据/映射探查，**禁止任何写操作**；
- 源码默认只保存哈希与行段定位（`source_capture: HASH_AND_LOCATOR_BY_DEFAULT`），不得在仓库内保存客户行数据；
- Catalog 输出仅作为数据映射证据/候选语义，**不得自动升级为业务主本体**；
- 环境限定为受控测试/SIT（`oracle-vm`），不接入生产写回热路径。

## 授权记录

| 角色 | 状态 | 说明 |
|---|---|---|
| DATA_OWNER | GRANTED | 项目 owner 以数据 owner 身份授权，2026-08-02 |
| DBA | PENDING | 原 profile 要求；owner 指示按只读先行，DBA 书面确认待补 |
| SECURITY_OWNER | PENDING | 同上，安全 owner 复核待补 |

owner 明确指示「没必要隔离、允许读操作」；本 ADR 在保留只读强制的前提下先行启用，DBA/SECURITY_OWNER 书面确认作为该专用 loop 的收尾条件之一，不阻塞只读验证。

## 后果

- 解锁 `CTR-MAP-001` 的 Oracle 映射 Spike 与语义投影重建的只读探查；
- 必须维护只读强制、审计留痕、Oracle 版本夹具与离线解析回归；
- 任何写、写回或生产连接仍被禁止，需另行 ADR 与授权。

## 待验证

- 真实 Oracle 只读连接成功；
- `SET TRANSACTION READ ONLY` 在真实 Oracle 上被强制且失败关闭；
- 元数据只读往返（如表/列清单，不含客户行数据）；
- 独立 QA 复跑只读连接并留存证据。
