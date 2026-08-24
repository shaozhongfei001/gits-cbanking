<template>
  <div class="ew">
    <div class="ew-header"><h1>持续经营工作台</h1><p>螺旋迭代闭环，驱动客户关系持续深化</p></div>

    <!-- 状态栏 -->
    <div class="ew-bar">
      <span>当前客户：<n-tag v-if="sc" type="info">{{ sc.customerName }}</n-tag><em v-else>未选择</em></span>
      <span>旅程：<n-tag v-if="jid" :type="jpTag">{{ jpLabel }}</n-tag><em v-else>未启动</em></span>
      <span v-if="jid">迭代轮次：<n-tag type="warning">Round {{ round }}</n-tag></span>
      <span class="ew-bar-r">
        <n-button v-if="sc" size="small" @click="openServiceProposal">服务建议书</n-button>
        <n-button v-if="sc" size="small" :loading="scgLd" @click="openSupplyChain">供应链图谱</n-button>
        <n-button size="small" :loading="dirLd" @click="refreshCustomerDirectory">刷新客户目录</n-button>
        <n-button size="small" @click="showCS=true">{{ sc?'切换客户':'选择客户' }}</n-button>
        <n-button v-if="sc&&!jid" type="warning" size="small" @click="doStart" :loading="ld">启动旅程</n-button>
        <n-button v-if="jid&&roundDone.has('POSTVISIT')" type="success" size="small" @click="doComplete" :loading="ld">完成旅程</n-button>
      </span>
    </div>

    <!-- 螺旋迭代流程图 -->
    <div class="ew-spiral">
      <!-- 启动节点 -->
      <div class="sp-node" :class="{active:curPhase==='START',done:!!jid}" @click="clickPhase('START')">
        <div class="sp-icon">{{ jid ? '✓' : '🚀' }}</div>
        <div class="sp-label">启动旅程</div>
        <div class="sp-sub">选择客户，进入经营</div>
      </div>
      <div class="sp-arrow" :class="{lit:!!jid}">→</div>

      <!-- 迭代环 -->
      <div class="sp-loop" :class="{active:!!jid}">
        <div class="sp-loop-badge">迭代环 Round {{ round }}</div>
        <div class="sp-loop-nodes">
          <div class="sp-node" :class="{active:curPhase==='PREVISIT',done:isDone('PREVISIT')}" @click="clickPhase('PREVISIT')">
            <div class="sp-icon">{{ isDone('PREVISIT') ? '✓' : '📋' }}</div>
            <div class="sp-label">访前准备</div>
            <div class="sp-sub">R1报告 + R2速战卡</div>
          </div>
          <div class="sp-arrow" :class="{lit:isDone('PREVISIT')}">→</div>
          <div class="sp-node" :class="{active:curPhase==='INTERACTION',done:isDone('INTERACTION')}" @click="clickPhase('INTERACTION')">
            <div class="sp-icon">{{ isDone('INTERACTION') ? '✓' : '🤝' }}</div>
            <div class="sp-label">互动执行</div>
            <div class="sp-sub">预约话术 / 会面脚本</div>
          </div>
          <div class="sp-arrow" :class="{lit:isDone('INTERACTION')}">→</div>
          <div class="sp-node" :class="{active:curPhase==='POSTVISIT',done:isDone('POSTVISIT')}" @click="clickPhase('POSTVISIT')">
            <div class="sp-icon">{{ isDone('POSTVISIT') ? '✓' : '📊' }}</div>
            <div class="sp-label">访后复盘</div>
            <div class="sp-sub">R4分析 + R5报告</div>
          </div>
          <div class="sp-arrow" :class="{lit:isDone('POSTVISIT')}">→</div>
          <div class="sp-node sp-decision" :class="{active:curPhase==='ITERATE',done:isDone('ITERATE')}" @click="clickPhase('ITERATE')">
            <div class="sp-icon">{{ isDone('ITERATE') ? '✓' : '🔄' }}</div>
            <div class="sp-label">迭代决策</div>
            <div class="sp-sub">R7更新 + R8下轮访前</div>
          </div>
        </div>
        <!-- 回环箭头 -->
        <div v-if="jid && isDone('ITERATE')" class="sp-loopback" @click="doNextRound">
          <div class="sp-loopback-arrow">↺</div>
          <div class="sp-loopback-label">进入 Round {{ round + 1 }}</div>
        </div>
      </div>

      <div class="sp-arrow" :class="{lit:isDone('ITERATE')}">→</div>

      <!-- 完成 -->
      <div class="sp-node" :class="{active:curPhase==='COMPLETE',done:isDone('COMPLETE')}" @click="clickPhase('COMPLETE')">
        <div class="sp-icon">{{ isDone('COMPLETE') ? '✓' : '🏁' }}</div>
        <div class="sp-label">完成旅程</div>
        <div class="sp-sub">CRM回写确认</div>
      </div>
    </div>

    <!-- 迭代历史时间线 -->
    <div v-if="roundHistory.length > 0" class="ew-timeline">
      <h3>迭代历史</h3>
      <div class="tl-track">
        <div v-for="(rh, idx) in roundHistory" :key="idx" class="tl-round" :class="{current: idx === roundHistory.length - 1}">
          <div class="tl-badge">R{{ idx + 1 }}</div>
          <div class="tl-detail">
            <div class="tl-phase">{{ rh.summary }}</div>
            <div class="tl-time">{{ rh.time }}</div>
            <div v-if="rh.evidenceCount > 0" class="tl-evidence">+{{ rh.evidenceCount }} 条新证据</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 操作面板 -->
    <div class="ew-actions">
      <h3>操作面板 <span v-if="jid" class="ew-actions-round">Round {{ round }}</span></h3>
      <n-grid :cols="2" :x-gap="12" :y-gap="12">
        <n-gi v-for="a in currentActions" :key="a.k">
          <n-card hoverable class="ew-act" :class="{disabled:!a.enabled}" @click="a.enabled && a.fn()">
            <div class="ew-act-icon">{{a.icon}}</div>
            <div class="ew-act-title">{{a.title}}</div>
            <div class="ew-act-desc">{{a.desc}}</div>
            <div class="ew-act-hint">
              <span v-if="!jid">需先启动旅程</span>
              <span v-else-if="a.done">已完成 ✓</span>
              <span v-else-if="a.roundHint" class="ew-act-round-hint">{{ a.roundHint }}</span>
            </div>
          </n-card>
        </n-gi>
      </n-grid>
    </div>

    <!-- 迭代决策面板 -->
    <div v-if="showIteratePanel" class="ew-result">
      <h3>迭代决策 — 新证据录入 <n-tag size="small" type="info">Round {{ round }} → {{ round + 1 }}</n-tag> <n-button text size="small" @click="showIteratePanel=false">关闭</n-button></h3>
      <n-card>
        <div class="sf"><b>当前轮次：</b>Round {{ round }} — 访后分析已完成，可录入新证据触发下一轮迭代</div>
        <div class="sf"><b>迭代逻辑：</b>新证据 → R7 更新关系报告 → R8 下一轮访前报告 → 自动进入 Round {{ round + 1 }}</div>
        <div class="sf">
          <b>新证据描述：</b>
          <n-input v-model:value="newEvidenceDesc" type="textarea" placeholder="描述新获取的证据信息，例如：客户CFO确认Q3有5000万设备采购预算..." :rows="3" />
        </div>
        <div class="sf" style="margin-top:12px">
          <n-button type="primary" @click="doIterate" :loading="ld" :disabled="!newEvidenceDesc.trim()">
            🔄 录入新证据，进入 Round {{ round + 1 }}
          </n-button>
          <n-button style="margin-left:12px" @click="doComplete" :loading="ld">
            🏁 无需迭代，完成旅程
          </n-button>
        </div>
        <div v-if="iterR" class="sf" style="margin-top:12px">
          <n-tag type="success">迭代成功</n-tag>
          R7 更新报告ID: {{ iterR.updatedReportId?.substring(0,8) }}...
          <br/>R8 下轮访前报告ID: {{ iterR.nextPrevisitReportId?.substring(0,8) }}...
        </div>
      </n-card>
    </div>

    <!-- 预约话术：外联能力保留，默认折叠为短条 -->
    <div v-if="outR" class="ew-booking">
      <div class="ew-booking-head">
        <span class="ew-booking-title">预约话术</span>
        <n-tag size="tiny" type="info">{{ chLabel(outR.channel) }}</n-tag>
        <span v-if="!outreachScriptEmpty" class="ew-booking-obj">{{ outR.objective }}</span>
        <n-button v-if="!outreachScriptEmpty" text size="tiny" @click="showOutreachDetail = !showOutreachDetail">{{ showOutreachDetail ? '收起' : '展开全文' }}</n-button>
        <n-button text size="tiny" @click="outR=null">关闭</n-button>
      </div>
      <p v-if="outreachScriptEmpty" class="ew-booking-line">DKWS 未返回该话术</p>
      <template v-else>
        <p class="ew-booking-line"><b>开场：</b><span class="hl">{{ outR.openingLine }}</span></p>
        <p class="ew-booking-line"><b>收口：</b>{{ outR.closingLine }}</p>
        <div v-if="showOutreachDetail" class="ew-booking-detail">
          <div class="sf"><b>话题要点：</b>
            <div v-for="(tp,i) in outR.talkingPoints" :key="i" class="tp">
              <n-tag size="small" :type="tp.priority<=2?'warning':'default'">P{{tp.priority}}</n-tag>
              <b>{{tp.topic}}</b> {{tp.detail}}
              <em v-if="tp.suggestedQuestion">建议提问：{{tp.suggestedQuestion}}</em>
            </div>
          </div>
          <div v-if="outR.riskReminders?.length" class="sf"><b>风险提醒：</b><ul><li v-for="(r,i) in outR.riskReminders" :key="i">{{r}}</li></ul></div>
          <div class="sf"><b>后续行动：</b>{{ outR.followUpAction }}</div>
        </div>
      </template>
    </div>

    <!-- 会面脚本：主面板展开 -->
    <div v-if="meetR" class="ew-result">
      <h3>会面脚本 <n-button text size="small" @click="meetR=null">关闭</n-button></h3>
      <n-card>
        <div v-if="meetingScriptEmpty" class="sf">DKWS 未返回该话术</div>
        <template v-else>
          <div class="sf"><b>会面目标：</b>{{meetR.meetingObjective}}</div>
          <div class="sf"><b>访前摘要：</b>{{meetR.previsitSummary}}</div>
          <div class="sf"><b>议程安排：</b>
            <div v-for="(ag,i) in meetR.agendaItems" :key="i" class="ag-item">
              <div><n-tag size="small" type="info">{{ag.durationMinutes}}分钟</n-tag> <b>{{ag.topic}}</b></div>
              <div>{{ag.keyPoints}}</div>
              <div v-if="ag.expectedOutcome" class="kq-bg">预期成果：{{ag.expectedOutcome}}</div>
            </div>
          </div>
          <div class="sf"><b>KYC探查问题：</b>
            <div v-for="(q,i) in meetR.kycQuestions" :key="i" class="kq">
              <div><n-tag size="small" type="warning">{{q.gapArea}}</n-tag><n-tag size="small">{{q.expectedAnswerType}}</n-tag></div>
              <div>{{q.question}}</div>
              <div v-if="q.purpose" class="kq-bg">目的：{{q.purpose}}</div>
            </div>
          </div>
          <div class="sf"><b>产品讨论：</b>
            <div v-for="(p,i) in meetR.productDiscussions" :key="i" class="pd">
              <b>{{p.productName}}</b> — 讨论角度：{{p.discussionAngle}}
              <div v-if="p.keySellingPoints?.length" class="kq-bg">卖点：<span v-for="(s,j) in p.keySellingPoints" :key="j" class="gi">{{s}}</span></div>
            </div>
          </div>
          <div v-if="meetR.riskPoints?.length" class="sf"><b>风险提示：</b><ul><li v-for="(r,i) in meetR.riskPoints" :key="i">{{r}}</li></ul></div>
          <div class="sf"><b>结束语：</b>{{meetR.closingSummary}}</div>
        </template>
      </n-card>
    </div>

    <!-- 访前报告 -->
    <div v-if="preR" class="ew-result">
      <h3>访前报告 & 速战卡 <n-tag size="small" type="info">Round {{ round }}</n-tag> <n-button text size="small" @click="preR=null">关闭</n-button></h3>
      <KnowledgePrevisitReport
        :report="preR.previsitReport"
        :battle-card="preR.battleCard"
        :assembly-trace="preR.assemblyTrace || []"
        :skill-sections="preR.skillSections || []"
        :skill-executive-summary="preR.skillExecutiveSummary || ''"
        :supply-chain-report="scgReport"
        :supply-chain-loading="scgLd"
      />
    </div>

    <!-- 访后分析 -->
    <div v-if="postR" class="ew-result">
      <h3>访后分析 <n-tag size="small" type="info">Round {{ round }}</n-tag> <n-button text size="small" @click="postR=null">关闭</n-button></h3>
      <n-card>
        <div class="sf"><b>拜访摘要：</b>{{postR.visitSummary}}</div>
        <div v-if="postR.keyFindings?.length" class="sf"><b>关键发现：</b>
          <div v-for="(f,i) in postR.keyFindings" :key="i" class="fi"><n-tag size="small">{{f.extractionType}}</n-tag>{{f.content}}<n-tag size="small" :type="f.confidence>=0.8?'success':f.confidence>=0.5?'warning':'error'">{{(f.confidence*100).toFixed(0)}}%</n-tag></div>
        </div>
        <div v-if="postR.opportunitySignals?.length" class="sf"><b>机会信号：</b>
          <div v-for="(s,i) in postR.opportunitySignals" :key="i" class="fi"><n-tag size="small" type="info">{{s.signalType}}</n-tag>{{s.description}}<n-tag size="small" :type="s.confidence>=0.8?'success':'warning'">{{(s.confidence*100).toFixed(0)}}%</n-tag></div>
        </div>
        <div v-if="postR.commitments?.length" class="sf"><b>承诺事项：</b>
          <div v-for="(c,i) in postR.commitments" :key="i" class="cm">{{c.content}}<span v-if="c.deadline||c.owner"> ({{c.owner||''}}{{c.deadline?'/ '+c.deadline:''}})</span></div>
        </div>
        <div v-if="postR.reconciliationItems?.length" class="sf"><b>事实对账：</b>
          <n-table size="small" :bordered="false"><thead><tr><th>事实</th><th>先前主张</th><th>新证据</th><th>结果</th></tr></thead>
          <tbody><tr v-for="(r,i) in postR.reconciliationItems" :key="i"><td>{{r.factDescription}}</td><td>{{r.previousClaim}}</td><td>{{r.newEvidence}}</td><td><n-tag size="small" :type="r.reconciliationResult==='CONFIRMED'?'success':r.reconciliationResult==='CONFLICT'?'error':'warning'">{{r.reconciliationResult}}</n-tag></td></tr></tbody></n-table>
        </div>
        <div v-if="postR.followUpActions?.length" class="sf"><b>后续行动：</b><ul><li v-for="(a,i) in postR.followUpActions" :key="i">{{a}}</li></ul></div>
        <div v-if="postR.nextStepRecommendation" class="sf"><b>下一步建议：</b><span class="hl">{{postR.nextStepRecommendation}}</span></div>
      </n-card>
    </div>

    <!-- 客户选择 -->
    <n-modal v-model:show="showCS" preset="dialog" title="选择客户" style="width:500px">
      <n-input v-model:value="sq" placeholder="搜索客户名称..." clearable />
      <div class="cs-list">
        <div v-for="c in fc" :key="c.customerId" class="cs-item" @click="pickCustomer(c)">
          <span>{{c.customerName}}</span><RiskBadge :level="c.riskLevel" />
        </div>
        <n-empty v-if="!fc.length" description="未找到客户" size="small" />
      </div>
    </n-modal>

    <!-- 渠道选择 -->
    <n-modal v-model:show="showCH" preset="dialog" title="选择外联渠道" style="width:400px">
      <div class="ch-opts">
        <n-card v-for="ch in channels" :key="ch.v" hoverable class="ch-card" @click="doOutreach(ch.v)">
          <div class="ch-icon">{{ch.icon}}</div><div class="ch-name">{{ch.label}}</div><div class="ch-desc">{{ch.desc}}</div>
        </n-card>
      </div>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { NGrid, NGi, NCard, NButton, NModal, NInput, NEmpty, NTag, NDescriptions, NDescriptionsItem, NTable, useMessage } from 'naive-ui'
