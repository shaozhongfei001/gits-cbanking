# W0｜Iteration log（append-only）

由 `scripts/record_gate.py` 追加实际attempt、命令、退出码、证据hash和下一动作。没有实际执行不得登记PASS。

## Attempt 1｜20260821T114012Z

- Gate: `p0_project_and_workspace`
- Command: `cd scenario/dkws-platform && PYTHONPATH=src:tests:scripts python3 -m unittest test_pipeline.TestWorkspace -v`
- Exit: `0`
- Evidence: `loops/P24-dkws-platform/evidence/p0_project_and_workspace-20260821T114012Z.log`
- SHA256: `27ad06755fe644416fa8b5a4a872e11c672ae8e0f2e9cfa78218e9f9d325cc94`

## Attempt 1｜20260821T114013Z

- Gate: `p1_contract_framework`
- Command: `cd scenario/dkws-platform && PYTHONPATH=src:tests:scripts python3 -m unittest test_contract test_seeds -v`
- Exit: `0`
- Evidence: `loops/P24-dkws-platform/evidence/p1_contract_framework-20260821T114013Z.log`
- SHA256: `3da6bf6b045993e51a5df42adac8fb73f4c9074015df244443caef42aea0f7e7`

## Attempt 1｜20260821T114013Z

- Gate: `p2_raw_ingest`
- Command: `cd scenario/dkws-platform && PYTHONPATH=src:tests:scripts python3 -m unittest test_pipeline.TestIngest test_graph.TestGraphIngest -v`
- Exit: `0`
- Evidence: `loops/P24-dkws-platform/evidence/p2_raw_ingest-20260821T114013Z.log`
- SHA256: `5e98abe385eefcfcebbc977326ae80a562bfac10af298d84432729fc20cc8117`

## Attempt 1｜20260821T114013Z

- Gate: `p3_structured_clean`
- Command: `cd scenario/dkws-platform && PYTHONPATH=src:tests:scripts python3 -m unittest test_pipeline.TestStateMachines test_extra_domains.TestExtraDomains -v`
- Exit: `0`
- Evidence: `loops/P24-dkws-platform/evidence/p3_structured_clean-20260821T114013Z.log`
- SHA256: `8e276748896b171099195fe241098416843b32b56c3ccd0ed4cdb064b9b55089`

## Attempt 1｜20260821T114013Z

- Gate: `p4_docs_normalize_slice`
- Command: `cd scenario/dkws-platform && PYTHONPATH=src:tests:scripts python3 -m unittest test_pipeline.TestDocs -v`
- Exit: `0`
- Evidence: `loops/P24-dkws-platform/evidence/p4_docs_normalize_slice-20260821T114013Z.log`
- SHA256: `91085bf8ea2884e0b7bfafb27648ecd4dba734ef430083326f7111d4124b19f9`

## Attempt 1｜20260821T114013Z

- Gate: `p5_knowledge_candidate`
- Command: `cd scenario/dkws-platform && PYTHONPATH=src:tests:scripts python3 -m unittest test_pipeline.TestKnowledge -v`
- Exit: `0`
- Evidence: `loops/P24-dkws-platform/evidence/p5_knowledge_candidate-20260821T114013Z.log`
- SHA256: `b48dde72bd54e09808253c99ad38a2584d2f6e293df0c702763f444470411fdc`

## Attempt 1｜20260821T114013Z

- Gate: `p6_core_publish`
- Command: `cd scenario/dkws-platform && PYTHONPATH=src:tests:scripts python3 -m unittest test_pipeline.TestPublish -v`
- Exit: `0`
- Evidence: `loops/P24-dkws-platform/evidence/p6_core_publish-20260821T114013Z.log`
- SHA256: `e96ebd588cbee0e139293b22104ddcb7065322dc3299e79f0dc264d1e4b7a8a7`

## Attempt 1｜20260821T114014Z

- Gate: `p7_projections`
- Command: `cd scenario/dkws-platform && PYTHONPATH=src:tests:scripts python3 -m unittest test_projection.ProjectionTestCase -v`
- Exit: `0`
- Evidence: `loops/P24-dkws-platform/evidence/p7_projections-20260821T114014Z.log`
- SHA256: `595f95cd98b3668cb9c325fabda89ab9a48b1e165d5e87a24781aa33fb161b71`

## Attempt 1｜20260821T114014Z

- Gate: `p8_services`
- Command: `cd scenario/dkws-platform && PYTHONPATH=src:tests:scripts python3 -m unittest test_pipeline.TestRuleExec -v && PYTHONPATH=src python3 -m dkws --help`
- Exit: `0`
- Evidence: `loops/P24-dkws-platform/evidence/p8_services-20260821T114014Z.log`
- SHA256: `bf98db2fb35949953c02413bd16674f650ad8c92e8c9d56d27bc7d14641d9ea4`

## Attempt 1｜20260821T114015Z

- Gate: `p9_security_perf_e2e`
- Command: `cd scenario/dkws-platform && PYTHONPATH=src:tests:scripts python3 -m unittest test_e2e.EndToEndTestCase test_security_perf test_previsit_report test_pipeline.TestTraceMatrix -v`
- Exit: `0`
- Evidence: `loops/P24-dkws-platform/evidence/p9_security_perf_e2e-20260821T114015Z.log`
- SHA256: `d651b8853c363ad94c3df1ecd1d22b07f083fd69debd986bd715e5613e6cbee1`
