# W0｜Iteration log（append-only）

由 `scripts/record_gate.py` 追加实际attempt、命令、退出码、证据hash和下一动作。没有实际执行不得登记PASS。

## Attempt 1｜20260920T132334Z

- Gate: `wi_a1_baseline`
- Command: `python3 scripts/onto1_attribution_rebuild.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a1_baseline-20260920T132334Z.log`
- SHA256: `a27d6469f5b59e60440f15c8db8ae5f8519845d5fe5f985a6d0fcd16d9486e14`

## Attempt 1｜20260920T132334Z

- Gate: `wi_a1_attribution_selftest`
- Command: `python3 scripts/onto1_attribution_rebuild.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a1_attribution_selftest-20260920T132334Z.log`
- SHA256: `3c0fa5555cad88d0c724f8ce408a1f7591de6b4e0c99e935fc8a4dac1ee44586`

## Attempt 1｜20260920T132334Z

- Gate: `wi_a2_consumer_scan`
- Command: `python3 scripts/onto1_consumer_scan.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a2_consumer_scan-20260920T132334Z.log`
- SHA256: `986810a09938aed4d57e29cddb2835dd9cd2e2bd4d0e9db0faaea87e0cacf952`

## Attempt 1｜20260920T132335Z

- Gate: `wi_a2_scan_mutation`
- Command: `python3 scripts/onto1_consumer_scan_tests.py`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a2_scan_mutation-20260920T132335Z.log`
- SHA256: `ea145ece22d9203d87e5f60a528cd7147707f97d5c680eaad5f058fd21f8075a`

## Attempt 1｜20260920T132340Z

- Gate: `index_status`
- Command: `make index-status`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/index_status-20260920T132340Z.log`
- SHA256: `f3a8aaebca09c4d1b706a4839189b5b6acd53d91d874d4dbd88e620d470e4b60`

## Attempt 1｜20260920T132343Z

- Gate: `security_check`
- Command: `make security-check`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/security_check-20260920T132343Z.log`
- SHA256: `af2711786f00656ab49ef008ccd3129437feee3f51642723efabf08adbd1fe1c`

## Attempt 1｜20260920T132346Z

- Gate: `contract_check`
- Command: `make check`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/contract_check-20260920T132346Z.log`
- SHA256: `2a4e7957f206590f96896f370745737ca35c777d047c31abe04366ac013a1204`

## Attempt 1｜20260920T134317Z

- Gate: `wi_a5_product_refs`
- Command: `python3 scripts/onto1_product_refs_probe.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a5_product_refs-20260920T134317Z.log`
- SHA256: `90f575fbc25416ac6a911d48fd0ded2f0b286f5315f4fc8a9c38599f6d568bb1`

## Attempt 1｜20260920T134317Z

- Gate: `wi_a5_product_refs_selftest`
- Command: `python3 scripts/onto1_product_refs_probe.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a5_product_refs_selftest-20260920T134317Z.log`
- SHA256: `3436a7acb9a4f9756c2395580834d203c3a0c989a7afe202ff95477173ce2193`

## Attempt 1｜20260920T134418Z

- Gate: `wi_a6_cq_fixtures`
- Command: `python3 scripts/onto1_cq_fixtures.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a6_cq_fixtures-20260920T134418Z.log`
- SHA256: `6dd390a085b3b3ffd29ea55908afcfed12f27c355f93bb50bbe490c15618dc7e`

## Attempt 1｜20260920T134418Z

- Gate: `wi_a6_cq_fixtures_selftest`
- Command: `python3 scripts/onto1_cq_fixtures.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a6_cq_fixtures_selftest-20260920T134418Z.log`
- SHA256: `ed452ff1b54dd8d34543fba9b5bf3b212e463e861f349a00352ac36b065a1124`

## Attempt 1｜20260920T140255Z

- Gate: `wi_review_package_integrity`
- Command: `python3 scripts/onto1_review_package_check.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_review_package_integrity-20260920T140255Z.log`
- SHA256: `23e0bf343d5103bd1bf269606d7c7c204f783dd82040739d66fb13287d0f1121`

## Attempt 1｜20260920T140255Z

- Gate: `wi_review_package_selftest`
- Command: `python3 scripts/onto1_review_package_check.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_review_package_selftest-20260920T140255Z.log`
- SHA256: `0f5f502c121b446aedd4a17b6f8f20e87cfba4aa001abb61ab1c3080e2abb0a5`

## Attempt 2｜20260920T141501Z

- Gate: `wi_review_package_integrity`
- Command: `python3 scripts/onto1_review_package_check.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_review_package_integrity-20260920T141501Z.log`
- SHA256: `23e0bf343d5103bd1bf269606d7c7c204f783dd82040739d66fb13287d0f1121`

## Attempt 2｜20260920T141504Z

- Gate: `wi_review_package_selftest`
- Command: `python3 scripts/onto1_review_package_check.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_review_package_selftest-20260920T141504Z.log`
- SHA256: `0f5f502c121b446aedd4a17b6f8f20e87cfba4aa001abb61ab1c3080e2abb0a5`

## Attempt 1｜20260920T142226Z

- Gate: `wi_a5_d4_pack`
- Command: `python3 scripts/onto1_d4_pack.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a5_d4_pack-20260920T142226Z.log`
- SHA256: `f39fef87d9de64157e1dcda99b1a9c23cb305c72a3115772f76cf8e795fa653e`

## Attempt 1｜20260920T142228Z

- Gate: `wi_a5_d4_pack_selftest`
- Command: `python3 scripts/onto1_d4_pack.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a5_d4_pack_selftest-20260920T142228Z.log`
- SHA256: `ed19925c9b389d922def52cdef9cfd2a12f34f034812c9d6d2b9cf5ab9df5de6`

## Attempt 1｜20260920T145540Z

- Gate: `wi_a3_reference_alignment`
- Command: `python3 scripts/onto1_reference_alignment_check.py --gate`
- Exit: `1`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a3_reference_alignment-20260920T145540Z.log`
- SHA256: `a45a509825a926f01799e7a1688489d89dead4cabb06985efa1f13448bf87319`

## Attempt 1｜20260920T145541Z

- Gate: `wi_a3_reference_alignment_selftest`
- Command: `python3 scripts/onto1_reference_alignment_check.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a3_reference_alignment_selftest-20260920T145541Z.log`
- SHA256: `2b78e96641135563bd7b41efad1ad161c31cf9f891ac94fdca698cf6da1edfe5`

## Attempt 1｜20260920T145541Z

- Gate: `wi_a4_iri_mapping`
- Command: `python3 scripts/onto1_iri_mapping_draft.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a4_iri_mapping-20260920T145541Z.log`
- SHA256: `d3d0ec31dd9e92df0819770665c46a496cf5c99f47769a8f9c71021b87d04d6a`

## Attempt 1｜20260920T145542Z

- Gate: `wi_a4_iri_mapping_selftest`
- Command: `python3 scripts/onto1_iri_mapping_draft.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a4_iri_mapping_selftest-20260920T145542Z.log`
- SHA256: `466ec799ae0b5132f8bf349a68b6c411b4130538e026c07120add2736a9e6e4c`

## Attempt 1｜20260920T145542Z

- Gate: `wi_a4_namespace_collision`
- Command: `python3 scripts/onto1_namespace_collision_check.py --gate`
- Exit: `2`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a4_namespace_collision-20260920T145542Z.log`
- SHA256: `75b016fa7e98182a66567e02e983c58f015fea1e3f360350dd7d448f038498ba`

## Attempt 1｜20260920T145542Z

- Gate: `wi_a4_namespace_collision_selftest`
- Command: `python3 scripts/onto1_namespace_collision_check.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a4_namespace_collision_selftest-20260920T145542Z.log`
- SHA256: `3c40336ec2fae41cb2ab8320ef183f9db2825bdb9368163f886d85af211d6c66`

## Attempt 1｜20260920T145542Z

- Gate: `wi_a5_d2_pack`
- Command: `python3 scripts/onto1_d2_normalization_pack.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a5_d2_pack-20260920T145542Z.log`
- SHA256: `fed583a8b74ed3c22d35288cd2680dfd9b77bccbcde846eb9b160994397ad6ea`

## Attempt 1｜20260920T145542Z

- Gate: `wi_a5_d2_pack_selftest`
- Command: `python3 scripts/onto1_d2_normalization_pack.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a5_d2_pack_selftest-20260920T145542Z.log`
- SHA256: `3e76c96432ac9e9c0821a4211598b4352c2186993e816a582c3269630d48f931`

## Attempt 2｜20260920T145634Z

- Gate: `wi_a3_reference_alignment`
- Command: `python3 scripts/onto1_reference_alignment_check.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a3_reference_alignment-20260920T145634Z.log`
- SHA256: `694b19f91a4e8f8e3b6f563ab0b8f84074b06b87f71adc50608af75b1622073c`

## Attempt 1｜20260920T145851Z

- Gate: `wi_evidence_board_check`
- Command: `python3 scripts/onto1_evidence_board_check.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_evidence_board_check-20260920T145851Z.log`
- SHA256: `368b7c43da9ac0d2f3d213a7c0f4f90bc1cf4d3c39ae466f01e5037c536d3e4a`

## Attempt 1｜20260920T145851Z

- Gate: `wi_evidence_board_check_selftest`
- Command: `python3 scripts/onto1_evidence_board_check.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_evidence_board_check_selftest-20260920T145851Z.log`
- SHA256: `088b7dc6d48e24c930fb9e7cc245a79720d8f0623a1c9d54f907b3b65844d098`

## Attempt 1｜20260920T150253Z

- Gate: `wi_zip_manifest_verify`
- Command: `python3 scripts/onto1_zip_manifest_verify.py --dryrun`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_zip_manifest_verify-20260920T150253Z.log`
- SHA256: `1a935ce82bfbd2573d3103c361165ac768127c9c9bf1898cf786b143b06bdd14`

## Attempt 1｜20260920T152214Z

- Gate: `wi_a2_wave0_readiness_precheck`
- Command: `python3 scripts/onto1_wave0_readiness.py --precheck`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a2_wave0_readiness_precheck-20260920T152214Z.log`
- SHA256: `c07eec9409d0d5cdd976671409ce2c79c05d5e517d7021f7b5fec77f502e0b3d`

## Attempt 1｜20260920T152214Z

- Gate: `wi_a2_wave0_readiness_selftest`
- Command: `python3 scripts/onto1_wave0_readiness.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a2_wave0_readiness_selftest-20260920T152214Z.log`
- SHA256: `c3b53df74f6ec28aeb6871d1b5b53dbfac9a6e74a082af6afcef3a7ca1cf1376`

## Attempt 1｜20260920T153242Z

- Gate: `wi_a2_obligation_triage`
- Command: `echo "# artifact=scripts/onto1_obligation_triage.py@$(sha256sum scripts/onto1_obligation_triage.py | cut -c1-16)"; python3 scripts/onto1_obligation_triage.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a2_obligation_triage-20260920T153242Z.log`
- SHA256: `050a4d60e7f04a9a36bb8cfc9f2831968475c4b286c2d79b1d95fa1bd189862c`

## Attempt 1｜20260920T153243Z

- Gate: `wi_a2_obligation_triage_selftest`
- Command: `echo "# artifact=scripts/onto1_obligation_triage.py@$(sha256sum scripts/onto1_obligation_triage.py | cut -c1-16)"; python3 scripts/onto1_obligation_triage.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a2_obligation_triage_selftest-20260920T153243Z.log`
- SHA256: `e37a25cdf606c5976ab83dd75235f10af40372ff6914bc8093aeecb74c9f21da`

## Attempt 2｜20260920T153255Z