import RiskBadge from '../components/RiskBadge.vue'
import { fetchCustomers, reloadCrmCustomerMaster, generateOutreachScript, generateMeetingScript, executePrevisit, preparePrevisit, executePostvisit, startJourney, handleNewEvidence, completeJourney, executeSupplyChainGraph } from '../api/engagement'
import KnowledgePrevisitReport from '../components/KnowledgePrevisitReport.vue'
import type { Customer, OutreachScriptResponse, MeetingScriptResponse, PrevisitExecutionResponse, PostvisitAnalysisContent, NewEvidenceResponse, SupplyChainGraphReport } from '../api/engagement'

const msg = useMessage()
const router = useRouter()
const ld = ref(false)
const scgLd = ref(false)
const dirLd = ref(false)
const custs = ref<Customer[]>([])
const sc = ref<Customer|null>(null)
const sq = ref('')
const showCS = ref(false)
const showCH = ref(false)
const jid = ref('')
const jph = ref('')
const oid = ref('') // operatingCaseId
const outR = ref<OutreachScriptResponse|null>(null)
const meetR = ref<MeetingScriptResponse|null>(null)
const showOutreachDetail = ref(false)
const preR = ref<PrevisitExecutionResponse|null>(null)
const scgReport = ref<SupplyChainGraphReport|null>(null)
const postR = ref<PostvisitAnalysisContent|null>(null)
const iterR = ref<NewEvidenceResponse|null>(null)
const showIteratePanel = ref(false)
const newEvidenceDesc = ref('')

