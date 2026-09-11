# GITS-KERT 整改 AR-R1 · 补交实物与追踪 V1.0

> 角色：GK-KE 交付 Tech Lead
> 日期：2026-09-11
> 对应报告发现项：F02（BLOCKER）、F09（MAJOR，范围绑定部分）、F10（MINOR，计数口径部分）
> 工作单：AR-R1 — 当前 ZIP/MANIFEST/验证器/原始输出；建立 REQ/C/CR/Loop/T 到路径、符号、测试、证据映射
> 交付 HEAD：`f79f2b1`（AR-R0 已把交付包纳入版本控制）

---

## 1. 实物交付清单（可独立读取，非仅声明）

### 1.1 交付包物理位置

| 项 | 值 |
|---|---|
| 仓库内路径 | `docs/dd/gk-ke-contract/` |
| git 提交 | `f79f2b1` `contract(gk-ke): vendor GK-KE-CONTRACT-V1.0 design package into repo` |
| 文件总数 | 119（117 MANIFEST 受控 + MANIFEST.json 自身 + 总契约 A） |
| 受控文件数 | 117（MANIFEST `files` 数组） |
| MANIFEST hash 完整性 | 117/117 逐项 sha256 一致，0 缺失 0 错配 |
| 排除项 | `.venv/`、`__pycache__/`、`*.pyc`（按 `.gitignore`） |

### 1.2 验证器与原始输出（可复现）

| 项 | 值 |
|---|---|
| 验证器 | `tools/validate_package.py` |
| 依赖 | `tools/requirements.txt`（`jsonschema==4.25.1`） |
| 运行命令 | `.venv/bin/python tools/validate_package.py` |
| 原始输出 | `acceptance/package_self_check.json`（125 项逐条，含 check/status/detail） |
| 复现结果（本会话） | `{"passed": 125, "failed": 0}` |
| 自检性质 | `scope=OFFLINE_AUTHOR_SELF_CHECK`，`independentQa=NOT_PERFORMED` |
| 未执行项（如实标注） | `serviceE2E` / `kuzuIntegration` / `lightRagIntegration` / `actualHumanApproval` 均 `NOT_PERFORMED` |

### 1.3 造数工具与重建

| 项 | 值 |
|---|---|
| 造数编译器 | `tools/build_simulation.py` |
| 样例生成器 | `tools/build_contract_examples.py` |
| 种子 | `simulation/seed_scenarios.json`（固定虚构，未调用云模型） |
| 重建方式 | 只读固定种子/原文，程序派生账务/余额/图，可复现 |

---

## 2. 实物规模验证（区分"文件存在 vs 内容完整"）

### 2.1 C07 最小参考数据计数（实测 vs 声称）

| 数据 | 总契约 C07 §1 声称 | 实测行数 | 判定 |
|---|---|---|---|
| 客户 customers | 12 | 12 | ✅ 一致 |
| 账户 accounts | 24 | 24 | ✅ 一致 |
| 产品 products | 6 | 6 | ✅ 一致 |
| 日历天 calendar | 30 | 30 | ✅ 一致 |
| 交易事件 transactions | 144 | 144 | ✅ 一致 |
| 借贷分录 ledger_entries | 288 | 288 | ✅ 一致 |
| 账户日余额 daily_balances | 720 | 720 | ✅ 一致 |
| 授信记录 credit_facilities | 12 | 12 | ✅ 一致 |
| 产品持有 holdings | 12 | 12 | ✅ 一致 |
| 文档 documents | 18 | 18 | ✅ 一致 |

**结论**：C07 最小参考数据**完整且精确匹配**，无缺项。这正面回应 F08"种子样例未证明覆盖完整模拟银行"——数据规模是够的，缺的是"独立复算 + 负例隔离"的验收证据链（归 AR-R3）。

### 2.2 C001 日均指标独立复算（F06 核心）

| 项 | 值 |
|---|---|
| 指标 | `SIM.METRIC.CUSTOMER_AVG_DEPOSIT` v1.0.0 |
| 客户 | `SIM-C001`，2 个账户（SIM-A0011 / SIM-A0012） |
| 期间 | 2026-09-01 ~ 2026-10-01（30 自然日，左闭右开） |
| 30 天余额总和 | 89,500,000.00 CNY |
| 日均（RoundHalfUp 2） | **2,983,333.33 CNY** |
| oracle expectedValue | `2983333.33` |
| **复算匹配** | ✅ **精确命中** |

推导式（oracle `derivation`）：`3000000 + 100000*25/30 - 200000*15/30`，与逐日余额独立复算交叉验证一致。

