# Architecture Decision Record Index

| ADR | 决策 | 状态 | 关键边界 |
|---|---|---|---|
| ADR-0001 | 可编译语义合同＋运行本体控制平面 | Accepted for engineering candidate | 关系库权威状态；RDF/搜索/向量为投影 |
| ADR-0002 | 模块化单体API＋独立Worker | Accepted for engineering candidate | 不提前引入微服务、Kafka、Temporal/Camunda |
| ADR-0003 | 生产关系数据库 | Open | 本地候选不反向决定生产数据库 |
| ADR-0004 | Apache Ossie | Conditional/Experimental | 仅交换Profile，不进核心和写回热路径 |
| ADR-0005 | 展示直接传递 | Accepted with boundary | 仅Experience/BFF可返回厂商展示对象 |
| ADR-0006 | Java 包名统一到 com.gien.gits | Accepted | owner批准；com.gientech.hzb.kno → com.gien.gits（仅Java包） |
| ADR-0007 | Oracle EDwCRM 只读访问启用 | Accepted with read-only boundary | DATA_OWNER已授权；只读强制；专用loop P1-oracle-readonly |
| ADR-0008 | 领域前缀与标识 hzb→gits | Accepted | owner批准；合同/URI/事件/制品名统一 gits；历史证据日志不回写 |
| ADR-0009 | gits:Customer Spike 权威源 A_ZHCX_CUST_BASE | Accepted spike_only (superseded for promotion by ADR-0010) | 源定位确认；正式化见 ADR-0010 / P4 |
| ADR-0010 | 引入 gits:Customer 语义类并正式登记 Source Contract | Accepted | 语义合同层；CTR-DATA-002；CTR-MAP-001→versioned_mapping；不进运营控制面；loop P4 |
| ADR-0011 | 六边形架构 (Ports & Adapters) | Accepted | 领域核心零基础设施依赖；适配器实现端口接口 |
| ADR-0012 | DMN引擎选型 — 轻量XML解析 vs KIE | Accepted | 选择轻量XML解析避免Jakarta/Javax冲突 |
| ADR-0013 | 可观测性技术栈选择 | Accepted | Micrometer+Prometheus+Zipkin+Logstash |
| ADR-0014 | Scenario 目录聚合重组 | Accepted | scenario/execute（原scenario-hermes）+ scenario/seed（原scenario_data）；Java包名不变 |
| ADR-0015 | Wiki-first知识架构与本体运行融合 | Proposed for P20 Owner review | Knowledge Map控制发现与路由；本体负责对象、关系、状态和约束 |
| ADR-0016 | 统一ActivationPlan作为双路径执行合同 | Proposed for P20 Owner review | Wiki/Ontology双路径必须汇合为版本化、可校验、可回放计划 |
| ADR-0017 | OpenWiki知识投影边界 | Proposed for P20 Owner review | OpenWiki仅为可替换投影和阅读入口，不是权威源或本体运行时 |
| ADR-0018 | Oracle 数据集市数据理解能力迁出至 Leibniz-KERT，废弃 OracleSourcePort | Accepted pending cross-repo execution | owner批准；数据理解由DKWS维护，GITS仅经Python Core公共HTTP消费；OracleSourcePort(claim表)零消费者予以废弃；specs/data标migration不删除；loop P38-oracle-deprecation(blocked) |

正式版本、Owner、日期、替代方案、后果和验证证据将在对应ADR评审时补齐；本索引不能替代ADR批准。
