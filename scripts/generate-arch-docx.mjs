import { Document, Packer, Paragraph, TextRun, ImageRun, HeadingLevel, AlignmentType, TableOfContents, PageNumber, Header, Footer, Table, TableRow, TableCell, WidthType } from 'docx';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.join(__dirname, '..');
const OUT = path.join(ROOT, 'docs', 'GITS-KNO-当前架构设计解读-DKWS.docx');
const INK = '2d3142', MUTED = '4f5d75', ACCENT = 'eb6c36', LINK = '2e5aa8', HDR_BG = 'f0f1f4';

const p = (text, o = {}) => new Paragraph({ spacing: { after: o.after ?? 120, line: 320 }, children: [new TextRun({ text, size: o.size || 22, color: o.color || INK, bold: o.bold, italics: o.italics })] });
const h1 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_1, spacing: { before: 320, after: 160 }, children: [new TextRun({ text: t, size: 32, bold: true, color: INK })] });
const h2 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_2, spacing: { before: 240, after: 120 }, children: [new TextRun({ text: t, size: 27, bold: true, color: ACCENT })] });
const h3 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_3, spacing: { before: 180, after: 100 }, children: [new TextRun({ text: t, size: 24, bold: true, color: LINK })] });
const bullet = (t, lv = 0) => new Paragraph({ bullet: { level: lv }, spacing: { after: 80, line: 300 }, children: [new TextRun({ text: t, size: 22, color: INK })] });
const kv = (l, v) => new Paragraph({ spacing: { after: 60, line: 300 }, children: [new TextRun({ text: `${l}：`, size: 22, bold: true, color: INK }), new TextRun({ text: v, size: 22, color: INK })] });
const img = (file, w, h, cap) => [
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 120, after: 60 }, children: [new ImageRun({ data: fs.readFileSync(path.join(ROOT, 'diagrams', file)), transformation: { width: w, height: h } })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 160 }, children: [new TextRun({ text: cap, size: 18, italics: true, color: MUTED })] }),
];
const cell = (t, o = {}) => new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: t, size: o.size || 20, bold: o.bold, color: o.color || INK })], spacing: { after: 0 } })], shading: o.shading ? { fill: o.shading } : undefined, width: o.width ? { size: o.width, type: WidthType.PERCENTAGE } : undefined });
const tbl = (rows, widths) => new Table({ width: { size: 100, type: WidthType.PERCENTAGE }, rows: rows.map((r, i) => new TableRow({ children: r.map((c, j) => cell(c, { bold: i === 0, shading: i === 0 ? HDR_BG : undefined, width: widths ? widths[j] : undefined })) })) });

const C = [];

// 封面
C.push(
  new Paragraph({ spacing: { before: 2400, after: 200 }, alignment: AlignmentType.CENTER, children: [new TextRun({ text: 'GITS-KNO', size: 64, bold: true, color: ACCENT })] }),
  new Paragraph({ spacing: { after: 400 }, alignment: AlignmentType.CENTER, children: [new TextRun({ text: '银行客户经理持续经营 · 知识工程平台', size: 40, bold: true, color: INK })] }),
  new Paragraph({ spacing: { after: 800 }, alignment: AlignmentType.CENTER, children: [new TextRun({ text: '当前架构设计解读（含 DKWS 场景层）', size: 28, color: MUTED })] }),
  new Paragraph({ spacing: { after: 100 }, alignment: AlignmentType.CENTER, children: [new TextRun({ text: '版本 V2.0 · 2026-08-22', size: 22, color: MUTED })] }),
  new Paragraph({ spacing: { after: 100 }, alignment: AlignmentType.CENTER, children: [new TextRun({ text: '分支 feature/P24-dkws-supplychain · HEAD 2e1118d', size: 20, color: MUTED })] }),
  new Paragraph({ spacing: { before: 1200 }, alignment: AlignmentType.CENTER, children: [new TextRun({ text: '本解读面向人类架构师，采用非技术语言描述系统结构、决策与演进', size: 20, italics: true, color: MUTED })] }),
  new Paragraph({ children: [new TextRun({ text: '\n\n\n', size: 20 })] }),
  new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun({ text: '目录', size: 32, bold: true, color: INK })] }),
  new TableOfContents('目录', { hyperlink: true, headingStyleRange: '1-3' }),
  new Paragraph({ children: [new TextRun({ text: '\n', size: 20 })] }),
);