- Gate: `wi_a2_obligation_triage`
- Command: `python3 scripts/onto1_obligation_triage.py --gate; rc=$?; echo "# artifact=scripts/onto1_obligation_triage.py@$(sha256sum scripts/onto1_obligation_triage.py | cut -c1-16)"; exit $rc`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a2_obligation_triage-20260920T153255Z.log`
- SHA256: `2f308b60ba47d81910181fd5d5990a6c092b5a4b8172e358e3d39e5faf8534b6`

## Attempt 2｜20260920T153256Z

- Gate: `wi_a2_obligation_triage_selftest`
- Command: `python3 scripts/onto1_obligation_triage.py --selftest; rc=$?; echo "# artifact=scripts/onto1_obligation_triage.py@$(sha256sum scripts/onto1_obligation_triage.py | cut -c1-16)"; exit $rc`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a2_obligation_triage_selftest-20260920T153256Z.log`
- SHA256: `f8fe1d2f51d9feaea2869c91bc6b546783d0e73fb16c2c4e22d6e7aa1e063df8`

## Attempt 3｜20260920T153327Z

- Gate: `wi_a2_obligation_triage`
- Command: `python3 scripts/onto1_gate_log.py scripts/onto1_obligation_triage.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a2_obligation_triage-20260920T153327Z.log`
- SHA256: `7a4c3397f1be99e416225343534f417761938f660ad4065beff3ce930e6d0097`

## Attempt 3｜20260920T153327Z

- Gate: `wi_a2_obligation_triage_selftest`
- Command: `python3 scripts/onto1_gate_log.py scripts/onto1_obligation_triage.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a2_obligation_triage_selftest-20260920T153327Z.log`
- SHA256: `de054ab41db546fc8de09d50639078a832bee274b510c16a6b2ed13fffd56c45`

## Attempt 1｜20260920T154613Z

- Gate: `wi_w15_a3_acceptance`
- Command: `python3 scripts/onto1_gate_log.py scripts/onto1_w15_acceptance.py`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_w15_a3_acceptance-20260920T154613Z.log`
- SHA256: `6b43facd3fe97453dc7af0f189774747d22c747b5029f5599e0074dce00fd60a`

## Attempt 2｜20260920T155915Z

- Gate: `wi_a4_namespace_collision`
- Command: `python3 scripts/onto1_gate_log.py scripts/onto1_namespace_collision_check.py --gate`
- Exit: `2`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a4_namespace_collision-20260920T155915Z.log`
- SHA256: `0e15da68d4c12304f597f6ca55f7ba4ae3b2a721c3666a66abfb7e7e4c142d76`

## Attempt 2｜20260920T155915Z

- Gate: `wi_a4_namespace_collision_selftest`
- Command: `python3 scripts/onto1_gate_log.py scripts/onto1_namespace_collision_check.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a4_namespace_collision_selftest-20260920T155915Z.log`
- SHA256: `ea37b351bbd116b77ed77eb644cb70213c1d889ebae8e56b30c5453b7a189c6b`

## Attempt 3｜20260920T155915Z

- Gate: `wi_a3_reference_alignment`
- Command: `python3 scripts/onto1_gate_log.py scripts/onto1_reference_alignment_check.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a3_reference_alignment-20260920T155915Z.log`
- SHA256: `18c2121df33d8d6de9ad1565c388fc3cb4f10c7b3152fec01f1d75e7638579cd`

## Attempt 2｜20260920T155916Z

- Gate: `wi_a3_reference_alignment_selftest`
- Command: `python3 scripts/onto1_gate_log.py scripts/onto1_reference_alignment_check.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a3_reference_alignment_selftest-20260920T155916Z.log`
- SHA256: `bac9cee3284c5f3864e583d4b4f41eeeb940bacaf9df332fc190f32b2c090acf`

## Attempt 4｜20260920T160118Z

- Gate: `wi_a2_obligation_triage`
- Command: `python3 scripts/onto1_gate_log.py scripts/onto1_obligation_triage.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a2_obligation_triage-20260920T160118Z.log`
- SHA256: `7f1ec69e16d8636d1531bec9fb7dee9b19cc34c8eb93ae436eaccd4a8d3fce5a`

## Attempt 4｜20260920T160119Z

- Gate: `wi_a2_obligation_triage_selftest`
- Command: `python3 scripts/onto1_gate_log.py scripts/onto1_obligation_triage.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a2_obligation_triage_selftest-20260920T160119Z.log`
- SHA256: `3f100153a876bb3e5aee7b4eeb1a9a0dd57be56ee730cc0a9d0ab6e6745865bd`

## Attempt 5｜20260920T160842Z

- Gate: `wi_a2_obligation_triage`
- Command: `python3 scripts/onto1_gate_log.py scripts/onto1_obligation_triage.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a2_obligation_triage-20260920T160842Z.log`
- SHA256: `3e3b5af94aa93a5342aaba55777e4d8e04fbaec0d8e134b38c6727d73fdcb875`

## Attempt 5｜20260920T160842Z

- Gate: `wi_a2_obligation_triage_selftest`
- Command: `python3 scripts/onto1_gate_log.py scripts/onto1_obligation_triage.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a2_obligation_triage_selftest-20260920T160842Z.log`
- SHA256: `ddbe868cff5f9685d078de1e77848b481232d635daee9e961dba4506d4d312b0`

## Attempt 2｜20260920T160937Z

- Gate: `wi_evidence_board_check`
- Command: `python3 scripts/onto1_evidence_board_check.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_evidence_board_check-20260920T160937Z.log`
- SHA256: `176e670d0006abf724c7852d4649b18a4ec7fbdf0275c8927d6785809c699ad8`

## Attempt 2｜20260920T160937Z

- Gate: `wi_evidence_board_check_selftest`
- Command: `python3 scripts/onto1_evidence_board_check.py --selftest`
- Exit: `2`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_evidence_board_check_selftest-20260920T160937Z.log`
- SHA256: `68843841a9c6fdc06259bf7eace95c47b713a9b4adbb08ac143654aa722c0035`

## Attempt 3｜20260920T160959Z

- Gate: `wi_evidence_board_check`
- Command: `python3 scripts/onto1_evidence_board_check.py --gate`
- Exit: `2`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_evidence_board_check-20260920T160959Z.log`
- SHA256: `02089571b82f672ecec2c31830739c5e4eb600eaa7475dd60da13469adf18d53`

## Attempt 3｜20260920T160959Z

- Gate: `wi_evidence_board_check_selftest`
- Command: `python3 scripts/onto1_evidence_board_check.py --selftest`
- Exit: `2`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_evidence_board_check_selftest-20260920T160959Z.log`
- SHA256: `b568e5c2f62265551d0e3cdb8c897b9979536925d1cf41b8522e12b980076321`

## Attempt 4｜20260920T161025Z

- Gate: `wi_evidence_board_check`
- Command: `python3 scripts/onto1_evidence_board_check.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_evidence_board_check-20260920T161025Z.log`
- SHA256: `1ef047feb332d439d9272024dcf0c1e3e16a57a59f0265cb79ca4b82cdb54561`

## Attempt 4｜20260920T161025Z

- Gate: `wi_evidence_board_check_selftest`
- Command: `python3 scripts/onto1_evidence_board_check.py --selftest`
- Exit: `2`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_evidence_board_check_selftest-20260920T161025Z.log`
- SHA256: `ecbfbed19eb3fa88275244332e9655452f24a8dff5195ad20f10b6471832dfc7`

## Attempt 5｜20260920T161034Z

- Gate: `wi_evidence_board_check_selftest`
- Command: `python3 scripts/onto1_evidence_board_check.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_evidence_board_check_selftest-20260920T161034Z.log`
- SHA256: `4455f5059446bc7f8a333af60f0564468216f7f917b45d1c0710dfcf8f45db78`

## Attempt 4｜20260920T161450Z

- Gate: `wi_a3_reference_alignment`
- Command: `python3 scripts/onto1_gate_log.py scripts/onto1_reference_alignment_check.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a3_reference_alignment-20260920T161450Z.log`
- SHA256: `1f50d1961d92079f98ee9987be81a5c92858c8a3cde30a0254aa648e2ed692dd`

## Attempt 3｜20260920T161452Z

- Gate: `wi_a3_reference_alignment_selftest`
- Command: `python3 scripts/onto1_gate_log.py scripts/onto1_reference_alignment_check.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a3_reference_alignment_selftest-20260920T161452Z.log`
- SHA256: `c9fac51ee67c6cda416f28454ae702484d8b66fb3527df6e9d79a4af75326068`

## Attempt 5｜20260920T161452Z

- Gate: `wi_evidence_board_check`
- Command: `python3 scripts/onto1_gate_log.py scripts/onto1_evidence_board_check.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_evidence_board_check-20260920T161452Z.log`
- SHA256: `71330e0ef8d2088e880b9033dda78522622449f178e153005ff2c5426c9cac4a`

## Attempt 6｜20260920T161534Z

- Gate: `wi_a2_obligation_triage`
- Command: `python3 scripts/onto1_gate_log.py scripts/onto1_obligation_triage.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a2_obligation_triage-20260920T161534Z.log`
- SHA256: `be775ea6cb9872ab489cf1c0cb688620c573946b9064726a74e809270fcaac05`

## Attempt 6｜20260920T161534Z

- Gate: `wi_a2_obligation_triage_selftest`
- Command: `python3 scripts/onto1_gate_log.py scripts/onto1_obligation_triage.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a2_obligation_triage_selftest-20260920T161534Z.log`
- SHA256: `20f7b6b69c484bb1400f667455e02c0b466e60ff6f80089cc9c1567757b7c737`

## Attempt 5｜20260920T161535Z

- Gate: `wi_a3_reference_alignment`
- Command: `python3 scripts/onto1_gate_log.py scripts/onto1_reference_alignment_check.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a3_reference_alignment-20260920T161535Z.log`
- SHA256: `5cf03a4f94137a1ec37291935ffca7b0e8bd10dbed8181cea3983f46b56eca13`

## Attempt 4｜20260920T161536Z

- Gate: `wi_a3_reference_alignment_selftest`
- Command: `python3 scripts/onto1_gate_log.py scripts/onto1_reference_alignment_check.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a3_reference_alignment_selftest-20260920T161536Z.log`
- SHA256: `c9fac51ee67c6cda416f28454ae702484d8b66fb3527df6e9d79a4af75326068`

## Attempt 6｜20260920T161536Z

- Gate: `wi_evidence_board_check`
- Command: `python3 scripts/onto1_gate_log.py scripts/onto1_evidence_board_check.py --gate`
- Exit: `2`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_evidence_board_check-20260920T161536Z.log`
- SHA256: `a97e5d2e6e63e4e2fa178f4df1474398c486b81d7cfc90b7d248086211531fff`

## Attempt 6｜20260920T161536Z

- Gate: `wi_evidence_board_check_selftest`
- Command: `python3 scripts/onto1_gate_log.py scripts/onto1_evidence_board_check.py --selftest`
- Exit: `2`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_evidence_board_check_selftest-20260920T161536Z.log`
- SHA256: `1e51195bbfaa6dda3d595ce993d13f60a4f5d14f9303f4092605d8a09b764ce3`

## Attempt 7｜20260920T161548Z

- Gate: `wi_evidence_board_check`
- Command: `python3 scripts/onto1_gate_log.py scripts/onto1_evidence_board_check.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_evidence_board_check-20260920T161548Z.log`
- SHA256: `45e2ada323a4a7aab80d485fe9665bdd2924915fee2ac117e190cec17ff55832`

## Attempt 7｜20260920T161548Z

- Gate: `wi_evidence_board_check_selftest`
- Command: `python3 scripts/onto1_gate_log.py scripts/onto1_evidence_board_check.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_evidence_board_check_selftest-20260920T161548Z.log`
- SHA256: `b21c4c250c64001eb9e287ff4660e9ca411509fa337b591ae1f508051cb0e6a9`

