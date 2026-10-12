# 剩余项闭环报告（Wave 2 · 2026-09-23 20:26）

来源：`evidence/pc-i1-closure/`（Wave 1：1B DIAG-1/2/3/5 + 1C DIAG-4）所列待决项 **F-4 / N-1…N-4 / DIAG-5**。
本轮范围：**仓内可闭环项**。未触碰 `frontend/src/**`、`specs/**`、`loops/PC-i1-chapter-inheritance/**`、`Leibniz-KERT`（KERT 仓）。
纪律：未 `push`；提交均为**单文件/单主题**（`git commit --only`），不夹带工作树内他人改动（提交前已核暂存区为空）。

---

## 一、本轮闭环（含证据）

### 1. N-3 索引门禁看不见 KERT 侧漂移 —— **已修**（提交 `5d5d79d`）

- **事实**：索引是**跨仓**派生物（本仓 + KERT），而 `scripts/ua_index_gate.py` 只度量本仓 HEAD
  ⇒ KERT 侧漂移**完全不可见**。
- **改前实测**：本仓 71 提交漂移有提示；**KERT 侧 `kertCommit=64f6f873` 落后 KERT HEAD `65b96df`
  178 提交，门禁零提示**。
- **改动**：新增 **F2·KERT 侧新鲜度**；KERT 仓路径优先级 `--kert-root` > `$KERT_REPO_ROOT` > 约定路径；
  默认 **advisory（WARN）**，`--strict-kert` 可升格为 FAIL（升格属门禁收紧，须 Owner 裁决）。
- **改后证据**：

```
WARN: F1 索引已过期：merge-meta.json 落后 HEAD 71 个提交（阈值 50），需按 SOP 刷新
WARN: F1 索引已过期：meta.json 落后 HEAD 71 个提交（阈值 50），需按 SOP 刷新
WARN: F2 KERT 侧索引已过期：.ua/merge-meta.json.kertCommit 落后 KERT HEAD 178 个提交（阈值 50）
      —— 原门禁**不度量**此项，故此前该漂移对门禁不可见
ua_index_gate: WARN (nodes=5106, drift={'merge-meta.json': 71, 'meta.json': 71}, kert_drift=178)
```

  `--json` 的 `evidence` 新增：`kert_root=/home/szf/dev/Leibniz-KERT`、
  `kert_head=65b96dfb…`、`kert_recorded_commit=64f6f873…`、`kert_drift=178`。
- **回归**：`scripts/ua_index_gate_tests.py` → **Ran 18 tests, OK**（红线 R1–R5 与 F1 判据未被破坏）。

### 2. N-4 「认领 25/23」口径 —— **已澄清**（提交 `5d5d79d`；**未改判定逻辑**）

- **实测集合**：`run_gates.GATES = 23`；`INJECTIONS = 21`（其中 **2 项为 loop 级门禁**
  `gk17-ref-anchor` / `gk17-triple-consistency`，**未登记进 GATES**）、`UNCOVERED_REASONS = 2`、
  `SELF_EXEMPT = 2`（`gate-selftest` / `gate-injection-tests`）⇒ 注入面 `claimed = 25`。
- **改动**：打印从「门禁认领 25/23」（分子 > 分母，易误读为计数 bug）拆为两个面 + 显式差额。
- **改后实跑输出**：

```
gate-injection-tests（逐门禁注入真实缺陷）—— 门禁链 23/23 已认领；另有 2 项 **loop 级门禁未登记进
run_gates.GATES**，一并纳入注入面：['gk17-ref-anchor', 'gk17-triple-consistency']
（⇒ 注入面 25 > 门禁链 23 属**登记不对称**，非覆盖缺口）
```

### 3. F-4 门禁自查盲区 —— 已由他方实现，本轮**验证其非空转**（并当场抓到实例）

- **现状**：`scripts/gate_injection_tests.py` 已含 F-4（字节级快照 + 备份 + 逐字节还原 +
  不可还原即 FAIL）；单测 `tests/tooling/test_gate_injection_bytecheck.py` 已入仓。
