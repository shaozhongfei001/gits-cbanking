# README-REPRO —— 独立复核指南

**目标**：没有本地仓库的评审人，也能核对本轮**关键结论**。

## 0. 包内结构
```
ONTO1-PREP-INDEPENDENT-REVIEW-20260921/
├── README-REPRO.md            # 本文件
├── ANCHORS.md / ANCHORS.json  # 仓库锚点（分支/HEAD/tree SHA/status）+ 零写入证明
├── CHANGE-LIST.json           # 锚点 → 本轮交付；未提交改动**单列**
├── KERT-ZERO-WRITE-PROOF.json # 基准提交 → HEAD 与工作区的 diff 证据
├── RESULTS.md                 # 结果口径三项 + 计数单位与重叠性
├── EXCLUSIONS.md              # 排除项
├── DELIVERABLES/              # 本轮五项交付（含逐类核清、条款核清）
├── SOURCE/                    # 生成脚本与配置（可直接运行）
├── EVIDENCE/                  # 原始证据文件 + gate-logs/（门禁原始日志）
└── MANIFEST.sha256            # 逐文件 SHA-256
```

## 1. 锚点（ONTO1-PREP-INDEPENDENT-REVIEW-20260921）
- GITS `gits-cbanking`：分支 `recover/PI-ARCH-product-catalog`｜HEAD `9a6dec78046172cd60cb8032f4419905e1958515`｜tree `39d3a9d3e7fb9bf2fab38ddd13e2af45fffc3f6f`
- KERT `Leibniz-KERT`：分支 `feature/m7-3-knowledge-map-route`｜HEAD `922a674d3385a803704bc900d4f8ca21523276ed`｜tree `d60fe598d3817a897d7cace4945bf2af70babba2`
- **本轮未产生新提交**：交付件均为工作区文件，已逐件进 `MANIFEST.sha256`。

## 2. 复核两项疑点（无需本地仓库）

### 疑点一：L1 是 8 类还是 32 类
1. 打开 `DELIVERABLES/32-classes-target-mapping.json`：
   - `classes_32` = 基线**来源盘点**（32 行，逐行含 `existing_iri / target_layer / action / tbox_owner / mapping_45_item`）；
   - `l1_candidate_model` = **L1 候选 8 类**（每类含 `design_source / baseline_successor_of / mapping_type`）。
2. 打开 `EVIDENCE/docs/architecture/ONTOLOGY-SPLIT-DESIGN-V2.0-REVIEW.md` §4.2，逐项比对 8 类名单。
3. 结论成立条件：`l1_candidate_model` 的**集合等于**设计 §4.2 的 8 类（脚本 `--gate` 的 R3 断言）。
4. 另见 `DELIVERABLES/l1-term-inventory.json` 的 `artifact_role = SOURCE_INVENTORY`：**来源盘点 ≠ L1 候选**。

### 疑点二：条款作用域
1. 打开 `DELIVERABLES/WI-A2-CLAUSE-SCOPE-AND-DISPOSAL-TIMING.md`：含**原文出处**（执行计划 §1 WI-A2 行与 §0 阶段表）与逐动作判定表。
2. 打开 `EVIDENCE/loops/ONTO1-ontology-split/evidence/consumer-scan-summary.csv`：
   `disposition` 分布含 `FOLLOW_MIGRATION` / `HOMONYM_REQUIRES_SOURCE_CHECK` / `CONTROL_PLANE_REQUIRED`
   ⇒ 处置表**未达 100%**（推翻"处置率 100%"的说法，该说法已在 FAILURES `W15TL-17` 记为我方口径错误）。
3. 结论：条款约束 **Wave 2/3 开工**；**不约束** 需求分析 / SIM 开发。

