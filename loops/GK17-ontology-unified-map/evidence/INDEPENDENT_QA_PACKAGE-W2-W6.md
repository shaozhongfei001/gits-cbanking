# GK17 · 独立 QA 判定包（W2 + W6）

```text
PACKET     : GK17-ontology-unified-map
SCOPE      : W2（本体真实进入知识路由）+ W6（V1–V4 实验与证据）的 ACCEPT 判定
PREPARED_BY: tech_lead（TL）—— **不得**由本角色作出判定
VERDICT_BY : independent_qa（ROLE_BOARD: responsibility = gate_review_and_V1_V4_verdict，
             status = unassigned_must_be_separate_session）
DATE       : 2026-09-15
HEAD_AT_PREP: 527291c（W6 交付提交）
```

> **本文件的用途**：把"两个 wave 卡在待判定"变成"**可判定**"。
> TL 只负责把判据、证据、复核命令、已知限制与待裁定问题**摆到桌面上**；
> **判定与签署由独立 QA 作出**。TL **不代签** `QA_PASS`（`tech_lead.forbidden` 首条）。

---

## 0. 复核前置（**先读，否则会撞假红**）

### 0.1 模块级门禁依赖"本地仓库新鲜度"（实测，已记 `FAILURES.md` `20260915T073300Z`）

`./mvnw -pl <module> ...`（**不带 `-am`**）会把模块依赖解析到 `~/.m2` 的**已安装工件**。
本仓库曾出现：`~/.m2` 里 `semantic-runtime` / `semantic-jena` 是 **WP2.1 之前**的旧快照
（实测旧 jar **不含** `OntologyPort` / `JenaOntologyAdapter`）⇒ 模块级门禁 `testCompile` 失败。

**且该失败只在 `testCompile` 出现、`default-compile` 无错** —— 主类靠**增量编译跳过**，
所以**陈旧 `target/` 会让门禁"看起来 PASS"**。

**复核前请先执行一次（幂等，约 3 秒）：**

```bash
cd /home/szf/dev/gits-cbanking
./mvnw --batch-mode --no-transfer-progress \
  -pl modules/semantic-runtime,modules/knowledge-architecture,adapters/semantic-jena \
  -am install -DskipTests -Ddependency-check.skip=true
```

- `-Ddependency-check.skip=true` 仅用于**该构建卫生动作**（`install` 会触发 `verify` 阶段的
  dependency-check，而它需联网拉 RetireJS，本环境端点不可达）。
  **它不是**跑门禁，**不改变**任何门禁结论：`backend_test` 仍为环境红、仍未计入通过。
- 若希望完全避免 `~/.m2` 依赖，可对所有模块级命令改用 `-am`（从反应堆构建依赖）。

### 0.2 门禁必须**串行**执行

依据 GK16 T-24（本仓实测）：并发跑门禁会互相污染证据并产生**假 FAIL**。请勿并行。

### 0.3 提交前请还原既有噪声文件

`evidence/gk-ke-chain-trace/trace.json` 每次跑门禁都会被重写，属既有噪声：
`git checkout -- evidence/gk-ke-chain-trace/trace.json`。

---

## 1. 变更集快照（判定对象）

| 项 | 值 |
|---|---|
| commit | `a1e183b`（W2）、`527291c`（W6） |
| `DefaultActivationPlanner.java` sha256 | `83e3b300e5e5ffb4c28c3cb38450d785fa8d871ecfa73d2839cfc3b18789398d` |
| `specs/semantic/gits-core.owl.ttl` sha256 | `705578d6324abd0c1bd2bd670e6f3c0ffd8e04c358d0134246c89a3acfc38d00` |
| `versions.ontology` 口径 | `CTR-SEM-002@sha256:705578d6324abd0c`（黄金计划已钉住该取值） |

**W2 交付文件**：`modules/knowledge-architecture/{pom.xml, ActivationPlan.java, plan/DefaultActivationPlanner.java, test/.../DefaultActivationPlannerTest.java}`、
`apps/api/.../config/KnowledgeArchitectureConfig.java`、`apps/api/src/test/.../KnowledgeArchitectureConfigTest.java`、
`adapters/knowledge-filesystem/{pom.xml, test/.../DefaultActivationPlannerFilesystemIT.java}`、
`specs/knowledge-architecture/schemas/activation-plan.schema.json`、两个 `AP-*-GOLDEN.json`、`generated/...`

