# W6｜ITER 记录

## ITER 1｜WP6.1 + WP6.2：V1–V4 实验与证据（2026-09-15）

- Actor: `tech_lead`｜BASE_HEAD: `a1e183b`（W2 交付提交）
- PLAN: `memory/waves/W6-PLAN.md`（**先写后做**，符合 Wave 级硬要求 #1）
- 证据包: `evidence/GK17-W6-V1-V4-证据包.md`

### 产出

| # | 文件 | 内容 |
|---|---|---|
| D1 | `apps/api/src/test/.../e2e/V1PrevisitChainTest.java` | V1 驱动：真实装配（真实 fs readers + 真实 Jena + 真实路由策略 + 真实规划器）→ 五步全落**原始**输出。**常驻 `./mvnw test`**；仅在显式 `-Dgk17.evidence.dir` 时才写 `evidence/`（跑测试不改仓库） |
| D2 | `evidence/gk17-v1-previsit-chain.json` | V1 原始输出（含 `planHash` / `versions.ontology` / **路由理由** 三个判据点名字段） |
| D3 | `evidence/gk17-v1-*.log`、`gk17-v1v2-*.log` | 运行日志 |
| D4 | `apps/api/src/test/.../e2e/V2OntologyOnlyChangeTest.java` | V2 驱动：只改本体（两种变异）、**地图指纹证明未动**、可重放 + 语义强度绊线 |
| D5 | `evidence/gk17-v2-ontology-only-change.json`、`gk17-v2-mutation-*.log` | V2 四变体对照 + 源码变异对照 |
| D6 | `evidence/gk17-v3-baseline-*.log`、`gk17-v3-selftest-*.log` | V3 基线 + 6 变异自证 |
| D7 | `evidence/gk17-v4-baseline-*.log`、`gk17-mutation-regression-*-W6.log` | V4 基线（内置 D1 变异）+ 注入矩阵 |
| D8 | `evidence/GK17-W6-V1-V4-证据包.md` | 汇总（含**覆盖度声明**与**非声明**） |

### V1 实测（原始输出摘录）

```
mode=ONTOLOGY_THEN_MAP  contract=AC-PREVISIT-001  priority=20
reason="先锁定客户事实和缺口，再定向加载文档知识"          ← 判据点名的"路由理由"
ontology=CTR-SEM-002@sha256:705578d6324abd0c  classes=32 objectProps=34 datatypeProps=1 individuals=0
selectedAssets=9  semanticQueries=5  ruleChecks=4  skills=[SP-02,SP-05,SP-15,SP-10]
planHash=a2413b72e01d7430
versions={knowledgeMap=KM-GITS-ROOT@0.1.0, routePolicy=RP-CORP-RM-001@0.1.0,
          activationContract=AC-PREVISIT-001@0.1.0, ontology=CTR-SEM-002@sha256:705578d6324abd0c}
skill 调用：skill-customer-previsit-report → SKILL_ERROR（KERT_REQUIRED，策略性 fail-closed）
对照    ：gk17-v1-port-probe → isOk=true（证明端口机制可用，非端口故障）
```

### V2 四变体

| 变体 | 本体版本尾 | 类数 | `planHash` |
|---|---|---|---|
| 基线 | `…705578d6324abd0c` | 32 | `a2413b72e01d7430` |
| 变异 A（新增类） | `…66be74f34e6c3f41` | 33 | **`6906980bcbb3d79c`** |
| 变异 B（加互斥关系，判据字面例） | `…06096dc29b50ba7d` | 32 | **`da83ce9db2994477`** |
| 恢复 | `…705578d6324abd0c` | 32 | `a2413b72e01d7430`（= 基线） |

地图指纹 `mapFingerprintUnchanged=true`（sha256 `22ded46cde92b218`）⇒ **不动地图**前提成立。

### 变异对照总表

| 判据 | 变异 | 变异前 | 变异后 | 恢复后 |
|---|---|---|---|---|
| V2 | 移除 `deterministicContent` 的本体版本（**源码**） | PASS | **FAIL**（`Failures: 1`，退出码 1） | PASS（sha256 复原 `83e3b300…`） |
| V3 | 地图 `assetRefs` 悬空 ID（脚本内，对副本） | PASS `violations=0` | **FAIL**（检出 + 文件） | PASS |
| V3 | 另 5 个 ID 空间（skill/contract/task/domain…） | PASS | **FAIL ×5** | PASS |
| V4 | 本体副本追加关系实例（D1） | PASS（D1=0） | **FAIL**（D1=1，`gits-core.owl.ttl:367`） | PASS（D1=0） |