## 3. 复现命令（在有仓库的环境中）
```bash
python3 scripts/onto1_class_reconciliation.py --gate      # 32 类 / L1 八类 / 计数算术
python3 scripts/onto1_construction_plan.py --gate         # 691 项批次计划
python3 scripts/onto1_l1_prep.py --gate                   # L1 骨架不变式
python3 scripts/onto1_l1_prep.py --migration              # 迁移覆盖率（499/364/125/64/34/325）
python3 scripts/onto1_c2_generator_check.py --gate        # 生成器根因（C-2）
python3 scripts/onto1_review_package_build.py --gate      # 本包自检
```
每条命令的**期望输出**见 `RESULTS.md` 与 `EVIDENCE/gate-logs/` 中的原始日志。

## 4. 原始证据与自检结果
| 门禁 | 状态 | exit | 原始日志 |
|---|---|---|---|
| `wi_construction_plan` | pass | 0 | `wi_construction_plan-20260921T072543Z.log` |
| `wi_construction_plan_selftest` | pass | 0 | `wi_construction_plan_selftest-20260921T072544Z.log` |
| `wi_l1_prep` | pass | 0 | `wi_l1_prep-20260921T072544Z.log` |
| `wi_l1_prep_selftest` | pass | 0 | `wi_l1_prep_selftest-20260921T072544Z.log` |
| `wi_c2_generator_check` | pass | 0 | `wi_c2_generator_check-20260921T050546Z.log` |
| `wi_c2_fix_verify` | pass | 0 | `wi_c2_fix_verify-20260921T050547Z.log` |
| `wi_d2_sim_projection` | pass | 0 | `wi_d2_sim_projection-20260921T050547Z.log` |
| `wi_log_hygiene` | pass | 0 | `wi_log_hygiene-20260921T050706Z.log` |
| `wi_a4_namespace_collision` | inconclusive | 3 | `wi_a4_namespace_collision-20260921T050548Z.log` |