// 1 概述
C.push(
  h1('1. 项目概述：一句话讲清楚这个系统'),
  p('GITS-KNO 是一个面向银行客户经理的「持续经营知识工程平台」。它的核心任务是：把客户经理在经营客户过程中产生的散乱信息，变成结构化的、可推理、可追溯的「客户知识」，并在合适的时候以合适的形态推送给合适的人。'),
  p('如果把传统 CRM 比作「客户信息的电子病历本」，那么 GITS-KNO 更像「客户的智慧档案室」——它不仅记录事实，还能把事实组织成线索（如 KYC 洞察、机会信号），并约束 AI 只能在人工确认的框架内行动。'),
  p('平台围绕一条主线运行：客户经理开启旅程 → 系统采集上下文与证据 → 语义推理与 LLM 生成洞察 → 规则引擎筛选机会 → 人工确认 → 执行动作并沉淀证据 → 知识回流。这条主线由「旅程引擎」编排，由「DKWS 知识平台」提供可信知识底座。'),
  kv('定位', '银行客户经理持续经营知识工程平台（人机共读、AI 受控）'),
  kv('当前阶段', 'P24 DKWS 供应链图谱 Loop（全部 Gate 完成，待独立 QA）'),
  kv('代码规模', '7 个领域模块 + 4 个适配器 + 2 个应用 + 1 个 Python 场景平台 + Vue3 前端'),
);

// 2 总体架构
C.push(
  h1('2. 总体架构：一个分层解耦的六边形系统'),
  p('系统采用「六边形架构 + Spring Modulith 模块化」组织。简单说：业务规则放在内核（modules），外部技术（数据库、Oracle、语义库、知识文件）放在外围（adapters），两者之间只通过「接口约定」（Port）通信，不直接互相依赖。这样做的收益是：换数据库、换语义引擎、换知识来源，都不会污染业务逻辑。'),
  ...img('dkws-system-architecture.png', 620, 349, '图 1 · GITS-KNO 系统架构图（橙色为 DKWS 场景层）'),
  h2('2.1 四个大层'),
  tbl([
    ['层', '目录', '职责', '通俗解释'],
    ['领域核心层', 'modules/', '7 个领域模块', '系统的「大脑」，只懂业务不懂技术'],
    ['适配防腐层', 'adapters/', '4 个适配器', '系统的「翻译官」，把外部技术翻译给大脑'],
    ['应用组装层', 'apps/', 'api + worker', '系统的「指挥部」，负责把模块组装成可运行的服务'],
    ['场景执行层', 'scenario/', 'execute + seed + dkws-platform', '系统的「演练场」，模拟真实业务并生产演示知识'],
    ['前端展示层', 'frontend/', 'Vue3 工作台', '客户经理的「操作界面」'],
  ], [16, 16, 26, 42]),
  h2('2.2 三大支柱'),
  bullet('六边形架构：内核不依赖任何框架，通过 Port 接口对外，外部适配器实现 Port。'),
  bullet('合同驱动（Contract-First）：所有 API 先在 OpenAPI 合同定义，生成代码后再写实现，`make check` 校验合同哈希一致性。'),
  bullet('事件驱动：核心操作后发布 CloudEvent，由 worker 异步消费，模块间松耦合。'),
);

