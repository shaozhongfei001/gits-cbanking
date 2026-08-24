const P = require('pptxgenjs');
const p = new P(); p.layout = 'LAYOUT_WIDE'; p.title = 'GITS-KNO 架构图集';
const C = {bg:'F8F9FB',dk:'2D3142',md:'4F5D75',lt:'7A8399',bl:'2E5AA8',or:'E86C36',gn:'42B883',wb:'FFFFFF',bd:'D0D5DD',ob:'FFE0C0',dep:'B0B5BF',pu:'7C3AED',yBg:'FEFCE8',pBg:'FDF2F8',bBg:'EFF6FF',gBg:'F0FDF4',gry:'F1F5F9'};
function box(s,x,y,w,h,f,l,lw,r){s.addShape(p.shapes.ROUNDED_RECTANGLE,{x,y,w,h,fill:{color:f},line:{color:l,width:lw||0.5},rectRadius:r||0.04})}
function txt(s,x,y,w,h,t,sz,c,b,a,f){s.addText(t,{x,y,w,h,fontSize:sz,bold:!!b,color:c,align:a||'center',fontFace:f})}
function zn(s,x,y,w,h,f,l,lw){s.addShape(p.shapes.RECTANGLE,{x,y,w,h,fill:{color:f},line:{color:l,width:lw||0.5}})}
function ar(s,x,y,w,h,c,d){s.addShape(p.shapes.LINE,{x,y,w:h<0?w:0,h:h<0?-h:h,line:{color:c||C.md,width:1.2,endArrowType:'triangle',dashType:d||'solid'}})}

// ═══ SLIDE 1 系统架构 ═══
const s1=p.addSlide();s1.background={fill:C.bg};
txt(s1,0.3,0.06,12.7,0.3,'GITS-KNO 系统架构',20,C.dk,true);
txt(s1,0.3,0.34,12.7,0.18,'DKWS = Skill运行时 + 知识工程 + 银行数据统一访问适配层',10,C.md);

// ZONE A
zn(s1,0.3,0.58,12.7,0.82,C.bBg,'BFDBFE',1);
txt(s1,0.4,0.6,4,0.18,'ZONE A · 前端 (frontend)',9,C.md,true);
txt(s1,0.4,0.76,4,0.13,'Vue3 + Naive UI + Tailwind + ECharts',8,C.lt);
['客户经营工作台','知识地图浏览器','供应链图谱','访前/访后报告','脚本生成/产品匹配'].forEach((n,i)=>{
  box(s1,0.4+i*2.5,0.9,2.35,0.4,C.wb,'93C5FD',0.8);
  txt(s1,0.4+i*2.5,0.94,2.35,0.28,n,10,C.dk,true);
});

// ZONE B
zn(s1,0.3,1.5,12.7,1.05,C.gBg,'BBF7D0',1);
txt(s1,0.4,1.52,4,0.18,'ZONE B · 应用服务 (apps)',9,C.md,true);
txt(s1,0.4,1.68,4,0.13,'Spring Boot · 端口驱动装配',8,C.lt);
// B1
box(s1,0.4,1.82,3.5,0.62,C.wb,'86EFAC',0.8);
txt(s1,0.4,1.84,3.5,0.16,'API 服务 (8080)',10,C.dk,true);
txt(s1,0.4,1.98,3.5,0.12,'客户旅程编排 · KYC洞察服务',8,C.md);
txt(s1,0.4,2.09,3.5,0.12,'客户上下文服务 · 报告生成',8,C.md);
txt(s1,0.4,2.2,3.5,0.12,'供应链图谱 · 知识装配',8,C.md);
// B2
box(s1,4.05,1.82,2.2,0.62,C.wb,'86EFAC',0.8);
txt(s1,4.05,1.84,2.2,0.16,'Worker (8090)',10,C.dk,true);
txt(s1,4.05,1.98,2.2,0.12,'领域事件消费',8,C.md);
txt(s1,4.05,2.09,2.2,0.12,'异步任务处理',8,C.md);
// B3
box(s1,6.4,1.82,2.4,0.62,C.ob,C.pu,1.5);
txt(s1,6.4,1.84,2.4,0.16,'DKWS Skill 供给',10,C.pu,true);
txt(s1,6.4,1.98,2.4,0.12,'Skill执行端口 · DSH HTTP适配器',8,C.md);
txt(s1,6.4,2.09,2.4,0.12,'降级Skill适配器 · LLM降级',8,C.md);
txt(s1,6.4,2.2,2.4,0.12,'替代知识文件系统',7,C.pu,true);
// B4
box(s1,8.95,1.82,2.3,0.62,C.wb,'86EFAC',0.8);
txt(s1,8.95,1.84,2.3,0.16,'场景执行 (scenario)',10,C.dk,true);
txt(s1,8.95,1.98,2.3,0.12,'模拟知识供给',8,C.md);
txt(s1,8.95,2.09,2.3,0.12,'知识装配结果',8,C.md);