// 迭代轮次追踪
const round = ref(1)
const roundDone = ref<Set<string>>(new Set())
const roundHistory = ref<{summary: string; time: string; evidenceCount: number}[]>([])

const channels = [
  {v:'PHONE',label:'电话',icon:'📞',desc:'电话外联，适合首次触达'},
  {v:'WECHAT',label:'微信',icon:'💬',desc:'微信沟通，适合日常维护'},
  {v:'EMAIL',label:'邮件',icon:'📧',desc:'正式邮件，适合方案推送'},
  {v:'FACE_TO_FACE',label:'面谈',icon:'🤝',desc:'当面拜访，适合深度沟通'}
]

function isDone(phase: string): boolean {
  if (phase === 'START') return !!jid.value
  if (phase === 'COMPLETE') return roundHistory.value.some(h => h.summary.includes('旅程完成'))
  return roundDone.value.has(phase)
}

const curPhase = computed(() => {
  if (!jid.value) return 'START'
  if (!roundDone.value.has('PREVISIT')) return 'PREVISIT'
  if (!roundDone.value.has('INTERACTION')) return 'INTERACTION'
  if (!roundDone.value.has('POSTVISIT')) return 'POSTVISIT'
  if (!roundDone.value.has('ITERATE')) return 'ITERATE'
  return 'COMPLETE'
})