**W6 交付文件**：`apps/api/src/test/.../e2e/{V1PrevisitChainTest, V2OntologyOnlyChangeTest}.java` + `evidence/` 下制品。

---

## 2. W2 判定清单（编排表判据照抄，未自改）

> **W2 ACCEPT 判据**：路由裁决**带本体依据**并写入 plan trace；本体不可达 ⇒ **fail-closed**；负例通过。

| # | 判据条款 | 证据 | 复核命令 | 期望 |
|---|---|---|---|---|
| W2-1 | 路由裁决**带本体依据**并写入 **plan trace** | `DefaultActivationPlannerTest.usesLoadedOntologyVersionAndWritesEvidenceIntoPlanTrace`；`V1PrevisitChainTest` 的 `step5_plan.ontologyEvidence` | `./mvnw -pl modules/knowledge-architecture -am test -Dtest=DefaultActivationPlannerTest` | `Tests run: 18, Failures: 0, Errors: 0`；且 `trace.ontologyEvidence` **含**版本 + `classes=32` + `objectProperties=34` + `datatypeProperties=1` + `individuals=0` + 来源 |
| W2-2 | 本体不可达 ⇒ **fail-closed**（不抛异常、不降级） | `deniesWhenOntologyMissingInsteadOfPlanningWithoutIt`、`deniesWhenOntologyMalformedInsteadOfPlanningWithoutIt` | 同上 | 同上；拒绝码 == 端口 `failureCode()`（`ONTOLOGY_MISSING` / `ONTOLOGY_MALFORMED`），消息带 `failureReason()` |
| W2-3 | `versions.ontology` **不再是占位串** | 两个黄金 + `V1PrevisitChainTest` | `git grep -n "CURRENT_BASE" -- specs generated modules apps adapters \| grep -v "OntologyPort.java"` | **零命中**。⚠ 注意：不加 `grep -v` 时会命中 **1 处** —— `modules/semantic-runtime/.../semantic/OntologyPort.java:10` 的 **javadoc 历史说明**（描述"曾被硬编码、本体从未被加载"这一问题），**不是生效取值**。判定口径应为"**生效**代码 / 合同 / 黄金中零命中" |
| W2-4 | **负例通过**（且非空转） | `FAILURES.md` `20260915T044040Z` 两条；变异日志见 §5 | §5 的 M1 / M2 配方 | M1 ⇒ **FAIL 2 条**；M2 ⇒ **FAIL（模块 1 + 端到端 1）**；恢复 ⇒ 全 PASS |
| W2-5 | 门禁：`make generate` / `make check` / `ontology_load` / `./mvnw test` | `evidence/contract_*.log`、`ontology_load-*.log`、`backend_test-*-W6-POSTFIX.log` | 见 §6 | `make check` exit 0（**22/23**，INTEGRITY FAILURES 空）；`ontology_load` `1/0/0/0`；`./mvnw test` api **603/0/0/4**、worker **22/0/0/0** |

**W2 设计裁定（请一并有据地复核）**：
1. 本体加载置于**请求级护栏之后、路由解析之前**（本体是四条 `routeMode` 的共同前置，不给部分 credit）；
2. `evidence()`（含**来源路径**，环境相关）**不入** `planHash`，只有本体**版本**入哈希 ——
   守护用例 `planHashIgnoresOntologySourcePathSoPlansStayReplayableAcrossMachines`
   （先断言两处来源的 `evidence` **确实不同**（反空转），再断言 `planHash` **相同**）。

---

## 3. W6 判定清单（判据原文来自 `docs/architecture/GK-KE-统一地图承担者论证-V1.0.md` §5）

> **W6 ACCEPT 判据**：**V1 链路可复核** + **V2/V3/V4 反例全部有变异对照**。

### V1 —— `PRE_VISIT_PREPARATION`（`ONTOLOGY_THEN_MAP`）完整链

