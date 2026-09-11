# GK1-l0-2-contract-activation｜剩余阻塞：G2 跨仓确认（唯一阻塞项）

> 角色：Tech Lead（planning_review）｜更新：2026-09-12｜HEAD：`23bf2c5`
> 状态：`qa_pass`（未退出）｜Baton：`independent_qa`（G4 已完成）
> 变更历史：本文件原记录 5 项 Owner 待签事项；Owner 已于 2026-09-12 签署 `GK-KE-OWNER-002`，故现仅剩 **G2**。

---

## 1. 已完成（Owner 决议 + 条件关闭）

| 项 | 状态 |
|---|---|
| Owner 决议 `GK-KE-OWNER-002` | ✅ 已签署（5× `APPROVED_WITH_CONDITIONS`）；文书 sha256 `3a456022…` |
| **G1** 版本与制品绑定 | ✅ 关闭（四版本角色区分；封版受控路径 `docs/dd/gk-ke-contract` tree `4c5f5373` 内容级验证） |
| **G3** 交换对象对应 | ✅ 关闭（20 项六类重算；纠正 3 处误分类） |
| **G4** 受影响范围复核 | ✅ 关闭（独立 QA session `qa-gk1-g4-001`；零合同差异 → 原 QA 证据有效 + 门禁复跑 + 变异复验） |
| **OF-02** 状态分离 | ✅ 关闭（三平面 + 3 反例；作废"无 SIM 前缀⇒非模拟数据"推断） |
| **OF-03** 版本制品绑定 | ✅ 关闭（内容级证明替代祖先推导） |
| **OF-04** 对象对应 | ✅ 关闭 |
| **OF-05** QA 证据精度 | ✅ 关闭（短 hash 补全；差异确认为时间差） |

## 2. 唯一剩余阻塞：G2（来源与转换绑定）

**性质**：跨仓人工确认（`Leibniz-KERT` 维护方）——**不在任何 Agent 权限内**。

**实测（TL 已执行检索，结果如实登记）**：对 `Leibniz-KERT @ 3b6640b` 检索五条映射键：

| 映射 | KERT 侧实测 | 判定 |
|---|---|---|
| 1 `KM-GITS-ROOT` | 未发现 SIM 转换 | 一致 |
| 2 `KM-CORP-RM-PREVISIT` → `SIM-MAP-FINANCE` | KERT **实际消费** `KM-CORP-RM-PREVISIT`（`src/kert/application/skills.py:637`），但**无 `SIM-MAP-FINANCE` 证据** | 部分 |
| 3 `ASSET-KNOW-PRODUCT-CARDS` → `SIM-ASSET-P001` | **零命中** | 未核对 |
| 4 `AC-PREVISIT-001` → `ActivationPlan` | 源**存在**已确认；转换关系未确认 | 部分 |
| 5 `RP-CORP-RM-001` → `SIM-ROUTE-001` | **零命中** | 未核对 |

**须 KERT 维护方回答的 4 问**（详见 `docs/architecture/GK-KE-L0-2-G2-KERT核对登记-V1.0.md` §3）：

1. 映射 3：`ASSET-KNOW-PRODUCT-CARDS` 的对象粒度是**集合 / 入口 / 单卡**？
2. 映射 5：`RP-CORP-RM-001` 的源版本、匹配条件、优先级、歧义处理 + 目标策略**内容 hash**？
3. 映射 2：`SIM-MAP-FINANCE` 的适用条件、必需节点、参数、依赖对齐——KERT 是否认领？
4. 映射 4：`AC-PREVISIT-001` → `ActivationPlan` 的编译依赖关系是否获 KERT 认可？

**警告**：KERT 仓内 `docs/integration/KERT_GITS_STATE_MAPPING_CANDIDATE.md` 是 **WP1-3 产品推荐状态映射**
（自述 `CANDIDATE / FROZEN=NO / IMPLEMENTED=NO`），**不得**引作 L0-2 五条映射的确认证据。

## 3. 由 G2 派生的未关闭项（不得静默放过）

| 项 | 因 G2 而 |
|---|---|
| **OC-01** 版本对象对应 | **未关闭**（§5 规定 OC-01 关闭前须完成 G2；与 Owner"证据不足"裁定一致） |
| **ACT-01** 契约激活 | **未生效**（§5 规定 G1–G4 全闭方可激活） |
| **OF-01** 映射粒度 | 部分关闭（映射 3 粒度、映射 5 策略 hash 待 KERT） |
| **G5** 激活记录 | 部分（签署已登记；激活事件待 G2 关闭） |
| Loop 退出 | **未退出**（保持 `qa_pass`，不标 `closed`） |

## 4. 另有两处决议前提被实测推翻（已在证据中登记）

1. §2.2 称"两个地图仍为通配 ID、**版本为空**" → 实测四个既有地图 `version=0.1.0`（**非空**）。
2. §2.2 称收口文档"未以祖先关系推导封版未改写" → 原收口文档确实仅用祖先关系；**现已改为内容级证明**。

## 5. 建议（供 Owner 裁定，TL 不自行决定）

**方案 A（等待）**：向 KERT 维护方发出 §2 四问，答复后关闭 G2 → 激活。
**方案 B（缩权激活）**：仅激活已获 KERT 侧一致确认部分（映射 1 根地图 + 映射 2 的消费关系），
映射 3/4/5 维持 `pending_owner_confirmation` 并**禁止参与运行时**。

方案 B 属**改变激活范围**，须 Owner 单独裁定 —— TI 不自行决定。

## 6. 授权延续说明

依 §5 末段：若条件全部成立且未改变业务含义，已签署的条件决议**提供激活授权**，
TL **无须再次向 Owner 询问相同方向**；但出现**不兼容变更 / 权限扩大 / 不同数据用途 / 无法维持转换关系**时，
须提交**具体差异补充决议**，不得用技术关闭代替业务决定。

映射 3/5 **无法维持已声明的转换关系**（KERT 零命中）→ **属上述"须补充决议"情形**，故在此停等。