const jpLabel = computed(() => ({PRE_VISIT:'访前',IN_VISIT:'拜访中',POST_VISIT:'访后',CONTINUOUS_ENGAGEMENT:'持续经营',COMPLETED:'已完成',KYC_COLLECT:'KYC采集',INSIGHT_ANALYSIS:'洞察分析',PRODUCT_MATCHING:'产品匹配',PREVISIT_PREP:'访前准备',POSTVISIT_REVIEW:'访后复盘'}[jph.value]||jph.value))
const jpTag = computed(() => ({PRE_VISIT:'warning',IN_VISIT:'info',POST_VISIT:'success',CONTINUOUS_ENGAGEMENT:'info',COMPLETED:'success',PREVISIT_PREP:'warning',POSTVISIT_REVIEW:'success'}[jph.value] as string||'default') as 'warning'|'info'|'success'|'default')
const fc = computed(() => { if(!sq.value) return custs.value.slice(0,20); const q=sq.value.toLowerCase(); return custs.value.filter(c=>c.customerName.toLowerCase().includes(q)).slice(0,20) })

function chLabel(v:string) { return channels.find(c=>c.v===v)?.label||v }

function isBlank(s?: string | null): boolean {
  return !s || !s.trim()
}

const outreachScriptEmpty = computed(() => {
  if (!outR.value) return false
  return isBlank(outR.value.objective) && isBlank(outR.value.openingLine)
})