### 2.3 经营闭环三值判定（F08 关键负例）

oracle `expected.json` 明确记录：

| 字段 | 值 | 含义 |
|---|---|---|
| `nominalUnusedCredit` | `8000000.00` | 名义未用额度 800 万 |
| `drawableAmount` | `null` | **不可提款金额为空** |
| `eligibility` | `UNKNOWN` | 用途/担保未核实，规则返回 UNKNOWN |

这正确体现了"客户说需 3000 万 / 源系统额度 2000 万已用 1200 万 / 名义未用 800 万 / 不能直接给可提款结论"的区分（F08 要求的核心语义）。

---

## 3. 合同→制品→测试→证据 映射表

### 3.1 C 合同 → Schema → 正负例 映射（来自 CONTRACT_INDEX.json）

| 合同 | Schema 数 | 正例 | 负例 | 状态 |
|---|---|---|---|---|
| C01 系统边界与理论 | 1（SemanticPackage） | 1 | 2 | CONTRACT_CANDIDATE |
| C02 注册中心与知识地图 | 2（AssetVersion、KnowledgeMap） | 2 | 4 | CONTRACT_CANDIDATE |
| C03 自动构建审核发布 | 3（Assertion、ReviewDecision、ReleaseManifest） | 3 | 6 | CONTRACT_CANDIDATE |
| C04 分析语义服务 | 3（MetricDefinition、SemanticRequest、SemanticResult） | 3 | 6 | CONTRACT_CANDIDATE |
| C05 RAG与图适配 | 2（GraphRequest、GraphResponse） | 2 | 4 | CONTRACT_CANDIDATE |
| C06 运行与接口 | 3（ActivationPlan、EvidenceBundle、ControlledAction） | 3 | 6 | CONTRACT_CANDIDATE |
| C07 模拟数据 | 0 | 0 | 0 | CONTRACT_CANDIDATE |
| C08 实施验收与变更 | 0 | 0 | 0 | CONTRACT_CANDIDATE |
| **合计** | **14** | **14** | **28** | — |

**判定**：14 Schema / 14 正例 / 28 负例，与 README 声称一致。Schema 合法是"结构前置检查"，不等于"服务已实现"。

### 3.2 需求 REQ → 合同 C → 验收 T 映射（来自总契约 §3 + 验收矩阵）

| 需求 ID | 合同 | 验收 | 本次阶段判定 |
|---|---|---|---|
| REQ-01 谁定义/保管/执行 | C01 | T01–T04 | 设计已写，服务未验（PLANNED_NOT_EXECUTED） |
| REQ-02 指标一致 | C04 | T11–T16 | 数据真值可复算✅，服务未验 |
| REQ-03 发现分散知识 | C02 | T05–T07、T17 | 设计已写，服务未验 |
| REQ-04 自动建图 | C03 | T08–T10、T18–T21 | 设计已写，服务未验 |
| REQ-05 RAG+图 | C05 | T22–T25 | 设计已写，服务未验 |
| REQ-06 经营动作 | C06 | T26–T29 | 设计已写，服务未验 |
| REQ-07 数据可模拟 | C07 | T30–T33 | 造数完整✅，隔离/负例待验 |
| REQ-08 按合同开发验收 | C08 | T34–T36 | 设计已写，服务未验 |

### 3.3 变更 CR → 兼容工作 → 责任 映射（来自总契约 C08 §1）

| 变更 | 内容 | 责任 |
|---|---|---|
| CR-01 | 公共核心独立 | 语义 Owner + 两领域 TL |
| CR-02 | 权威矩阵细化 | 数据 Owner + KERT/GITS |
| CR-03 | 注册与地图增量 | 契约 Owner |
| CR-04 | 自动构建与发布 | 知识 Owner |
| CR-05 | 语义查询 | 指标 Owner |
| CR-06 | 图组件（Kuzu） | 图适配维护者 |
| CR-07 | 既有 RAG + LightRAG | 检索 Owner |
| CR-08 | 模拟与动作 | 数据/业务 Owner |

### 3.4 实施 Loop → 产物 → 退出标准 映射（来自总契约 C08 §2）