// ZONE C
zn(s1,0.3,2.68,12.7,1.15,C.yBg,'FDE68A',1);
txt(s1,0.4,2.7,6,0.18,'ZONE C · 领域模块 (modules)',9,C.md,true);
txt(s1,0.4,2.86,6,0.13,'端口接口驱动 · 纯业务逻辑 · 无框架依赖',8,C.lt);
const mods=[
  {n:'运营本体',p:['声明调解','领域事件发布','场景数据供给','Oracle数据源']},
  {n:'客户旅程',p:['LLM客户端','Skill执行','CRM回写通道','评估']},
  {n:'知识架构',p:['知识地图·知识要素','知识百科·资产目录','激活契约·路由策略','DKWS数据投影(待集成)'],dkws:3},
  {n:'人工动作',p:['审计日志','任务·承诺','机会·外部事件','录音授权']}
];
mods.forEach((m,i)=>{
  const mx=0.4+i*3.15,mw=m.dkws?2.7:2.5;
  box(s1,mx,3.0,mw,0.72,C.wb,'FCD34D',0.8);
  txt(s1,mx,3.02,mw,0.15,m.n,10,C.dk,true);
  m.p.forEach((pt,j)=>{
    const isDkws=m.dkws&&j===m.dkws-1;
    txt(s1,mx,3.15+j*0.14,mw,0.12,'端口: '+pt,8,isDkws?C.pu:C.bl);
  });
});

// ZONE D
zn(s1,0.3,3.94,12.7,0.92,C.pBg,'FBCFE8',1);
txt(s1,0.4,3.96,4,0.18,'ZONE D · 适配层 (adapters)',9,C.md,true);
txt(s1,0.4,4.12,5,0.13,'端口接口实现 · 防腐层 · 外部系统对接',8,C.lt);
const adps=[
  {n:'关系持久化',d:['MyBatis·JDBC仓储','MySQL/H2读写']},
  {n:'DMN决策',d:['KIE DMN Runtime','降级决策表']},
  {n:'CRM回写',d:['HTTP CRM回写','日志CRM回写']},
  {n:'LLM客户端',d:['真实LLM客户端(REST)','模拟LLM客户端']},
  {n:'DKWS Skill 适配',d:['DSH HTTP Skill执行适配器','降级Skill执行适配器'],dk:1}
];
adps.forEach((a,i)=>{
  const ax=0.4+i*2.5,aw=a.dk?2.8:i<1?2.3:1.7;
  box(s1,ax,4.28,aw,0.48,a.dk?C.ob:C.wb,a.dk?C.pu:'F9A8D4',a.dk?1.5:0.8);
  txt(s1,ax,4.3,aw,0.15,a.n,10,a.dk?C.pu:C.dk,true);
  a.d.forEach((dt,j)=>txt(s1,ax,4.43+j*0.12,aw,0.11,dt,8,C.md));
});

// Deprecated
box(s1,4.0,4.8,2.8,0.2,'F1F5F9','CBD5E1',0.4);
txt(s1,4.0,4.82,2.0,0.14,'Oracle只读',8,C.dep,false);
txt(s1,6.0,4.82,0.8,0.14,'→ DKWS 适配',7,C.pu,true);