const meetingScriptEmpty = computed(() => {
  if (!meetR.value) return false
  return isBlank(meetR.value.meetingObjective) && !(meetR.value.agendaItems && meetR.value.agendaItems.length)
})

// 操作面板：根据当前阶段动态展示
const currentActions = computed(() => {
  const actions = [
    {k:'previsit',title:'执行访前准备（一键）',desc:'按知识地图任务映射，自动生成预约话术 + 会面脚本 + R1访前报告 + R2速战卡',icon:'📈',fn:handlePrevisit,done:isDone('PREVISIT'),enabled:!!jid.value,roundHint: isDone('PREVISIT') ? `Round ${round.value} 已完成` : (round.value > 1 ? `R8 下轮访前已就绪` : '')},
    {k:'postvisit',title:'执行访后复盘',desc:'R4分析 + R5A内部报告 + R5B CRM报告 + 事实对账',icon:'📊',fn:handlePostvisit,done:isDone('POSTVISIT'),enabled:!!jid.value && isDone('PREVISIT'),roundHint: !isDone('PREVISIT') ? '需先完成访前准备' : ''},
    {k:'iterate',title:'迭代决策',desc:'录入新证据 → R7更新报告 → R8下轮访前 → 进入下一轮',icon:'🔄',fn:handleIterate,done:isDone('ITERATE'),enabled:!!jid.value && isDone('POSTVISIT'),roundHint: !isDone('POSTVISIT') ? '需先完成访后复盘' : (round.value > 1 ? '可继续迭代或完成旅程' : '')},
    {k:'complete',title:'完成旅程',desc:'确认CRM回写，关闭经营旅程',icon:'🏁',fn:doComplete,done:isDone('COMPLETE'),enabled:!!jid.value && isDone('POSTVISIT'),roundHint: ''}
  ]
  return actions
})

function clickPhase(phase: string) {
  if (phase === 'START') { if(!sc.value) showCS.value=true; else if(!jid.value) doStart() }
  else if (phase === 'PREVISIT') handlePrevisit()
  else if (phase === 'INTERACTION') handlePrevisit()
  else if (phase === 'POSTVISIT') handlePostvisit()
  else if (phase === 'ITERATE') handleIterate()
  else if (phase === 'COMPLETE') doComplete()
}

async function refreshCustomerDirectory() {
  dirLd.value = true
  try {
    try {
      const reload = await reloadCrmCustomerMaster()
      msg.success(`客户目录已同步（${reload.upsertedCount}）`)
    } catch (e: unknown) {
      const status = (e as { response?: { status?: number } }).response?.status
      if (status !== 404) {
        const message = (e as { response?: { data?: { message?: string } }; message?: string }).response?.data?.message
          || (e as { message?: string }).message
          || '未知错误'
        msg.warning(`目录同步未完成：${message}`)
      }
    }
    custs.value = await fetchCustomers()
  } catch (e: unknown) {
    const message = (e as { message?: string }).message || '未知错误'
    msg.error(`刷新客户目录失败：${message}`)
  } finally {
    dirLd.value = false
  }
}

async function pickCustomer(c:Customer) {
  sc.value=c; showCS.value=false
  resetJourney()
  msg.info(`已选择客户：${c.customerName}，请点击"启动旅程"开始经营流程`)
}

function resetJourney() {
  jid.value=''; jph.value=''; oid.value=''
  outR.value=null; meetR.value=null; preR.value=null; scgReport.value=null; postR.value=null; iterR.value=null
  showOutreachDetail.value=false
  round.value=1; roundDone.value=new Set(); roundHistory.value=[]
  showIteratePanel.value=false; newEvidenceDesc.value=''
}

async function doStart() {
  if(!sc.value){msg.warning('请先选择客户');showCS.value=true;return}
  ld.value=true
  try{
    const r=await startJourney(sc.value.customerId)
    jid.value=r.journeyId; jph.value=r.phase; oid.value=r.operatingCaseId
    roundDone.value.add('START')
    msg.success(`旅程已启动 (ID: ${r.journeyId.substring(0,8)}...)`)
  }catch(e:any){msg.error(`启动旅程失败：${e.message||'未知错误'}`)}
  finally{ld.value=false}
}

function openServiceProposal() {
  if(!sc.value){msg.warning('请先选择客户');showCS.value=true;return}
  router.push({ name: 'ServiceProposalView', query: { customerId: sc.value.customerId } })
}

async function openSupplyChain() {
  if(!sc.value){msg.warning('请先选择客户');showCS.value=true;return}
  scgLd.value=true
  try{
    scgReport.value=await executeSupplyChainGraph(sc.value.customerId)
    msg.success('供应链图谱已生成，见访前报告 KI-FRONT-001')
    if(!preR.value){
      await router.push({ name: 'SupplyChainGraphReport', params: { requestId: scgReport.value.requestId } })
    }
  }catch(e:any){msg.error(`供应链图谱执行失败：${e.response?.data?.message||e.message||'未知错误'}`)}
  finally{scgLd.value=false}
}

function handleOutreach(){if(!jid.value){msg.warning('请先启动旅程');return}showCH.value=true}

async function doOutreach(ch:string) {
  showCH.value=false; if(!sc.value||!jid.value)return; ld.value=true
  try{const r=await generateOutreachScript(sc.value.customerId,sc.value.rmId,oid.value,jid.value,ch);outR.value=r;showOutreachDetail.value=false;roundDone.value.add('INTERACTION');msg.success('预约话术已生成')}
  catch(e:any){msg.error(`生成预约话术失败：${e.message||'未知错误'}`)}
  finally{ld.value=false}
}