| Loop | 工作 | 本次状态 |
|---|---|---|
| L0-1 现状定位 | 固定 HEAD/合同索引/字段对照 | 未执行（待下一 Loop） |
| L0-2 契约激活 | 审 CR-01–08、补 OpenAPI | 未执行 |
| L1-1 公共语义 | 12 类型/域扩展 | 未执行 |
| L1-2 模拟源 | 导入种子、模拟 API | 未执行 |
| L2-1 语义查询 | 指标/编译器/复算 | 未执行（数据真值已就绪） |
| L2-2 注册中心 | Registry API | 未执行 |
| L3-1 工厂与候选 | ingestion/ReviewPackage | 未执行 |
| L3-2 审核发布 | Review UI/Release Manager | 未执行 |
| L4-1 地图激活 | TaskTemplate/路由 | 未执行 |
| L4-2 GITS 闭环 | 解读→体检→推荐→确认 | 未执行 |
| L5-1 Kuzu | GraphQueryPort | 未执行 |
| L5-2 LightRAG | A/B/C 试验 | 未执行（不阻塞 L4） |
| L6 运行验收 | 并发/故障/恢复 | 未执行 |

---

## 4. 三态区分（关键：回应 F02/F09）

AR-R1 要求"能区分文件不存在、内容缺失、未执行和已通过"。本次建立如下状态语义：

| 状态 | 含义 | 本次数量 |
|---|---|---|
| `FILE_PRESENT` | 文件存在且 hash 可验证 | 119 文件全部 |
| `CONTENT_COMPLETE` | 内容完整（如造数规模精确匹配） | C07 数据 10/10 项 |
| `VERIFIED` | 已独立验证（如 C001 复算命中） | C001 日均复算 |
| `NOT_PERFORMED` | 服务级未执行 | T01–T36 全部、5 项集成 |
| `NOT_PROVIDED` | 字段缺失 | 服务级证据（HEAD/运行/trace） |

**关键结论**：
- **文件层**：全部 `FILE_PRESENT`，hash 117/117 一致（F02 的"实物缺失"已在本仓库内补交，评审方现在可独立读取）。
- **内容层**：C07 造数规模、C001 日均真值均 `VERIFIED`。
- **服务层**：全部 `NOT_PERFORMED`——这是 D（设计包）阶段的如实状态，不是缺陷。

---

## 5. 历史 QA 声明的范围绑定（回应 F09）

清单 B §12 声称的两类历史 QA，本次 AR-R1 明确其**不继承**关系：

| 声明 | 实际范围 | 本次验收绑定 |
|---|---|---|
| 125/0 包自检 | 本交付包离线自检（本次已复现） | ✅ 绑定 HEAD `f79f2b1` + MANIFEST 117 项 hash |
| 1808 测试 / 覆盖率 0.8001 / qa-gkd-formal-001 | `gits-cbanking` 主仓库安全工作（spring-security/tomcat CVE），**非本交付包** | ❌ 不继承，需单列其独立 HEAD/范围 |
| 15 模块 / 零 ≥7 CVE | 主仓库安全分支 | ❌ 不继承 |

**结论**：125/0 是本次交付包真实可复现的自检（已绑定 HEAD+hash）；1808/0.8001 是主仓库另一安全工作项，与本知识工程交付**无继承关系**，各自独立验收。

---

## 6. AR-R1 退出条件核对

| 报告要求 | 状态 | 说明 |
|---|---|---|
| 当前 ZIP/MANIFEST | ✅ | 已纳入 git `f79f2b1`，MANIFEST 117 项 hash 全验 |
| 验证器 | ✅ | `validate_package.py` 可复现 125/0 |
| 原始输出 | ✅ | `package_self_check.json` 125 项逐条 |
| REQ→C→CR→Loop→T 映射 | ✅ | §3 四张映射表 |
| 区分"不存在/缺失/未执行/已通过" | ✅ | §4 五态语义 |
| 历史 QA 范围绑定 | ✅ | §5 明确 125/0 继承、1808 不继承 |

**F02 关闭条件：全部满足。** 评审方现在可从 `docs/dd/gk-ke-contract/` 独立读取全部实物并复现自检。

---

## 7. TL 落盘声明

```
[AR-R1] 实物已补交: docs/dd/gk-ke-contract/ (HEAD f79f2b1, 119文件, hash 117/117)
        自检复现: 125/0, 5项NOT_PERFORMED如实标注
        内容验证: C07造数10/10精确匹配, C001日均2983333.33复算命中
        三态: 文件层全PRESENT, 内容层VERIFIED, 服务层全NOT_PERFORMED(D阶段如实)
        历史QA: 125/0继承(已绑定HEAD), 1808/0.8001不继承(独立安全工作)
        F02关闭: 全部满足 ✅
```

AR-R1 完成。F02/F09/F10 的实物与追踪证据已齐备。下一步 AR-R2（修复核心设计覆盖），优先 F06 分析语义服务覆盖。