## 5. 零写入证明（KERT）
- 基准提交：`64f6f873`（指定基准：本 Loop 索引依据中记录的 KERT 提交 `64f6f873`（PKG-A1 开工声明所载索引基准；GITS 侧对应 `71169042`）。）
- 基准 → HEAD：.github/workflows/ci.yml                           |  125 +-
 docs/adr/ADR-017-lightrag-retrieval-store.md       |  194 ++
 docs/architecture.md                               |    2 +-
 docs/contracts/schemas/assembly-trace.schema.json  |   11 +-
 docs/development/M3_PLAN_GITS_INTEGRATION.md       |    6 +-
 docs/evaluation-sqlite-graph-base.md               |    2 +-
 .../KERT_GATE0_EVIDENCE_PACK_CANDIDATE.md          |    2 +-
 ...ERT_PENDING_OWNER_DECISION_M7_EVOLUTION_V1.0.md |    4 +-
 .../KERT_STATUS_BASELINE_REVISION_CANDIDATE_M7.md  |    6 +-
 docs/integration/KERT_GITS_CONTRACT_DIFF.md        |    8 +-
 evidence/kert-e2e-ci/HANDOFF-2026-09-15.md         |    4 +-
 evidence/kert-e2e-ci/TASK_PACKAGE_D-E2E-01.md      |    4 +-
 evidence/m7-3/CANDIDATE-CONTRACT-MERGE-V1-V2.md    |  115 +-
 evidence/m7-3/CANDIDATE-M7-1-B1-EQUIVALENT-SWAP.md |  543 +++-
 evidence/m7-3/DECISION_SHEET_M7_CLOSURE.md         |   97 +-
 evidence/m7-3/DIFF-D-24-JOBS-ENDPOINT.md           |   84 +
 evidence/m7-3/EVIDENCE-CONFIRM-RUN-M7-1-B1.md      |  211 ++
 ...DENCE-D31-ONTOLOGY-OWL-SHACL-MATERIALIZATION.md |  200 ++
 .../m7-3/EVIDENCE-OFFICIAL-RERUN-M7-1-B1-B2.md     |  351 +++
 ...-SEMANTICS-MAP-RESERVATION-AND-LINEAGE-INPUT.md |  105 +
 evidence/m7-3/INVENTORY_D-28-ENUM-SOURCES.md       |   83 +
 evidence/m7-3/INVENTORY_V1_LINE_REFERENCES.md      |  215 ++
 evidence/m7-3/PLAN_D-23-PYTEST-ADOPTION.md         |  246 ++
 .../m7-3/PLAN_D-6-E2E-ASSERTION-STRENGTHENING.md   |  157 ++
 .../m7-3/PROPOSAL_REGISTER_UNDECLARED_V1_PATHS.md  |   23 +-
 evidence/m7-3/confirm-run-m7-1-b1-audit.log        |  137 +
 .../m7-3/confirm-run-m7-1-b1-baseline-audit.py     |  244 ++
 evidence/m7-3/confirm-run-m7-1-b1-probe.log        |  233 ++
 evidence/m7-3/confirm-run-m7-1-b1-probe.py         |  195 ++
 evidence/m7-3/confirm-run-m7-1-b1-sets.json        | 2772 ++++++++++++++++++++
 .../90_control/ontology/PROVENANCE.json            |   38 +
 .../ontology/customer-source-mapping.r2rml.ttl     |   15 +
 .../90_control/ontology/gits-core.owl.ttl          |  364 +++
 .../90_control/ontology/gits-core.shacl.ttl        |  268 ++
 .../90_control/ontology/products.ttl               |  115 +
 examples/gits_adapter/README.md                    |    8 +-
 examples/gits_adapter/curl/list_skills.sh          |   25 -
 examples/gits_adapter/python/kert_client.py        |   26 +-
 pyproject.toml                                     |   23 +-
 requirements-lock.txt                              |   12 +
 specs/kert-openapi-v1.yaml                         |  720 ++++-
 src/kert/application/ontology_materialize.py       |  345 +++
 .../product_recommendation/sp15_skill.py           |   18 +-
 src/kert/application/report.py                     |   22 +-
 src/kert/application/service_proposal.py           |   36 +-
 src/kert/application/services.py                   |  229 +-
 src/kert/application/skills.py                     |  291 +-
 src/kert/domain/knowledge_map.py                   |    6 +
 src/kert/domain/ontology_assets.py                 |  245 ++
 src/kert/domain/ontology_parse.py                  |  199 ++
 src/kert/domain/ontology_reference.py              |  106 +
 src/kert/domain/route_policy.py                    |    9 +-
 src/kert/infrastructure/lightrag_client.py         |  429 +++
 tests/e2e/kert_api_validation.py                   |   30 +-
 tests/e2e/test_all_skills_execution.py             |   57 +-
 tests/e2e/test_api_validation_adoption.py          |  144 +
 .../integration/test_contract_shape_conformance.py |  265 +-
 tests/integration/test_lightrag_publication.py     |  363 +++
 tests/integration/test_lightrag_retrieval.py       |  104 +
 tests/integration/test_ontology_materialization.py |  285 ++
 tests/integration/test_plan_materialization.py     |  193 ++
 tests/integration/test_routing_api.py              |    9 +-
 .../integration/test_six_ring_chain_end_to_end.py  |  266 ++
 tests/integration/test_skills_capability_swap.py   |  422 +++
 tests/performance/test_concurrency_benchmark.py    |   17 +
 tests/unit/test_contract_enum_single_source.py     |  113 +
 tests/unit/test_gate_state_single_source.py        |  158 ++
 tests/unit/test_knowledge_source.py                |    4 +-
 tests/unit/test_ontology_assets_and_parse.py       |   91 +
 tests/unit/test_ontology_lineage_consistency.py    |   98 +
 tests/unit/test_ontology_reasoning_is_neutral.py   |   99 +
 tests/unit/test_provision_cli.py                   |   32 +-
 .../test_semantics_carriers_and_reservations.py    |  156 ++
 tests/unit/test_skills_capability_swap_guards.py   |  476 ++++
 74 files changed, 13058 insertions(+), 252 deletions(-)