async function handleMeeting() {
  if(!jid.value){msg.warning('请先启动旅程');return}
  if(!sc.value){msg.warning('请先选择客户');return}
  ld.value=true
  try{const r=await generateMeetingScript(sc.value.customerId,sc.value.rmId,oid.value,jid.value);meetR.value=r;roundDone.value.add('INTERACTION');msg.success('会面脚本已生成')}
  catch(e:any){msg.error(`生成会面脚本失败：${e.message||'未知错误'}`)}
  finally{ld.value=false}
}

async function handlePrevisit() {
  if(!jid.value){msg.warning('请先启动旅程');return}
  if(!sc.value){msg.warning('请先选择客户');return}
  ld.value=true
  scgReport.value=null
  scgLd.value=true
  const graphJob=executeSupplyChainGraph(sc.value.customerId)
    .then(g=>{scgReport.value=g})
    .catch((e:any)=>{msg.warning(`供应链图谱未生成：${e.response?.data?.message||e.message||'未知错误'}`)})
    .finally(()=>{scgLd.value=false})
  try{
    const r=await preparePrevisit(jid.value,sc.value.customerId,oid.value,`Round ${round.value} 访前调研`,sc.value.rmId)
    // 一键访前包：外联脚本 + 会面脚本 + R1 访前报告 + R2 速战卡（知识地图任务映射驱动）
    outR.value=r.outreachScript||null
    showOutreachDetail.value=false
    meetR.value=r.meetingScript||null
    preR.value={previsitReport:r.previsitReport,battleCard:r.battleCard,supplyChainMarkdown:r.supplyChainMarkdown||'',assemblyTrace:r.assemblyTrace||[],skillReportTitle:r.skillReportTitle,skillExecutiveSummary:r.skillExecutiveSummary,skillSections:r.skillSections||[]} as PrevisitExecutionResponse
    roundDone.value.add('INTERACTION')
    roundDone.value.add('PREVISIT')
    msg.success(`Round ${round.value} 访前包已自动生成（预约话术+会面+R1+R2）`)
    await graphJob
  }catch(e:any){msg.error(`一键访前准备失败：${e.message||'未知错误'}`)}
  finally{ld.value=false}
}

async function handlePostvisit() {
  if(!jid.value){msg.warning('请先启动旅程');return}
  if(!sc.value){msg.warning('请先选择客户');return}
  if(!isDone('PREVISIT')){msg.warning('请先完成访前准备');return}
  ld.value=true
  try{
    const r=await executePostvisit(jid.value,sc.value.customerId,oid.value,'客户面谈记录（待录入）')
    postR.value={analysisId:r.analysisId||'',journeyId:jid.value,visitSummary:'访后分析已完成',keyFindings:[],opportunitySignals:[],commitments:[],reconciliationItems:[],followUpActions:['CRM回写已触发：'+(r.crmCommandCount||0)+'条命令'],nextStepRecommendation:r.allCommandsRequireHumanConfirm?'部分操作需要人工确认，请检查CRM回写命令':'所有操作已自动执行'} as PostvisitAnalysisContent
    roundDone.value.add('POSTVISIT')
    // 记录迭代历史
    roundHistory.value.push({
      summary: `Round ${round.value}: 访前→互动→访后复盘完成`,
      time: new Date().toLocaleString('zh-CN'),
      evidenceCount: 0
    })
    msg.success(`Round ${round.value} 访后分析已完成`)
  }catch(e:any){msg.error(`执行访后分析失败：${e.message||'未知错误'}`)}
  finally{ld.value=false}
}

function handleIterate() {
  if(!jid.value){msg.warning('请先启动旅程');return}
  if(!isDone('POSTVISIT')){msg.warning('请先完成访后复盘');return}
  showIteratePanel.value = true
}

async function doIterate() {
  if(!sc.value){msg.warning('请先选择客户');return}
  if(!newEvidenceDesc.value.trim()){msg.warning('请输入新证据描述');return}
  ld.value=true
  try{
    const prevReportId = preR.value?.previsitReport?.reportId || undefined
    const r=await handleNewEvidence(jid.value,sc.value.customerId,oid.value,newEvidenceDesc.value.trim(),prevReportId)
    iterR.value=r
    roundDone.value.add('ITERATE')
    // 更新迭代历史
    if (roundHistory.value.length > 0) {
      roundHistory.value[roundHistory.value.length - 1].evidenceCount++
    }
    msg.success(`新证据已录入，R7+R8 已生成，即将进入 Round ${round.value + 1}`)
    // 自动进入下一轮
    setTimeout(() => doNextRound(), 1500)
  }catch(e:any){msg.error(`迭代决策失败：${e.message||'未知错误'}`)}
  finally{ld.value=false}
}

function doNextRound() {
  round.value++
  roundDone.value = new Set()
  outR.value=null; meetR.value=null; preR.value=null; scgReport.value=null; postR.value=null; iterR.value=null
  showOutreachDetail.value=false
  showIteratePanel.value=false; newEvidenceDesc.value=''
  msg.info(`已进入 Round ${round.value}，请执行访前准备`)
}