// 3 六大决策
C.push(
  h1('3. 六大设计决策（为什么这么设计）'),
  h2('3.1 语义与运营双核（ADR-0001）'),
  p('系统拆成「语义层」与「运营层」两个核心。语义层负责「理解」——把散乱事实变成本体推理可用的知识（Apache Jena）；运营层负责「执行」——客户旅程、机会、任务等日常经营动作。两者通过事件解耦，互不阻塞。'),
  h2('3.2 六边形端口-适配器（ADR-0002/0011）'),
  p('模块之间禁止直接依赖实现类，必须通过 Port 接口。例如领域层定义 ClaimReconciliationPort，适配层提供 DMN 规则实现与手写回退实现，配置切换即可，业务代码不变。'),
  h2('3.3 数据库策略：主库 + 只读源（ADR-0003）'),
  p('本地开发默认 H2 内存库（MySQL 兼容模式），无需安装数据库；生产主库为 PostgreSQL，Oracle 仅作只读数据源。Flyway 迁移脚本维护 H2/MySQL 双方言，种子数据自动加载。'),
  h2('3.4 AI 受控边界（AI_GUIDE + 红线）'),
  p('AI 只能产出候选 Claim/Proposal，不能直接写入权威事实；正式 ControlledAction 必须经人工确认、权限复核、幂等校验与回执。开发角色只能记录 DEV_SELF_CHECK_PASS，QA_PASS 只能由独立 QA 记录。'),
  h2('3.5 合同 SSOT（CONTRACT_INDEX + generated/）'),
  p('specs/CONTRACT_INDEX.yaml 是唯一合同注册入口；generated/ 全部由 make generate 生成、禁止手工修改；合同变化必须先改权威源、再生成、再实现。'),
  h2('3.6 知识服务模拟平台（DKWS）'),
  p('为验证「文件目录型数据知识服务」的可行性，项目在 scenario/dkws-platform 用 Python 实现了 DKWS：以五层工作区承载原始数据 → 加工 → 核心知识 → 服务投影 → 控制 的完整知识生产链路，P0-P9 十阶段管线落地契约化、幂等、人工审核、发布回滚等企业级要求。它是当前 P24 Loop 的主角。'),
);

// 4 DKWS 详解
C.push(
  h1('4. DKWS：文件目录型数据知识服务模拟平台'),
  h2('4.1 DKWS 是什么、解决什么问题'),
  p('DKWS（Data-Knowledge Workspace Service）是一个「用文件目录当数据库、用契约当 Schema、用人工审核当权限控制」的知识生产平台。它的出发点很朴素：把任何知识（产品知识、供应链图谱、客户 360°、规则）都装进一套统一的目录 + 契约 + 管线里，让 AI 可以可信地消费这些知识。'),
  p('它解决的三大问题：'),
  bullet('知识可信：MANIFEST + SHA-256 幂等校验，重复执行不产生脏数据；'),
  bullet('知识受控：系统禁止自签 OWNER/QA，知识必须经人工确认才能发布；'),
  bullet('知识服务化：发布后产出 Parquet/向量/图/规则四种投影，CLI 与 HTTP 双通道提供服务。'),
  ...img('dkws-business-flowchart.png', 620, 349, '图 2 · 端到端业务流程与 DKWS P0-P9 管线'),
  h2('4.2 五层工作区'),
  tbl([
    ['编号', '名称', '作用', '典型内容'],
    ['01', 'raw 原始接入', '承接所有原始材料', 'xlsx、md、外部报告'],
    ['02', 'work 加工产物', '清洗、规范化、切片', 'Parquet(zstd)、U/Q 标记'],
    ['03', 'core 核心知识', '受控知识本体', 'KE 元素、知识地图、规则'],
    ['04', 'serve 服务投影', '面向服务的形态', '向量、图、规则文件'],
    ['90', 'control 控制', '契约、清单、发布状态', 'MANIFEST、Release、CURRENT'],
  ], [12, 22, 28, 38]),
  h2('4.3 P0-P9 十阶段管线'),
  tbl([
    ['阶段', '名称', '产出'],
    ['P0', '初始化', '五层工作区目录骨架'],
    ['P1', '契约化', '20+ 文件 MD 契约模板（knowledge-map、tasks、activation、rules）'],
    ['P2', '原始接入', 'MANIFEST + SHA-256 幂等'],
    ['P3', '结构化清洗', 'Parquet（zstd 压缩，可降级 CSV）'],
    ['P4', '文档登记', '规范化 + 稳定切片'],
    ['P5', '知识候选', '冲突检测 + 人工审核门禁'],
    ['P6', '发布', 'Release + CURRENT + 回滚'],
    ['P7', '服务投影', 'Parquet / 向量 / 图 / 规则'],
    ['P8', '服务供给', 'CLI query/search/rule + 可选 HTTP'],
    ['P9', '安全与验收', '安全基线 + 性能 + E2E'],
  ], [10, 22, 68]),
  h2('4.4 DKWS 在系统中的角色'),
  bullet('知识供给：通过 KnowledgeAssembler 读取 DKWS 知识资产，为供应链图谱、产品知识等场景提供数据源；'),
  bullet('人机共读：知识地图/目录/契约由机器可读的文件承载，同时人可直接阅读 Markdown；'),
  bullet('合规演示：作为「文件目录型知识服务」的模拟平台，验证企业级知识治理（幂等、审核、发布、回滚）在目录形态下可行。'),
);