| 项 | 内容 |
|---|---|
| 判据原文 | 跑通完整链：路由裁决 → 本体查实体/关系 → 地图按结果定向激活资产 → SKILL 调用 → 输出证据。通过 = 有**可复核的原始输出**（含 `planHash`、`versions.ontology`、**路由理由**） |
| 证据 | `evidence/gk17-v1-previsit-chain.json`；日志 `evidence/gk17-v1-*.log`、`gk17-v1v2-*.log` |
| 复核命令 | `./mvnw -pl apps/api -am test -Dtest=V1PrevisitChainTest -Dsurefire.failIfNoSpecifiedTests=false -Dgk17.evidence.dir=loops/GK17-ontology-unified-map/evidence` |
| 期望 | `Tests run: 1, Failures: 0`；制品含 `step1_routeDecision.reason="先锁定客户事实和缺口，再定向加载文档知识"`、`step2_ontology.ontologyVersion`、`step5_plan.planHash` |
| 实测值 | `planHash=a2413b72e01d7430`；`versions={KM-GITS-ROOT@0.1.0, RP-CORP-RM-001@0.1.0, AC-PREVISIT-001@0.1.0, ontology=CTR-SEM-002@sha256:705578d6324abd0c}`；`selectedAssets=9`、`semanticQueries=5`、`ruleChecks=4`、`skills=[SP-02,SP-05,SP-15,SP-10]` |
| ⚠ 已知限制 | 见 **Q1**（② 只到 T-Box；查询未执行）与 **Q2**（④ 为策略性 fail-closed，无业务产物） |

### V2 —— 只改本体、不动地图 ⇒ 计划必须变化

| 项 | 内容 |
|---|---|
| 证据 | `evidence/gk17-v2-ontology-only-change.json` |
| 复核命令 | `./mvnw -pl apps/api -am test -Dtest=V2OntologyOnlyChangeTest -Dsurefire.failIfNoSpecifiedTests=false -Dgk17.evidence.dir=loops/GK17-ontology-unified-map/evidence` |
| 期望 | `Tests run: 1, Failures: 0`；四变体：基线 `a2413b72e01d7430` → 新增类 `6906980bcbb3d79c`(33 类) → 加互斥关系 `da83ce9db2994477` → 恢复回基线；`mapFingerprintUnchanged=true` |
| 变异对照 | §5 的 M3：移除本体版本 ⇒ **FAIL** |
| ⚠ 已知限制 | 见 **Q3**（本体**语义**未驱动资产/规则/技能选择；`assets/rules/skills` 在所有变体下完全相同 —— 已有**绊线断言**把该限制钉成可执行） |

### V3 —— 地图引用不存在的个体 ⇒ 必须拒绝

| 项 | 内容 |
|---|---|
| 证据 | `evidence/gk17-v3-baseline-*.log`、`evidence/gk17-v3-selftest-*.log` |
| 复核命令 | `python3 scripts/gk17_ref_anchor_check.py --root .` → `--selftest` |
| 期望 | 基线 `verdict=PASS violations=0`（exit 0）；`--selftest` = `SELFTEST RESULT: PASS (6 mutations)`（6 个变异逐个 FAIL、`[restored] PASS`） |
| 判据字面形状 | `fake_assetRef` ⇒ `ASSET-DOES-NOT-EXIST-GK17 referenced by specs/.../DOMAIN_MAP.md (field: assetRefs, NO_ANCHOR_IN_AUTHORITATIVE_SOURCE)` |
| ⚠ 已知限制 | 见 **Q4**（锚定空间是既有权威 ID 空间，含 `entrypoints.tasks` 对齐本体 `TaskType`；**不是** A-Box 个体锚定） |

### V4 —— 地图与本体手工不一致 ⇒ 门禁必须检出

| 项 | 内容 |
|---|---|
| 证据 | `evidence/gk17-v4-baseline-*.log`、`evidence/gk17-mutation-regression-*-W6.log` |
| 复核命令 | `python3 scripts/gk17_triple_consistency_check.py --root .`；另 `python3 scripts/gate_injection_tests.py` |
| 期望 | 基线 D1–D4 全 `OK`、不一致项 0；内置变异 D1 由 0→1 **被捕获**（给出行号 `specs/semantic/gits-core.owl.ttl:367`），撤销后恢复 0；注入矩阵 **20 项全部被检出** |
| ⚠ 已知限制 | 见 **Q5**（D2/D4 **尚无脚本内置**变异探针 —— 现仅由独立注入门禁覆盖；另 D4「有能无力」需产品 Owner 定性后才有真实输入） |

---

## 4. 请独立 QA 逐条作答（便于签署）