- 基准 → 工作区：.github/workflows/ci.yml                           |  492 +++-
 .understandignore                                  |   13 +-
 docs/adr/ADR-017-lightrag-retrieval-store.md       |  200 ++
 docs/architecture.md                               |    2 +-
 docs/contracts/schemas/assembly-trace.schema.json  |   11 +-
 docs/development/M3_PLAN_GITS_INTEGRATION.md       |    6 +-
 docs/evaluation-sqlite-graph-base.md               |    2 +-
 .../KERT_GATE0_EVIDENCE_PACK_CANDIDATE.md          |    2 +-
 ...ERT_PENDING_OWNER_DECISION_M7_EVOLUTION_V1.0.md |    4 +-
 .../KERT_STATUS_BASELINE_REVISION_CANDIDATE_M7.md  |    6 +-
 docs/integration/KERT_GITS_CONTRACT_DIFF.md        |    8 +-
 evidence/kert-e2e-ci/HANDOFF-2026-09-15.md         |    4 +-
 evidence/kert-e2e-ci/TASK_PACKAGE_D-E2E-01.md      |    4 +-
 evidence/m7-3/CANDIDATE-CONTRACT-MERGE-V1-V2.md    |  115 +-
 evidence/m7-3/CANDIDATE-M7-1-B1-EQUIVALENT-SWAP.md |  543 +++-
 evidence/m7-3/DECISION_SHEET_M7_CLOSURE.md         |   97 +-
 evidence/m7-3/DIFF-D-24-JOBS-ENDPOINT.md           |   84 +
 evidence/m7-3/EVIDENCE-CONFIRM-RUN-M7-1-B1.md      |  211 ++
 ...DENCE-D31-ONTOLOGY-OWL-SHACL-MATERIALIZATION.md |  200 ++
 .../m7-3/EVIDENCE-OFFICIAL-RERUN-M7-1-B1-B2.md     |  351 +++
 ...-SEMANTICS-MAP-RESERVATION-AND-LINEAGE-INPUT.md |  105 +
 evidence/m7-3/INVENTORY_D-28-ENUM-SOURCES.md       |   83 +
 evidence/m7-3/INVENTORY_V1_LINE_REFERENCES.md      |  215 ++
 evidence/m7-3/PLAN_D-23-PYTEST-ADOPTION.md         |  246 ++
 .../m7-3/PLAN_D-6-E2E-ASSERTION-STRENGTHENING.md   |  157 ++
 .../m7-3/PROPOSAL_REGISTER_UNDECLARED_V1_PATHS.md  |   23 +-
 evidence/m7-3/confirm-run-m7-1-b1-audit.log        |  137 +
 .../m7-3/confirm-run-m7-1-b1-baseline-audit.py     |  244 ++
 evidence/m7-3/confirm-run-m7-1-b1-probe.log        |  233 ++
 evidence/m7-3/confirm-run-m7-1-b1-probe.py         |  195 ++
 evidence/m7-3/confirm-run-m7-1-b1-sets.json        | 2772 ++++++++++++++++++++
 .../90_control/ontology/PROVENANCE.json            |   38 +
 .../ontology/customer-source-mapping.r2rml.ttl     |   15 +
 .../90_control/ontology/gits-core.owl.ttl          |  364 +++
 .../90_control/ontology/gits-core.shacl.ttl        |  268 ++
 .../90_control/ontology/products.ttl               |  115 +
 .../90_control/schema/route_policy.json            |   28 +-
 examples/gits_adapter/README.md                    |    8 +-
 examples/gits_adapter/curl/list_skills.sh          |   25 -
 examples/gits_adapter/python/kert_client.py        |   26 +-
 pyproject.toml                                     |   31 +-
 requirements-lock.txt                              |   12 +
 specs/kert-openapi-v1.yaml                         |  720 ++++-
 src/kert/api/server.py                             |   97 +-
 src/kert/application/gates.py                      |    3 +-
 src/kert/application/interaction_memory.py         |    7 +-
 src/kert/application/jobs.py                       |    5 +-
 src/kert/application/ontology_materialize.py       |  360 +++
 .../product_recommendation/sp15_skill.py           |   23 +-
 src/kert/application/proposal_rules.py             |   11 +-
 src/kert/application/provision.py                  |   45 +-
 src/kert/application/report.py                     |   38 +-
 src/kert/application/service_proposal.py           |   65 +-
 src/kert/application/services.py                   |  579 +++-
 src/kert/application/skills.py                     |  326 ++-
 src/kert/cli/main.py                               |    7 +-
 src/kert/domain/contracts/specs.py                 |   16 +-
 src/kert/domain/knowledge_map.py                   |    6 +
 src/kert/domain/ontology_assets.py                 |  245 ++
 src/kert/domain/ontology_parse.py                  |  243 ++
 src/kert/domain/ontology_reference.py              |  106 +
 src/kert/domain/route_policy.py                    |    9 +-
 src/kert/dsh/app.py                                |   40 +-
 src/kert/dsh/static/index.html                     |    1 +
 src/kert/infrastructure/adapters/llm.py            |    3 +-
 src/kert/infrastructure/lightrag_client.py         |  429 +++
 tests/conftest.py                                  |   10 +-
 tests/e2e/kert_api_validation.py                   |   30 +-
 tests/e2e/test_all_skills_execution.py             |   57 +-
 tests/e2e/test_api_validation_adoption.py          |  144 +
 .../integration/test_contract_shape_conformance.py |  265 +-
 .../integration/test_control_plane_consistency.py  |  135 +-
 tests/integration/test_interaction_memory.py       |   13 +-
 tests/integration/test_lightrag_publication.py     |  363 +++
 tests/integration/test_lightrag_retrieval.py       |  104 +
 tests/integration/test_ontology_materialization.py |  310 +++
 tests/integration/test_plan_materialization.py     |  193 ++
 tests/integration/test_routing_api.py              |   35 +-
 tests/integration/test_service_proposal.py         |   17 +-
 .../integration/test_six_ring_chain_end_to_end.py  |  266 ++
 tests/integration/test_skill_routing_trace.py      |    2 +-
 tests/integration/test_skills_capability_swap.py   |  422 +++
 tests/integration/test_sp15_skill_registration.py  |   11 +-
 tests/performance/BASELINE.md                      |  135 +-
 tests/performance/test_concurrency_benchmark.py    |  432 ++-
 tests/unit/test_activation_plan.py                 |   12 +-
 tests/unit/test_contract_enum_single_source.py     |  201 ++
 tests/unit/test_gate_state_single_source.py        |  158 ++
 tests/unit/test_knowledge_map.py                   |   36 +-
 tests/unit/test_knowledge_source.py                |    4 +-
 tests/unit/test_ontology_assets_and_parse.py       |  122 +
 tests/unit/test_ontology_lineage_consistency.py    |   98 +
 tests/unit/test_ontology_reasoning_is_neutral.py   |   99 +
 tests/unit/test_provision.py                       |  159 +-
 tests/unit/test_provision_cli.py                   |   38 +-
 tests/unit/test_route_policy.py                    |   15 +-
 .../test_semantics_carriers_and_reservations.py    |  156 ++
 tests/unit/test_skills_capability_swap_guards.py   |  476 ++++
 98 files changed, 15128 insertions(+), 469 deletions(-)
- 与本轮产出路径**交集**：`空`
- **诚实限度**：若评审人要求更强的归因，需要 KERT 侧在基准提交时的**文件级哈希快照**（当前不掌握）；本包仅提供上述可复核证据。

## 6. 独立仓存在性
- L1 独立语义契约库：**不存在**（L1 独立语义契约库尚未建立；仅有候选骨架 `evidence/prep/l1-skeleton/`）
- 集成契约仓：**不存在**（L4 集成契约注册表仅登记为候选 `CTR-SEM-005`）

## 7. 非声明
本包**不构成**委员批准 / `QA_PASS` / 正式基线生效 / 生产可用；**未**合并、发布或改动正式基线；
C-2 关闭仅指**命名空间兼容项**，不代表分仓重构完成（见 `RESULTS.md` §3）。
