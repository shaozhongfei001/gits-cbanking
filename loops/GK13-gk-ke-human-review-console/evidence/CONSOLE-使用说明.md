# GK-KE 人工验收台 · 使用说明（OC-03 / OC-04 / OC-05）

> Loop：`GK13-gk-ke-human-review-console`｜HEAD：`89fda91`｜状态：`ready_for_independent_qa`（等待人工操作验证）

## 1. 启动

```bash
cd /home/szf/dev/gits-cbanking
python3 scripts/gk_ke_console_server.py --port 8765
```

浏览器打开 **http://127.0.0.1:8765/**

> 当前已在本机 8765 端口运行中（只读，Ctrl+C 停止）。
> 零外部依赖：仅 Python stdlib + 单文件 HTML，无需 npm / maven。

## 2. 界面结构

四个页签：

| 页签 | 用途 |
|---|---|
| **OC-03 审核与发布** | Publishable 八项谓词 / 双维审核 / 状态机 / 投影 / 运行有效性 |
| **OC-04 地图与计划** | MapSpec / 路由判定 / 确定性计划 / DAG |
| **OC-05 经营闭环** | 解读（3000 万）/ 体检（UNKNOWN）/ 推荐 / 确认 / 模拟跟进 / 超时对账 |
| **审阅问题** | OC-03/04/05 的 18 个待答问题，可直接对照批注 |

## 3. 核心操作：注入违规验证防线

每个页签顶部有 **注入按钮**。点任一违规，判定区**立即显示对应的拒绝码**。

### OC-03（7 项）

| 注入 | 应显示 |
|---|---|
| `HALF_PUBLISH` | `HALF_PUBLISH` HTTP 409（C03 §6 原子发布） |
| `SELF_APPROVAL` | `SELF_APPROVAL` HTTP 403（C03 §4 双维审核） |
| `CONTENT_CHANGED` | `CONTENT_CHANGED_AFTER_APPROVAL` HTTP 409 |
| `EXPIRED_APPROVAL` | `EXPIRED_APPROVAL_COUNTED` HTTP 409 |
| `REVOKED_SEARCHABLE` | `REVOKED_STILL_SEARCHABLE` HTTP 409 |
| `ROLLBACK_TO_REVOKED` | `ROLLBACK_TO_REVOKED` HTTP 409 |
| `PURPOSE_UPGRADE` | `PURPOSE_FLAG_SILENT_UPGRADE` HTTP 422 |

### OC-04（5 项）

| 注入 | 应显示 |
|---|---|
| `ROUTE_AMBIGUOUS` | `ROUTE_AMBIGUOUS`（同优先级多规则，不自行选择） |
| `NO_MATCH` | `NO_MATCH_REJECT`（无匹配，不用默认模式扩大任务集合） |
| `GITS_WRITEBACK` | `GITS_WRITEBACK_IN_KERT_PLAN` |
| `DEPENDENCY_CYCLE` | `DEPENDENCY_CYCLE` |
| `MISSING_CAPABILITY` | `REQUIRED_CAPABILITY_MISSING` |

### OC-05（6 项 — **请重点验证第 1 条**）

| 注入 | 应显示 |
|---|---|
| **`FORBIDDEN_ACTION`** | **`FORBIDDEN_ACTION_REJECTED`**（转账/放款/授信审批 —— **安全红线**） |
| `STALE_VERSION` | `STALE_TARGET_VERSION_REJECTED` |
| `MISSING_CONFIRMATION` | `MISSING_CONFIRMATION_REJECTED` |
| `TIMEOUT_AS_FAILURE` | `TIMEOUT_RESULT_UNKNOWN` |
| `STATEMENT_AS_FACT` | `STATEMENT_AS_FACT_REJECTED` |
| `UNKNOWN_ADMITTED` | `UNKNOWN_PURPOSE_NOT_ADMITTED` |

## 4. 验证方法（建议 5 分钟）

1. 打开页签，停在 **「✓ 正例（无违规）」** → 判定区应显示 **「未触发任何拒绝」**
2. 逐个点击注入按钮 → 每次都出现**对应**的拒绝码
3. **关键**：若点某按钮**没有**出现拒绝码 → 该防线是"纸面上的"，请**记录下来**
4. 三项页签、共 18 个按钮走一遍

> **这正是本控制台的存在意义**：让"防线真的会拦"变成**可亲眼验证**的事实，
> 而不是只写在文档里的声明。

## 5. 只读保证

- 控制台**不写入任何文件**（门禁已实测：注入前后文件字节完全一致）
- 「注入」仅在**内存**中污染数据副本后求值
- 所有数据为 SIM 夹具，界面全程显示 `simulationOnly = true` 与「非生产」水印

## 6. 与其他交付物的关系

| 交付物 | 性质 | 位置 |
|---|---|---|
| **本控制台（路径 A）** | **操作验证**（浏览器实际点选） | `tools/gk-ke-console/` |
| 人工审阅包（路径 B） | **书面证据审阅**（离线对照） | `docs/dispatch/GK-KE-OC030405-人工审阅包-V1.0.md` |
| 门禁脚本 | **自动化证明**（断言非空转） | `scripts/gk_ke_*_tests.py` |

三者在 `EVIDENCE.json` 中各自留痕，互不替代。

## 7. 已知边界

- 这是**只读验收台**，不是业务系统：不能新增知识、不能真实发布
- 数据是**夹具**，不是真实银行数据
- 不覆盖并发/负载（属 L6 运行验收范围，已由 `gk_ke_l6_runtime_acceptance_tests.py` 覆盖）
- 路径 A 的定位是**让领域专家能判"规则对不对"**，不是**让系统生产可用**