## Attempt 6｜20260920T162821Z

- Gate: `wi_a3_reference_alignment`
- Command: `python3 scripts/onto1_gate_log.py scripts/onto1_reference_alignment_check.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a3_reference_alignment-20260920T162821Z.log`
- SHA256: `fd5c1508b77258ce72a90e4f291de213c6f31595cbe5139e16bdf8db968383a4`

## Attempt 7｜20260920T165523Z

- Gate: `wi_a3_reference_alignment`
- Command: `python3 scripts/onto1_gate_log.py scripts/onto1_reference_alignment_check.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a3_reference_alignment-20260920T165523Z.log`
- SHA256: `a935b64e8181fa85224ece752ac94ca96b8de729a679ab779e65f2dd37698367`

## Attempt 5｜20260920T165525Z

- Gate: `wi_a3_reference_alignment_selftest`
- Command: `python3 scripts/onto1_gate_log.py scripts/onto1_reference_alignment_check.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a3_reference_alignment_selftest-20260920T165525Z.log`
- SHA256: `4fcd2c412e8ed095dfb81e74b5a6ea40ab39e28858d73dc235e914e9873b1d4d`

## Attempt 2｜20260921T043315Z

- Gate: `wi_a5_d2_pack`
- Command: `python3 scripts/onto1_d2_normalization_pack.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a5_d2_pack-20260921T043315Z.log`
- SHA256: `e1d2776aba611cac6df9cd8e7dfad77bef2554fd9c7141570d1f0925de8d573d`

## Attempt 2｜20260921T043315Z

- Gate: `wi_a5_d2_pack_selftest`
- Command: `python3 scripts/onto1_d2_normalization_pack.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a5_d2_pack_selftest-20260921T043315Z.log`
- SHA256: `bae87fea98c95ad63a6caadddaa3b9fa8563f2771ba02bee7b68aa489927c69e`

## Attempt 1｜20260921T043434Z

- Gate: `wi_c2_fix_verify`
- Command: `python3 scripts/onto1_c2_fix_verify.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_c2_fix_verify-20260921T043434Z.log`
- SHA256: `a7c182eda86aa28f40dfb80150a462182636b39d77d6e7c5d388c590b1e2d5d6`

## Attempt 1｜20260921T043434Z

- Gate: `wi_c2_fix_verify_selftest`
- Command: `python3 scripts/onto1_c2_fix_verify.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_c2_fix_verify_selftest-20260921T043434Z.log`
- SHA256: `69c9b53a86ee4f2392eefdae0daac3e71afe65e34c0d692a770e53c217b0223c`

## Attempt 1｜20260921T043434Z

- Gate: `wi_d2_relation_resolution`
- Command: `python3 scripts/onto1_product_relation_resolution.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_d2_relation_resolution-20260921T043434Z.log`
- SHA256: `a742d4a6165aff6730eda632d2aafb336eabf423ab837399879b97194f505e8e`

## Attempt 1｜20260921T043434Z

- Gate: `wi_d2_relation_resolution_selftest`
- Command: `python3 scripts/onto1_product_relation_resolution.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_d2_relation_resolution_selftest-20260921T043434Z.log`
- SHA256: `dc30e39f0a7e5f75d08158b21044221a7260d8c22319c72c8185af1dc4c67e98`

## Attempt 2｜20260921T043435Z

- Gate: `wi_w15_a3_acceptance`
- Command: `python3 scripts/onto1_gate_log.py scripts/onto1_w15_acceptance.py`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_w15_a3_acceptance-20260921T043435Z.log`
- SHA256: `2c9f0cf6b2822ff170dec12dee90342d51509b75e121393fa7939dc8ffa21750`

## Attempt 3｜20260921T043435Z

- Gate: `wi_a4_namespace_collision`
- Command: `python3 scripts/onto1_gate_log.py scripts/onto1_namespace_collision_check.py --gate`
- Exit: `3`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a4_namespace_collision-20260921T043435Z.log`
- SHA256: `769a4611440cc0671f58eb144f70fc62db7cc76cf6bebc2a1b7a134259e5d7e4`

## Attempt 3｜20260921T043435Z

- Gate: `wi_a4_namespace_collision_selftest`
- Command: `python3 scripts/onto1_gate_log.py scripts/onto1_namespace_collision_check.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a4_namespace_collision_selftest-20260921T043435Z.log`
- SHA256: `995151668bb0b7be7d74fa841580d20d91c5e4abc0f4c954a94d227473200ded`

## Attempt 8｜20260921T043435Z

- Gate: `wi_a3_reference_alignment`
- Command: `python3 scripts/onto1_gate_log.py scripts/onto1_reference_alignment_check.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a3_reference_alignment-20260921T043435Z.log`
- SHA256: `ab3240e0bb54e04c0365119ea2d31932810711bff084001ce399886f14b03789`

## Attempt 6｜20260921T043437Z

- Gate: `wi_a3_reference_alignment_selftest`
- Command: `python3 scripts/onto1_gate_log.py scripts/onto1_reference_alignment_check.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a3_reference_alignment_selftest-20260921T043437Z.log`
- SHA256: `4fcd2c412e8ed095dfb81e74b5a6ea40ab39e28858d73dc235e914e9873b1d4d`

## Attempt 1｜20260921T050546Z

- Gate: `wi_c2_generator_check`
- Command: `python3 scripts/onto1_c2_generator_check.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_c2_generator_check-20260921T050546Z.log`
- SHA256: `d25cf2b3f7f1ed2ba163db45e65c134bd6392d8259e90f6898f840767cf07428`

## Attempt 1｜20260921T050546Z

- Gate: `wi_c2_generator_check_selftest`
- Command: `python3 scripts/onto1_c2_generator_check.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_c2_generator_check_selftest-20260921T050546Z.log`
- SHA256: `8e3cedd20014fcb298a7951a184123c29e1fdacd52897afeb467d400f41dca8c`

## Attempt 1｜20260921T050547Z

- Gate: `wi_d2_sim_projection`
- Command: `python3 scripts/onto1_sim_projection.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_d2_sim_projection-20260921T050547Z.log`
- SHA256: `974eb2b2bbdb527cb14f3d8039cd43f5cbc98638e540e2c6399361553f0cdbe5`

## Attempt 1｜20260921T050547Z

- Gate: `wi_d2_sim_projection_selftest`
- Command: `python3 scripts/onto1_sim_projection.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_d2_sim_projection_selftest-20260921T050547Z.log`
- SHA256: `9ae3b698a8593129200aee0a123d51413a1a63059b07cd6df77450c6d97d36fc`

## Attempt 2｜20260921T050547Z

- Gate: `wi_c2_fix_verify`
- Command: `python3 scripts/onto1_c2_fix_verify.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_c2_fix_verify-20260921T050547Z.log`
- SHA256: `a7c182eda86aa28f40dfb80150a462182636b39d77d6e7c5d388c590b1e2d5d6`

## Attempt 2｜20260921T050547Z

- Gate: `wi_c2_fix_verify_selftest`
- Command: `python3 scripts/onto1_c2_fix_verify.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_c2_fix_verify_selftest-20260921T050547Z.log`
- SHA256: `69c9b53a86ee4f2392eefdae0daac3e71afe65e34c0d692a770e53c217b0223c`

## Attempt 2｜20260921T050547Z

- Gate: `wi_d2_relation_resolution`
- Command: `python3 scripts/onto1_product_relation_resolution.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_d2_relation_resolution-20260921T050547Z.log`
- SHA256: `a742d4a6165aff6730eda632d2aafb336eabf423ab837399879b97194f505e8e`

## Attempt 2｜20260921T050547Z

- Gate: `wi_d2_relation_resolution_selftest`
- Command: `python3 scripts/onto1_product_relation_resolution.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_d2_relation_resolution_selftest-20260921T050547Z.log`
- SHA256: `dc30e39f0a7e5f75d08158b21044221a7260d8c22319c72c8185af1dc4c67e98`

## Attempt 4｜20260921T050548Z

- Gate: `wi_a4_namespace_collision`
- Command: `python3 scripts/onto1_gate_log.py scripts/onto1_namespace_collision_check.py --gate`
- Exit: `3`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a4_namespace_collision-20260921T050548Z.log`
- SHA256: `769a4611440cc0671f58eb144f70fc62db7cc76cf6bebc2a1b7a134259e5d7e4`

## Attempt 4｜20260921T050548Z

- Gate: `wi_a4_namespace_collision_selftest`
- Command: `python3 scripts/onto1_gate_log.py scripts/onto1_namespace_collision_check.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a4_namespace_collision_selftest-20260921T050548Z.log`
- SHA256: `995151668bb0b7be7d74fa841580d20d91c5e4abc0f4c954a94d227473200ded`

## Attempt 1｜20260921T050706Z

- Gate: `wi_log_hygiene`
- Command: `python3 scripts/onto1_log_hygiene.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_log_hygiene-20260921T050706Z.log`
- SHA256: `7af2ba91f377b78cbd1495ca17371b56dc6dc5483beabac6e80aa00ab41e387f`

## Attempt 1｜20260921T050706Z

- Gate: `wi_log_hygiene_selftest`
- Command: `python3 scripts/onto1_log_hygiene.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_log_hygiene_selftest-20260921T050706Z.log`
- SHA256: `c3276857077fe515b994166f6c4f6129e55ee348f48d4aee146089a2989a9d16`

## Attempt 1｜20260921T072543Z

- Gate: `wi_construction_plan`
- Command: `python3 scripts/onto1_construction_plan.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_construction_plan-20260921T072543Z.log`
- SHA256: `3075d44dd2b4b83e480d4634a329af491bf248eb00792804b0d67500ffc78ccb`

## Attempt 1｜20260921T072544Z

- Gate: `wi_construction_plan_selftest`
- Command: `python3 scripts/onto1_construction_plan.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_construction_plan_selftest-20260921T072544Z.log`
- SHA256: `57f99f7c547aa9bad7b82e10e8c80cd4408ed3addd9d81ebb4d2f86d03baaf2e`

## Attempt 1｜20260921T072544Z

- Gate: `wi_l1_prep`
- Command: `python3 scripts/onto1_l1_prep.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_l1_prep-20260921T072544Z.log`
- SHA256: `4f059cee5a4f057a22edccee63a2453b2db920c18e17baac4fd7d7d8b239c912`

## Attempt 1｜20260921T072544Z

- Gate: `wi_l1_prep_selftest`
- Command: `python3 scripts/onto1_l1_prep.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_l1_prep_selftest-20260921T072544Z.log`
- SHA256: `e7b4cccbcc81f59fda23ae17fb0bd5e50816ffad2823de9d669a5073e2fbb2be`

## Attempt 1｜20260921T082840Z

- Gate: `wi_class_reconciliation`
- Command: `python3 scripts/onto1_class_reconciliation.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_class_reconciliation-20260921T082840Z.log`
- SHA256: `5c353f9d1ca33bfb877e69b9ff433930cc564a27624f09ba8d67c810a0997df1`

## Attempt 1｜20260921T082840Z

- Gate: `wi_class_reconciliation_selftest`
- Command: `python3 scripts/onto1_class_reconciliation.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_class_reconciliation_selftest-20260921T082840Z.log`
- SHA256: `feff2b3a679c4211da858c689d5bdea03b16900275ebbed820d7c6beed111d5f`

## Attempt 1｜20260921T082840Z

- Gate: `wi_review_package`
- Command: `python3 scripts/onto1_review_package_build.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_review_package-20260921T082840Z.log`
- SHA256: `cc822c0be66e1aa92d30c68330fc44088bd77860f094c7d9d55d98227eca0340`

## Attempt 3｜20260921T082840Z

- Gate: `wi_review_package_selftest`
- Command: `python3 scripts/onto1_review_package_check.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_review_package_selftest-20260921T082840Z.log`
- SHA256: `0f5f502c121b446aedd4a17b6f8f20e87cfba4aa001abb61ab1c3080e2abb0a5`

## Attempt 2｜20260921T092921Z

- Gate: `wi_construction_plan`
- Command: `python3 scripts/onto1_construction_plan.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_construction_plan-20260921T092921Z.log`
- SHA256: `187f2676bcd3b7d47178c57fa9d381cb6a3e5413fc7bdc61736b23c6f63a8043`

## Attempt 2｜20260921T092921Z

- Gate: `wi_construction_plan_selftest`
- Command: `python3 scripts/onto1_construction_plan.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_construction_plan_selftest-20260921T092921Z.log`
- SHA256: `57f99f7c547aa9bad7b82e10e8c80cd4408ed3addd9d81ebb4d2f86d03baaf2e`

## Attempt 2｜20260921T092921Z

- Gate: `wi_l1_prep`
- Command: `python3 scripts/onto1_l1_prep.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_l1_prep-20260921T092921Z.log`
- SHA256: `4f059cee5a4f057a22edccee63a2453b2db920c18e17baac4fd7d7d8b239c912`

## Attempt 2｜20260921T092921Z

- Gate: `wi_l1_prep_selftest`
- Command: `python3 scripts/onto1_l1_prep.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_l1_prep_selftest-20260921T092921Z.log`
- SHA256: `e7b4cccbcc81f59fda23ae17fb0bd5e50816ffad2823de9d669a5073e2fbb2be`

## Attempt 2｜20260921T092921Z

- Gate: `wi_class_reconciliation`
- Command: `python3 scripts/onto1_class_reconciliation.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_class_reconciliation-20260921T092921Z.log`
- SHA256: `9077ced0207c3b4a22ad1d996a611941ff4c8f1f9605173305c55f21e2f01eb1`

## Attempt 2｜20260921T092921Z

- Gate: `wi_class_reconciliation_selftest`
- Command: `python3 scripts/onto1_class_reconciliation.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_class_reconciliation_selftest-20260921T092921Z.log`
- SHA256: `16502694579c4713e37301abb46f5a1d09d4ec90357371f64ed3f7dd2d8a969d`

## Attempt 1｜20260921T092921Z

- Gate: `wi_prep_package_build`
- Command: `python3 scripts/onto1_review_package_build.py --gate`
- Exit: `1`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_prep_package_build-20260921T092921Z.log`
- SHA256: `d7c9a31f2c9b660708a5f36c8bcb62fe71d37c9b9fba9d2de14940669898e215`