// ZONE E
zn(s1,0.3,5.08,12.7,0.82,C.gry,'E2E8F0',1);
txt(s1,0.4,5.1,6,0.18,'ZONE E · 数据存储',9,C.md,true);
txt(s1,0.4,5.26,8,0.13,'GITS 本体仅管理 MySQL；其余数据存储全部由 DKWS 统一访问',8,C.lt);
box(s1,0.4,5.42,2.5,0.38,C.wb,'64748B',1.5);
txt(s1,0.4,5.44,2.5,0.15,'MySQL / H2',10,C.dk,true);
txt(s1,0.4,5.57,2.5,0.12,'GITS 本体 · Flyway · 种子数据',8,C.md);
box(s1,3.1,5.42,9.7,0.38,C.ob,C.pu,2);
txt(s1,3.1,5.44,9.7,0.15,'DKWS 统一数据访问层',11,C.pu,true);
txt(s1,3.1,5.57,9.7,0.12,'Oracle (只读) · 知识地图/要素/资产 · 供应链图谱数据',8,C.pu);

// 连线
ar(s1,6.3,1.32,0,0.18,C.md);
ar(s1,2.15,2.44,0,0.24,C.md);
ar(s1,5.15,2.44,0,0.24,C.md);
ar(s1,7.6,2.44,0,0.24,C.pu);
ar(s1,1.65,3.72,0,0.22,C.md);
ar(s1,4.3,3.72,0,0.22,C.md);
ar(s1,7.05,3.72,0,0.22,C.pu);
ar(s1,1.55,4.76,0,0.32,C.md);
ar(s1,9.8,4.76,0,0.32,C.pu);

// 底部演进
zn(s1,0.3,6.0,12.7,0.5,'FAF5FF','C4B5FD',0.5);
s1.addText([
  {text:'架构演进：',options:{fontSize:8,bold:true,color:C.pu}},
  {text:'① 知识文件系统/InMemoryKnowledgeStore 已完全移除，知识供给由 DKWS Skill API 替代  ',options:{fontSize:7,color:C.md}},
  {text:'② Oracle只读由 DKWS 统一适配  ',options:{fontSize:7,color:C.md}},
  {text:'③ Zone E 仅 MySQL 由 GITS 直接管理  ',options:{fontSize:7,color:C.md}},
  {text:'④ scenario/seed 非架构层，仅为 H2 种子数据资产',options:{fontSize:7,color:C.md}}
],{x:0.4,y:6.03,w:12.5,h:0.45});

