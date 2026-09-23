window.WALKTHROUGH_DATA = {
  "base": "http://127.0.0.1:15173",
  "generatedAt": "2026-09-23T07:18:51.380Z",
  "scenarios": [
    {
      "id": "flow-previsit-1",
      "flow": "访前链",
      "level": "L1",
      "name": "① 启动旅程（写路径）",
      "path": "/engagement",
      "howto": "左上「互动记录·访前路径」→ 点「启动旅程」",
      "expect": "顶部状态条由「旅程 未启动」→「旅程 INSIGHT_ANALYSIS / 完成旅程」；出现「待准备/准备完整度/活动时间线」",
      "assertHint": "应发出 201 POST /api/v1/engagement/journey/start",
      "captured": {
        "http": 200,
        "apiCount": 5,
        "apiBad": [],
        "api": [
          "200 /src/api/auth.ts",
          "200 /src/api/engagement.ts",
          "200 /src/api/v11.ts",
          "200 /api/v1/commitments",
          "200 /api/v1/engagement/customer?rmId=ALL"
        ],
        "mainLen": 159,
        "main": "⌕ ＋ 全局新建 ？♢亮色开开发会话总行公司金融部GITS Bank × 互动记录·访前路径 × 当前客户华东精工装备集团有限公司|旅程未启动切换客户启动旅程—准备完整度—待核实问题—客户参会人—关联需求关键工作0 / 3确认拜访目标与成功标准补齐行业/客户证据确定专家与会中分工活动时间线1 项请先选择客户并启动旅程",
        "emptyWords": [
          "未启动"
        ],
        "redLineHits": [],
        "absolutePaths": [],
        "shot": "shots/flow-previsit-1.jpg"
      }
    },
    {
      "id": "flow-previsit-2",
      "flow": "访前链",
      "level": "L1",
      "name": "② 访前目标与信息缺口",
      "path": "/engagement/previsit/gaps",
      "howto": "在①点「打开访前工作区 →」",
      "expect": "列出「已知 / 未知 / 优先问题」（如未知 ESG、冲突：实控人持股比例）；URL 带 journeyId",
      "assertHint": "数据源 GET /api/v1/engagement/kyc/{customerId}/gap-profile",
      "captured": {
        "http": 200,
        "apiCount": 4,
        "apiBad": [],
        "api": [
          "200 /src/api/auth.ts",
          "200 /src/api/engagement.ts",
          "200 /src/api/v11.ts",
          "200 /api/v1/commitments"
        ],
        "mainLen": 61,
        "main": "⌕ ＋ 全局新建 ？♢亮色开开发会话总行公司金融部GITS Bank × 访前目标与信息缺口 × 缺客户对象，暂无访前缺口",
        "emptyWords": [
          "暂无"
        ],
        "redLineHits": [],
        "absolutePaths": [],
        "shot": "shots/flow-previsit-2.jpg"
      }
    },
    {
      "id": "flow-previsit-3",
      "flow": "访前链",
      "level": "L1",
      "name": "③ 生成访前包（跨服务 KERT）",
      "path": "/engagement/previsit/evidence",
      "howto": "在②点「去证据装配」→ 点「生成访前包」",
      "expect": "空态文案「尚未执行一键访前」消失，出现**装配轨迹**（skillId / KM-CORP-RM-PREVISIT）",
      "assertHint": "应发出 200 POST /api/v1/engagement/journey/{id}/prepare-previsit",
      "captured": {
        "http": 200,
        "apiCount": 4,
        "apiBad": [],
        "api": [
          "200 /src/api/auth.ts",
          "200 /src/api/engagement.ts",
          "200 /src/api/v11.ts",
          "200 /api/v1/commitments"
        ],
        "mainLen": 157,
        "main": "⌕ ＋ 全局新建 ？♢亮色开开发会话总行公司金融部GITS Bank × 访前知识证据装配 × 只读消费既有 preparePrevisit 返回（唯一 KERT 入口）；无来源则空态，禁止无来源结论。 尚未执行一键访前。请先点击「生成访前包」触发 KERT（外联 + 会面 + R1 报告），装配轨迹将在此展示。",
        "emptyWords": [
          "尚未",
          "只读"
        ],
        "redLineHits": [],
        "absolutePaths": [],
        "shot": "shots/flow-previsit-3.jpg"
      }
    },
    {
      "id": "flow-previsit-4",
      "flow": "访前链",
      "level": "L1",
      "name": "④ 访前包预览",
      "path": "/engagement/previsit/pack",
      "howto": "在③点「去访前包」",
      "expect": "出现「外联脚本 / 会面脚本」等**实质交付物**文本，不再是「尚未生成访前包」",
      "assertHint": "同③的返回；不得为空态",
      "captured": {
        "http": 200,
        "apiCount": 4,
        "apiBad": [],
        "api": [
          "200 /src/api/auth.ts",
          "200 /src/api/engagement.ts",
          "200 /src/api/v11.ts",
          "200 /api/v1/commitments"
        ],
        "mainLen": 87,
        "main": "⌕ ＋ 全局新建 ？♢亮色开开发会话总行公司金融部GITS Bank × 访前包预览 × 尚未生成访前包。请先在「访前知识证据装配」点击「生成访前包」（KERT 一键访前）。",
        "emptyWords": [
          "尚未"
        ],
        "redLineHits": [],
        "absolutePaths": [],
        "shot": "shots/flow-previsit-4.jpg"
      }
    },
    {
      "id": "pc-interpretation",
      "flow": "产品解读（PC-i1）",
      "level": "L1",
      "name": "产品中心 · 产品解读",
      "path": "/product-center/PROD-CM-003",
      "howto": "左栏「产品中心」→ 选产品 → 滚到「P38 章级承接」",
      "expect": "8 章二选一（有数据渲正文 / 无数据具名「待接入」）；承接区标题为「章节标题 + 卡内第 N 节」；无绝对路径",
      "assertHint": "期望值来源 GET /api/v1/product-center/products/PROD-CM-003",
      "captured": {
        "http": 200,
        "apiCount": 11,
        "apiBad": [],
        "api": [
          "200 /src/api/auth.ts",
          "200 /src/api/engagement.ts",
          "200 /src/api/v11.ts",
          "200 /api/v1/commitments",
          "200 /src/api/productKnowledge.ts",
          "200 /src/api/productCenter.ts?t=1790134993175",
          "200 /api/v1/product-center/products",
          "200 /api/v1/product-center/families"
        ],
        "mainLen": 2973,
        "main": "⌕ ＋ 全局新建 ？♢亮色开开发会话总行公司金融部GITS Bank × 企业金融产品中心 × 法人账户透支PROD-CM-003·DEMO-PROD-CM-003·现金管理未发布受控版本OVERDRAFT_FACILITYSHORT_TERM_LIQUIDITYAUTOMATIC_REPAYMENT产品目的待核验使用方式待核验计息口径待核验适用主体待核验 收藏PC5 下载内部说明PC5 生成客观产品讲解提纲PC5产品适用边界不等于具体客户的适配或推荐结论。额度、期限、利率、费用、担保方式与办理时效以最终批复和协议约定为准，本页不作任何承诺。一句话定义法人账户透支是银行与对公客户签订协议，允许其在结算账户存款不足时在核定额度内透支的融资服务。审批与协议边界房地产开发、证券投资等禁止用途主体。解决什么业务问题核定透支额度，账户余额不足时自动透支。；存入资金自动偿还透支。产品不是什么房地产开发、证券投资等禁止用途主体。；禁止用于股权投资、证券投资等非经营用途。与相邻产品的客观差异配套产品：流动资金贷款。业务定义经营稳定、信用评级较高的中型及以上企业。对客 / RM 解释经营稳定、信用评级较",
        "emptyWords": [
          "尚未",
          "待接入",
          "待核验"
        ],
        "redLineHits": [],
        "absolutePaths": [],
        "shot": "shots/pc-interpretation.jpg"
      }
    },
    {
      "id": "an-operating",
      "flow": "经营分析",
      "level": "L1",
      "name": "经营指标分析",
      "path": "/analytics/operating-metrics",
      "howto": "侧栏「经营指标分析」",
      "expect": "机构表格有真实数据（非 503/空态）；可切换分布维度与时间",
      "assertHint": "GET /kert-api/v1/analytics/metrics… 应 200",
      "captured": {
        "http": 200,
        "apiCount": 10,
        "apiBad": [],
        "api": [
          "200 /src/api/auth.ts",
          "200 /src/api/engagement.ts",
          "200 /src/api/v11.ts",
          "200 /api/v1/commitments",
          "200 /src/api/analytics.ts",
          "200 /kert-api/v1/analytics/orgs",
          "200 /kert-api/v1/analytics/periods",
          "200 /kert-api/v1/analytics/dimensions"
        ],
        "mainLen": 544,
        "main": "⌕ ＋ 全局新建 ？♢亮色开开发会话总行公司金融部GITS Bank × 经营指标分析 × 经营指标分析按机构评价对公经营表现（客户规模 / 业务规模 / 盈利贡献 / 资产质量）；行=机构，分布维度为客户范围过滤条件。分布维度行业机构福建省分行时间2010-12分 析机构名称客户数比上月比年初新增客户数客户收入总额小企业贡献度非小企业贡献度账户总数销户数销户余额不动户数泉州分行810.0% ↑0.0% ↑035,886.4317,628.1118,258.322523924,781.255厦门分行790.0% ↑0.0% ↑034,646.4813,055.321,591.182844120,332.524三明分行730.0% ↑0.0% ↑029,930.6111,875.0918,055.522463417,769.352漳州分行670.0% ↑0.0% ↑028,562.611,92916,633.62352816,470.572客户指标分析 · 各成员对比（点击表格行切换重点）（万元）泉州分行81厦门分行79三明分行73漳州分行67泉州分行 · 12个月趋势（custCnt）",
        "emptyWords": [],
        "redLineHits": [],
        "absolutePaths": [],
        "shot": "shots/an-operating.jpg"
      }
    },
    {
      "id": "an-monitors",
      "flow": "经营分析",
      "level": "L1",
      "name": "指标监视器",
      "path": "/analytics/monitors",
      "howto": "侧栏「指标监视器」",
      "expect": "表格 + 告警图例；点击行联动趋势图",
      "assertHint": "GET /kert-api/v1/analytics/metrics?screen=monitor-balance 应 200",
      "captured": {
        "http": 200,
        "apiCount": 10,
        "apiBad": [],
        "api": [
          "200 /src/api/auth.ts",
          "200 /src/api/engagement.ts",
          "200 /src/api/v11.ts",
          "200 /api/v1/commitments",
          "200 /src/api/analytics.ts",
          "200 /kert-api/v1/analytics/orgs",
          "200 /kert-api/v1/analytics/periods",
          "200 /kert-api/v1/analytics/metrics?screen=monitor-balance&dim=INDUSTRY&orgId=350000&period=201012"
        ],
        "mainLen": 1058,
        "main": "⌕ ＋ 全局新建 ？♢亮色开开发会话总行公司金融部GITS Bank × 指标监视器 × 指标监视器核心业务量当期变动、存贷比水平与不良分布监控；主指标环比超 ±15% 的行红色告警（阈值可配置）。分布维度行业机构福建省分行时间2010-12分 析行业名称存款余额比上月比年初贷款余额比上月比年初发放贷款金额比上月结算量金额比上月居民服务和其他服务业476,255.710.5% ↑7.6% ↑379,553.63-2.5% ↓12.1% ↑30,589.66-5.4% ↓872,637.4914.4% ↑教育437,214.010.4% ↑6.6% ↑324,750.91-2.2% ↓-2.0% ↓22,768.391.2% ↑738,408.08-3.3% ↓金融业432,780.151.0% ↑8.8% ↑350,885.61-2.3% ↓13.6% ↑25,783.9-4.9% ↓729,208.711.1% ↑批发和零售业431,303.950.9% ↑7.7% ↑341,130.34-4.8% ↓4.2% ↑25,792.27-17.4% ↓733,268.32-4.0% ↓制",
        "emptyWords": [],
        "redLineHits": [],
        "absolutePaths": [],
        "shot": "shots/an-monitors.jpg"
      }
    },
    {
      "id": "an-segments",
      "flow": "经营分析",
      "level": "L1",
      "name": "细分客群分析",
      "path": "/analytics/segments",
      "howto": "侧栏「细分客群分析」",
      "expect": "客群结构画像（数量/户均价值）有真实数据",
      "assertHint": "GET /kert-api/v1/analytics/metrics?screen=segment-distribution 应 200",
      "captured": {
        "http": 200,
        "apiCount": 10,
        "apiBad": [],
        "api": [
          "200 /src/api/auth.ts",
          "200 /src/api/v11.ts",
          "200 /src/api/engagement.ts",
          "200 /api/v1/commitments",
          "200 /src/api/analytics.ts",
          "200 /kert-api/v1/analytics/periods",
          "200 /kert-api/v1/analytics/orgs",
          "200 /kert-api/v1/analytics/metrics?screen=segment-distribution&dim=INDUSTRY&orgId=350000&period=201012"
        ],
        "mainLen": 851,
        "main": "⌕ ＋ 全局新建 ？♢亮色开开发会话总行公司金融部GITS Bank × 细分客群分析 × 细分客群分析客群结构画像（数量 / 户均价值 / 基础账户）与分条线业务透视；行=维度成员，分段维度阈值由参数配置驱动。分布维度行业机构福建省分行时间2010-12分 析维度成员客户数占比比上月比年初平均存款余额平均贷款余额平均结算金额平均利润贡献平均持有产品数基本户数账户数居民服务和其他服务业4615.33%0.0% ↑0.0% ↑10,353.398,251.1718,970.38399.565.9630157金融业4013.33%0.0% ↑0.0% ↑10,819.58,772.1418,230.22393.325.6326144批发和零售业4013.33%0.0% ↑0.0% ↑10,782.68,528.2618,331.71420.636.6529118教育3913.00%0.0% ↑0.0% ↑11,210.628,326.9518,933.54374.776.1326136制造业3712.33%0.0% ↑0.0% ↑11,421.89,570.9119,273.22410.7",
        "emptyWords": [],
        "redLineHits": [],
        "absolutePaths": [],
        "shot": "shots/an-segments.jpg"
      }
    },
    {
      "id": "an-combo",
      "flow": "经营分析",
      "level": "L1",
      "name": "组合查询工具",
      "path": "/analytics/combo-query",
      "howto": "侧栏「组合查询工具」→ 设条件 → 查询",
      "expect": "返回客户清单（白名单校验 fail-closed）",
      "assertHint": "查询走 KERT 白名单；无结果须具名",
      "captured": {
        "http": 200,
        "apiCount": 8,
        "apiBad": [],
        "api": [
          "200 /src/api/auth.ts",
          "200 /src/api/engagement.ts",
          "200 /src/api/v11.ts",
          "200 /api/v1/commitments",
          "200 /src/api/analytics.ts",
          "200 /kert-api/v1/analytics/periods",
          "200 /kert-api/v1/analytics/orgs",
          "200 /kert-api/v1/analytics/dimensions"
        ],
        "mainLen": 179,
        "main": "⌕ ＋ 全局新建 ？♢亮色开开发会话总行公司金融部GITS Bank × 组合条件查询分析 × 组合条件查询分析客户级多条件圈选（营销 / 尽调名单）；数值条件由 KERT 白名单校验（fail-closed）。机构福建省分行时间2010-12客户名称模糊匹配信用等级不限企业规模不限所属行业不限数值条件存款时点金额≥ 总行级重点客户 战略客户 小企业查 询",
        "emptyWords": [],
        "redLineHits": [],
        "absolutePaths": [],
        "shot": "shots/an-combo.jpg"
      }
    },
    {
      "id": "acct-overview",
      "flow": "客户",
      "level": "L2",
      "name": "客户记录 · 经营总览",
      "path": "/customers/CUST-CORP-0003",
      "howto": "侧栏「客户全景」→ 选客户",
      "expect": "经营总览有真实数据；缺失项具名「待核验」",
      "assertHint": "—",
      "captured": {
        "http": 200,
        "apiCount": 11,
        "apiBad": [],
        "api": [
          "200 /src/api/auth.ts",
          "200 /src/api/engagement.ts",
          "200 /src/api/v11.ts",
          "200 /api/v1/commitments",
          "200 /api/v1/engagement/kyc/CUST-CORP-0003/gap-profile",
          "200 /api/v1/engagement/journey?customerId=CUST-CORP-0003",
          "200 /api/v1/engagement/claims?customerId=CUST-CORP-0003",
          "200 /api/v1/engagement/customer/CUST-CORP-0003/transactions"
        ],
        "mainLen": 1118,
        "main": "⌕ ＋ 全局新建 ？♢亮色开开发会话总行公司金融部GITS Bank × 客户记录·经营总览 × 编辑经营结论 原因：P04 仅授权 C0 只读消费；经营结论写回无本 Loop 合同。解除路径：后续 Loop 在合同批准后启用写 Action北京绿源环保集团低风险行业能源业规模大型客户层级重点客户风险等级低风险统一社会信用代码91110000MA1FL8XX5N注册资本1.00亿元客户经理张明远管辖区华北关系概要重点集团客户，旗下5家子公司，环保行业龙头，PPP项目经验丰富KYC缺口摘要3未知项海外环保项目布局碳中和技改资金缺口政府回款账期2部分已知旗下5家子公司经营状况PPP项目合同台账2过期项财务数据(2024年报)环保资质证书有效期优先问题：核实PPP项目投资总额口径获取最新财务报表确认碳中和技改资金来源机会信号关系变化已检测客户与政府合作方的关系调整，可能影响PPP项目回款节奏，需持续跟踪 置信度: 52% 2026/8/10产品机会已确认客户未来3年计划投入5亿元用于碳中和技术改造，可推荐绿色信贷专项方案 置信度: 76% 2026/7/22融资需求已检测客户正在推进3个大型",
        "emptyWords": [
          "只读"
        ],
        "redLineHits": [],
        "absolutePaths": [],
        "shot": "shots/acct-overview.jpg"
      }
    },
    {
      "id": "audit",
      "flow": "治理",
      "level": "L2",
      "name": "审计与权限",
      "path": "/audit-trace",
      "howto": "侧栏「审批与审计」→ 审计与权限",
      "expect": "审计条目可读；导出/验证权限为设计性禁用并具名原因",
      "assertHint": "禁用入口**不得**计为故障",
      "captured": {
        "http": 200,
        "apiCount": 5,
        "apiBad": [],
        "api": [
          "200 /src/api/auth.ts",
          "200 /src/api/engagement.ts",
          "200 /src/api/v11.ts",
          "200 /api/v1/commitments",
          "200 /api/v1/audit-trace"
        ],
        "mainLen": 674,
        "main": "⌕ ＋ 全局新建 ？♢亮色开开发会话总行公司金融部GITS Bank × 审计与权限 × 导出审计包 原因：无导出审计包 API，禁止导出。解除路径：待导出审计包 / 验权 API 纳入合同后由独立 Loop 启用验证权限 原因：无验证权限 API，禁止从前端验权写回。解除路径：待导出审计包 / 验权 API 纳入合同后由独立 Loop 启用只读消费 fetchAuditTrace。导出审计包与验证权限未授权。实体类型实体ID操作人时间实体类型实体ID操作操作人角色关联ID2026-08-12T17:00:00ZHumanGatehg-0005-d01-evidenceDECIDEP-RISK-001COMPLIANCE_OFFICERcorr-jny-0012026-08-12T14:30:00ZCrmWritebackCommandcrm-cmd-0002DECIDEP-RM-001RELATIONSHIP_MANAGERcorr-jny-0012026-08-12T14:30:00ZHumanGatehg-0003-c01-planDECIDEP-RM-001RELATIONSH",
        "emptyWords": [
          "只读"
        ],
        "redLineHits": [],
        "absolutePaths": [],
        "shot": "shots/audit.jpg"
      }
    },
    {
      "id": "signals",
      "flow": "信号",
      "level": "C",
      "name": "经营信号对象主页",
      "path": "/signals",
      "howto": "侧栏「经营信号」",
      "expect": "信号卡可读；对无画像客户（CUST-CORP-0004/0005）的请求会 404 ⇒ 记 BLOCKED（数据缺口）",
      "assertHint": "已定性：数据缺口非接口缺陷",
      "captured": {
        "http": 200,
        "apiCount": 39,
        "apiBad": [
          "404 GET /api/v1/engagement/kyc/CUST-CORP-0005/gap-profile",
          "404 GET /api/v1/engagement/kyc/CUST-CORP-0004/gap-profile",
          "404 GET /api/v1/engagement/kyc/CUST-CORP-0006/gap-profile"
        ],
        "api": [
          "200 /src/api/auth.ts",
          "200 /src/api/engagement.ts",
          "200 /src/api/v11.ts",
          "200 /api/v1/commitments",
          "200 /api/v1/engagement/customer?rmId=ALL",
          "200 /api/v1/engagement/kyc/CUST-CORP-0003/gap-profile",
          "200 /api/v1/engagement/customer/CUST-CORP-0003/transactions",
          "200 /api/v1/engagement/claims?customerId=CUST-CORP-0003"
        ],
        "mainLen": 425,
        "main": "⌕ ＋ 全局新建 ？♢亮色开开发会话总行公司金融部GITS Bank × 经营信号对象主页 × 批量指派 原因：本 Loop 禁止信号写回；即使存在 confirm/dismiss 合同也不作为页面主动作。解除路径：后续 Loop 在明确授权后启用受控写 Action筛选信号内容或客户 互动对象 经营旅程 C1 候选列表：由 fetchCustomers + fetchCustomerContext.opportunitySignals 装配，不等于自动执行。互动对象打开 P10 列表；经营旅程打开 P11 访前路径工作台（在那里启动旅程）。客户与政府合作方的关系调整，可能影响PPP项目回款节奏，需持续跟踪北京绿源环保集团关系变化已检测客户未来3年计划投入5亿元用于碳中和技术改造，可推荐绿色信贷专项方案北京绿源环保集团产品机会已确认客户正在推进3个大型污水处理PPP项目，总投资约8亿元，有绿色债券发行融资需求北京绿源环保集团融资需求已检测",
        "emptyWords": [],
        "redLineHits": [],
        "absolutePaths": [],
        "shot": "shots/signals.jpg"
      }
    }
  ]
};