- **本轮证据**：
  - `make tooling-test` → **Ran 36 tests, OK**；
  - 实跑整条注入门禁（当前**超脏**工作树）→

```
[BYTE-DRIFT] 字节级快照复核：**1 项内容被改写**：['evidence/gk-ke-capability-probe/report.json']
[BYTE-RESTORE] 已按运行前备份**逐字节还原并复核** 1 项：['evidence/gk-ke-capability-probe/report.json']
```

  ⇒ 该文件**运行前已 dirty**，旧「行文本」口径下**既检测不到也不会回滚**；F-4 后可见且自动还原。
  **这是在真实工作树上、非构造样本下的非空转证据。**
- **判定不变**：`__GATE_VERDICT__=INCONCLUSIVE`（20 项检出 / pending 3 = 未设计 2 + 只读跳过 1）—— **≠ 通过**。

### 4. DIAG-3 analytics 4 条 —— 从「自限证据」升级为**合规验证**

- 改前（1B）：KERT `.venv` 缺 duckdb ⇒ 只能借**系统 python3** 临时起服，1B 自限
  「该运行不得当 analytics 验收通过」。
- 现状：KERT `.venv` 已具备 **duckdb 1.5.5**。
- 本轮证据（**声明 venv 下的服务** + `QA_BASE_URL=http://127.0.0.1:15173`）：
  `e2e/analytics.spec.ts` → **5 passed (9.9s)**（含 4 条曾 BLOCKED 的用例：侧边栏组跳转、经营指标分析、
  细分客群分析、组合查询、指标监视器）。
- ⇒ 该 4 条**不再是 BLOCKED**；1B 的「证据强度自限」解除。

### 5. 重启脚本长期保留（提交 `090e264`）

- `scripts/restart-gits-kert.sh`：`up` / `down` / `status`（+ `--with-lightrag`）；复刻既有启动参数；
  不硬编码密钥；只按精确模式停止（不误伤 8106(dkws)）；不做任何 git 操作。
- 已用其**自身**跑通一轮并全绿（详 `evidence/pc-i1-closure/` 与终端记录：三服务 200 + 分析端点 200 +
  产品中心/产品卡 API 200 + live 跨服务用例 1 passed）。

---

## 二、仍未闭环（具名 + 归属 + 依据）

| # | 事项 | 归属 | 现状与依据 |
|---|---|---|---|
**N-1** | KERT `requirements-lock.txt`（58 行）**仍缺 `duckdb`**，而 `pyproject.toml:28` 声明 `duckdb>=1.0` ⇒ **声明/锁不一致**（重建 venv 会再次丢失，analytics 回到 503） | KERT 维护方 | 环境侧已通（venv 有 1.5.5，本轮 5/5 验证）；**仓库侧未闭环**（一行修复） |
**N-2** | KERT 侧 S3 判据：下游 `bank-front-kyc-gap-check` 的 `kycGaps` 不承载「未执行/覆盖不足」，`NOT_RUN` 与「真无冲突」同形；判据要求的枚举 `COVERAGE_INSUFFICIENT`/`COVERAGE_NOT_REPORTED`/`VERIFY_REQUIRED` 在 KERT 仓**仍零命中** | KERT 维护方 | 未闭环（需补结构化覆盖状态字段 + 判据升级 V1.2.0，不回溯） |
**DIAG-5** | 索引全量刷新 | TL / Owner | **未执行**。改后门禁显示**双仓欠账**（本仓 71 / KERT 178）；增量驱动 `.ua/tmp/ua_incr.py` **仍不存在**（CFI-OPEN-01 未入库）⇒ 只能全量（≈3.7M tokens / 小时级）。**须明确接受成本后方可执行** |
**N-3 升格** | F2 是否改为默认阻塞（或 `--strict-kert` 默认开 / Makefile 传参） | Owner | 待裁决。一旦升格，`make index-status` 会立刻 FAIL（当前 178 欠账） |
**N-4 登记** | 是否把 `gk17-ref-anchor`/`gk17-triple-consistency` 登记进 `run_gates.GATES` | Owner | 待裁决。登记会改变门禁链规模，并使 GK17 `LOOP.yaml` 的「22/23」文案失效（跨 loop） |
**CFI-OPEN-01** | 增量驱动未入库 ⇒ 刷新只能全量 | UA 插件 / EZ 侧 | 未闭环（**阻塞 DIAG-5 的低成本路径**） |