// 5 P24
C.push(
  h1('5. P24 当前工作：供应链图谱知识服务'),
  h2('5.1 目标'),
  p('在 DKWS 平台上打通「供应链图谱」知识的生产与消费闭环：由 DKWS 生产供应链图谱知识资产，后端 KnowledgeAssembler 组装成供应链图谱 Markdown，前端以力导向图展示，客户经理据此洞察客户上下游关联。'),
  h2('5.2 已完成的 Gate（10/10 PASS，待独立 QA）'),
  bullet('G1 供应链图谱 DTO 与合同：SupplyChainGraphNode/Edge/Report 等与 OpenAPI 对齐；'),
  bullet('G2 供应链图谱 API：SupplyChainGraphController 提供图谱查询端点；'),
  bullet('G3 知识组装：KnowledgeAssembler.supplyChainMarkdown 组装 DKWS 知识；'),
  bullet('G4 前端可视化：SupplyChainGraphReport + SupplyChainForceGraph（ECharts 力导向图）；'),
  bullet('G5 集成与回退：供应链图谱与客户上下文、KYC 洞察联动；'),
  bullet('G6 后端测试 + 前端类型检查 + E2E 影子验证。'),
);

// 6 模块清单
C.push(
  h1('6. 模块清单：七个领域模块一张表'),
  tbl([
    ['模块', '职责', '关键 Port/接口', '依赖'],
    ['operational-ontology', '运营本体：客户、声明、机会、KYC', 'ClaimReconciliationPort、DomainEventPublisher', '无框架'],
    ['semantic-runtime', '语义推理：本体、图谱', '（经 Jena 适配器）', 'Jena'],
    ['context-evidence', '客户上下文与证据采集', 'EvidencePort', '事件'],
    ['human-action', '人工动作门禁、CRM 回写', 'CrmWritebackChannel', '外部 CRM'],
    ['evaluation', '评估评分、KYC 洞察', 'KycInsightPort', '本体'],
    ['scenario-customer-journey', '旅程编排：开场/回访/新证据', 'JourneyPort', '事件'],
    ['scenario-hermes', '场景知识提供（LLM 读图方案A）', 'KnowledgeWikiPort', 'LLM'],
  ], [22, 28, 30, 20]),
);

// 7 技术栈
C.push(
  h1('7. 技术栈一览'),
  ...img('dkws-tech-stack.png', 620, 349, '图 3 · GITS-KNO 分层技术栈'),
  h2('7.1 后端'),
  bullet('Java 21 + Spring Boot 3.5 + Spring Modulith（模块化架构强制）'),
  bullet('MyBatis（XML Mapper + resultMap 显式映射）+ Flyway 迁移（H2/MySQL 双方言）'),
  bullet('Apache Jena（语义图谱/本体推理）、KIE DMN（规则引擎）'),
  bullet('CloudEvent 事件 + Zipkin 链路 + Micrometer/Prometheus 指标 + JSON 结构化日志'),
  h2('7.2 前端'),
  bullet('Vue3 + TypeScript + Vite + Pinia + vue-query（TanStack Query）'),
  bullet('Naive UI（主）+ TDesign Vue Next（辅助，仅缺口组件）'),
  bullet('ECharts（图表，含供应链力导向图）、Tailwind CSS'),
  h2('7.3 场景与工程'),
  bullet('DKWS 平台：Python（scenario/dkws-platform，pytest 54 项）'),
  bullet('构建：Maven + Makefile（generate/check/test/evidence）· 测试：JUnit5/AssertJ/Mockito + Vitest + Playwright'),
);