| 编号 | 问题 | TL 的呈现（**不是**结论） |
|---|---|---|
| **Q1** | V1 的 ②"本体查实体/关系"**当前只到 T-Box 加载 + 查询声明**（本体 `individuals=0`；`SemanticQueryPort` 在 `apps/api/src/main` **未装配**，实测 grep 无命中 ⇒ 实体级查询**未执行**）—— 是否影响 **V1 通过**？ | TL 未伪造生产不存在的步骤；缺口已如实写入 `gk17-v1-previsit-chain.json` 的 `v1CoverageGaps`。可选读法：(a) 视为"链路已通、数据面待 W3.2/W4"而 V1 通过；(b) 视为 V1 未达标，须待 A-Box 就绪后重跑 |
| **Q2** | V1 的 ④ SKILL 调用为**策略性 fail-closed**（`skill-customer-previsit-report` 在 `NO_LOCAL_FILL` 内，返回 `KERT_REQUIRED`），**有轨迹、无业务产物** —— 是否满足"SKILL 调用"？ | 同一用例含**对照**（策略外技能 `gk17-v1-port-probe` ⇒ `isOk=true`）以区分"策略拒绝"与"端口故障" |
| **Q3** | V2：**机制**成立（本体变 ⇒ `planHash`/`versions.ontology` 必变，地图指纹不变，可重放），但本体**语义**（互斥关系本身）**未驱动** `selectedAssets`/`ruleChecks`/`skills` —— V2 是否达标？ | 提示（**非结论**）：编排表中"前置/互斥/配套"的**语义消费**属 **WP7.1（产品负责人）** 交付面，见 `docs/dispatch/GK17-ontology-unified-map-长程编排-V1.0.md` |
| **Q4** | V3 的锚定空间为**既有权威 ID 空间**（`KM/KD/ASSET/SP/AC/RP` + `entrypoints.tasks` 对齐本体 `gits:TaskType`），**不是**"地图 → A-Box 个体"锚定 —— 是否视为通过？ | 该限制由门禁脚本自身 docstring 的「既有缺口/诚实缺口」明示 |
| **Q5** | V4 的 D2/D4 **无脚本内置**变异探针（仅 D1 有；D2/D4 由独立注入门禁覆盖）—— 是否满足"V4 反例有变异对照"？ | 已在 `NEXT_SESSION.md` 的 W8 必办登记为"把 D2/D4 专门探针内置到 `--selftest`"；该脚本属 **gate_owner** 独占路径，TL 未越界修改 |
| **Q6** | W2 的两条设计裁定（本体加载位置；`evidence` 不入 `planHash`）是否被认可？ | 均有守护用例（见 §2） |

---

## 5. 变异复核配方（**让 QA 能独立复现"非空转"**，请务必执行至少 M1 + M3）

> 三者均遵守：**先备份 → 施加变异 → 期望 FAIL → 还原 → 期望 PASS**；且**校验源码 sha256 前后一致**
> （`DefaultActivationPlanner.java` 应为 `83e3b300e5e5ffb4c28c3cb38450d785fa8d871ecfa73d2839cfc3b18789398d`）。

**M1 —— 移除本体 fail-closed 守卫（复现历史缺陷：静默降级为占位快照）**

```bash
cd /home/szf/dev/gits-cbanking
F=modules/knowledge-architecture/src/main/java/com/gien/gits/knowledge/plan/DefaultActivationPlanner.java
cp "$F" /tmp/qa-m1.bak
python3 - "$F" <<'PY'
import sys
p=sys.argv[1]; s=open(p,encoding="utf-8").read()
old="""        OntologyLoadResult ontologyResult = ontologyPort.load();
        if (!ontologyResult.isLoaded()) {
            return new PlanDecision.Deny(ontologyResult.failureCode(), ontologyResult.failureReason());
        }
        OntologySnapshot ontology = ontologyResult.snapshot();
"""
new="""        OntologyLoadResult ontologyResult = ontologyPort.load();
        OntologySnapshot ontology = ontologyResult.isLoaded()
                ? ontologyResult.snapshot()
                : new OntologySnapshot("CTR-SEM-001/002@CURRENT_BASE", "shadow", 0, 0, 0, 0);
"""
assert s.count(old)==1
open(p,"w",encoding="utf-8").write(s.replace(old,new))
PY
./mvnw --batch-mode --no-transfer-progress -pl modules/knowledge-architecture -am test \
  -Dtest=DefaultActivationPlannerTest -Dsurefire.failIfNoSpecifiedTests=false   # 期望 FAIL 2 条
echo "exit=$? （期望非 0）"
cp /tmp/qa-m1.bak "$F" && sha256sum "$F"   # 期望回到 83e3b300…
```