**已由他方闭环（本轮复核确认）**：`F-4`（实现+单测入仓）、`R-3/CFI-OPEN-04`（`ua_index_gate*.py` 已入仓）、
`H-1`（`generated/` 无漂移）、`DIAG-3` 的环境前置（venv 装 duckdb）、`PC-i1` 状态（`qa_pass`，独立 QA 复验报告
`independent-qa-reverify-20260923-1316.md`）。

---

## 三、未覆盖 / 存疑（必填）

1. 本报告**不含 KERT 仓改动**（本轮未触碰 KERT）；N-1/N-2 的「已修」须以其仓内提交为准。
2. F2 的 KERT 路径解析含**本机约定路径** `/home/szf/dev/Leibniz-KERT`；可用 `--kert-root`/`$KERT_REPO_ROOT` 覆盖。
   异机运行会得到「未配置 ⇒ 不可判定」的 WARN（**不静默跳过**）。是否需要更通用的配置方式，待定。
3. 本仓工作树**长期脏且被并行会话持续提交**（核查期间 HEAD：`652a23f` → `29ef95b` → 本轮 `090e264`/`5d5d79d`），
   任何「计数/基线」均为**时点快照**。
4. **未跑 `make check` 全链**：其中含写型门禁 `contract_generate`（会改写受控制品 `generated/**`）；
   本轮只跑与本改动直接相关的门禁与测试（`ua_index_gate_tests.py` 18 OK、`make tooling-test` 36 OK、
   `gate_injection_tests.py` 实跑一次）。
5. F-4 的**fail-closed 分支**（漂移文件 > `SNAPSHOT_MAX_BYTES` = 8 MiB ⇒ 无备份 ⇒ 无法还原 ⇒ FAIL）
   未取得实测样本，仅有单测覆盖（`test_gate_injection_bytecheck.py`）。
6. F2 未在**第二台机器/第二条 KERT 路径**上验证（仅本机 + 单一 KERT 仓）。

---

## 四、环境变动登记

- **未重启任何服务**：当前栈为本轮之前由 `scripts/restart-gits-kert.sh` 启动的实例（前端 15173 / 后端 18080 /
  KERT 8107 / LightRAG 9621）。**未改任何环境变量**。
- **实跑 `scripts/gate_injection_tests.py` 一次**：按其设计对 20 处受控目标「破坏 → 还原」；
  另**新增** 1 项写副作用 `evidence/gk-ke-capability-probe/report.json`，被 F-4 字节级**自动还原**。
  工作树计数：跑前 `M=33`（他人提交后）→ 跑后 `M=35`，增量恰为本轮我修改的 **2 个脚本**
  ⇒ **门禁实跑零净污染**（可用 `git diff --quiet` 复核）。
- **本轮提交**（未 push）：
  - `090e264` `chore(dev): 本地栈重启脚本（GITS 前端/后端 + KERT 技能 8107）`（1 file, +178）
  - `5d5d79d` `fix(governance): 索引门禁补 KERT 侧新鲜度（F2/N-3）+ 注入门禁 25/23 口径澄清（N-4）`（2 files, +83/-5）
- 临时产物（不入仓）：`/tmp/gate-inj-n4.log`、`/tmp/analytics-declared.log`、`/tmp/restart-gits-kert-*`、
  `/tmp/restart-*.env`（**含 KERT_LIGHTRAG_API_KEY 明文，权限 600，可删**）。