## Attempt 1｜20260921T092921Z

- Gate: `wi_prep_package_build_selftest`
- Command: `python3 scripts/onto1_review_package_build.py --selftest`
- Exit: `1`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_prep_package_build_selftest-20260921T092921Z.log`
- SHA256: `4aaa5e5166a5424f85acf25b15f5424fcd7063e7f15d6495736dcc90df4923ab`

## Attempt 2｜20260921T092928Z

- Gate: `wi_prep_package_build`
- Command: `python3 scripts/onto1_review_package_build.py --gate`
- Exit: `1`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_prep_package_build-20260921T092928Z.log`
- SHA256: `d7c9a31f2c9b660708a5f36c8bcb62fe71d37c9b9fba9d2de14940669898e215`

## Attempt 2｜20260921T092928Z

- Gate: `wi_prep_package_build_selftest`
- Command: `python3 scripts/onto1_review_package_build.py --selftest`
- Exit: `1`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_prep_package_build_selftest-20260921T092928Z.log`
- SHA256: `4d75d1f051450e384f24c81cfc6ab32952de2bfa7fb2e08e2d0a6d49893d0f61`

## Attempt 3｜20260921T092935Z

- Gate: `wi_prep_package_build`
- Command: `python3 scripts/onto1_review_package_build.py --gate`
- Exit: `2`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_prep_package_build-20260921T092935Z.log`
- SHA256: `c81198a07b6ad70cc7ed258a6ca03613f837bd4e6b0f25fb0a9661b035dba2d2`

## Attempt 3｜20260921T092935Z

- Gate: `wi_prep_package_build_selftest`
- Command: `python3 scripts/onto1_review_package_build.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_prep_package_build_selftest-20260921T092935Z.log`
- SHA256: `bbb0909b7b4e5658b1112d5119462c1d8375d3191716dca8e1a76fbb68334455`

## Attempt 4｜20260921T093002Z

- Gate: `wi_prep_package_build`
- Command: `python3 scripts/onto1_review_package_build.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_prep_package_build-20260921T093002Z.log`
- SHA256: `8372852599af564028f5e9a85e9dbcb546198faef520b243575178a5f20dda65`

## Attempt 4｜20260921T093002Z

- Gate: `wi_prep_package_build_selftest`
- Command: `python3 scripts/onto1_review_package_build.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_prep_package_build_selftest-20260921T093002Z.log`
- SHA256: `bbb0909b7b4e5658b1112d5119462c1d8375d3191716dca8e1a76fbb68334455`

## Attempt 5｜20260921T093025Z

- Gate: `wi_prep_package_build`
- Command: `python3 scripts/onto1_review_package_build.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_prep_package_build-20260921T093025Z.log`
- SHA256: `8372852599af564028f5e9a85e9dbcb546198faef520b243575178a5f20dda65`

## Attempt 5｜20260921T093025Z

- Gate: `wi_prep_package_build_selftest`
- Command: `python3 scripts/onto1_review_package_build.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_prep_package_build_selftest-20260921T093025Z.log`
- SHA256: `bbb0909b7b4e5658b1112d5119462c1d8375d3191716dca8e1a76fbb68334455`

## Attempt 3｜20260921T095055Z

- Gate: `wi_construction_plan`
- Command: `python3 scripts/onto1_construction_plan.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_construction_plan-20260921T095055Z.log`
- SHA256: `3951b28e5dccf7df89a425bea9cd51e726d89fa63f57545c89a36a39e2f58a87`

## Attempt 3｜20260921T095056Z

- Gate: `wi_construction_plan_selftest`
- Command: `python3 scripts/onto1_construction_plan.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_construction_plan_selftest-20260921T095056Z.log`
- SHA256: `bac632a33b9309db60f60cd882741c6770574468cbc16ed0d31be8fa2f360b8a`

## Attempt 3｜20260921T095056Z

- Gate: `wi_class_reconciliation`
- Command: `python3 scripts/onto1_class_reconciliation.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_class_reconciliation-20260921T095056Z.log`
- SHA256: `9077ced0207c3b4a22ad1d996a611941ff4c8f1f9605173305c55f21e2f01eb1`

## Attempt 3｜20260921T095056Z

- Gate: `wi_class_reconciliation_selftest`
- Command: `python3 scripts/onto1_class_reconciliation.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_class_reconciliation_selftest-20260921T095056Z.log`
- SHA256: `16502694579c4713e37301abb46f5a1d09d4ec90357371f64ed3f7dd2d8a969d`

## Attempt 6｜20260921T095104Z

- Gate: `wi_prep_package_build`
- Command: `python3 scripts/onto1_review_package_build.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_prep_package_build-20260921T095104Z.log`
- SHA256: `8372852599af564028f5e9a85e9dbcb546198faef520b243575178a5f20dda65`

## Attempt 6｜20260921T095104Z

- Gate: `wi_prep_package_build_selftest`
- Command: `python3 scripts/onto1_review_package_build.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_prep_package_build_selftest-20260921T095104Z.log`
- SHA256: `bbb0909b7b4e5658b1112d5119462c1d8375d3191716dca8e1a76fbb68334455`

## Attempt 4｜20260921T102852Z

- Gate: `wi_construction_plan`
- Command: `python3 scripts/onto1_construction_plan.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_construction_plan-20260921T102852Z.log`
- SHA256: `dce110a3d4f3eefb0d4bb126dbd4dc3bb6477684d558f20fb0cdb3506f88d229`

## Attempt 4｜20260921T102852Z

- Gate: `wi_construction_plan_selftest`
- Command: `python3 scripts/onto1_construction_plan.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_construction_plan_selftest-20260921T102852Z.log`
- SHA256: `fb0e5070d5750e59a40e6cfa44a32137ff0140d818606a9728d526937bd6b393`

## Attempt 7｜20260921T102858Z

- Gate: `wi_prep_package_build`
- Command: `python3 scripts/onto1_review_package_build.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_prep_package_build-20260921T102858Z.log`
- SHA256: `8372852599af564028f5e9a85e9dbcb546198faef520b243575178a5f20dda65`

## Attempt 7｜20260921T102858Z

- Gate: `wi_prep_package_build_selftest`
- Command: `python3 scripts/onto1_review_package_build.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_prep_package_build_selftest-20260921T102858Z.log`
- SHA256: `bbb0909b7b4e5658b1112d5119462c1d8375d3191716dca8e1a76fbb68334455`

## Attempt 8｜20260921T102927Z

- Gate: `wi_prep_package_build`
- Command: `python3 scripts/onto1_review_package_build.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_prep_package_build-20260921T102927Z.log`
- SHA256: `8372852599af564028f5e9a85e9dbcb546198faef520b243575178a5f20dda65`

## Attempt 8｜20260921T102927Z

- Gate: `wi_prep_package_build_selftest`
- Command: `python3 scripts/onto1_review_package_build.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_prep_package_build_selftest-20260921T102927Z.log`
- SHA256: `bbb0909b7b4e5658b1112d5119462c1d8375d3191716dca8e1a76fbb68334455`

## Attempt 1｜20260921T120644Z

- Gate: `wi_c2_consumer_scan`
- Command: `python3 scripts/onto1_c2_consumer_scan.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_c2_consumer_scan-20260921T120644Z.log`
- SHA256: `10ea92a6411aaa2de87e253c9791a0b1ecd60b6ff89d80b23f72474e94449396`

## Attempt 1｜20260921T120647Z

- Gate: `wi_c2_consumer_scan_selftest`
- Command: `python3 scripts/onto1_c2_consumer_scan.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_c2_consumer_scan_selftest-20260921T120647Z.log`
- SHA256: `e2c8c9f90252e43a22f80ea052a14dca745f96110be364a258d0456c1f807550`

## Attempt 1｜20260921T133207Z

- Gate: `wi_a2_disposition`
- Command: `python3 scripts/onto1_disposition_ledger.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a2_disposition-20260921T133207Z.log`
- SHA256: `78334525651ad9389ae8f8489604c3e5e5e77ed4766165f48ac50e761de27fa7`

## Attempt 1｜20260921T133207Z

- Gate: `wi_a2_disposition_selftest`
- Command: `python3 scripts/onto1_disposition_ledger.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a2_disposition_selftest-20260921T133207Z.log`
- SHA256: `f15f0a8942ef64cc4043c1f1ed89363b4a339c19dc4d2b47dda25ef23bc4792c`

## Attempt 1｜20260921T133409Z

- Gate: `wi_a3_closeout`
- Command: `python3 scripts/onto1_a3_closeout.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a3_closeout-20260921T133409Z.log`
- SHA256: `50f026b0855ce96a36249b9315599450bb3e28c7eaf2e2410db2c40ecd2b499a`

## Attempt 1｜20260921T133415Z

- Gate: `wi_a3_closeout_selftest`
- Command: `python3 scripts/onto1_a3_closeout.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a3_closeout_selftest-20260921T133415Z.log`
- SHA256: `f5209db340e7f9ec4705b1c0e959043b52699a2c242184f343b6b5fabce007f7`

## Attempt 5｜20260921T133420Z