// ═══ SLIDE 2 业务流程 ═══
const s2=p.addSlide();s2.background={fill:C.bg};
txt(s2,0.3,0.06,12.7,0.3,'GITS-KNO 客户经营知识工程 · 业务流程',20,C.dk,true);
const PH=[
  {t:'PHASE 0 · 种子数据准备',c:C.md,y:0.5,dk:false,ss:['scenario/seed 权威源|0','GITS H2 入库|0','DKWS 只读接入|1','五层工作区构建|1']},
  {t:'PHASE 1 · 客户旅程启动',c:C.md,y:1.2,dk:false,ss:['客户识别|0','Orchestrator 编排|0','Skill执行端口|1','DKWS Skill 执行|1','旅程状态持久化|0']},
  {t:'PHASE 2 · 知识供给（DKWS Skill专用）',c:C.bl,y:1.9,dk:false,ss:['访前报告生成|0','DKWS 访前报告|1','外联脚本生成|0','DKWS 外联脚本|1','产品匹配|0','DKWS 产品匹配|1']},
  {t:'PHASE 3 · 评估与决策',c:C.md,y:2.6,dk:false,ss:['KYC 洞察|0','DMN 声明调解|0','声明候选记录|0','CRM 回写|0','承诺管理|0']},
  {t:'PHASE 4 · DKWS 供应链图谱',c:C.or,y:3.3,dk:true,ss:['seed 只读接入|1','数据接入解析|1','五层工作区|1','Skill数据投影|1','图谱数据输出|1','前端 ECharts 渲染|1']},
  {t:'PHASE 5 · 语义运行时',c:C.md,y:4.0,dk:false,ss:['OWL 本体加载|0','SHACL 校验|0','推理引擎|0','语义查询|0']},
  {t:'PHASE 6 · 安全与运维',c:C.md,y:4.7,dk:false,ss:['API Key|0','CORS|0','OWASP 检查|0','Prometheus|0','Zipkin|0','结构化日志|0']}
];
PH.forEach(ph=>{
  zn(s2,0.3,ph.y,12.7,0.6,ph.dk?C.ob:C.wb,ph.c,ph.dk?1.2:0.5);
  txt(s2,0.4,ph.y+0.02,8,0.16,ph.t,9,ph.c,true);
  ph.ss.forEach((raw,i)=>{
    const[n,dk]=raw.split('|'),sx=0.4+i*2.1;
    box(s2,sx,ph.y+0.2,1.95,0.32,dk==='1'?C.ob:C.wb,dk==='1'?C.or:C.dk,dk==='1'?1.0:0.7);
    txt(s2,sx,ph.y+0.22,1.95,0.26,n,8,dk==='1'?C.or:C.dk,true);
    if(i<ph.ss.length-1)s2.addShape(p.shapes.LINE,{x:sx+1.95,y:ph.y+0.36,w:0.15,h:0,line:{color:dk==='1'?C.or:C.md,width:0.8,endArrowType:'triangle'}});
  });
});
zn(s2,0.3,5.45,12.7,0.95,'F0F1F3',C.bd,0.3);
s2.addText([
  {text:'架构演进说明\n',options:{fontSize:9,bold:true,color:C.or}},
  {text:'1. 知识文件系统/InMemoryKnowledgeStore 已完全移除，知识供给由 DKWS Skill API 替代\n',options:{fontSize:7,color:C.md}},
  {text:'2. Oracle只读 由 DKWS 统一适配，GITS 不再直连 Oracle\n',options:{fontSize:7,color:C.md}},
  {text:'3. Zone F 数据存储仅 MySQL/H2 由 GITS 直接管理，其余全部由 DKWS 统一访问\n',options:{fontSize:7,color:C.md}},
  {text:'4. DKWS = Skill运行时 + 知识工程 + 银行各种数据统一访问适配层\n',options:{fontSize:7,color:C.md}},
  {text:'5. knowledge-architecture 端口接口保留，实现为 fail-closed 桩（DKWS 待集成）\n',options:{fontSize:7,color:C.md}},
  {text:'6. Phase 2 知识供给：5 个场景全部走 DKWS Skill-only（访前/外联/会面/产品/知识地图）\n',options:{fontSize:7,color:C.md}},
  {text:'7. scenario/seed 仅为 H2 种子数据资产，非架构层；知识数据由 DKWS 供给\n',options:{fontSize:7,color:C.md}},
  {text:'DKWS 不可达时 fail-closed：返回空结构，不回填 H2 种子数据',options:{fontSize:7,color:C.or,bold:true}}
],{x:0.4,y:5.47,w:12.5,h:0.9});

