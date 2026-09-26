# Wave 2/3 施工清单（由 A-11 演练结果固化）

- 条目 **462**：B8_内容级重绑（IRI/词表/哈希） 156 · B7_导入级耦合（代码导入本体包） 65 · B4_L3_运行本体 106 · B2_L1_L2_语义规格层 135
- 处理口径分布：含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改）（228） · 无术语命中（仅随命名空间迁移）（225） · 受限改名（词边界）+ IRI 级替换（9）

| 仓库 | 文件 | 批次 | 责任 Wave | 处理口径 | IRI 替换 | 受限改名 | 盲风险跳过 |
|---|---|---|---|---|---|---|---|
| gits | `specs/knowledge-architecture/instances/product/products.ttl` | B8 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 1 | 0 | 1 |
| gits | `specs/knowledge-architecture/instances/product/products.ttl` | B8 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 1 | 0 | 1 |
| kert | `src/kert/application/skills.py` | B8 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 4 |
| kert | `src/kert/domain/knowledge_source.py` | B8 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `adapters/knowledge-filesystem/src/test/java/com/gien/gits/adapter/filesystem/DefaultActivationPlannerFilesystemIT.java` | B8 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `adapters/knowledge-filesystem/src/test/java/com/gien/gits/adapter/filesystem/DefaultActivationPlannerFilesystemIT.java` | B8 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `adapters/semantic-jena/src/main/java/com/gien/gits/adapter/jena/JenaOntologyAdapter.java` | B8 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `adapters/semantic-jena/src/main/java/com/gien/gits/adapter/jena/JenaOntologyAdapter.java` | B8 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `adapters/semantic-jena/src/test/java/com/gien/gits/adapter/jena/JenaAdapterIntegrationTest.java` | B8 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `adapters/semantic-jena/src/test/java/com/gien/gits/adapter/jena/JenaAdapterIntegrationTest.java` | B8 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `adapters/semantic-jena/src/test/java/com/gien/gits/adapter/jena/JenaOntologyAdapterTest.java` | B8 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `adapters/semantic-jena/src/test/java/com/gien/gits/adapter/jena/JenaOntologyAdapterTest.java` | B8 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `apps/api/src/main/java/com/gien/gits/adapter/persistence/scenario/JdbcCustomerJourneyRepository.java` | B8 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 2 |
| gits | `apps/api/src/main/java/com/gien/gits/adapter/persistence/scenario/JdbcMeetingScriptRepository.java` | B8 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 2 |
| gits | `apps/api/src/main/java/com/gien/gits/adapter/persistence/scenario/JdbcOutreachScriptRepository.java` | B8 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `apps/api/src/main/java/com/gien/gits/adapter/persistence/scenario/JdbcPrevisitReportContentRepository.java` | B8 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `apps/api/src/main/java/com/gien/gits/api/config/KnowledgeArchitectureConfig.java` | B8 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `apps/api/src/main/java/com/gien/gits/api/config/KnowledgeArchitectureConfig.java` | B8 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `apps/api/src/main/java/com/gien/gits/api/controller/ClaimController.java` | B7 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `apps/api/src/main/java/com/gien/gits/api/controller/CommitmentController.java` | B7 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `apps/api/src/main/java/com/gien/gits/api/controller/CustomerContextController.java` | B7 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 3 |
| gits | `apps/api/src/main/java/com/gien/gits/api/controller/EngagementClaimController.java` | B7 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `apps/api/src/main/java/com/gien/gits/api/controller/EngagementJourneyController.java` | B7 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `apps/api/src/main/java/com/gien/gits/api/controller/EvaluationController.java` | B7 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `apps/api/src/main/java/com/gien/gits/api/controller/ExternalEventController.java` | B7 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `apps/api/src/main/java/com/gien/gits/api/controller/HumanGateController.java` | B7 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 2 |
| gits | `apps/api/src/main/java/com/gien/gits/api/controller/InteractionController.java` | B7 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `apps/api/src/main/java/com/gien/gits/api/controller/InteractionsV1Controller.java` | B7 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `apps/api/src/main/java/com/gien/gits/api/controller/KycInsightController.java` | B7 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `apps/api/src/main/java/com/gien/gits/api/controller/OperatingCaseController.java` | B7 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `apps/api/src/main/java/com/gien/gits/api/controller/OpportunityController.java` | B7 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `apps/api/src/main/java/com/gien/gits/api/controller/TaskController.java` | B7 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `apps/api/src/main/java/com/gien/gits/api/dto/AuditTraceEntryDto.java` | B7 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `apps/api/src/main/java/com/gien/gits/api/dto/HumanGateDto.java` | B7 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `apps/api/src/main/java/com/gien/gits/api/dto/ListedInteractionDto.java` | B7 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `apps/api/src/main/java/com/gien/gits/api/service/CommitmentService.java` | B7 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `apps/api/src/main/java/com/gien/gits/api/service/CustomerJourneyService.java` | B7 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 2 |
| gits | `apps/api/src/main/java/com/gien/gits/api/service/ExternalEventService.java` | B7 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `apps/api/src/main/java/com/gien/gits/api/service/OpportunityService.java` | B7 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `apps/api/src/main/java/com/gien/gits/api/service/ProductRecommendationHumanGateService.java` | B7 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `apps/api/src/main/java/com/gien/gits/api/service/ReportGenerationService.java` | B7 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `apps/api/src/main/java/com/gien/gits/api/service/ScenarioSeedDataService.java` | B8 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 5 | 2 |
| gits | `apps/api/src/main/java/com/gien/gits/api/service/ScenarioSeedDataService.java` | B8 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 5 | 2 |
| gits | `apps/api/src/main/java/com/gien/gits/api/service/ServiceProposalService.java` | B7 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 3 |
| gits | `apps/api/src/main/java/com/gien/gits/api/service/SupplyChainGraphService.java` | B7 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 2 |
| gits | `apps/api/src/main/java/com/gien/gits/api/service/TaskService.java` | B7 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `apps/api/src/main/java/com/gien/gits/api/service/report/CrmCallReportStrategy.java` | B7 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `apps/api/src/main/java/com/gien/gits/api/service/report/InternalRelationshipReportStrategy.java` | B7 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `apps/api/src/main/java/com/gien/gits/api/service/report/NextPrevisitReportStrategy.java` | B7 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `apps/api/src/main/java/com/gien/gits/api/service/report/ReportContext.java` | B7 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `apps/api/src/main/java/com/gien/gits/api/service/report/ReportStrategy.java` | B7 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `apps/api/src/main/java/com/gien/gits/api/service/report/UpdatedRelationshipReportStrategy.java` | B7 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `apps/api/src/main/resources/claim-reconciliation.dmn` | B8 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `apps/api/src/main/resources/claim-reconciliation.dmn` | B8 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `apps/api/src/test/java/com/gien/gits/api/config/KnowledgeArchitectureConfigTest.java` | B8 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `apps/api/src/test/java/com/gien/gits/api/config/KnowledgeArchitectureConfigTest.java` | B8 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `apps/api/src/test/java/com/gien/gits/api/controller/AuditTraceControllerTest.java` | B7 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `apps/api/src/test/java/com/gien/gits/api/controller/CommitmentControllerTest.java` | B7 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `apps/api/src/test/java/com/gien/gits/api/controller/CustomerContextControllerTest.java` | B7 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 3 |
| gits | `apps/api/src/test/java/com/gien/gits/api/controller/EngagementClaimControllerTest.java` | B7 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `apps/api/src/test/java/com/gien/gits/api/controller/EvaluationControllerTest.java` | B7 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `apps/api/src/test/java/com/gien/gits/api/controller/InteractionsV1ControllerTest.java` | B7 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `apps/api/src/test/java/com/gien/gits/api/controller/KycInsightControllerTest.java` | B7 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `apps/api/src/test/java/com/gien/gits/api/controller/OperatingCaseControllerTest.java` | B7 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `apps/api/src/test/java/com/gien/gits/api/controller/OpportunityControllerTest.java` | B7 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `apps/api/src/test/java/com/gien/gits/api/controller/TaskControllerTest.java` | B7 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `apps/api/src/test/java/com/gien/gits/api/e2e/FullChainE2eIT.java` | B8 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 2 |
| gits | `apps/api/src/test/java/com/gien/gits/api/e2e/FullChainE2eIT.java` | B8 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 2 |
| gits | `apps/api/src/test/java/com/gien/gits/api/e2e/MechanismE2eIT.java` | B8 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `apps/api/src/test/java/com/gien/gits/api/e2e/MechanismE2eIT.java` | B8 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `apps/api/src/test/java/com/gien/gits/api/e2e/MechanismE2eIT.java` | B8 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `apps/api/src/test/java/com/gien/gits/api/e2e/V1PrevisitChainTest.java` | B8 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 2 |
| gits | `apps/api/src/test/java/com/gien/gits/api/e2e/V1PrevisitChainTest.java` | B8 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 2 |
| gits | `apps/api/src/test/java/com/gien/gits/api/e2e/V1PrevisitChainTest.java` | B8 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 2 |
| gits | `apps/api/src/test/java/com/gien/gits/api/e2e/V2OntologyOnlyChangeTest.java` | B8 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `apps/api/src/test/java/com/gien/gits/api/e2e/V2OntologyOnlyChangeTest.java` | B8 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `apps/api/src/test/java/com/gien/gits/api/e2e/V2OntologyOnlyChangeTest.java` | B8 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `apps/api/src/test/java/com/gien/gits/api/integration/PersistenceIntegrationTest.java` | B8 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 2 |
| gits | `apps/api/src/test/java/com/gien/gits/api/service/CommitmentServiceTest.java` | B7 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `apps/api/src/test/java/com/gien/gits/api/service/ExternalEventServiceTest.java` | B7 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `apps/api/src/test/java/com/gien/gits/api/service/MeetingScriptServiceTest.java` | B7 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 2 |
| gits | `apps/api/src/test/java/com/gien/gits/api/service/OpportunityServiceTest.java` | B7 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `apps/api/src/test/java/com/gien/gits/api/service/OutreachScriptServiceTest.java` | B7 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 2 |
| gits | `apps/api/src/test/java/com/gien/gits/api/service/ProductMatchingServiceTest.java` | B7 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 3 |
| gits | `apps/api/src/test/java/com/gien/gits/api/service/ProductRecommendationHumanGateServiceTest.java` | B7 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `apps/api/src/test/java/com/gien/gits/api/service/ReportGenerationServicePreviousReportIdTest.java` | B7 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `apps/api/src/test/java/com/gien/gits/api/service/ServiceProposalServiceTest.java` | B7 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 2 |
| gits | `apps/api/src/test/java/com/gien/gits/api/service/SupplyChainGraphServiceTest.java` | B7 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 2 |
| gits | `apps/api/src/test/java/com/gien/gits/api/service/TaskServiceTest.java` | B7 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `apps/api/src/test/java/com/gien/gits/api/service/report/ReportStrategyCoverageTest.java` | B7 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `apps/worker/src/main/java/com/gien/gits/worker/config/WorkerConfig.java` | B7 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `apps/worker/src/main/java/com/gien/gits/worker/handlers/ClaimCandidateRecordedHandler.java` | B7 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `apps/worker/src/main/java/com/gien/gits/worker/handlers/ControlledActionRequestedHandler.java` | B7 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `apps/worker/src/test/java/com/gien/gits/worker/handlers/ClaimCandidateRecordedHandlerTest.java` | B7 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `modules/context-evidence/src/main/java/com/gien/gits/context/DefaultContextAssembler.java` | B7 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `modules/context-evidence/src/main/java/com/gien/gits/context/EvidenceBundle.java` | B7 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `modules/context-evidence/src/test/java/com/gien/gits/context/DefaultContextAssemblerTest.java` | B7 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `modules/context-evidence/src/test/java/com/gien/gits/context/EvidenceBundleTest.java` | B7 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `modules/human-action/src/main/java/com/gien/gits/action/port/TaskRepository.java` | B7 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `modules/human-action/src/main/java/com/gien/gits/action/port/WritableTaskRepository.java` | B7 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `modules/human-action/src/test/java/com/gien/gits/action/ControlledActionServiceTest.java` | B7 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `modules/knowledge-architecture/src/main/java/com/gien/gits/knowledge/ActivationContract.java` | B4 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `modules/knowledge-architecture/src/main/java/com/gien/gits/knowledge/ActivationContract.java` | B4 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `modules/knowledge-architecture/src/main/java/com/gien/gits/knowledge/ActivationPlan.java` | B8 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `modules/knowledge-architecture/src/main/java/com/gien/gits/knowledge/AssetManifest.java` | B4 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `modules/knowledge-architecture/src/main/java/com/gien/gits/knowledge/AssetManifest.java` | B4 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `modules/knowledge-architecture/src/main/java/com/gien/gits/knowledge/KnowledgeElement.java` | B4 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `modules/knowledge-architecture/src/main/java/com/gien/gits/knowledge/KnowledgeMap.java` | B4 | W3_CONSUMER_SWITCH | 受限改名（词边界）+ IRI 级替换 | 0 | 2 | 0 |
| gits | `modules/knowledge-architecture/src/main/java/com/gien/gits/knowledge/KnowledgeMap.java` | B4 | W3_CONSUMER_SWITCH | 受限改名（词边界）+ IRI 级替换 | 0 | 2 | 0 |
| gits | `modules/knowledge-architecture/src/main/java/com/gien/gits/knowledge/RoutePolicy.java` | B4 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `modules/knowledge-architecture/src/main/java/com/gien/gits/knowledge/plan/ActivationPlanRequest.java` | B4 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `modules/knowledge-architecture/src/main/java/com/gien/gits/knowledge/plan/DefaultActivationPlanner.java` | B8 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 3 | 1 |
| gits | `modules/knowledge-architecture/src/main/java/com/gien/gits/knowledge/plan/DefaultActivationPlanner.java` | B8 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 3 | 1 |
| gits | `modules/knowledge-architecture/src/main/java/com/gien/gits/knowledge/port/ActivationContractPort.java` | B4 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `modules/knowledge-architecture/src/main/java/com/gien/gits/knowledge/port/ActivationContractPort.java` | B4 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `modules/knowledge-architecture/src/main/java/com/gien/gits/knowledge/port/ActivationPlannerPort.java` | B4 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `modules/knowledge-architecture/src/main/java/com/gien/gits/knowledge/port/AssetCatalogPort.java` | B4 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `modules/knowledge-architecture/src/main/java/com/gien/gits/knowledge/port/KnowledgeElementPort.java` | B4 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `modules/knowledge-architecture/src/main/java/com/gien/gits/knowledge/port/KnowledgeMapPort.java` | B4 | W3_CONSUMER_SWITCH | 受限改名（词边界）+ IRI 级替换 | 0 | 3 | 0 |
| gits | `modules/knowledge-architecture/src/main/java/com/gien/gits/knowledge/port/KnowledgeMapPort.java` | B4 | W3_CONSUMER_SWITCH | 受限改名（词边界）+ IRI 级替换 | 0 | 3 | 0 |
| gits | `modules/knowledge-architecture/src/main/java/com/gien/gits/knowledge/port/KnowledgeWikiPort.java` | B4 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `modules/knowledge-architecture/src/main/java/com/gien/gits/knowledge/port/RoutePolicyEvaluatorPort.java` | B4 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `modules/knowledge-architecture/src/main/java/com/gien/gits/knowledge/port/RoutePolicyPort.java` | B4 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `modules/knowledge-architecture/src/main/java/com/gien/gits/knowledge/repository/InMemoryKnowledgeStore.java` | B4 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 6 | 1 |
| gits | `modules/knowledge-architecture/src/main/java/com/gien/gits/knowledge/route/DefaultRoutePolicyEvaluator.java` | B4 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `modules/knowledge-architecture/src/test/java/com/gien/gits/knowledge/KnowledgeMapTest.java` | B4 | W3_CONSUMER_SWITCH | 受限改名（词边界）+ IRI 级替换 | 0 | 8 | 0 |
| gits | `modules/knowledge-architecture/src/test/java/com/gien/gits/knowledge/KnowledgeMapTest.java` | B4 | W3_CONSUMER_SWITCH | 受限改名（词边界）+ IRI 级替换 | 0 | 8 | 0 |
| gits | `modules/knowledge-architecture/src/test/java/com/gien/gits/knowledge/RoutePolicyTest.java` | B4 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `modules/knowledge-architecture/src/test/java/com/gien/gits/knowledge/plan/DefaultActivationPlannerTest.java` | B8 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 8 | 2 |
| gits | `modules/knowledge-architecture/src/test/java/com/gien/gits/knowledge/plan/DefaultActivationPlannerTest.java` | B8 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 8 | 2 |
| gits | `modules/knowledge-architecture/src/test/java/com/gien/gits/knowledge/plan/DefaultActivationPlannerTest.java` | B8 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 8 | 2 |
| gits | `modules/knowledge-architecture/src/test/java/com/gien/gits/knowledge/plan/DefaultActivationPlannerTest.java` | B8 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 8 | 2 |
| gits | `modules/knowledge-architecture/src/test/resources/gk-ke-hash/ControlledAction.json` | B4 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `modules/knowledge-architecture/src/test/resources/gk-ke-hash/MetricDefinition.json` | B4 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `modules/operational-ontology/src/main/java/com/gien/gits/ontology/AuditTraceEntry.java` | B4 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `modules/operational-ontology/src/main/java/com/gien/gits/ontology/BankRelationshipSnapshot.java` | B4 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `modules/operational-ontology/src/main/java/com/gien/gits/ontology/Claim.java` | B4 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `modules/operational-ontology/src/main/java/com/gien/gits/ontology/Commitment.java` | B4 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `modules/operational-ontology/src/main/java/com/gien/gits/ontology/Commitment.java` | B4 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `modules/operational-ontology/src/main/java/com/gien/gits/ontology/ControlledAction.java` | B4 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `modules/operational-ontology/src/main/java/com/gien/gits/ontology/CreditFacility.java` | B4 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `modules/operational-ontology/src/main/java/com/gien/gits/ontology/Customer.java` | B4 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 2 |
| gits | `modules/operational-ontology/src/main/java/com/gien/gits/ontology/Customer.java` | B4 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 2 |
| gits | `modules/operational-ontology/src/main/java/com/gien/gits/ontology/Evidence.java` | B4 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `modules/operational-ontology/src/main/java/com/gien/gits/ontology/ExternalEvent.java` | B4 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `modules/operational-ontology/src/main/java/com/gien/gits/ontology/GroupRelationship.java` | B4 | W3_CONSUMER_SWITCH | 受限改名（词边界）+ IRI 级替换 | 0 | 3 | 0 |
| gits | `modules/operational-ontology/src/main/java/com/gien/gits/ontology/HumanConfirmation.java` | B4 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `modules/operational-ontology/src/main/java/com/gien/gits/ontology/HumanGate.java` | B4 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `modules/operational-ontology/src/main/java/com/gien/gits/ontology/HumanGate.java` | B4 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `modules/operational-ontology/src/main/java/com/gien/gits/ontology/Interaction.java` | B4 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `modules/operational-ontology/src/main/java/com/gien/gits/ontology/KycGapProfile.java` | B4 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `modules/operational-ontology/src/main/java/com/gien/gits/ontology/KycGapProfile.java` | B4 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `modules/operational-ontology/src/main/java/com/gien/gits/ontology/LegalEntity.java` | B4 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `modules/operational-ontology/src/main/java/com/gien/gits/ontology/OperatingCase.java` | B4 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `modules/operational-ontology/src/main/java/com/gien/gits/ontology/OpportunitySignal.java` | B4 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `modules/operational-ontology/src/main/java/com/gien/gits/ontology/PolicyRule.java` | B4 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `modules/operational-ontology/src/main/java/com/gien/gits/ontology/ProductKnowledgeCard.java` | B4 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `modules/operational-ontology/src/main/java/com/gien/gits/ontology/RelationshipReport.java` | B4 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `modules/operational-ontology/src/main/java/com/gien/gits/ontology/Transaction.java` | B4 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `modules/operational-ontology/src/main/java/com/gien/gits/ontology/TransactionRecord.java` | B4 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `modules/operational-ontology/src/main/java/com/gien/gits/ontology/domain/ClaimLifecycleEvent.java` | B4 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `modules/operational-ontology/src/main/java/com/gien/gits/ontology/domain/InteractionExtension.java` | B4 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `modules/operational-ontology/src/main/java/com/gien/gits/ontology/domain/Opportunity.java` | B4 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `modules/operational-ontology/src/main/java/com/gien/gits/ontology/domain/Opportunity.java` | B4 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `modules/operational-ontology/src/main/java/com/gien/gits/ontology/domain/ProductKnowledgeVersion.java` | B4 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `modules/operational-ontology/src/main/java/com/gien/gits/ontology/port/AuditTraceRepository.java` | B4 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `modules/operational-ontology/src/main/java/com/gien/gits/ontology/port/BankRelationshipSnapshotRepository.java` | B4 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `modules/operational-ontology/src/main/java/com/gien/gits/ontology/port/ClaimRepository.java` | B4 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `modules/operational-ontology/src/main/java/com/gien/gits/ontology/port/CommitmentRepository.java` | B4 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `modules/operational-ontology/src/main/java/com/gien/gits/ontology/port/CommitmentRepository.java` | B4 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `modules/operational-ontology/src/main/java/com/gien/gits/ontology/port/CreditFacilityRepository.java` | B4 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `modules/operational-ontology/src/main/java/com/gien/gits/ontology/port/CustomerRepository.java` | B4 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `modules/operational-ontology/src/main/java/com/gien/gits/ontology/port/CustomerRepository.java` | B4 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `modules/operational-ontology/src/main/java/com/gien/gits/ontology/port/ExternalEventRepository.java` | B4 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `modules/operational-ontology/src/main/java/com/gien/gits/ontology/port/ExternalEventRepository.java` | B4 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `modules/operational-ontology/src/main/java/com/gien/gits/ontology/port/GroupRelationshipRepository.java` | B4 | W3_CONSUMER_SWITCH | 受限改名（词边界）+ IRI 级替换 | 0 | 3 | 0 |
| gits | `modules/operational-ontology/src/main/java/com/gien/gits/ontology/port/HumanGateRepository.java` | B4 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `modules/operational-ontology/src/main/java/com/gien/gits/ontology/port/HumanGateRepository.java` | B4 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `modules/operational-ontology/src/main/java/com/gien/gits/ontology/port/InteractionExtensionRepository.java` | B4 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `modules/operational-ontology/src/main/java/com/gien/gits/ontology/port/InteractionRepository.java` | B4 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `modules/operational-ontology/src/main/java/com/gien/gits/ontology/port/KycGapProfileRepository.java` | B4 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `modules/operational-ontology/src/main/java/com/gien/gits/ontology/port/KycGapProfileRepository.java` | B4 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `modules/operational-ontology/src/main/java/com/gien/gits/ontology/port/LegalEntityRepository.java` | B4 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `modules/operational-ontology/src/main/java/com/gien/gits/ontology/port/OperatingCaseRepository.java` | B4 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `modules/operational-ontology/src/main/java/com/gien/gits/ontology/port/OpportunityRepository.java` | B4 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `modules/operational-ontology/src/main/java/com/gien/gits/ontology/port/OpportunityRepository.java` | B4 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `modules/operational-ontology/src/main/java/com/gien/gits/ontology/port/OpportunitySignalRepository.java` | B4 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `modules/operational-ontology/src/main/java/com/gien/gits/ontology/port/PolicyRuleRepository.java` | B4 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `modules/operational-ontology/src/main/java/com/gien/gits/ontology/port/ProductCatalogRepository.java` | B4 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `modules/operational-ontology/src/main/java/com/gien/gits/ontology/port/ProductKnowledgeVersionRepository.java` | B4 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `modules/operational-ontology/src/main/java/com/gien/gits/ontology/port/RelationshipReportRepository.java` | B4 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `modules/operational-ontology/src/main/java/com/gien/gits/ontology/port/TransactionRecordRepository.java` | B4 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `modules/operational-ontology/src/main/java/com/gien/gits/ontology/port/TransactionRepository.java` | B4 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `modules/operational-ontology/src/main/java/com/gien/gits/ontology/port/WritableClaimRepository.java` | B4 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `modules/operational-ontology/src/main/java/com/gien/gits/ontology/port/WritableCommitmentRepository.java` | B4 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `modules/operational-ontology/src/main/java/com/gien/gits/ontology/port/WritableCustomerRepository.java` | B4 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `modules/operational-ontology/src/main/java/com/gien/gits/ontology/port/WritableExternalEventRepository.java` | B4 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `modules/operational-ontology/src/main/java/com/gien/gits/ontology/port/WritableGroupRelationshipRepository.java` | B4 | W3_CONSUMER_SWITCH | 受限改名（词边界）+ IRI 级替换 | 0 | 2 | 0 |
| gits | `modules/operational-ontology/src/main/java/com/gien/gits/ontology/port/WritableInteractionExtensionRepository.java` | B4 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `modules/operational-ontology/src/main/java/com/gien/gits/ontology/port/WritableInteractionRepository.java` | B4 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `modules/operational-ontology/src/main/java/com/gien/gits/ontology/port/WritableKycGapProfileRepository.java` | B4 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `modules/operational-ontology/src/main/java/com/gien/gits/ontology/port/WritableLegalEntityRepository.java` | B4 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `modules/operational-ontology/src/main/java/com/gien/gits/ontology/port/WritableOperatingCaseRepository.java` | B4 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `modules/operational-ontology/src/main/java/com/gien/gits/ontology/port/WritableOpportunityRepository.java` | B4 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `modules/operational-ontology/src/main/java/com/gien/gits/ontology/port/WritableOpportunitySignalRepository.java` | B4 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `modules/operational-ontology/src/main/java/com/gien/gits/ontology/port/WritablePolicyRuleRepository.java` | B4 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `modules/operational-ontology/src/main/java/com/gien/gits/ontology/port/WritableProductCatalogRepository.java` | B4 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `modules/operational-ontology/src/main/java/com/gien/gits/ontology/port/WritableProductKnowledgeVersionRepository.java` | B4 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `modules/operational-ontology/src/main/java/com/gien/gits/ontology/port/WritableRelationshipReportRepository.java` | B4 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `modules/operational-ontology/src/test/java/com/gien/gits/ontology/ExternalEventTest.java` | B4 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `modules/operational-ontology/src/test/java/com/gien/gits/ontology/OperationalOntologyTest.java` | B4 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `modules/operational-ontology/src/test/java/com/gien/gits/ontology/PolicyRuleTest.java` | B4 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `modules/operational-ontology/src/test/java/com/gien/gits/ontology/RecordModelTest.java` | B4 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 6 | 2 |
| gits | `modules/operational-ontology/src/test/java/com/gien/gits/ontology/RecordModelTest.java` | B4 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 6 | 2 |
| gits | `modules/semantic-runtime/src/main/java/com/gien/gits/semantic/OntologyPort.java` | B8 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `modules/semantic-runtime/src/test/java/com/gien/gits/semantic/FailClosedSemanticQueryGuardTest.java` | B8 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `modules/semantic-runtime/src/test/java/com/gien/gits/semantic/InMemorySemanticRepositoryTest.java` | B8 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `modules/semantic-runtime/src/test/java/com/gien/gits/semantic/InMemorySemanticRepositoryTest.java` | B8 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `modules/semantic-runtime/src/test/java/com/gien/gits/semantic/SemanticPackageTest.java` | B8 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `scripts/_gen_gk_ke_l4_1_activation.py` | B8 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `scripts/_gen_gk_ke_l4_1_activation.py` | B8 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `scripts/_gen_gk_ke_openapi_negatives.py` | B8 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `scripts/_gen_gk_ke_openapi_negatives.py` | B8 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `scripts/contract_pipeline.py` | B8 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `scripts/contract_pipeline.py` | B8 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `scripts/gate_injection_tests.py` | B8 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `scripts/gate_injection_tests.py` | B8 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `scripts/gate_injection_tests.py` | B8 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `scripts/gate_injection_tests.py` | B8 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `scripts/gen_doc.js` | B8 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `scripts/gen_gov_doc.js` | B8 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `scripts/generate_mapping_doc.js` | B8 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `scripts/generate_mapping_doc.js` | B8 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `scripts/gk17_prodcard_to_rdf.py` | B8 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `scripts/gk17_prodcard_to_rdf.py` | B8 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `scripts/gk17_prodcard_to_rdf.py` | B8 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `scripts/gk17_ref_anchor_check.py` | B8 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `scripts/gk17_ref_anchor_check.py` | B8 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `scripts/gk17_ref_anchor_check.py` | B8 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `scripts/gk17_ref_anchor_check.py` | B8 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `scripts/gk17_triple_consistency_check.py` | B8 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `scripts/gk17_triple_consistency_check.py` | B8 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `scripts/gk17_triple_consistency_check.py` | B8 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `scripts/gk_ke_l2_1_semantic_query_tests.py` | B8 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `scripts/gk_ke_l4_1_map_activation_tests.py` | B8 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `scripts/oracle_customer_to_operating_case.py` | B8 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 3 |
| gits | `scripts/oracle_customer_to_operating_case.py` | B8 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 3 |
| gits | `scripts/oracle_customer_to_operating_case.py` | B8 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 3 |
| gits | `scripts/regression-run.sh` | B8 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `scripts/run_p20_shadow_e2e.py` | B8 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `scripts/run_p20_shadow_e2e.py` | B8 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `scripts/run_p22_shadow_e2e.py` | B8 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `scripts/run_p22_shadow_e2e.py` | B8 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `scripts/semantic_rule_gate.py` | B8 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/CONTRACT_INDEX.yaml` | B8 | W2_SPLIT | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 2 | 2 |
| gits | `specs/CONTRACT_INDEX.yaml` | B8 | W2_SPLIT | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 2 | 2 |
| gits | `specs/CONTRACT_INDEX.yaml` | B8 | W2_SPLIT | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 2 | 2 |
| gits | `specs/SPEC_INDEX.md` | B8 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/SPEC_INDEX.md` | B8 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/actions/controlled-action.schema.json` | B8 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/actions/controlled-action.schema.json` | B8 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/data/customer-source-mapping.r2rml.ttl` | B8 | W2_SPLIT | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 2 | 0 | 1 |
| gits | `specs/data/customer-source-mapping.r2rml.ttl` | B8 | W2_SPLIT | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 2 | 0 | 1 |
| gits | `specs/data/customer-source-mapping.r2rml.ttl` | B8 | W2_SPLIT | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 2 | 0 | 1 |
| gits | `specs/data/source-contract.schema.json` | B8 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/evaluation/run-manifest.schema.json` | B8 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/evidence/evidence-bundle.schema.json` | B8 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/evidence/evidence-bundle.schema.json` | B8 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/gk-ke/v1/examples/negative/ActivationPlan_3.json` | B8 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/gk-ke/v1/examples/openapi/negative/querySemantic_1.json` | B8 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/gk-ke/v1/examples/openapi/positive/createPlan.json` | B8 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/gk-ke/v1/examples/openapi/positive/executeKnowledge.json` | B8 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/knowledge-architecture/activation/activation_plan.json` | B8 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/knowledge-architecture/activation/compiled_plan.json` | B2 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/knowledge-architecture/activation/map_dependency_lock.json` | B2 | W2_SPLIT | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `specs/knowledge-architecture/activation/map_dependency_lock.json` | B2 | W2_SPLIT | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `specs/knowledge-architecture/activation/map_spec.json` | B2 | W2_SPLIT | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `specs/knowledge-architecture/activation/map_spec.json` | B2 | W2_SPLIT | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `specs/knowledge-architecture/activation/route_policy.json` | B2 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/knowledge-architecture/activation/task_template.json` | B2 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/knowledge-architecture/activations/AC-FACT-RECONCILIATION-001.json` | B2 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/knowledge-architecture/activations/AC-FACT-RECONCILIATION-001.json` | B2 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/knowledge-architecture/activations/AC-FACT-RECONCILIATION-001.json` | B2 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/knowledge-architecture/activations/AC-PREVISIT-001.json` | B2 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/knowledge-architecture/activations/AC-PREVISIT-001.json` | B2 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/knowledge-architecture/activations/AC-PRODUCT-RECOMMEND-001.json` | B2 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/knowledge-architecture/activations/AC-PRODUCT-RECOMMEND-001.json` | B2 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/knowledge-architecture/assets/foundational-data/credit-facility.md` | B2 | W2_SPLIT | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `specs/knowledge-architecture/assets/foundational-data/credit-facility.md` | B2 | W2_SPLIT | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `specs/knowledge-architecture/assets/foundational-data/customer-profile.md` | B2 | W2_SPLIT | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `specs/knowledge-architecture/assets/foundational-data/customer-profile.md` | B2 | W2_SPLIT | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `specs/knowledge-architecture/assets/foundational-data/external-event.md` | B2 | W2_SPLIT | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `specs/knowledge-architecture/assets/foundational-data/interaction-history.md` | B2 | W2_SPLIT | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `specs/knowledge-architecture/assets/foundational-data/interaction-history.md` | B2 | W2_SPLIT | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `specs/knowledge-architecture/assets/foundational-data/transaction-summary.md` | B2 | W2_SPLIT | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `specs/knowledge-architecture/assets/foundational-data/transaction-summary.md` | B2 | W2_SPLIT | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `specs/knowledge-architecture/assets/knowledge-rules/claim-reconciliation.md` | B2 | W2_SPLIT | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `specs/knowledge-architecture/assets/knowledge-rules/claim-reconciliation.md` | B2 | W2_SPLIT | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `specs/knowledge-architecture/assets/knowledge-rules/customer-ontology.md` | B8 | W2_SPLIT | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `specs/knowledge-architecture/assets/knowledge-rules/customer-ontology.md` | B8 | W2_SPLIT | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `specs/knowledge-architecture/assets/knowledge-rules/customer-ontology.md` | B8 | W2_SPLIT | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `specs/knowledge-architecture/assets/knowledge-rules/evidence-policy.md` | B2 | W2_SPLIT | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 2 |
| gits | `specs/knowledge-architecture/assets/knowledge-rules/evidence-policy.md` | B2 | W2_SPLIT | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 2 |
| gits | `specs/knowledge-architecture/assets/knowledge-rules/kyc-question-library.md` | B2 | W2_SPLIT | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `specs/knowledge-architecture/assets/knowledge-rules/product-cards.md` | B2 | W2_SPLIT | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `specs/knowledge-architecture/assets/knowledge-rules/product-rules.md` | B2 | W2_SPLIT | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `specs/knowledge-architecture/assets/knowledge-rules/visit-sop.md` | B2 | W2_SPLIT | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `specs/knowledge-architecture/assets/process-tools/sp02-context-assembly.md` | B2 | W2_SPLIT | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `specs/knowledge-architecture/assets/process-tools/sp05-kyc-gap.md` | B2 | W2_SPLIT | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `specs/knowledge-architecture/assets/process-tools/sp05-kyc-gap.md` | B2 | W2_SPLIT | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `specs/knowledge-architecture/assets/process-tools/sp07-evidence-sufficiency.md` | B2 | W2_SPLIT | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 2 |
| gits | `specs/knowledge-architecture/assets/process-tools/sp07-evidence-sufficiency.md` | B2 | W2_SPLIT | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 2 |
| gits | `specs/knowledge-architecture/assets/process-tools/sp10-report-generation.md` | B2 | W2_SPLIT | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `specs/knowledge-architecture/assets/process-tools/sp15-product-fit.md` | B2 | W2_SPLIT | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `specs/knowledge-architecture/assets/runtime-feedback/agent-run-trace.md` | B2 | W2_SPLIT | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `specs/knowledge-architecture/assets/runtime-feedback/evaluation-cases.md` | B2 | W2_SPLIT | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `specs/knowledge-architecture/assets/runtime-feedback/human-gate-feedback.md` | B2 | W2_SPLIT | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `specs/knowledge-architecture/assets/runtime-feedback/skill-invocation-trace.md` | B2 | W2_SPLIT | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 2 |
| gits | `specs/knowledge-architecture/assets/runtime-feedback/skill-invocation-trace.md` | B2 | W2_SPLIT | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 2 |
| gits | `specs/knowledge-architecture/capabilities/SIM-CAP-EIGHT-DIM.json` | B2 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/knowledge-architecture/capabilities/SIM-CAP-EIGHT-DIM.json` | B2 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/knowledge-architecture/capabilities/SIM-CAP-FACT-RECON.json` | B2 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/knowledge-architecture/capabilities/SIM-CAP-FACT-RECON.json` | B2 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/knowledge-architecture/capabilities/SIM-CAP-KYC-GAP.json` | B2 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/knowledge-architecture/capabilities/SIM-CAP-KYC-GAP.json` | B2 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/knowledge-architecture/capabilities/SIM-CAP-PRODUCT-CONDITION.json` | B2 | W2_SPLIT | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `specs/knowledge-architecture/capabilities/SIM-CAP-PRODUCT-CONDITION.json` | B2 | W2_SPLIT | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `specs/knowledge-architecture/capabilities/SIM-CAP-PRODUCT-DOCTOR.json` | B2 | W2_SPLIT | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 2 |
| gits | `specs/knowledge-architecture/capabilities/SIM-CAP-PRODUCT-REC.json` | B2 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/knowledge-architecture/capabilities/SIM-CAP-PRODUCT-REC.json` | B2 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/knowledge-architecture/closed-loop/closed_loop_run.json` | B2 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/knowledge-architecture/contracts/ThreeStageInteraction.json` | B2 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/knowledge-architecture/contracts/UpstreamFieldMapping.json` | B2 | W2_SPLIT | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `specs/knowledge-architecture/contracts/_preregistration-v1.2.0-draft.json` | B2 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/knowledge-architecture/elements/KI-009/KE-009-01.md` | B2 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/knowledge-architecture/elements/KI-009/KE-009-02.md` | B2 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/knowledge-architecture/elements/KI-009/KE-009-03.md` | B2 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/knowledge-architecture/elements/KI-009/KE-009-04.md` | B2 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/knowledge-architecture/elements/KI-009/KE-009-05.md` | B2 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/knowledge-architecture/elements/KI-009/KE-009-06.md` | B2 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/knowledge-architecture/elements/KI-009/KE-009-07.md` | B2 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/knowledge-architecture/elements/KI-009/KE-009-08.md` | B2 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/knowledge-architecture/elements/KI-FRONT-001/KE-FRONT-001-01.md` | B2 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/knowledge-architecture/elements/KI-FRONT-001/KE-FRONT-001-02.md` | B2 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/knowledge-architecture/elements/KI-FRONT-001/KE-FRONT-001-03.md` | B2 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/knowledge-architecture/elements/KI-FRONT-002/KE-FRONT-002-01.md` | B2 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/knowledge-architecture/elements/KI-FRONT-002/KE-FRONT-002-02.md` | B2 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/knowledge-architecture/elements/KI-FRONT-002/KE-FRONT-002-03.md` | B2 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/knowledge-architecture/elements/KI-FRONT-002/KE-FRONT-002-04.md` | B2 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/knowledge-architecture/elements/KI-FRONT-002/KE-FRONT-002-05.md` | B2 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/knowledge-architecture/elements/KI-FRONT-002/KE-FRONT-002-06.md` | B2 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/knowledge-architecture/elements/KI-FRONT-002/KE-FRONT-002-07.md` | B2 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/knowledge-architecture/elements/KI-FRONT-002/KE-FRONT-002-08.md` | B2 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/knowledge-architecture/elements/KI-FRONT-002/KE-FRONT-002-09.md` | B2 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/knowledge-architecture/elements/KI-FRONT-003/KE-FRONT-003-01.md` | B2 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/knowledge-architecture/elements/KI-FRONT-003/KE-FRONT-003-02.md` | B2 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/knowledge-architecture/elements/KI-FRONT-003/KE-FRONT-003-03.md` | B2 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/knowledge-architecture/elements/KI-FRONT-003/KE-FRONT-003-04.md` | B2 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/knowledge-architecture/elements/KI-FRONT-003/KE-FRONT-003-05.md` | B2 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/knowledge-architecture/elements/KI-FRONT-003/KE-FRONT-003-06.md` | B2 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/knowledge-architecture/elements/KI-FRONT-004/KE-FRONT-004-01.md` | B2 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/knowledge-architecture/elements/KI-FRONT-004/KE-FRONT-004-02.md` | B2 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/knowledge-architecture/elements/KI-FRONT-004/KE-FRONT-004-03.md` | B2 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/knowledge-architecture/elements/KI-FRONT-004/KE-FRONT-004-04.md` | B2 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/knowledge-architecture/elements/KI-FRONT-005/KE-FRONT-005-01.md` | B2 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/knowledge-architecture/elements/KI-FRONT-005/KE-FRONT-005-02.md` | B2 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/knowledge-architecture/elements/KI-FRONT-005/KE-FRONT-005-03.md` | B2 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/knowledge-architecture/elements/KI-FRONT-005/KE-FRONT-005-04.md` | B2 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/knowledge-architecture/elements/KI-FRONT-006/KE-FRONT-006-01.md` | B2 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/knowledge-architecture/elements/KI-FRONT-006/KE-FRONT-006-02.md` | B2 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/knowledge-architecture/elements/KI-FRONT-006/KE-FRONT-006-03.md` | B2 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/knowledge-architecture/elements/KI-FRONT-006/KE-FRONT-006-04.md` | B2 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/knowledge-architecture/elements/KI-FRONT-006/KE-FRONT-006-05.md` | B2 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/knowledge-architecture/elements/knowledge-items-index.json` | B2 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/knowledge-architecture/examples/AP-FACT-RECON-GOLDEN.json` | B8 | W2_SPLIT | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `specs/knowledge-architecture/examples/AP-PREVISIT-GOLDEN.json` | B8 | W2_SPLIT | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `specs/knowledge-architecture/graph/graph_manifest.json` | B2 | W2_SPLIT | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 2 |
| gits | `specs/knowledge-architecture/industry/SIM-IND-MANUFACTURING.json` | B2 | W2_SPLIT | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `specs/knowledge-architecture/instances/product/UNRESOLVED.json` | B8 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/knowledge-architecture/instances/product/UNRESOLVED.json` | B8 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/knowledge-architecture/maps/ROOT_KNOWLEDGE_MAP.md` | B2 | W2_SPLIT | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 2 |
| gits | `specs/knowledge-architecture/maps/ROOT_KNOWLEDGE_MAP.md` | B2 | W2_SPLIT | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 2 |
| gits | `specs/knowledge-architecture/maps/corporate-rm/DOMAIN_MAP.md` | B2 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/knowledge-architecture/maps/corporate-rm/DOMAIN_MAP.md` | B2 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/knowledge-architecture/maps/corporate-rm/fact-reconciliation.md` | B2 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/knowledge-architecture/maps/corporate-rm/fact-reconciliation.md` | B2 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/knowledge-architecture/maps/corporate-rm/previsit-preparation.md` | B2 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/knowledge-architecture/maps/corporate-rm/previsit-preparation.md` | B2 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/knowledge-architecture/registry/Capability.json` | B2 | W2_SPLIT | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `specs/knowledge-architecture/registry/Capability.json` | B2 | W2_SPLIT | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `specs/knowledge-architecture/registry/Capability.json` | B2 | W2_SPLIT | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `specs/knowledge-architecture/registry/CapabilityIdMapping.json` | B2 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/knowledge-architecture/registry/MapVersion.json` | B2 | W2_SPLIT | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `specs/knowledge-architecture/registry/negatives/invalid_edge_endpoint.json` | B2 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/knowledge-architecture/registry/provider-bindings.json` | B2 | W2_SPLIT | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `specs/knowledge-architecture/registry/semantic-probes/SIM-CAP-COMMITMENT.json` | B2 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/knowledge-architecture/registry/semantic-probes/SIM-CAP-EIGHT-DIM.json` | B2 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/knowledge-architecture/registry/semantic-probes/SIM-CAP-FACT-RECON.json` | B2 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/knowledge-architecture/registry/semantic-probes/SIM-CAP-KYC-GAP.json` | B2 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/knowledge-architecture/registry/semantic-probes/SIM-CAP-MEETING-SCRIPT.json` | B2 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/knowledge-architecture/registry/semantic-probes/SIM-CAP-OUTREACH-SCRIPT.json` | B2 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/knowledge-architecture/registry/semantic-probes/SIM-CAP-PRODUCT-CONDITION.json` | B2 | W2_SPLIT | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `specs/knowledge-architecture/registry/semantic-probes/SIM-CAP-PRODUCT-DOCTOR.json` | B2 | W2_SPLIT | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 2 |
| gits | `specs/knowledge-architecture/registry/semantic-probes/SIM-CAP-PRODUCT-DOCTOR.json` | B2 | W2_SPLIT | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 2 |
| gits | `specs/knowledge-architecture/registry/semantic-probes/SIM-CAP-REPORT-ASSEMBLE.json` | B2 | W2_SPLIT | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `specs/knowledge-architecture/registry/semantic-probes/SIM-CAP-SUPPLY-CHAIN.json` | B2 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/knowledge-architecture/routes/RP-CORP-RM-001.json` | B2 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/knowledge-architecture/schemas/activation-contract.schema.json` | B8 | W2_SPLIT | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `specs/knowledge-architecture/schemas/activation-contract.schema.json` | B8 | W2_SPLIT | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `specs/knowledge-architecture/schemas/activation-plan.schema.json` | B8 | W2_SPLIT | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `specs/knowledge-architecture/schemas/asset-manifest.schema.json` | B8 | W2_SPLIT | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `specs/knowledge-architecture/schemas/asset-manifest.schema.json` | B8 | W2_SPLIT | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `specs/knowledge-architecture/schemas/knowledge-element.schema.json` | B8 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/knowledge-architecture/schemas/knowledge-map.schema.json` | B8 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/knowledge-architecture/schemas/route-policy.schema.json` | B8 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/knowledge-architecture/schemas/skill-descriptor.schema.json` | B8 | W2_SPLIT | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `specs/knowledge-architecture/schemas/skill-descriptor.schema.json` | B8 | W2_SPLIT | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `specs/knowledge-architecture/skills/SP-02.json` | B2 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/knowledge-architecture/skills/SP-05.json` | B2 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/knowledge-architecture/skills/SP-07.json` | B2 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/knowledge-architecture/skills/SP-10.json` | B2 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/knowledge-architecture/skills/SP-15.json` | B2 | W2_SPLIT | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 2 |
| gits | `specs/knowledge-architecture/tests/activation_plan_golden_cases.jsonl` | B2 | W2_SPLIT | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `specs/knowledge-architecture/tests/negative_security_cases.jsonl` | B2 | W2_SPLIT | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `specs/knowledge-architecture/tests/routing_cases.jsonl` | B2 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/openapi/gk-ke-v1.openapi.json` | B8 | W2_SPLIT | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 3 | 1 |
| gits | `specs/openapi/gk-ke-v1.openapi.json` | B8 | W2_SPLIT | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 3 | 1 |
| gits | `specs/openapi/gk-ke-v1.openapi.json` | B8 | W2_SPLIT | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 3 | 1 |
| gits | `specs/rules/claim-reconciliation.dmn` | B8 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/rules/claim-reconciliation.dmn` | B8 | W2_SPLIT | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| gits | `specs/skills/context-assembly.skill.schema.json` | B8 | W2_SPLIT | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| gits | `specs/skills/context-assembly.skill.schema.json` | B8 | W2_SPLIT | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| kert | `examples/bank-front-knowledge-maps/90_control/ontology/PROVENANCE.json` | B8 | W3_KERT_ASSETS | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| kert | `examples/bank-front-knowledge-maps/90_control/ontology/PROVENANCE.json` | B8 | W3_KERT_ASSETS | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| kert | `examples/bank-front-knowledge-maps/90_control/ontology/PROVENANCE.json` | B8 | W3_KERT_ASSETS | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| kert | `examples/bank-front-knowledge-maps/90_control/ontology/customer-source-mapping.r2rml.ttl` | B8 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 2 | 0 | 1 |
| kert | `examples/bank-front-knowledge-maps/90_control/ontology/customer-source-mapping.r2rml.ttl` | B8 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 2 | 0 | 1 |
| kert | `examples/bank-front-knowledge-maps/90_control/ontology/customer-source-mapping.r2rml.ttl` | B8 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 2 | 0 | 1 |
| kert | `examples/bank-front-knowledge-maps/90_control/ontology/gits-core.owl.ttl` | B8 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 1 | 17 | 4 |
| kert | `examples/bank-front-knowledge-maps/90_control/ontology/gits-core.owl.ttl` | B8 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 1 | 17 | 4 |
| kert | `examples/bank-front-knowledge-maps/90_control/ontology/gits-core.owl.ttl` | B8 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 1 | 17 | 4 |
| kert | `examples/bank-front-knowledge-maps/90_control/ontology/gits-core.owl.ttl` | B8 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 1 | 17 | 4 |
| kert | `examples/bank-front-knowledge-maps/90_control/ontology/gits-core.owl.ttl` | B8 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 1 | 17 | 4 |
| kert | `examples/bank-front-knowledge-maps/90_control/ontology/gits-core.shacl.ttl` | B8 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 1 | 3 | 4 |
| kert | `examples/bank-front-knowledge-maps/90_control/ontology/gits-core.shacl.ttl` | B8 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 1 | 3 | 4 |
| kert | `examples/bank-front-knowledge-maps/90_control/ontology/products.ttl` | B8 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| kert | `examples/bank-front-knowledge-maps/90_control/ontology/products.ttl` | B8 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| kert | `examples/bank-front-knowledge-maps/90_control/schema/ontology_reference.json` | B8 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| kert | `examples/bank-front-knowledge-maps/90_control/schema/ontology_reference.json` | B8 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| kert | `specs/kert-openapi-v1.yaml` | B8 | W2_SPLIT | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 2 |
| kert | `specs/kert-openapi-v1.yaml` | B8 | W2_SPLIT | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 2 |
| kert | `specs/kert-openapi-v1.yaml` | B8 | W2_SPLIT | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 2 |
| kert | `src/kert/application/services.py` | B8 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| kert | `src/kert/application/skills.py` | B8 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 4 |
| kert | `src/kert/application/skills.py` | B8 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 4 |
| kert | `src/kert/application/skills.py` | B8 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 4 |
| kert | `src/kert/domain/activation_plan.py` | B8 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 2 |
| kert | `src/kert/domain/activation_plan.py` | B8 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 2 |
| kert | `src/kert/domain/activation_plan.py` | B8 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 2 |
| kert | `src/kert/domain/knowledge_source.py` | B8 | W3_CONSUMER_SWITCH | 含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改） | 0 | 0 | 1 |
| kert | `src/kert/dsh/static/rings.js` | B8 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |
| kert | `src/kert/infrastructure/runtime_store.py` | B8 | W3_CONSUMER_SWITCH | 无术语命中（仅随命名空间迁移） | 0 | 0 | 0 |

> **使用方式**：按 `handling` 分派 —— 『随 make generate』的交由制品流水线；『须显式清单』的**不得批处理**（见 `breakpoint-advisory/`）；其余可按通道机械执行。
> 未裁定四条断点出口前，涉及 `Customer / Product / Skill / Asset` 的项**不得开工**。