- Gate: `wi_a4_namespace_collision_selftest`
- Command: `python3 scripts/onto1_gate_log.py scripts/onto1_namespace_collision_check.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a4_namespace_collision_selftest-20260921T133420Z.log`
- SHA256: `995151668bb0b7be7d74fa841580d20d91c5e4abc0f4c954a94d227473200ded`

## Attempt 7｜20260921T133421Z

- Gate: `wi_a3_reference_alignment_selftest`
- Command: `python3 scripts/onto1_gate_log.py scripts/onto1_reference_alignment_check.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a3_reference_alignment_selftest-20260921T133421Z.log`
- SHA256: `4fcd2c412e8ed095dfb81e74b5a6ea40ab39e28858d73dc235e914e9873b1d4d`

## Attempt 3｜20260921T133421Z

- Gate: `wi_d2_relation_resolution`
- Command: `python3 scripts/onto1_product_relation_resolution.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_d2_relation_resolution-20260921T133421Z.log`
- SHA256: `d200dbbf5de6f9edc8d33edff26d25b780d01ab2197071b05e6ca3bf06de9c09`

## Attempt 3｜20260921T133421Z

- Gate: `wi_d2_relation_resolution_selftest`
- Command: `python3 scripts/onto1_product_relation_resolution.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_d2_relation_resolution_selftest-20260921T133421Z.log`
- SHA256: `a3a17198b3bb897657729c883e1b5ad7cf5eee5f833071f0a77ac8f07c3dc13e`

## Revision epoch 1｜A-2/C7 冻结复交：脚本集新增 3 个仪器（onto1_disposition_ledger / onto1_a3_closeout / onto1_signature_verify）⇒ fileset_sha256 变更，登记日志须与新 revision 一致｜2026-09-21T13:34:58.221076+00:00
- 依 **D-15**：预算按 revision 纪元计数（修复尝试与 revision 重记口径分离）。

## Attempt 2｜20260921T133458Z

- Gate: `wi_a3_reference_alignment`
- Revision epoch: 1
- Command: `python3 scripts/onto1_gate_log.py scripts/onto1_reference_alignment_check.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a3_reference_alignment-20260921T133458Z.log`
- SHA256: `3659812aa3849a580f1e3b79b3ca7022fe5598f188e071e8c1ab5b883dc844e0`

## Attempt 2｜20260921T133631Z

- Gate: `wi_a4_sim_migration_verify`
- Revision epoch: 1
- Command: `python3 scripts/onto1_sim_migration_verify.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a4_sim_migration_verify-20260921T133631Z.log`
- SHA256: `3de3b85a95b83549fb660767e10ef4de42ed8667ab1ca4da8054b6012a939f35`

## Attempt 2｜20260921T133631Z

- Gate: `wi_a4_sim_migration_verify_selftest`
- Revision epoch: 1
- Command: `python3 scripts/onto1_sim_migration_verify.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a4_sim_migration_verify_selftest-20260921T133631Z.log`
- SHA256: `dc20047e1ff7485369176304e9a96c792c17c9bc89236816e12891cb02e17539`

## Attempt 2｜20260921T133631Z

- Gate: `wi_a5_l3_load_fixture`
- Revision epoch: 1
- Command: `python3 scripts/onto1_l3_load_fixture.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a5_l3_load_fixture-20260921T133631Z.log`
- SHA256: `5fa469a4dc3d8ca995c6b1b4e172101e95f0edb19d48b817ce212ebb9eeb8e3b`

## Attempt 2｜20260921T133631Z

- Gate: `wi_a5_l3_load_fixture_selftest`
- Revision epoch: 1
- Command: `python3 scripts/onto1_l3_load_fixture.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a5_l3_load_fixture_selftest-20260921T133631Z.log`
- SHA256: `11008ae01f0b6165dc88cc1c42b2c4b69c567dcc5a4413701878821407588e0e`

## Attempt 2｜20260921T133631Z

- Gate: `wi_a5_l2_patch_plan`
- Revision epoch: 1
- Command: `python3 scripts/onto1_l3_load_fixture.py --plan-gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a5_l2_patch_plan-20260921T133631Z.log`
- SHA256: `c95e14e27ef7738a6e4a65c8f44e671e127c204cfef4274ff29a2fff1b5175c9`

## Attempt 2｜20260921T133632Z

- Gate: `wi_a7_signature_verify`
- Revision epoch: 1
- Command: `python3 scripts/onto1_signature_verify.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a7_signature_verify-20260921T133632Z.log`
- SHA256: `0701550675d952a6221dd16562dba8ef3b5714ba0295aed25ae12ab528085de9`

## Attempt 2｜20260921T133632Z

- Gate: `wi_a7_signature_verify_selftest`
- Revision epoch: 1
- Command: `python3 scripts/onto1_signature_verify.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a7_signature_verify_selftest-20260921T133632Z.log`
- SHA256: `3b366232f682511171c9c527a0d5d7ed641b333da881c8b0917771c381b35fc2`

## Attempt 2｜20260921T135302Z

- Gate: `wi_a2_disposition`
- Revision epoch: 1
- Command: `python3 scripts/onto1_disposition_ledger.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a2_disposition-20260921T135302Z.log`
- SHA256: `d3637f1af4aab13ee5bb32e65d5e66d4dd69fad84bb2e9f14c97dd2624770d07`

## Attempt 2｜20260921T135303Z

- Gate: `wi_a2_disposition_selftest`
- Revision epoch: 1
- Command: `python3 scripts/onto1_disposition_ledger.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a2_disposition_selftest-20260921T135303Z.log`
- SHA256: `f15f0a8942ef64cc4043c1f1ed89363b4a339c19dc4d2b47dda25ef23bc4792c`

## Attempt 2｜20260921T135304Z

- Gate: `wi_a3_closeout`
- Revision epoch: 1
- Command: `python3 scripts/onto1_a3_closeout.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a3_closeout-20260921T135304Z.log`
- SHA256: `3fcda21d369ec2fc8e641bd53af43e0be634b2487e8a664273e441209588306d`

## Attempt 2｜20260921T135309Z

- Gate: `wi_a3_closeout_selftest`
- Revision epoch: 1
- Command: `python3 scripts/onto1_a3_closeout.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a3_closeout_selftest-20260921T135309Z.log`
- SHA256: `f5209db340e7f9ec4705b1c0e959043b52699a2c242184f343b6b5fabce007f7`

## Attempt 3｜20260921T135313Z

- Gate: `wi_a4_sim_migration_verify`
- Revision epoch: 1
- Command: `python3 scripts/onto1_sim_migration_verify.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a4_sim_migration_verify-20260921T135313Z.log`
- SHA256: `18a368e60ad9131fa737e9600063539d162aeadc0dcd729c5cf2f718a0a46ca9`

## Attempt 3｜20260921T135314Z

- Gate: `wi_a4_sim_migration_verify_selftest`
- Revision epoch: 1
- Command: `python3 scripts/onto1_sim_migration_verify.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a4_sim_migration_verify_selftest-20260921T135314Z.log`
- SHA256: `0a3217b2300357f2e36e9ee06d3e4f9e6c45926361b32bd254067a940523379e`

## Attempt 3｜20260921T135314Z

- Gate: `wi_a5_l3_load_fixture`
- Revision epoch: 1
- Command: `python3 scripts/onto1_l3_load_fixture.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a5_l3_load_fixture-20260921T135314Z.log`
- SHA256: `bef34c40f5d7e63d3b0bb0d1f4af6fef160db9e5daf1b83b34553e184e1e0c5e`

## Attempt 3｜20260921T135314Z

- Gate: `wi_a5_l3_load_fixture_selftest`
- Revision epoch: 1
- Command: `python3 scripts/onto1_l3_load_fixture.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a5_l3_load_fixture_selftest-20260921T135314Z.log`
- SHA256: `a1528bd75df088f7b8dd3f5c5c07db5f98b5de1ba21aff1555fdcac73bfa53f8`

## Attempt 3｜20260921T135314Z

- Gate: `wi_a5_l2_patch_plan`
- Revision epoch: 1
- Command: `python3 scripts/onto1_l3_load_fixture.py --plan-gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a5_l2_patch_plan-20260921T135314Z.log`
- SHA256: `6a690da296e4c1d955d7744b6f9aedea58b72d5f3bb09f1f3f189493ca99b759`

## Attempt 3｜20260921T135314Z

- Gate: `wi_a7_signature_verify`
- Revision epoch: 1
- Command: `python3 scripts/onto1_signature_verify.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a7_signature_verify-20260921T135314Z.log`
- SHA256: `0701550675d952a6221dd16562dba8ef3b5714ba0295aed25ae12ab528085de9`

## Attempt 3｜20260921T135314Z

- Gate: `wi_a7_signature_verify_selftest`
- Revision epoch: 1
- Command: `python3 scripts/onto1_signature_verify.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a7_signature_verify_selftest-20260921T135314Z.log`
- SHA256: `3b366232f682511171c9c527a0d5d7ed641b333da881c8b0917771c381b35fc2`

## Attempt 2｜20260921T135314Z

- Gate: `wi_d2_relation_resolution`
- Revision epoch: 1
- Command: `python3 scripts/onto1_product_relation_resolution.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_d2_relation_resolution-20260921T135314Z.log`
- SHA256: `8e1a1afb0424fc77a06c23add0595c8f0c9bea143495ad77fe97f6cbbb61fc21`

## Attempt 2｜20260921T135314Z

- Gate: `wi_d2_relation_resolution_selftest`
- Revision epoch: 1
- Command: `python3 scripts/onto1_product_relation_resolution.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_d2_relation_resolution_selftest-20260921T135314Z.log`
- SHA256: `a3a17198b3bb897657729c883e1b5ad7cf5eee5f833071f0a77ac8f07c3dc13e`

## Attempt 2｜20260921T135315Z

- Gate: `wi_c2_consumer_scan`
- Revision epoch: 1
- Command: `python3 scripts/onto1_c2_consumer_scan.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_c2_consumer_scan-20260921T135315Z.log`
- SHA256: `435d650504949a10f82775171d9498c009cde65709e4885958b7640b04d851c4`

## Attempt 2｜20260921T135318Z

- Gate: `wi_c2_consumer_scan_selftest`
- Revision epoch: 1
- Command: `python3 scripts/onto1_c2_consumer_scan.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_c2_consumer_scan_selftest-20260921T135318Z.log`
- SHA256: `e2c8c9f90252e43a22f80ea052a14dca745f96110be364a258d0456c1f807550`

## Attempt 2｜20260921T140018Z

- Gate: `wi_a8_sim_rehearsal`
- Revision epoch: 1
- Command: `python3 scripts/onto1_sim_rehearsal.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a8_sim_rehearsal-20260921T140018Z.log`
- SHA256: `79edf8fca4e84bb79478efd05bebba304976c7e9be5f60facd057f407909c936`

## Attempt 2｜20260921T140019Z

- Gate: `wi_a8_sim_rehearsal_selftest`
- Revision epoch: 1
- Command: `python3 scripts/onto1_sim_rehearsal.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a8_sim_rehearsal_selftest-20260921T140019Z.log`
- SHA256: `f3b280622d84dff241e67fcb6b2fac788e2c639d7c96830bf038bca1fcd1e3ae`

## Attempt 2｜20260921T140843Z

- Gate: `wi_a8_sim_rehearsal_full`
- Revision epoch: 1
- Command: `python3 scripts/onto1_sim_rehearsal_full.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a8_sim_rehearsal_full-20260921T140843Z.log`
- SHA256: `8aabf26f6609c83a42a4e5ab37abc78bf37675bcaef8579b02555c2f5d627c94`

## Attempt 2｜20260921T140843Z