// ═══ SLIDE 3 技术栈 ═══
const s3=p.addSlide();s3.background={fill:C.bg};
txt(s3,0.3,0.06,12.7,0.3,'GITS-KNO 技术栈全景',20,C.dk,true);
const LY=[
  {t:'L1 前端',c:C.gn,y:0.5,items:['Vue 3|0','TypeScript|0','Vite|0','Naive UI|0','Pinia|0','vue-query|0','Tailwind|0','ECharts|0','Vitest|0']},
  {t:'L2 应用',c:'6DB33F',y:1.2,items:['Spring Boot|0','Modulith|0','Flyway|0','H2 / MySQL|0','MyBatis|0','JaCoCo|0','Actuator|0','Micrometer|0']},
  {t:'L3 领域核心',c:C.dk,y:1.9,items:['端口接口|0','密封接口|0','Record数据传输|0','KIE DMN|0','OWL / SHACL|0','JUnit 5|0','AssertJ|0']},
  {t:'L4 场景层',c:C.bl,y:2.6,items:['Skill执行端口|1','Skill执行路由|1','Skill标识映射|1','H2 种子数据|0','DKWS 知识供给|1']},
  {t:'L5 DKWS · Skill运行时+知识工程+银行数据统一访问',c:C.or,y:3.3,items:['FastAPI|1','Pydantic v2|1','SQLAlchemy|1','10个Skill API|1','状态机|1','五层工作区|1','数据接入 (Ingest)|1','客户知识|1']},
  {t:'L6 适配层',c:C.md,y:4.0,items:['关系持久化|0','语义持久化|0','知识文件系统|2','Oracle只读|3','CRM回写|0','DSH Skill执行|1']},
  {t:'L7 数据存储 · GITS 仅管理 MySQL，其余由 DKWS 统一访问',c:'B0B5BF',y:4.7,items:['MySQL / H2|0','Flyway|0','DKWS 统一数据访问|1']}
];
LY.forEach(ly=>{
  const isDk=ly.c===C.or,isSc=ly.c===C.bl;
  zn(s3,0.3,ly.y,12.7,0.6,isDk?C.ob:isSc?'D6E4F0':C.wb,isDk||isSc?ly.c:C.bd,isDk?1.5:isSc?1.0:0.5);
  txt(s3,0.4,ly.y+0.02,8,0.16,ly.t,9,ly.c,true);
  const cnt=ly.items.length,iw=Math.min(1.5,12.3/cnt);
  ly.items.forEach((raw,i)=>{
    const[n,dk]=raw.split('|');
    const isDep=dk==='2',isDkws=dk==='3';
    box(s3,0.4+i*(iw+0.08),ly.y+0.2,iw,0.32,isDep?'E8E8E8':isDkws?'E8E8E8':dk==='1'?C.ob:'F5F6F8',isDep?C.dep:isDkws?C.dep:dk==='1'?C.or:ly.c,isDep?0.3:isDkws?0.3:dk==='1'?1.0:0.4);
    txt(s3,0.4+i*(iw+0.08),ly.y+0.22,iw,0.24,n,7,isDep?C.dep:isDkws?C.dep:dk==='1'?C.or:C.dk,isDep?false:dk==='1');
  });
});
zn(s3,0.3,5.4,12.7,0.95,'F0F1F3',C.bd,0.3);
s3.addText([
  {text:'架构演进\n',options:{fontSize:9,bold:true,color:C.or}},
  {text:'■ 知识文件系统 / InMemoryKnowledgeStore 已完全移除，知识供给由 DKWS Skill API 替代\n',options:{fontSize:7,color:C.md}},
  {text:'■ Oracle只读 由 DKWS 统一适配：GITS 不再直连 Oracle，通过 DKWS 访问\n',options:{fontSize:7,color:C.md}},
  {text:'■ Zone F 数据存储仅 MySQL/H2 由 GITS 直接管理，其余全部由 DKWS 统一访问\n',options:{fontSize:7,color:C.md}},
  {text:'■ DKWS = Skill运行时 + 知识工程 + 银行各种数据统一访问适配层\n',options:{fontSize:7,color:C.md}},
  {text:'■ knowledge-architecture 端口接口保留，实现为 fail-closed 桩（DKWS 待集成）\n',options:{fontSize:7,color:C.md}},
  {text:'■ scenario/seed 仅为 H2 种子数据资产，非架构层；知识数据由 DKWS 供给',options:{fontSize:7,color:C.or,bold:true}}
],{x:0.4,y:5.42,w:12.5,h:0.9});

p.writeFile({fileName:'/home/szf/dev/gits-knowledge-engineering/diagrams/GITS-KNO-架构图集.pptx'})
.then(()=>console.log('PPT OK')).catch(e=>console.error(e));