// 8 数据流
C.push(
  h1('8. 一次完整旅程的数据流（讲故事）'),
  h2('8.1 正向主线'),
  bullet('① 客户经理在前端工作台发起旅程（开场）→ ② API 网关鉴权（X-API-KEY）→ ③ 旅程引擎编排 → ④ 上下文与证据采集 → ⑤ 语义推理 + LLM 生成 KYC 洞察 → ⑥ DMN 规则筛选机会信号、生成任务 → ⑦ 人工确认门禁 → ⑧ 执行动作（任务/CRM 回写）→ ⑨ 报告与证据沉淀 → ⑩ 知识回流 DKWS。'),
  h2('8.2 知识回流支线'),
  bullet('沉淀的证据进入 DKWS P2 原始接入 → P3 清洗 → P4 登记 → P5 知识候选（人工审核）→ P6 发布 → P7 投影 → P8 服务供给；知识再经 KnowledgeAssembler 回流到洞察阶段，形成闭环。'),
  h2('8.3 事件驱动细节'),
  bullet('EngagementOrchestrator 在 startJourney/postvisit/newEvidence 后发布领域事件；KycInsightService 在 claimCandidateRecorded 后发布；CrmWritebackService 在 controlledActionRequested 后发布；worker 异步消费，模块间不直接调用。'),
);

// 9 演进
C.push(
  h1('9. 演进方向与已知约束'),
  h2('9.1 演进方向'),
  bullet('DKWS 生产可用：启动时内存索引替代每请求扫盘；knowledge-architecture 集成进 apps/api 运行时；按 classification 过滤权限；单向权威流保障。'),
  bullet('供应链图谱深化：图谱推理（多级上下游）、图谱与 KYC 洞察联动。'),
  bullet('人侧共读：评估 BookStack/Outline 或自建「人机共读」界面。'),
  h2('9.2 已知约束与风险'),
  bullet('OpenWiki 评估结论为不引入（权限/内网 CDN/非结构化三大硬伤），见 docs/architecture/OPENWIKI_CODE_LEVEL_ASSESSMENT.md。'),
  bullet('真实平台选型（RAG/GraphDB/MetadataCatalog）留空待 Owner 指定。'),
  bullet('apps/api 存量 JaCoCo 行覆盖率门槛 0.80，P23 已通过补测达标，后续需持续维护。'),
);

// 10 术语
C.push(
  h1('10. 术语速查表'),
  tbl([
    ['术语', '通俗解释'],
    ['Port（端口）', '领域层定义的能力接口，如 ClaimReconciliationPort'],
    ['Adapter（适配器）', '实现 Port 的外部对接代码，如 DMN 适配器、MyBatis 适配器'],
    ['六边形架构', '内核 + 外围通过接口解耦的架构风格'],
    ['Spring Modulith', 'Spring 官方模块化工具，强制模块边界与依赖方向'],
    ['云事件（CloudEvent）', '跨模块事件的标准载体'],
    ['DKWS', '文件目录型数据知识服务模拟平台（P24 主角）'],
    ['KE 元素', '知识工程元素，最小可管理知识单元'],
    ['知识地图', '知识资产的目录/索引，人机共读'],
    ['供应链图谱', '客户上下游关联的可视化知识（P24 正在做）'],
  ], [26, 74]),
  new Paragraph({ spacing: { before: 400 }, children: [new TextRun({ text: '—— 全文完 · 本文档随分支演进同步维护 ——', size: 20, italics: true, color: MUTED })] }),
);

const doc = new Document({
  styles: { default: { document: { run: { font: '微软雅黑', size: 22, color: INK } } } },
  features: { updateFields: true },
  sections: [{
    properties: {},
    headers: { default: new Header({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ text: 'GITS-KNO 架构解读 · V2.0', size: 16, color: MUTED })] })] }) },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: '第 ', size: 18, color: MUTED }), new TextRun({ children: [PageNumber.CURRENT], size: 18, color: MUTED }), new TextRun({ text: ' 页', size: 18, color: MUTED })] })] }) },
    children: C,
  }],
});

Packer.toBuffer(doc).then((buf) => {
  fs.writeFileSync(OUT, buf);
  console.log('OK ->', OUT, buf.length, 'bytes');
}).catch((e) => { console.error(e); process.exit(1); });
