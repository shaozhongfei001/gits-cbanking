# C05 既有 RAG、LightRAG 与 Kuzu 图服务适配合同

版本 1.0.0；状态 CONTRACT_CANDIDATE；需求 REQ-05。决策：保留既有向量 RAG 为基础证据检索；LightRAG 作为候选抽取/图辅助检索试验适配器；Kuzu 按用户指定用于 KERT 内隔离模拟图服务。

## 1. 是否应引入 LightRAG

建议引入一个可关闭的 LightRAG Spike，用相同资料和题集验证实体关系抽取与跨文档问题。它不是注册中心或知识地图审核系统。任务地图的 `requires/uses/dependsOn` 必须由任务/能力合同与审核决定形成，不能直接采用内容图中的共现边。

官方资料说明 LightRAG 提供实体/关系辅助检索、local/global/hybrid/naive/mix 模式；SDK 支持插入自定义图。官方支持存储列表未列 Kuzu，因此不声明原生兼容。Kuzu 官方仓库在 2025-10-10 归档，历史版本仍可使用，模拟环境拟锁定 0.11.3 并校验具体 wheel/hash。技术依据与访问日期见 references/技术依据与决策.md。

## 2. 三条路径

| 路径 | 实现 | 数据来源 | 正式可用条件 |
|---|---|---|---|
| 基础检索 | ExistingRagAdapter | 既有向量 RAG 的文档版本和片段 | 来源定位、权限、版本、用途过滤通过 |
| 图服务 | KuzuGraphAdapter | KERT 发布清单投影的节点/边 | 发布版本和边级来源/权限可校验 |
| LightRAG 试验 | LightRagAdapter（独立工作区） | 获准资料或已认定断言的自定义图投影 | 与基线比较获准；不直连权威写入口 |

LightRAG 工作区与 Kuzu 不共享底层数据库文件，不通过两套写入器维护同一权威图。首期不开发完整 Kuzu LightRAG storage 插件：候选阶段导出带来源关系，KERT 认定后投影到 Kuzu。若启用 LightRAG 在线图检索，优先把已认定内容按其自定义图接口写入独立可重建检索投影；此投影也非权威。接口能否无损保留边级时态/权限需 Spike 验证，不能凭自定义图 API 推定已满足。

## 3. 既有向量 RAG 的最低适配能力

必须尽可能复用 docId/sourceVersion、chunkId、原文定位、embedding model/version、集合版本、ACL 和检索接口。不得直接复用不兼容的旧向量空间；LightRAG 的实体/关系向量不等同于原文 chunk 向量。

LegacyRagHit 至少映射 sourceId、sourceVersion、fragmentId、locator、text、score、permissionDecisionRef。旧系统如果无法提供版本或 ACL，先完成适配与目录对账；只得到答案字符串时不能作为可认定的证据接口。禁止为了填充 EvidenceBundle 而编造页码或原文 hash。必要时从有权原文补取证据，原文也不可得则该路径不可用于关键结论。

普通问题直接走原有 RAG，无需 GraphRAG 包裹一层。可加关键词召回和重排，但这是独立增强，评估时不能将其收益全部归功于图。

## 4. Kuzu 模拟图模型

数据库/目录分离：candidate-graph 与 published/{releaseId}。同一物理库不能只凭一个易漏条件区分候选与正式图。每次发布从 KERT 源清单重建新投影，关闭旧写入器后只读打开对应发布目录；单写 Worker 排队，容量与并发通过模拟用例测量。

内容图节点：Entity、Assertion、SourceFragment。建议 Assertion 节点实体化，绑定 subject、predicate、object/value、validFrom/to、sourceVersion、scope、releaseId；避免一条合并边丢失多个来源、时间及冲突。导航图节点为 Task、Asset、Capability、Domain，与内容图节点类型区分。

GraphQueryPort 接受 queryId/version、parameters、releaseId、authorizedScope、maxHops/maxNodes/timeout；只允许注册查询。返回 paths、assertionRefs、sourceRefs、graphProjectionVersion、truncated、warnings；路径仅表示关系证据，不自动表明因果或准入。

图失效可以重建；普通 RAG/规则/指标路径仍可使用。若当前任务明确 graphRequired=true，图服务失败须拒绝该必需子任务，不能假装普通检索已经回答关系问题。

## 5. 权限传播与发布隔离

图中的标题、邻居、关系、摘要同样可能泄漏信息。检索前用授权语料空间隔离，检索中限制节点/边，装配前复核；跨权汇总形成的摘要不得仅在最后过滤引用就对外发布。摘要可见范围应不宽于其全部依赖的共同可见范围；无法证明时按授权分区重建或关闭该模式。

撤销 sourceVersion 后，通过 dependencyRefs 标记受影响 assertion/map/index；在线 deny-list 先阻断使用，后台删除/重建派生表示。索引删除是维护操作，不能删除受保留要求约束的原始证据；删除权限与审计保留权分别控制。

## 6. 试验设计：把收益拆开测

同一语料、模型、提示预算、权限和固定评测集下比较：A 既有 RAG；B 既有 RAG + 注册/地图路由；C 在 B 上加图检索/LightRAG。A→B 评估导航与治理收益，B→C 才是图增强增益。

题组：单条款、精确指标、客户准入、多文档产业关系、跨材料主题、同名实体、时间冲突、越权与撤销。指标与准入组不得交给 GraphRAG 计算/审批。建议初次功能集 60 题、独立留出 20 题；后续至少每组 30 题再报告稳定性。报告逐题证据、正确性、人审工时、构建与更新成本、延迟 p50/p95；不能仅用 LLM judge 总分。

试验启用门槛建议：关键权限/出处负例零失败；关系/主题组正确率相较 B 提高至少 10 个百分点且无关键退化；维护成本与新增业务价值经 Owner 明确接受。小样本须报告样本量、差异区间和失败个例；该阈值是待签合同目标，未报告为实际结果。

## 7. 退出与替换

Kuzu/LightRAG 依赖锁文件、制品校验和离线归档由开发 Loop 生成，不自动下载 latest。Kuzu 替换时仅 GraphQueryPort/投影适配变更，公共 ID、断言、地图、计划和证据合同不变。OpenSPG/KAG 本期不作为依赖；未来只有明确功能缺口与对照收益才新增 ADR。