### 门禁

| 门禁 | 结果 |
|---|---|
| `V1PrevisitChainTest` / `V2OntologyOnlyChangeTest` | **PASS**（`2/0/0/0`） |
| `./mvnw test`（全量测试面，含两条新驱动） | **PASS**（api **603/0/0/4** = 601 + 2；worker `22/0/0/0`；15 模块全 SUCCESS） |
| `ontology_load`（`MechanismE2eIT`） | **PASS**（`1/0/0/0`）—— 见下"门禁可复现性" |
| `gk17_ref_anchor_check`（V3） | **PASS**（基线 `violations=0`；`--selftest` 6 变异全检出） |
| `gk17_triple_consistency_check`（V4） | **PASS**（不一致项 0；D1 变异被捕获、撤销恢复） |
| `gate_injection_tests.py`（`gk17_mutation_regression`） | `INCONCLUSIVE` —— 20 项注入全检出，但 **3 个门禁未取得负例证据** ⇒ **不计为通过** |
| `make check` | PASS（exit 0，22/23，INTEGRITY FAILURES 空；`gate-injection-tests` INCONCLUSIVE、`semantic-consumption` READINESS NOT MET **均不计为通过**） |

### 门禁可复现性缺陷（本轮实测新增，已记 `FAILURES.md` `20260915T073300Z`）

V1 驱动首次运行时撞到：**`ontology_load` 的文档化命令**（`./mvnw -q -pl apps/api test -Dtest=MechanismE2eIT -DskipITs=false`）
因 `~/.m2` 里 `semantic-runtime` / `semantic-jena` 是 **WP2.1 之前**的旧快照而 `testCompile` 失败。

**两条实测事实（都与直觉相反，故记）**：

1. 旧 jar 确无 `OntologyPort`，且 `JenaOntologyAdapter` 也找不到；
2. 该命令**只在 `testCompile` 失败、`default-compile` 无错** —— 因为主类上次全反应堆构建已编译、本次**增量跳过**。
   ⇒ **该命令此前那次"PASS"是靠陈旧 `target/` 达成的**（典型"门禁 PASS ≠ 正确"）。

**处置**：遵守"**不许改命令**"，**不改 `LOOP.yaml` 的命令**，而是按该命令**既有前提**重装工件
（`-pl modules/semantic-runtime,modules/knowledge-architecture,adapters/semantic-jena -am install -DskipTests -Ddependency-check.skip=true`，
其中 `-Ddependency-check.skip=true` 仅用于**构建卫生动作**、**不是**跑门禁，并已显式记录），随后**按原命令**重跑 ⇒ **PASS**（`1/0/0/0`）。

### 三处待 ACCEPT 裁定（**不得**由实现方自判）

1. **V1**：②"本体查实体/关系"只到 T-Box（`individuals=0`；`SemanticQueryPort` 未装配，查询未执行）⇒ 是否影响 V1 通过；
2. **V2**：本体**语义**未驱动资产/规则/技能选择（只有版本入哈希）⇒ 若要求语义驱动则**未达标**（绊线断言已钉住）；
3. **V3**：锚定空间是**既有权威 ID 空间**（含 `entrypoints.tasks` 对齐本体），**不是** A-Box 个体锚定 ⇒ 是否视为通过。

### 非声明

- W6 **尚未 ACCEPT**；本 ITER **不是** `QA_PASS`，**不代表** `PRODUCTION_READY`；
- **不**声称真实 dsh/KERT 平台已接通、**不**声称 A-Box 查询可用、**不**声称本体已"参与"选择；
- `gate-injection-tests` 的 `INCONCLUSIVE` **未计为通过**；`backend_test` / `frontend_test` 仍为**环境红**；
- W6 的 pending gate `gk17_v1_v4_experiments` **未进 `LOOP.yaml.gates`** ⇒ 本轮**未**经 `record_gate.py`
  落 `EVIDENCE.json`（Loop 记忆单写者，本工作区有其他执行者并发提交），登记留给持 baton 的编排者。