- Gate: `wi_a8_sim_rehearsal_full_selftest`
- Revision epoch: 1
- Command: `python3 scripts/onto1_sim_rehearsal_full.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a8_sim_rehearsal_full_selftest-20260921T140843Z.log`
- SHA256: `6e5ad4a737b02dcc66e248fac0e9310c3ffb72967e3bb6be468c9af0521861a6`

## Attempt 2｜20260921T140844Z

- Gate: `wi_a9_l1_candidate`
- Revision epoch: 1
- Command: `python3 scripts/onto1_l1_candidate_model.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a9_l1_candidate-20260921T140844Z.log`
- SHA256: `b584acb59bd745682ed0aeb62773f0d0e436b0c37342ad82f919e31a28922c5d`

## Attempt 2｜20260921T140844Z

- Gate: `wi_a9_l1_candidate_selftest`
- Revision epoch: 1
- Command: `python3 scripts/onto1_l1_candidate_model.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a9_l1_candidate_selftest-20260921T140844Z.log`
- SHA256: `c6f996b3d107366fa9b1a66c289d23e8657a3e3b9b29e4a38146eed632f5149e`

## Attempt 2｜20260921T140844Z

- Gate: `wi_a10_breakpoint_advisory`
- Revision epoch: 1
- Command: `python3 scripts/onto1_breakpoint_advisories.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a10_breakpoint_advisory-20260921T140844Z.log`
- SHA256: `a9c05c06f7101669b28871f13e2ad90bffce9eb24bc5208620ced252b5aa20fb`

## Attempt 2｜20260921T140844Z

- Gate: `wi_a10_breakpoint_advisory_selftest`
- Revision epoch: 1
- Command: `python3 scripts/onto1_breakpoint_advisories.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a10_breakpoint_advisory_selftest-20260921T140844Z.log`
- SHA256: `e8e3b3d7d789df70ea8e88c46af997f7088818c022d83f79fa6443f9d5381b93`

## Attempt 2｜20260921T142825Z

- Gate: `wi_a11_sim_rehearsal_sim4`
- Revision epoch: 1
- Command: `python3 scripts/onto1_sim_rehearsal_multibatch.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a11_sim_rehearsal_sim4-20260921T142825Z.log`
- SHA256: `51cf5cc550fa90c923874a2c3a712b4aae9b0e7ca58bdb4c5a763ec49944ea2c`

## Attempt 2｜20260921T142826Z

- Gate: `wi_a11_sim_rehearsal_sim4_selftest`
- Revision epoch: 1
- Command: `python3 scripts/onto1_sim_rehearsal_multibatch.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a11_sim_rehearsal_sim4_selftest-20260921T142826Z.log`
- SHA256: `f365b21a65a866fe518838f9138658c3f72072b9eb81672ffeabae537e99bd6a`

## Attempt 2｜20260921T142826Z

- Gate: `wi_a12_breakpoint_option_rehearsal`
- Revision epoch: 1
- Command: `python3 scripts/onto1_breakpoint_option_rehearsal.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a12_breakpoint_option_rehearsal-20260921T142826Z.log`
- SHA256: `184c610be9c5ab931f90b0483974811350cf233eb55860ffdf53616046201d41`

## Attempt 2｜20260921T142826Z

- Gate: `wi_a12_breakpoint_option_rehearsal_selftest`
- Revision epoch: 1
- Command: `python3 scripts/onto1_breakpoint_option_rehearsal.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a12_breakpoint_option_rehearsal_selftest-20260921T142826Z.log`
- SHA256: `c4589cb89058186de5e3ba30ec820671e91622cc996b2e454c86e71adffb55e9`

## Attempt 2｜20260921T142826Z

- Gate: `wi_a13_migration_runner`
- Revision epoch: 1
- Command: `python3 scripts/onto1_migration_runner.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a13_migration_runner-20260921T142826Z.log`
- SHA256: `32eae64fcea6e2e4b1584db01f12d295a8f0576ea8ca73b30af6dbe07f41fab8`

## Attempt 2｜20260921T142826Z

- Gate: `wi_a13_migration_runner_selftest`
- Revision epoch: 1
- Command: `python3 scripts/onto1_migration_runner.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a13_migration_runner_selftest-20260921T142826Z.log`
- SHA256: `f006c0fec728d3da7bc49f95e479ee1d979b372bd8ed652cc154a3d82cb6f622`

## Attempt 2｜20260921T143747Z

- Gate: `wi_a14_migration_worklist`
- Revision epoch: 1
- Command: `python3 scripts/onto1_migration_worklist.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a14_migration_worklist-20260921T143747Z.log`
- SHA256: `d7eae2229dd824d30277c29d86931b2567db0f74a94e7fb8599286e9e5e1081b`

## Attempt 2｜20260921T143747Z

- Gate: `wi_a14_migration_worklist_selftest`
- Revision epoch: 1
- Command: `python3 scripts/onto1_migration_worklist.py --selftest`
- Exit: `2`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a14_migration_worklist_selftest-20260921T143747Z.log`
- SHA256: `2afc0d96f1bba1135b0372e06fdf33a1710196af65a9d97720cd55f884b5eb15`

## Attempt 2｜20260921T143748Z

- Gate: `wi_a15_breakpoint_execution_pack`
- Revision epoch: 1
- Command: `python3 scripts/onto1_breakpoint_execution_pack.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a15_breakpoint_execution_pack-20260921T143748Z.log`
- SHA256: `a55a2fb761e637df98d85bcdbd62c27d9d45e7a3e2ee369f142f9a6e0acc4286`

## Attempt 2｜20260921T143748Z

- Gate: `wi_a15_breakpoint_execution_pack_selftest`
- Revision epoch: 1
- Command: `python3 scripts/onto1_breakpoint_execution_pack.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a15_breakpoint_execution_pack_selftest-20260921T143748Z.log`
- SHA256: `536a88694094e8f436f3424b6d91506121d8351939829e7d2e083e6aa51da85c`

## Attempt 2｜20260921T143748Z

- Gate: `wi_a16_kert_registration_request`
- Revision epoch: 1
- Command: `python3 scripts/onto1_kert_registration_request.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a16_kert_registration_request-20260921T143748Z.log`
- SHA256: `e11bf0b808b6a60fe1246f320daa02c36ff86468836a3d565d5f55dc3d0494d6`

## Attempt 2｜20260921T143748Z

- Gate: `wi_a16_kert_registration_request_selftest`
- Revision epoch: 1
- Command: `python3 scripts/onto1_kert_registration_request.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a16_kert_registration_request_selftest-20260921T143748Z.log`
- SHA256: `3f79752b6a904126a96d75c3757f328c53522323898bad694efd8e6b1abb1a01`

## Attempt 3｜20260921T143804Z

- Gate: `wi_a14_migration_worklist_selftest`
- Revision epoch: 1
- Command: `python3 scripts/onto1_migration_worklist.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a14_migration_worklist_selftest-20260921T143804Z.log`
- SHA256: `6e088bf3bcaa942189dcaa19a2be59721b85e4faf4fa0f57d9caec4b835689ec`

## Attempt 2｜20260921T145032Z

- Gate: `wi_a17_scenario_readiness`
- Revision epoch: 1
- Command: `python3 scripts/onto1_scenario_readiness.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a17_scenario_readiness-20260921T145032Z.log`
- SHA256: `5b5f68283537f3a69bbb72090050035ec4cf03435bad0b05a99d765aedaf8062`

## Attempt 2｜20260921T145100Z

- Gate: `wi_a17_scenario_readiness_selftest`
- Revision epoch: 1
- Command: `python3 scripts/onto1_scenario_readiness.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a17_scenario_readiness_selftest-20260921T145100Z.log`
- SHA256: `7cf63004d402bcd3a63c9416fe84746c0d6f4763bc16f93513edbcbe06ec1179`

## Attempt 3｜20260921T151756Z

- Gate: `wi_c2_consumer_scan`
- Revision epoch: 1
- Command: `python3 scripts/onto1_c2_consumer_scan.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_c2_consumer_scan-20260921T151756Z.log`
- SHA256: `435d650504949a10f82775171d9498c009cde65709e4885958b7640b04d851c4`

## Attempt 3｜20260921T151800Z

- Gate: `wi_c2_consumer_scan_selftest`
- Revision epoch: 1
- Command: `python3 scripts/onto1_c2_consumer_scan.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_c2_consumer_scan_selftest-20260921T151800Z.log`
- SHA256: `e2c8c9f90252e43a22f80ea052a14dca745f96110be364a258d0456c1f807550`

## Attempt 2｜20260921T151802Z

- Gate: `wi_construction_plan`
- Revision epoch: 1
- Command: `python3 scripts/onto1_construction_plan.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_construction_plan-20260921T151802Z.log`
- SHA256: `15d6dd34180b0d0a6c3769d894da7a3a2f39c83579af791eac70a458669d2dac`

## Attempt 2｜20260921T151802Z

- Gate: `wi_construction_plan_selftest`
- Revision epoch: 1
- Command: `python3 scripts/onto1_construction_plan.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_construction_plan_selftest-20260921T151802Z.log`
- SHA256: `fb0e5070d5750e59a40e6cfa44a32137ff0140d818606a9728d526937bd6b393`

## Attempt 3｜20260921T151802Z

- Gate: `wi_a13_migration_runner`
- Revision epoch: 1
- Command: `python3 scripts/onto1_migration_runner.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a13_migration_runner-20260921T151802Z.log`
- SHA256: `720c9ff5559b3e2948a5f2836df455d5417640e416c13b51132cefe6e3693e21`

## Attempt 3｜20260921T151802Z

- Gate: `wi_a13_migration_runner_selftest`
- Revision epoch: 1
- Command: `python3 scripts/onto1_migration_runner.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a13_migration_runner_selftest-20260921T151802Z.log`
- SHA256: `f006c0fec728d3da7bc49f95e479ee1d979b372bd8ed652cc154a3d82cb6f622`

## Attempt 3｜20260921T151808Z

- Gate: `wi_a16_kert_registration_request`
- Revision epoch: 1
- Command: `python3 scripts/onto1_kert_registration_request.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a16_kert_registration_request-20260921T151808Z.log`
- SHA256: `7798c6b4a410a919e0a4fca4e8f5ecb2c4fec9597ff49721d3cd5047a30ffd5d`

## Attempt 3｜20260921T151808Z

- Gate: `wi_a16_kert_registration_request_selftest`
- Revision epoch: 1
- Command: `python3 scripts/onto1_kert_registration_request.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a16_kert_registration_request_selftest-20260921T151808Z.log`
- SHA256: `3f79752b6a904126a96d75c3757f328c53522323898bad694efd8e6b1abb1a01`

## Attempt 3｜20260921T152931Z

- Gate: `wi_a15_breakpoint_execution_pack`
- Revision epoch: 1
- Command: `python3 scripts/onto1_breakpoint_execution_pack.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a15_breakpoint_execution_pack-20260921T152931Z.log`
- SHA256: `a55a2fb761e637df98d85bcdbd62c27d9d45e7a3e2ee369f142f9a6e0acc4286`

## Attempt 3｜20260921T152931Z

- Gate: `wi_a15_breakpoint_execution_pack_selftest`
- Revision epoch: 1
- Command: `python3 scripts/onto1_breakpoint_execution_pack.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a15_breakpoint_execution_pack_selftest-20260921T152931Z.log`
- SHA256: `536a88694094e8f436f3424b6d91506121d8351939829e7d2e083e6aa51da85c`

## Attempt 3｜20260921T155409Z

- Gate: `wi_a2_disposition`
- Revision epoch: 1
- Command: `python3 scripts/onto1_disposition_ledger.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a2_disposition-20260921T155409Z.log`
- SHA256: `e0552f1c0867f2ff6ec45d7746086d2c45ed17058904707c4b637745017b7092`

## Attempt 3｜20260921T155410Z

- Gate: `wi_a2_disposition_selftest`
- Revision epoch: 1
- Command: `python3 scripts/onto1_disposition_ledger.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a2_disposition_selftest-20260921T155410Z.log`
- SHA256: `26bb6e192fd03143a0bc9c0ff822dc3e742d726e831d8e33e1937ebf5d9811a7`

## Attempt 2｜20260921T155415Z

- Gate: `wi_log_hygiene`
- Revision epoch: 1
- Command: `python3 scripts/onto1_log_hygiene.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_log_hygiene-20260921T155415Z.log`
- SHA256: `390cdcf7cf17c339d2032b4d905f07fb59fcec866f14b96924b42c6fd2afd491`

## Attempt 2｜20260921T155415Z

- Gate: `wi_log_hygiene_selftest`
- Revision epoch: 1
- Command: `python3 scripts/onto1_log_hygiene.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_log_hygiene_selftest-20260921T155415Z.log`
- SHA256: `b30ead1ca0408c350616a814d5de14ebccd3a05d6422ff9a44b0e09069a36762`

## Attempt 4｜20260921T155415Z

- Gate: `wi_a13_migration_runner`
- Revision epoch: 1
- Command: `python3 scripts/onto1_migration_runner.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a13_migration_runner-20260921T155415Z.log`
- SHA256: `720c9ff5559b3e2948a5f2836df455d5417640e416c13b51132cefe6e3693e21`

## Attempt 4｜20260921T155415Z

- Gate: `wi_a13_migration_runner_selftest`
- Revision epoch: 1
- Command: `python3 scripts/onto1_migration_runner.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a13_migration_runner_selftest-20260921T155415Z.log`
- SHA256: `6e874ed64cbfa2dd8d89c7a5168a9f0e7d74dce0b644e54189228721f8306fad`

## Attempt 4｜20260921T155420Z

- Gate: `wi_a15_breakpoint_execution_pack`
- Revision epoch: 1
- Command: `python3 scripts/onto1_breakpoint_execution_pack.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a15_breakpoint_execution_pack-20260921T155420Z.log`
- SHA256: `5df26e223fa03080e709a9c129592ecc5aaf928282c95d4650a7668aa912af2e`

## Attempt 4｜20260921T155420Z

- Gate: `wi_a15_breakpoint_execution_pack_selftest`
- Revision epoch: 1
- Command: `python3 scripts/onto1_breakpoint_execution_pack.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a15_breakpoint_execution_pack_selftest-20260921T155420Z.log`
- SHA256: `536a88694094e8f436f3424b6d91506121d8351939829e7d2e083e6aa51da85c`

## Attempt 4｜20260921T155420Z

- Gate: `wi_a7_signature_verify`
- Revision epoch: 1
- Command: `python3 scripts/onto1_signature_verify.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a7_signature_verify-20260921T155420Z.log`
- SHA256: `0701550675d952a6221dd16562dba8ef3b5714ba0295aed25ae12ab528085de9`

## Attempt 4｜20260921T155421Z

- Gate: `wi_a7_signature_verify_selftest`
- Revision epoch: 1
- Command: `python3 scripts/onto1_signature_verify.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a7_signature_verify_selftest-20260921T155421Z.log`
- SHA256: `2e036dfafa04eb09e1ee53fcb582718fe8c2dc7e1f80bd5655f149e1a215125b`

## Attempt 2｜20260922T035137Z

- Gate: `wi_a5_d2_pack`
- Revision epoch: 1
- Command: `python3 scripts/onto1_d2_normalization_pack.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a5_d2_pack-20260922T035137Z.log`
- SHA256: `bc5c7cd3b73a5319b8e8b8f02e90c81100015deefd1729892eb3abff7484fb68`

## Attempt 2｜20260922T035137Z

- Gate: `wi_a5_d2_pack_selftest`
- Revision epoch: 1
- Command: `python3 scripts/onto1_d2_normalization_pack.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a5_d2_pack_selftest-20260922T035137Z.log`
- SHA256: `074be7be6779407a14b54627a73fdc395162ada1abd9d8896c4410c3c9ad63b3`

## Attempt 2｜20260922T035138Z

- Gate: `wi_a6_cq_fixtures`
- Revision epoch: 1
- Command: `python3 scripts/onto1_cq_fixtures.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a6_cq_fixtures-20260922T035138Z.log`
- SHA256: `6dd390a085b3b3ffd29ea55908afcfed12f27c355f93bb50bbe490c15618dc7e`

## Attempt 2｜20260922T035138Z

- Gate: `wi_a6_cq_fixtures_selftest`
- Revision epoch: 1
- Command: `python3 scripts/onto1_cq_fixtures.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a6_cq_fixtures_selftest-20260922T035138Z.log`
- SHA256: `7feffbfdc6fee3759a7979433355248901c0211a94a0f89d47904cc2f70d50c4`

## Attempt 2｜20260922T035138Z

- Gate: `wi_d2_sim_projection`
- Revision epoch: 1
- Command: `python3 scripts/onto1_sim_projection.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_d2_sim_projection-20260922T035138Z.log`
- SHA256: `ec49ef7a30f99ef27e25e7d4670a309c7dce91710f6b64716d9a24e92677831c`

## Attempt 2｜20260922T035138Z

- Gate: `wi_d2_sim_projection_selftest`
- Revision epoch: 1
- Command: `python3 scripts/onto1_sim_projection.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_d2_sim_projection_selftest-20260922T035138Z.log`
- SHA256: `ee8799b0247e0d2e784d7f4a4d75b62ca5cc06363111dc8b87592c81b2eb8ce0`

## Attempt 3｜20260922T060456Z

- Gate: `wi_d2_relation_resolution`
- Revision epoch: 1
- Command: `python3 scripts/onto1_product_relation_resolution.py --gate`
- Exit: `2`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_d2_relation_resolution-20260922T060456Z.log`
- SHA256: `2e6b77dfa8da48ce90382a242671a6a64ba4f634b155ad74e904708570370719`