async function doComplete() {
  if(!jid.value){msg.warning('请先启动旅程');return}
  ld.value=true
  try{
    await completeJourney(jid.value)
    roundDone.value.add('COMPLETE')
    roundHistory.value.push({
      summary: `旅程完成（共 ${round.value} 轮迭代）`,
      time: new Date().toLocaleString('zh-CN'),
      evidenceCount: 0
    })
    msg.success('旅程已完成，CRM回写已确认')
  }catch(e:any){msg.error(`完成旅程失败：${e.message||'未知错误'}`)}
  finally{ld.value=false}
}

onMounted(async()=>{try{custs.value=await fetchCustomers()}catch(e){console.error('Failed to load customers:',e)}})
</script>

<style scoped>
.ew {
  max-width: 1200px;
  margin: 0 auto;
  padding: var(--space-6);
}

.ew-header h1 {
  font-size: var(--text-2xl);
  color: var(--text-primary);
  margin: 0 0 var(--space-1);
  font-weight: 600;
}

.ew-header p {
  color: var(--text-tertiary);
  font-size: var(--text-sm);
  margin: 0 0 var(--space-5);
}

/* Status Bar */
.ew-bar {
  display: flex;
  align-items: center;
  gap: var(--space-5);
  padding: var(--space-3) var(--space-4);
  background: var(--bg-surface);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-md);
  margin-bottom: var(--space-6);
  font-size: var(--text-sm);
  color: var(--text-secondary);
}

.ew-bar em {
  color: var(--text-tertiary);
  font-style: italic;
}

.ew-bar-r {
  margin-left: auto;
  display: flex;
  gap: var(--space-2);
}

/* Flow Steps - replaced by Spiral */
.ew-spiral {
  display: flex;
  align-items: flex-start;
  overflow-x: auto;
  padding: var(--space-4) 0;
  margin-bottom: var(--space-6);
  gap: var(--space-2);
}

.sp-node {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 100px;
  padding: var(--space-3);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-normal);
  border: 2px solid var(--border-light);
  background: var(--bg-surface-soft);
  color: var(--text-tertiary);
}

.sp-node.active {
  background: var(--brand-primary);
  color: var(--text-inverse);
  border-color: var(--brand-primary);
  box-shadow: var(--shadow-md);
}

.sp-node.done {
  background: var(--color-success-bg);
  border-color: var(--color-success-border);
  color: var(--color-success);
}

.sp-node:not(.active):not(.done):hover {
  border-color: var(--border-normal);
  color: var(--text-secondary);
}

.sp-decision {
  border-style: dashed;
}

.sp-icon {
  font-size: 24px;
  margin-bottom: var(--space-1);
}

.sp-label {
  font-size: var(--text-sm);
  font-weight: 600;
  margin-bottom: 2px;
}

.sp-sub {
  font-size: var(--text-xs);
  opacity: 0.8;
  text-align: center;
}

.sp-arrow {
  font-size: 18px;
  color: var(--border-light);
  align-self: center;
  transition: color var(--transition-normal);
  padding: 0 var(--space-1);
}

.sp-arrow.lit {
  color: var(--brand-primary);
}

.sp-loop {
  border: 2px dashed var(--border-light);
  border-radius: var(--radius-lg);
  padding: var(--space-3);
  transition: border-color var(--transition-normal);
}

.sp-loop.active {
  border-color: var(--brand-primary);
  background: rgba(var(--brand-primary-rgb, 59,130,246), 0.03);
}

.sp-loop-badge {
  text-align: center;
  font-size: var(--text-xs);
  font-weight: 700;
  color: var(--brand-primary);
  margin-bottom: var(--space-2);
  text-transform: uppercase;
  letter-spacing: 1px;
}

.sp-loop-nodes {
  display: flex;
  align-items: flex-start;
  gap: var(--space-1);
}

.sp-loopback {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  margin-top: var(--space-2);
  padding: var(--space-2);
  border-radius: var(--radius-md);
  background: var(--color-success-bg);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.sp-loopback:hover {
  background: var(--color-success-border);
}

.sp-loopback-arrow {
  font-size: 20px;
  color: var(--color-success);
  animation: pulse 2s infinite;
}

.sp-loopback-label {
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--color-success);
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* Timeline */
.ew-timeline {
  margin-bottom: var(--space-6);
}

.ew-timeline h3 {
  font-size: var(--text-lg);
  color: var(--text-primary);
  margin: 0 0 var(--space-3);
  padding-bottom: var(--space-2);
  border-bottom: 2px solid var(--brand-primary);
}

.tl-track {
  display: flex;
  gap: var(--space-3);
  overflow-x: auto;
  padding: var(--space-2) 0;
}

.tl-round {
  display: flex;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-md);
  background: var(--bg-surface-soft);
  border: 1px solid var(--border-light);
  min-width: 200px;
}

.tl-round.current {
  border-color: var(--brand-primary);
  background: rgba(var(--brand-primary-rgb, 59,130,246), 0.05);
}

.tl-badge {
  background: var(--brand-primary);
  color: var(--text-inverse);
  font-size: var(--text-xs);
  font-weight: 700;
  padding: 2px 8px;
  border-radius: var(--radius-xs);
  align-self: flex-start;
  white-space: nowrap;
}

