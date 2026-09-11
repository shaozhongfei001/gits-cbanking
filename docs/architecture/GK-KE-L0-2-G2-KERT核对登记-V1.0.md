# GK-KE L0-2 条件 G2 登记：来源与转换绑定（KERT 核对）

> 角色：Tech Lead（planning_review）｜Loop：`GK1-l0-2-contract-activation`｜日期：2026-09-12
> 依据：`GK-KE-OWNER-002` §5 G2「三仓按实际性质记录为两 Git 仓库 + 一文档目录快照；完成 §3 五条逐项核对与 KERT 提供方确认」
> 跨仓核验对象：`/home/szf/dev/Leibniz-KERT` @ `3b6640b993f4834d36833fa0bc3005d73768b594`（分支 `feature/PI-ARCH-L10-L13`）
> 性质：**跨仓核对登记**。G2 关闭需 KERT 维护方确认；TL 只能提供核对事实，不能代证。

---

## 1. 三仓性质登记（G2 要件一）

| 仓库 | 性质 | 锚点 | 权威角色 |
|---|---|---|---|
| `/home/szf/dev/gits-cbanking` | **Git 仓库** | `411e669`（分支 `feature/GK-KE-L0-contract`） | 权威源 `specs/` + 实现 |
| `/home/szf/dev/Leibniz-KERT` | **Git 仓库** | `3b6640b993f4834d36833fa0bc3005d73768b594` | KERT 实现（Python） |
| `/home/szf/dev/gits-kert-docs` | **非 git 文档目录快照** | 无 HEAD | 文档承载，**本 Loop 无依赖**（见 §4） |

## 2. §3 五条映射的 KERT 侧核对（G2 要件二）

### 2.1 逐条实测结果

| # | 映射项 | KERT 仓内证据 | 核对判定 |
|---|---|---|---|
| 1 | `KM-GITS-ROOT@0.1.0` → 无 SIM 对应 | 未发现 KERT 对根地图做 SIM 转换；KERT 仅消费任务地图 | **一致**：根地图确实无 SIM 对应（导航/定位用） |
| 2 | `KM-CORP-RM-PREVISIT@0.1.0` → `SIM-MAP-FINANCE@1.0.0` | `src/kert/application/skills.py:637` 硬编码 `_trace_knowledge_map(trace, "KM-CORP-RM-PREVISIT", "PRE_VISIT_PREPARATION")`；`docs/v13-return-to-gits.md:104` 同源 | **部分**：KERT **实际消费** `KM-CORP-RM-PREVISIT` + `PRE_VISIT_PREPARATION`（与本仓一致）；但 **KERT 侧无 `SIM-MAP-FINANCE` 或任何 SIM 映射的代码/文档证据** → 该映射是本仓单方候选 |
| 3 | `ASSET-KNOW-PRODUCT-CARDS` → `SIM-ASSET-P001@1.0.0` | **KERT 仓内零命中**（`grep` 无结果） | **未核对**：源对象在 KERT 侧不存在引用 → **§3 要求的"KERT 先确认源对象是集合/入口/单卡"无法完成** |
| 4 | `AC-PREVISIT-001` → `ActivationPlan` | `docs/integration/KERT_GITS_STATE_MAPPING_CANDIDATE.md:216` 确认 `AC-PREVISIT-001` **存在**（与 `AC-FACT-RECONCILIATION-001` 并列） | **部分**：源对象存在已确认；但"编译依赖"转换关系（设计契约 → 运行计划）**无 KERT 侧确认** |
| 5 | `RP-CORP-RM-001` → `SIM-ROUTE-001@1.0.0` | **KERT 仓内零命中**（`grep` 无结果） | **未核对**：策略内容 hash 与确定性验证**无法完成** |

### 2.2 KERT 侧唯一相关文档的性质（重要）

KERT 仓内 `docs/integration/KERT_GITS_STATE_MAPPING_CANDIDATE.md` 与 `docs/v13-return-to-gits.md` 是 **GITS↔KERT 产品推荐状态映射（WP1-3）**，
与 L0-2 的五条**换对象映射不同范畴**，且该文档自述：

- `status=CANDIDATE`
- `FROZEN=NO`
- `IMPLEMENTED=NO`

**不得**将其引用为 L0-2 五条映射的确认证据。

---

## 3. G2 关闭判定

| G2 要件 | 状态 | 依据 |
|---|---|---|
| 三仓按实际性质记录 | ✅ **已满足** | §1（本文档） |
| `gits-kert-docs` 不参与权威依据 | ✅ **已满足** | §4 |
| §3 五条逐项核对 | ⚠️ **3/5 无法完成** | §2.1：映射 3、5 在 KERT 零命中；映射 2、4 仅源对象存在性确认，转换关系未确认 |
| **KERT 提供方确认** | ❌ **未获得** | 本仓无法替 KERT 维护方签署 |

**G2 结论：未关闭。**

**须 KERT 维护方提供的具体确认（不可由 TL 代办）**：

1. **映射 3**：`ASSET-KNOW-PRODUCT-CARDS` 在 KERT 侧的**对象粒度**——是集合、入口还是单卡？
   （§3 明确要求"来源对象的粒度需在 KERT 中先确认"）
2. **映射 5**：`RP-CORP-RM-001` 的**源版本、匹配条件、优先级、歧义处理**，以及目标策略的**内容 hash**
   （§3 明确要求"需绑定策略内容与确定性验证"）
3. **映射 2**：`SIM-MAP-FINANCE` 的**适用条件、必需节点、参数、依赖对齐**（KERT 侧是否认领该 SIM 地图）
4. **映射 4**：`AC-PREVISIT-001` → `ActivationPlan` 的**编译依赖关系**是否被 KERT 认可（设计契约 ≠ 运行计划）

---

## 4. `gits-kert-docs` 无依赖声明（G2 要件三）

本 Loop 的合同权威源为 `specs/`；封版受控物为 `docs/dd/gk-ke-contract`（主仓 git 内，tree `4c5f5373`，145 文件）。
**本 Loop 未引用 `gits-kert-docs` 任何内容**，对其**无依赖**。→ 无须提供其快照指纹。

---

## 5. 对 OC-01 的影响

`GK-KE-OWNER-002` §5 规定：**OC-01 关闭前须完成 G2**。
因 G2 未关闭 → **OC-01 未关闭**（与 Owner 决议"当前证据不足，不得标为已关闭"一致）。

**不得**因 G1/G3/G4 已关闭而推定 OC-01 可关闭。

---

## 6. TL 已尽事项与剩余阻塞

| 项 | 状态 |
|---|---|
| 三仓性质登记 | ✅ |
| `gits-kert-docs` 无依赖声明 | ✅ |
| §3 五条逐项核对（本仓可完成部分） | ✅（3/5 需跨仓） |
| KERT 侧证据检索（`grep` × 5 键 + 交叉引用） | ✅ 已执行，结果如实登记 |
| KERT 提供方确认 | ❌ **跨仓人工动作** |
| 激活登记 / OC-01 关闭 | ⛔ **阻塞于 G2** |

**TL 建议（供 Owner 参考）**：向 KERT 维护方发出 §3 四项确认请求；
若 KERT 短期内无法确认，可考虑**缩权激活**——即仅激活**已获 KERT 侧一致确认的部分**
（映射 1 根地图、映射 2 的 `KM-CORP-RM-PREVISIT` 消费关系），
对映射 3/4/5 维持 `pending_owner_confirmation` 并**禁止其参与运行时**。
此方案须 Owner 单独裁定，**TL 不自行决定**。