## Attempt 4｜20260922T060456Z

- Gate: `wi_d2_relation_resolution`
- Revision epoch: 1
- Command: `python3 scripts/onto1_product_relation_resolution.py --gate`
- Exit: `2`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_d2_relation_resolution-20260922T060456Z.log`
- SHA256: `2e6b77dfa8da48ce90382a242671a6a64ba4f634b155ad74e904708570370719`

## Attempt 3｜20260922T060456Z

- Gate: `wi_d2_relation_resolution_selftest`
- Revision epoch: 1
- Command: `python3 scripts/onto1_product_relation_resolution.py --selftest`
- Exit: `2`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_d2_relation_resolution_selftest-20260922T060456Z.log`
- SHA256: `5fbacbd90f05bf2e0b6ac1379ca976fb7559ba4d1149333caba559e1b2c6489d`

## Attempt 4｜20260922T060456Z

- Gate: `wi_d2_relation_resolution_selftest`
- Revision epoch: 1
- Command: `python3 scripts/onto1_product_relation_resolution.py --selftest`
- Exit: `2`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_d2_relation_resolution_selftest-20260922T060456Z.log`
- SHA256: `5fbacbd90f05bf2e0b6ac1379ca976fb7559ba4d1149333caba559e1b2c6489d`

## Attempt 3｜20260922T060457Z

- Gate: `wi_a3_closeout`
- Revision epoch: 1
- Command: `python3 scripts/onto1_a3_closeout.py --gate`
- Exit: `2`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a3_closeout-20260922T060457Z.log`
- SHA256: `82b80ce1d33dec97c9633a2cacb996a15f2cb2566a138aa90f87fa6b97737b43`

## Attempt 4｜20260922T060502Z

- Gate: `wi_a3_closeout`
- Revision epoch: 1
- Command: `python3 scripts/onto1_a3_closeout.py --gate`
- Exit: `2`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a3_closeout-20260922T060502Z.log`
- SHA256: `82b80ce1d33dec97c9633a2cacb996a15f2cb2566a138aa90f87fa6b97737b43`

## Attempt 3｜20260922T060507Z

- Gate: `wi_a3_closeout_selftest`
- Revision epoch: 1
- Command: `python3 scripts/onto1_a3_closeout.py --selftest`
- Exit: `2`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a3_closeout_selftest-20260922T060507Z.log`
- SHA256: `62d473050837cf0f77539291f1634f789b4f27a01d82a1e767ea8f847111f65c`

## Attempt 4｜20260922T060513Z

- Gate: `wi_a3_closeout_selftest`
- Revision epoch: 1
- Command: `python3 scripts/onto1_a3_closeout.py --selftest`
- Exit: `2`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a3_closeout_selftest-20260922T060513Z.log`
- SHA256: `62d473050837cf0f77539291f1634f789b4f27a01d82a1e767ea8f847111f65c`

## Attempt 3｜20260922T060518Z

- Gate: `wi_d2_sim_projection`
- Revision epoch: 1
- Command: `python3 scripts/onto1_sim_projection.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_d2_sim_projection-20260922T060518Z.log`
- SHA256: `10c504170f5e1ea613af22d99c4e3ab058949d203cc39e2ea7d5e961ecd69579`

## Attempt 3｜20260922T060518Z

- Gate: `wi_d2_sim_projection_selftest`
- Revision epoch: 1
- Command: `python3 scripts/onto1_sim_projection.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_d2_sim_projection_selftest-20260922T060518Z.log`
- SHA256: `4d1b0f2845d74e4c407e07af67ca4df4c807eaa930c51e059adfbd1dec945223`

## Attempt 4｜20260922T060526Z

- Gate: `wi_a5_l3_load_fixture`
- Revision epoch: 1
- Command: `python3 scripts/onto1_l3_load_fixture.py --gate`
- Exit: `2`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a5_l3_load_fixture-20260922T060526Z.log`
- SHA256: `3506fe69c068f973aa57cbfc0edbba9185aca0262059e43772e302660e323f33`

## Attempt 4｜20260922T060526Z

- Gate: `wi_a5_l3_load_fixture_selftest`
- Revision epoch: 1
- Command: `python3 scripts/onto1_l3_load_fixture.py --selftest`
- Exit: `2`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a5_l3_load_fixture_selftest-20260922T060526Z.log`
- SHA256: `d14114fba93242affde9ffcc897551ba70546abfb1d8d05df227c1f2b53d1655`

## Attempt 4｜20260922T060526Z

- Gate: `wi_a5_l2_patch_plan`
- Revision epoch: 1
- Command: `python3 scripts/onto1_l3_load_fixture.py --plan-gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a5_l2_patch_plan-20260922T060526Z.log`
- SHA256: `6a690da296e4c1d955d7744b6f9aedea58b72d5f3bb09f1f3f189493ca99b759`

## Attempt 5｜20260922T060826Z

- Gate: `wi_a3_closeout`
- Revision epoch: 1
- Command: `python3 scripts/onto1_a3_closeout.py --gate`
- Exit: `2`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a3_closeout-20260922T060826Z.log`
- SHA256: `a1dbd87ba2f55fcd2126b9e57c0a52e5f17a4dc2250bef758d00533ab6718438`

## Attempt 6｜20260922T060832Z

- Gate: `wi_a3_closeout`
- Revision epoch: 1
- Command: `python3 scripts/onto1_a3_closeout.py --gate`
- Exit: `2`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a3_closeout-20260922T060832Z.log`
- SHA256: `a1dbd87ba2f55fcd2126b9e57c0a52e5f17a4dc2250bef758d00533ab6718438`

## Attempt 5｜20260922T060837Z

- Gate: `wi_a3_closeout_selftest`
- Revision epoch: 1
- Command: `python3 scripts/onto1_a3_closeout.py --selftest`
- Exit: `2`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a3_closeout_selftest-20260922T060837Z.log`
- SHA256: `62d473050837cf0f77539291f1634f789b4f27a01d82a1e767ea8f847111f65c`

