# 锚点（实际提交）

## GITS
- 仓库：`gits-cbanking`（`/home/szf/dev/gits-cbanking`）
- 分支：`recover/PI-ARCH-product-catalog`｜HEAD：`9a6dec78046172cd60cb8032f4419905e1958515`
- tree SHA：`39d3a9d3e7fb9bf2fab38ddd13e2af45fffc3f6f`
- `git status --porcelain` 条目：**242**（分类 {'M': 24, 'D': 2, '??': 216}）

## KERT
- 仓库：`Leibniz-KERT`（`/home/szf/dev/Leibniz-KERT`）
- 分支：`feature/m7-3-knowledge-map-route`｜HEAD：`922a674d3385a803704bc900d4f8ca21523276ed`
- tree SHA：`d60fe598d3817a897d7cace4945bf2af70babba2`
- `git status --porcelain` 条目：**80**

## 独立仓存在性
- L1 独立语义契约库：**不存在**（L1 独立语义契约库尚未建立；仅有候选骨架 `evidence/prep/l1-skeleton/`）
- 集成契约仓：**不存在**（L4 集成契约注册表仅登记为候选 `CTR-SEM-005`）

## KERT 零写入证明（基准 → HEAD 与工作区）
- 基准提交：`64f6f873`
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
- 与本轮产出路径交集：`空`

## 变更归属
- 本轮**未产生新提交**；HEAD 快照不含本轮交付。
- 本轮交付：28 件（**工作区未提交**，见 `CHANGE-LIST.json`）