**M3 —— 把本体版本从 `planHash` 移除（V2/V2.3 的核心断言）**

```bash
F=modules/knowledge-architecture/src/main/java/com/gien/gits/knowledge/plan/DefaultActivationPlanner.java
cp "$F" /tmp/qa-m3.bak
python3 - "$F" <<'PY'
import sys
p=sys.argv[1]; s=open(p,encoding="utf-8").read()
old="        sb.append(ontologyVersion).append('|');\n"
assert s.count(old)==1
open(p,"w",encoding="utf-8").write(s.replace(old,""))
PY
./mvnw --batch-mode --no-transfer-progress -pl apps/api -am test \
  -Dtest=V2OntologyOnlyChangeTest -Dsurefire.failIfNoSpecifiedTests=false    # 期望 FAIL 1 条
echo "exit=$? （期望非 0）"
cp /tmp/qa-m3.bak "$F" && sha256sum "$F"   # 期望回到 83e3b300…
```

**M2（可选）** —— 与 M3 同一变异，改用模块级 + 端到端两个用例：

```bash
./mvnw --batch-mode --no-transfer-progress -pl modules/knowledge-architecture -am test \
  -Dtest=DefaultActivationPlannerTest -Dsurefire.failIfNoSpecifiedTests=false        # 期望 FAIL 1 条
./mvnw --batch-mode --no-transfer-progress -pl adapters/knowledge-filesystem -am test \
  -Dtest=DefaultActivationPlannerFilesystemIT -Dsurefire.failIfNoSpecifiedTests=false  # 期望 FAIL 1 条
```

---

## 6. 复核命令速查（含**不得计为通过**项）

| 命令 | 期望 | 注意 |
|---|---|---|
| `make generate` | PASS | 合同先行已执行；`generated/` 只经 make generate |
| `make check` | exit 0；**22/23**；INTEGRITY FAILURES 空 | ⚠ 其中 `gate-injection-tests` = **INCONCLUSIVE**、`semantic-consumption` = **READINESS NOT MET** ⇒ **两项均不得计为通过** |
| `./mvnw -q -pl apps/api test -Dtest=MechanismE2eIT -DskipITs=false` | `1/0/0/0` | 需先做 §0.1 |
| `./mvnw --batch-mode --no-transfer-progress test` | api **603/0/0/4**、worker **22/0/0/0**、15 模块 SUCCESS | 不进 `verify`（避开联网 dependency-check） |
| `python3 scripts/gk17_ref_anchor_check.py --root .` / `--selftest` | `violations=0` / `PASS (6 mutations)` | — |
| `python3 scripts/gk17_triple_consistency_check.py --root .` | 不一致项 0；D1 变异被捕获 | — |
| `python3 scripts/gate_injection_tests.py` | 20 项注入全检出；`__GATE_VERDICT__=INCONCLUSIVE` | ⚠ **INCONCLUSIVE 不得计为通过** |
| `python3 scripts/loop_guard.py --loop GK17-ontology-unified-map` | `loop-guard: PASS` | — |
| `make backend-test` / `make frontend-test` | **环境红**（OWASP 需联网 / 沙箱守卫阻断 npm ci） | ⚠ 不得读作通过，也不得为它改门禁构成 |

---

## 7. 非声明（**判定方请一并核对**）

- 本包**不是** `QA_PASS`，**不代表** `PRODUCTION_READY`；TL **未代签**任何结论或 Owner 决议；
- TL **未**声称：真实 dsh/KERT 平台已接通、A-Box 实体/关系查询可用、本体已"参与"计划选择、V3 已锚定 A-Box 个体；
- TL **未**修改：`docs/dd/gk-ke-contract/` 封版制品、`generated/`（仅经 `make generate`）、`LOOP.yaml` 的门禁命令、
  `gate_owner` 独占的门禁脚本、他人并发改动（根 `FAILURES.md`、`Makefile`、`AGENTS.md`、`diagrams/` 等）；
- W6 的 pending gate `gk17_v1_v4_experiments` **未进 `LOOP.yaml.gates`** ⇒ 本轮**未**经 `record_gate.py`
  落 `EVIDENCE.json`（Loop 记忆单写者，且本工作区有其他执行者并发提交）；登记留给持 baton 的编排者；
- 本包所有"实测"均有对应日志（`evidence/`），标注为"推断/未验证"者**不得**当作结论引用。