## Attempt 6｜20260922T060842Z

- Gate: `wi_a3_closeout_selftest`
- Revision epoch: 1
- Command: `python3 scripts/onto1_a3_closeout.py --selftest`
- Exit: `2`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a3_closeout_selftest-20260922T060842Z.log`
- SHA256: `62d473050837cf0f77539291f1634f789b4f27a01d82a1e767ea8f847111f65c`

## Attempt 5｜20260922T060848Z

- Gate: `wi_a5_l3_load_fixture`
- Revision epoch: 1
- Command: `python3 scripts/onto1_l3_load_fixture.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a5_l3_load_fixture-20260922T060848Z.log`
- SHA256: `9a6a775e0afd15e441726f4c36f9993c1f751d087f9b14e56cffca7c89d4907c`

## Attempt 5｜20260922T060848Z

- Gate: `wi_a5_l3_load_fixture_selftest`
- Revision epoch: 1
- Command: `python3 scripts/onto1_l3_load_fixture.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a5_l3_load_fixture_selftest-20260922T060848Z.log`
- SHA256: `a1528bd75df088f7b8dd3f5c5c07db5f98b5de1ba21aff1555fdcac73bfa53f8`

## Attempt 3｜20260922T060848Z

- Gate: `wi_a5_d2_pack`
- Revision epoch: 1
- Command: `python3 scripts/onto1_d2_normalization_pack.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a5_d2_pack-20260922T060848Z.log`
- SHA256: `a420941120709f183a04e720c3b3daf809566e120fa17bd6334b682aaeb818aa`

## Attempt 3｜20260922T060848Z

- Gate: `wi_a5_d2_pack_selftest`
- Revision epoch: 1
- Command: `python3 scripts/onto1_d2_normalization_pack.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a5_d2_pack_selftest-20260922T060848Z.log`
- SHA256: `951eb2738a392a8fd5cf2eb08b5aad4bfc4eb34855c5ee476f2874278a89c7f4`

## Attempt 2｜20260922T060848Z

- Gate: `wi_a4_namespace_collision`
- Revision epoch: 1
- Command: `python3 scripts/onto1_gate_log.py scripts/onto1_namespace_collision_check.py --gate`
- Exit: `3`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a4_namespace_collision-20260922T060848Z.log`
- SHA256: `cd931a615216bc72e40df9a93d28f54a65d85ea3939bd0556eeb4b8c830ad9f4`

## Attempt 3｜20260922T060848Z

- Gate: `wi_a4_namespace_collision`
- Revision epoch: 1
- Command: `python3 scripts/onto1_gate_log.py scripts/onto1_namespace_collision_check.py --gate`
- Exit: `3`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a4_namespace_collision-20260922T060848Z.log`
- SHA256: `cd931a615216bc72e40df9a93d28f54a65d85ea3939bd0556eeb4b8c830ad9f4`

## Attempt 2｜20260922T060849Z

- Gate: `wi_a4_namespace_collision_selftest`
- Revision epoch: 1
- Command: `python3 scripts/onto1_gate_log.py scripts/onto1_namespace_collision_check.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a4_namespace_collision_selftest-20260922T060849Z.log`
- SHA256: `ff4358bf318c3029464368608792da265308221b044d92ae5c7f7b6735fa0908`

## Attempt 2｜20260922T060849Z

- Gate: `wi_a5_product_refs`
- Revision epoch: 1
- Command: `python3 scripts/onto1_product_refs_probe.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a5_product_refs-20260922T060849Z.log`
- SHA256: `90f575fbc25416ac6a911d48fd0ded2f0b286f5315f4fc8a9c38599f6d568bb1`

## Attempt 2｜20260922T060849Z

- Gate: `wi_a5_product_refs_selftest`
- Revision epoch: 1
- Command: `python3 scripts/onto1_product_refs_probe.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a5_product_refs_selftest-20260922T060849Z.log`
- SHA256: `718e48f9dbae91750c02a39b47a8736b4c5ac483b8ff38d5e3689ceb4ad6f3a0`

## Attempt 7｜20260922T060944Z

- Gate: `wi_a3_closeout`
- Revision epoch: 1
- Command: `python3 scripts/onto1_a3_closeout.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a3_closeout-20260922T060944Z.log`
- SHA256: `bfc70f890c336c8c38433d5087f84eacbf5d14646cba66764cb62ee6b4d2ac35`

## Attempt 7｜20260922T060949Z

- Gate: `wi_a3_closeout_selftest`
- Revision epoch: 1
- Command: `python3 scripts/onto1_a3_closeout.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a3_closeout_selftest-20260922T060949Z.log`
- SHA256: `f5209db340e7f9ec4705b1c0e959043b52699a2c242184f343b6b5fabce007f7`

## Attempt 4｜20260922T060955Z

- Gate: `wi_a4_namespace_collision`
- Revision epoch: 1
- Command: `python3 scripts/onto1_gate_log.py scripts/onto1_namespace_collision_check.py --gate`
- Exit: `3`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a4_namespace_collision-20260922T060955Z.log`
- SHA256: `cd931a615216bc72e40df9a93d28f54a65d85ea3939bd0556eeb4b8c830ad9f4`

## Attempt 5｜20260922T060955Z

- Gate: `wi_a4_namespace_collision`
- Revision epoch: 1
- Command: `python3 scripts/onto1_gate_log.py scripts/onto1_namespace_collision_check.py --gate`
- Exit: `3`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a4_namespace_collision-20260922T060955Z.log`
- SHA256: `cd931a615216bc72e40df9a93d28f54a65d85ea3939bd0556eeb4b8c830ad9f4`

## Attempt 3｜20260922T060955Z

- Gate: `wi_a4_namespace_collision_selftest`
- Revision epoch: 1
- Command: `python3 scripts/onto1_gate_log.py scripts/onto1_namespace_collision_check.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a4_namespace_collision_selftest-20260922T060955Z.log`
- SHA256: `ff4358bf318c3029464368608792da265308221b044d92ae5c7f7b6735fa0908`

## Attempt 4｜20260922T062208Z

- Gate: `wi_a2_disposition`
- Revision epoch: 1
- Command: `python3 scripts/onto1_gate_log.py scripts/onto1_disposition_ledger.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a2_disposition-20260922T062208Z.log`
- SHA256: `e3f61f8031228ddbd401064dd2fa7ac5cc25942bf9b15469e790f7466dc6c0b0`

## Attempt 4｜20260922T062209Z

- Gate: `wi_a2_disposition_selftest`
- Revision epoch: 1
- Command: `python3 scripts/onto1_gate_log.py scripts/onto1_disposition_ledger.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a2_disposition_selftest-20260922T062209Z.log`
- SHA256: `a4ce7e8c1fd479bccab8f2d8f300c9e3674b275b096bd9224d5fde89eb2c0aa8`

## Attempt 4｜20260922T062214Z

- Gate: `wi_a5_d2_pack`
- Revision epoch: 1
- Command: `python3 scripts/onto1_gate_log.py scripts/onto1_d2_normalization_pack.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a5_d2_pack-20260922T062214Z.log`
- SHA256: `36619fdfce0746d0b4e1b1e8eb88e1612b523aedf7c7aa9df29518b7a614c6c3`

## Attempt 4｜20260922T062214Z

- Gate: `wi_a5_d2_pack_selftest`
- Revision epoch: 1
- Command: `python3 scripts/onto1_gate_log.py scripts/onto1_d2_normalization_pack.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a5_d2_pack_selftest-20260922T062214Z.log`
- SHA256: `880e27dd68c82950d09d19d12fb05525dfbb3493b0bafed42898e95be7dc9e86`

## Attempt 6｜20260922T062214Z

- Gate: `wi_a5_l3_load_fixture`
- Revision epoch: 1
- Command: `python3 scripts/onto1_gate_log.py scripts/onto1_l3_load_fixture.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a5_l3_load_fixture-20260922T062214Z.log`
- SHA256: `e9ab81fa421b93a39248941dcfd7079dd82f1cd682c5685f9e05a37da949e373`

## Attempt 6｜20260922T062214Z

- Gate: `wi_a5_l3_load_fixture_selftest`
- Revision epoch: 1
- Command: `python3 scripts/onto1_gate_log.py scripts/onto1_l3_load_fixture.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a5_l3_load_fixture_selftest-20260922T062214Z.log`
- SHA256: `0d06c4136ad4cff3b1a3aa99c2fca06a6e1661effe0d92fb2decb2315909b125`

## Attempt 8｜20260922T062215Z

- Gate: `wi_a3_closeout`
- Revision epoch: 1
- Command: `python3 scripts/onto1_gate_log.py scripts/onto1_a3_closeout.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a3_closeout-20260922T062215Z.log`
- SHA256: `f931def6299afd0f221819ffbd4896fd72b5bf3ff6bb8ed24f4e2a3506b53d96`

## Attempt 8｜20260922T062220Z

- Gate: `wi_a3_closeout_selftest`
- Revision epoch: 1
- Command: `python3 scripts/onto1_gate_log.py scripts/onto1_a3_closeout.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a3_closeout_selftest-20260922T062220Z.log`
- SHA256: `7b27c7e609f17edd1f7edbfe840056059bbc5b03fd22fe566f4eefe095182b89`

## Attempt 3｜20260922T062225Z

- Gate: `wi_a6_cq_fixtures`
- Revision epoch: 1
- Command: `python3 scripts/onto1_gate_log.py scripts/onto1_cq_fixtures.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a6_cq_fixtures-20260922T062225Z.log`
- SHA256: `c0f4da3ae750a071b844ebeb4255ccd601de5763f1751f284a3db0bc3f7e4360`

## Attempt 3｜20260922T062225Z

- Gate: `wi_a6_cq_fixtures_selftest`
- Revision epoch: 1
- Command: `python3 scripts/onto1_gate_log.py scripts/onto1_cq_fixtures.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a6_cq_fixtures_selftest-20260922T062225Z.log`
- SHA256: `200d4d1c59e8b2a40793a014d95068d8f698398f33e0a95a1730241283ddc052`

## Attempt 4｜20260922T062226Z

- Gate: `wi_d2_sim_projection`
- Revision epoch: 1
- Command: `python3 scripts/onto1_gate_log.py scripts/onto1_sim_projection.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_d2_sim_projection-20260922T062226Z.log`
- SHA256: `ca59df912a5511f5cb1c13c3658e719e14261f18b5479addb0ace5b1b3c3ecdf`

## Attempt 4｜20260922T062226Z

- Gate: `wi_d2_sim_projection_selftest`
- Revision epoch: 1
- Command: `python3 scripts/onto1_gate_log.py scripts/onto1_sim_projection.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_d2_sim_projection_selftest-20260922T062226Z.log`
- SHA256: `7b05d562574ebbba7138a734e7ab6dffffff942fb1acab410ea2b7f6aaeb49cf`

## Attempt 3｜20260922T062226Z

- Gate: `wi_a5_product_refs`
- Revision epoch: 1
- Command: `python3 scripts/onto1_gate_log.py scripts/onto1_product_refs_probe.py --gate`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a5_product_refs-20260922T062226Z.log`
- SHA256: `ff38da171783d103594081173d0c87a27f02ce38a0627dd35e0c06e66e584e1e`

## Attempt 3｜20260922T062226Z

- Gate: `wi_a5_product_refs_selftest`
- Revision epoch: 1
- Command: `python3 scripts/onto1_gate_log.py scripts/onto1_product_refs_probe.py --selftest`
- Exit: `0`
- Evidence: `loops/ONTO1-ontology-split/evidence/wi_a5_product_refs_selftest-20260922T062226Z.log`
- SHA256: `5928c5ea5e8a18822733dbf2882bc65d5f6b9d1670afae6468da4576107c3b1b`