.tl-phase {
  font-size: var(--text-sm);
  color: var(--text-primary);
  font-weight: 500;
}

.tl-time {
  font-size: var(--text-xs);
  color: var(--text-tertiary);
}

.tl-evidence {
  font-size: var(--text-xs);
  color: var(--color-success);
  font-weight: 500;
}

/* Actions Panel */
.ew-actions {
  margin-bottom: var(--space-8);
}

.ew-actions h3 {
  font-size: var(--text-lg);
  color: var(--text-primary);
  margin: 0 0 var(--space-4);
  padding-bottom: var(--space-2);
  border-bottom: 2px solid var(--brand-primary);
}

.ew-actions-round {
  font-size: var(--text-sm);
  color: var(--brand-primary);
  font-weight: 600;
  margin-left: var(--space-2);
}

.ew-act {
  cursor: pointer;
  transition: transform var(--transition-fast), box-shadow var(--transition-fast);
  text-align: center;
}

.ew-act:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.ew-act.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.ew-act.disabled:hover {
  transform: none;
  box-shadow: none;
}

.ew-act-icon {
  font-size: 28px;
  margin-bottom: var(--space-2);
}

.ew-act-title {
  font-size: var(--text-base);
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: var(--space-1);
}

.ew-act-desc {
  font-size: var(--text-xs);
  color: var(--text-secondary);
}

.ew-act-hint {
  margin-top: var(--space-2);
  font-size: var(--text-xs);
  color: var(--brand-accent);
}

/* Result Panels */
.ew-booking {
  margin-bottom: var(--space-4);
  padding: 10px 14px;
  border: 1px solid var(--border-light, #e5e7eb);
  border-radius: 8px;
  background: #f8fafc;
  animation: fadeIn 0.3s ease-out;
}
.ew-booking-head {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}
.ew-booking-title {
  font-weight: 700;
  font-size: 13px;
  color: #1e3a8a;
}
.ew-booking-obj {
  flex: 1;
  min-width: 120px;
  font-size: 12px;
  color: #64748b;
}
.ew-booking-line {
  margin: 6px 0 0;
  font-size: 13px;
  color: #374151;
}
.ew-booking-detail {
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px dashed var(--border-light, #e5e7eb);
}
.ew-result {
  margin-bottom: var(--space-8);
  animation: fadeIn 0.3s ease-out;
}

.ew-result h3 {
  font-size: var(--text-lg);
  color: var(--text-primary);
  margin: 0 0 var(--space-4);
  padding-bottom: var(--space-2);
  border-bottom: 2px solid var(--brand-primary);
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
}

.sf {
  margin-bottom: var(--space-3);
  font-size: var(--text-sm);
  line-height: var(--leading-relaxed);
}

.sf b {
  color: var(--text-primary);
}

.sf ul {
  padding-left: var(--space-5);
  margin: var(--space-1) 0;
  color: var(--text-secondary);
}

.hl {
  background: var(--brand-primary-lighter);
  padding: 2px var(--space-2);
  border-radius: var(--radius-xs);
  font-weight: 500;
  color: var(--brand-primary-dark);
}

.tp {
  padding: var(--space-1) 0;
  border-bottom: 1px dashed var(--border-light);
}

.tp em {
  color: var(--brand-accent);
  font-size: var(--text-xs);
  margin-left: var(--space-2);
}

.ag-item {
  margin-bottom: var(--space-2);
}

.kq {
  margin-bottom: var(--space-2);
  padding: var(--space-2);
  background: var(--bg-surface-soft);
  border-radius: var(--radius-sm);
}

.kq-bg {
  font-size: var(--text-xs);
  color: var(--text-tertiary);
  margin-top: var(--space-1);
}

.pd {
  padding: var(--space-1) 0;
  border-bottom: 1px dashed var(--border-light);
}

.gaps > div {
  margin-bottom: var(--space-2);
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--space-1);
}

.gi {
  background: var(--bg-hover);
  padding: 2px var(--space-2);
  border-radius: var(--radius-xs);
  font-size: var(--text-xs);
  margin: 2px;
}

.ri {
  background: var(--color-danger-bg);
  color: var(--color-danger);
}

.ps-card {
  margin-bottom: var(--space-2);
}

.ps-h {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  margin-bottom: var(--space-1);
}

.bc-h {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  margin-bottom: var(--space-2);
}

.bc-obj {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  margin-bottom: var(--space-3);
}

.fi {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-1) 0;
  border-bottom: 1px dashed var(--border-light);
}

.cm {
  padding: var(--space-1) 0;
  border-bottom: 1px dashed var(--border-light);
}

/* Customer Select Modal */
.cs-list {
  max-height: 300px;
  overflow-y: auto;
  margin-top: var(--space-3);
}

.cs-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: background var(--transition-fast);
}

.cs-item:hover {
  background: var(--bg-hover);
}

/* Channel Select Modal */
.ch-opts {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-3);
}

.ch-card {
  cursor: pointer;
  text-align: center;
  transition: border-color var(--transition-fast);
}

.ch-card:hover {
  border-color: var(--brand-primary);
}

.ch-icon {
  font-size: 28px;
  margin-bottom: var(--space-1);
}

.ch-name {
  font-weight: 600;
  color: var(--text-primary);
}

.ch-desc {
  font-size: var(--text-xs);
  color: var(--text-tertiary);
}
</style>
