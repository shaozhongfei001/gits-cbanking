<template>
  <div class="knowledge-previsit">
    <!-- 任务区：任务定义（访前准备任务） -->
    <div class="task-header">
      <div class="task-title">
        <span class="task-badge">TASK-FRONT-001</span>
        <span class="task-name">访前准备任务</span>
      </div>
      <p class="task-objective">
        拜访目标：{{ report.visitObjective || '—' }}
        <span v-if="report.reportId">· {{ report.reportId }}</span>
      </p>
      <p class="task-mapping">
        知识地图任务映射：知识域(KD) → 知识条目(KI) → 知识要素(KE)，LLM 优先读图后生成
      </p>
    </div>

    <!-- 知识区：按 KI 分组 -->
    <div class="ki-grid">
      <!-- KI-009 企业客户基本信息 -->
      <section class="ki-block">
        <h3 class="ki-title"><span class="ki-id">KI-009</span> 企业客户基本信息</h3>
        <div class="ki-body" v-if="report.customerOverview">
          <div class="kv"><span class="k">行业</span><span class="v">{{ report.customerOverview.industry }}</span></div>
          <div class="kv"><span class="k">规模</span><span class="v">{{ report.customerOverview.enterpriseScale }}</span></div>
          <div class="kv"><span class="k">客户层级</span><span class="v">{{ report.customerOverview.customerTier }}</span></div>
          <div class="kv"><span class="k">注册资本</span><span class="v">{{ fmtMoney(report.customerOverview.registeredCapitalCny) }}</span></div>
          <div class="kv"><span class="k">风险等级</span><span class="v">{{ report.customerOverview.riskLevel }}</span></div>
          <div class="kv"><span class="k">关系摘要</span><span class="v">{{ report.customerOverview.relationshipSummary }}</span></div>
        </div>
      </section>

      <!-- KI-FRONT-001 公司供应链图谱 -->
      <section class="ki-block ki-supplychain">
        <h3 class="ki-title"><span class="ki-id">KI-FRONT-001</span> 公司供应链图谱</h3>
        <div class="ki-body" v-if="supplyChainLines.length">
          <div v-for="(row, i) in supplyChainLines" :key="i" class="sc-row">
            <span class="sc-badge" :class="'sc-'+row.kind">{{ row.kindLabel }}</span>
            <span class="sc-name">{{ row.name }}</span>
            <span class="sc-attrs">{{ row.attrs }}</span>
          </div>
          <p class="ki-note" v-if="scUnknown.length">· 待补充：{{ scUnknown.join('；') }}</p>
        </div>
        <div class="ki-body" v-else>
          <p class="ki-note">（未获取到供应链图谱数据）</p>
        </div>
      </section>

      <!-- KI-FRONT-002 产业链八维研判 -->
      <section class="ki-block">
        <h3 class="ki-title"><span class="ki-id">KI-FRONT-002</span> 产业链八维研判</h3>
        <div class="ki-body">
          <p class="strategy">{{ report.visitStrategy || '—' }}</p>
          <template v-if="report.riskReminders && report.riskReminders.length">
            <p class="ki-sub">风险提醒（K-Type-E 综合研判）</p>
            <ul><li v-for="(r, i) in report.riskReminders" :key="i">{{ r }}</li></ul>
          </template>
        </div>
      </section>

      <!-- KI-FRONT-003 行内变动行为 -->
      <section class="ki-block">
        <h3 class="ki-title"><span class="ki-id">KI-FRONT-003</span> 行内变动行为</h3>
        <div class="ki-body">
          <p class="ki-note">（行内交易/结算/对账变动，LLM 依据 KI-FRONT-003 经营对账要素生成）</p>
        </div>
      </section>

      <!-- KI-FRONT-004 事实承诺事项 -->
      <section class="ki-block">
        <h3 class="ki-title"><span class="ki-id">KI-FRONT-004</span> 事实承诺事项 / 沟通话术</h3>
        <div class="ki-body" v-if="report.keyQuestions && report.keyQuestions.length">
          <p class="ki-sub">待确认问题（K-Type-P 话术）</p>
          <ul><li v-for="(q, i) in report.keyQuestions" :key="i">{{ q }}</li></ul>
        </div>
      </section>

      <!-- KI-FRONT-005 KYC信息缺口 -->
      <section class="ki-block">
        <h3 class="ki-title"><span class="ki-id">KI-FRONT-005</span> KYC信息缺口</h3>
        <div class="ki-body" v-if="report.kycGapSummary">
          <template v-if="report.kycGapSummary.knownItems?.length">
            <p class="ki-sub">已确认</p>
            <ul><li v-for="(k, i) in report.kycGapSummary.knownItems" :key="i">{{ k }}</li></ul>
          </template>
          <template v-if="report.kycGapSummary.unknownItems?.length">
            <p class="ki-sub">未知缺口</p>
            <ul><li v-for="(u, i) in report.kycGapSummary.unknownItems" :key="i">{{ u }}</li></ul>
          </template>
          <template v-if="report.kycGapSummary.priorityQuestions?.length">
            <p class="ki-sub">优先问题</p>
            <ul><li v-for="(p, i) in report.kycGapSummary.priorityQuestions" :key="i">{{ p }}</li></ul>
          </template>
        </div>
      </section>

      <!-- KI-FRONT-006 产品候选组合 -->
      <section class="ki-block">
        <h3 class="ki-title"><span class="ki-id">KI-FRONT-006</span> 产品候选组合</h3>
        <div class="ki-body" v-if="report.productSchemes?.length">
          <div v-for="scheme in report.productSchemes" :key="scheme.productId" class="product">
            <p class="product-name">{{ scheme.productName }} <span class="amount">{{ scheme.suggestedAmount || '' }}</span></p>
            <p class="product-reason">{{ scheme.matchReason }}</p>
            <p class="product-term" v-if="scheme.suggestedTerm">期限：{{ scheme.suggestedTerm }}</p>
          </div>
        </div>
      </section>
    </div>

    <!-- 速战卡（R2）按知识条目标注 -->
    <div class="battle-card" v-if="battleCard">
      <h3 class="bc-title">60秒速战卡 <span class="bc-id">R2</span></h3>
      <p class="bc-meta">{{ battleCard.customerName }} · {{ battleCard.visitObjective }}
        <span class="bc-tier">{{ battleCard.customerTier }} · {{ battleCard.riskLevel }}</span></p>
      <div class="bc-section">
        <p class="bc-sub">要点（KI-009/002）</p>
        <ul><li v-for="(p, i) in battleCard.keyPoints" :key="i">{{ p }}</li></ul>
      </div>
      <div class="bc-section">
        <p class="bc-sub">产品提示（KI-FRONT-006）</p>
        <ul><li v-for="(p, i) in battleCard.productHints" :key="i">{{ p }}</li></ul>
      </div>
      <div class="bc-section">
        <p class="bc-sub">别忘了（KI-FRONT-004/005）</p>
        <ul><li v-for="(p, i) in battleCard.dontForget" :key="i">{{ p }}</li></ul>
      </div>
      <p class="bc-bottom">底线：{{ battleCard.bottomLine }}</p>
    </div>

    <!-- 知识组装模拟控制台：实时滚动，逐 KI 打印组装轨迹 -->
    <section class="dbg-console">
      <div class="dbg-head">
        <span>🖥️ 知识组装模拟控制台</span>
        <n-tag size="tiny" :type="consoleReady ? 'success' : 'info'">{{ consoleReady ? '已完成' : '组装中…' }}</n-tag>
      </div>
      <div class="dbg-body">
        <div v-for="(ln, i) in consoleLines" :key="i" class="dbg-line">
          <span class="dbg-time">{{ ln.time }}</span>
          <span class="dbg-icon">{{ ln.icon }}</span>
          <span class="dbg-text">{{ ln.text }}</span>
        </div>
        <div v-if="consoleReady && !consoleLines.length" class="dbg-empty">（无轨迹输出）</div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

interface PrevisitReport {
  reportId?: string
  visitObjective?: string
  customerOverview?: { industry: string; enterpriseScale: string; customerTier: string; registeredCapitalCny: number; riskLevel: string; relationshipSummary: string }
  kycGapSummary?: { knownItems?: string[]; partialKnownItems?: string[]; unknownItems?: string[]; priorityQuestions?: string[] }
  productSchemes?: { productId: string; productName: string; matchReason: string; suggestedAmount?: string; suggestedTerm?: string }[]
  keyQuestions?: string[]
  riskReminders?: string[]
  visitStrategy?: string
}
interface BattleCard {
  customerName?: string
  visitObjective?: string
  customerTier?: string
  riskLevel?: string
  keyPoints?: string[]
  productHints?: string[]
  dontForget?: string[]
  bottomLine?: string
}
const props = defineProps<{ report: PrevisitReport; battleCard?: BattleCard; supplyChainMarkdown?: string }>()

function fmtMoney(v: number): string {
  if (v == null) return '—'
  return (v / 100000000).toFixed(0) + '亿'
}

type ScRow = { name: string; attrs: string; kind: 'up' | 'mid' | 'down' | 'note'; kindLabel: string }

// ---- 供应链图谱解析（来自后端 supplyChainMarkdown：每行 "- 名称：类别 采购 3280万 / 采购占比% 42 ..."） ----
const supplyChainLines = computed<ScRow[]>(() => {
  const md = props.supplyChainMarkdown || ''
  if (!md.trim()) return []
  const lines: ScRow[] = []
  for (const raw of md.split('\n')) {
    const t = raw.trim()
    if (!t) continue
    // 小节标题（### 上游供应商 / ### 下游客户 / ### 中游集成商）
    if (t.startsWith('###')) {
      const title = t.replace(/^#+\s*/, '')
      if (title.includes('上游')) lines.push({ name: title, attrs: '', kind: 'note', kindLabel: '上游' })
      else if (title.includes('中游')) lines.push({ name: title, attrs: '', kind: 'note', kindLabel: '中游' })
      else if (title.includes('下游')) lines.push({ name: title, attrs: '', kind: 'note', kindLabel: '下游' })
      continue
    }
    // 数据行：- 名称：字段 / 字段 / ...
    const body = t.replace(/^-\s*/, '')
    const [name, ...rest] = body.split('：')
    const rel = t.includes('上游') || body.includes('采购') && !body.includes('销售')
      ? 'up' : body.includes('销售') ? 'down' : body.includes('集成') ? 'mid' : 'up'
    const attrs = rest.join('：').trim()
    lines.push({
      name: (name || '').trim() || body,
      attrs,
      kind: rel,
      kindLabel: rel === 'down' ? '下游客户' : rel === 'mid' ? '中游集成' : '上游供应商'
    })
  }
  return lines
})

// 未明确的未知项占位（演示）
const scUnknown = computed<string[]>(() => [])

// ---- 知识组装模拟控制台（实时滚动，逐 KI 打印轨迹） ----
type ConsoleLine = { time: string; icon: string; text: string }
const consoleLines = ref<ConsoleLine[]>([])
const consoleReady = ref(false)

const KI_TRAIL: { ki: string; name: string; load: boolean }[] = [
  { ki: 'KI-009', name: '企业客户基本信息', load: true },
  { ki: 'KI-FRONT-001', name: '公司供应链图谱', load: true },
  { ki: 'KI-FRONT-002', name: '产业链八维研判', load: true },
  { ki: 'KI-FRONT-003', name: '行内变动行为', load: true },
  { ki: 'KI-FRONT-004', name: '事实承诺事项', load: true },
  { ki: 'KI-FRONT-005', name: 'KYC信息缺口', load: true },
  { ki: 'KI-FRONT-006', name: '产品候选组合', load: true }
]

const ts = () => new Date().toLocaleTimeString('zh-CN', { hour12: false })

function push(icon: string, text: string) {
  consoleLines.value.push({ time: ts(), icon, text })
}

function delay(ms: number) { return new Promise(r => setTimeout(r, ms)) }

async function playAssembly() {
  consoleReady.value = false
  consoleLines.value = []
  push('🧭', '进入知识地图 KM-CORP-RM-PREVISIT，任务 PRE_VISIT_PREPARATION')
  await delay(200)
  for (const x of KI_TRAIL) {
    push('📖', `读取知识条目 ${x.ki}（${x.name}）`)
    await delay(150)
    push('🔎', `按 assetBinding 解析数据映射：${x.ki}${!x.load ? '（无结构化数据，文本要素）' : ''}`)
    await delay(150)
    if (x.load) {
      push('📦', `取数完成：${x.ki} → 已读取并能采集到该条目数据`)
    } else {
      push('📄', `装配文本要素：${x.ki} → KE 内容纳入上下文`)
    }
    await delay(150)
    push(x.load ? '✅' : '⚪', `${x.ki} 装配完成`)
    await delay(120)
  }
  push('🏁', `访前报告生成完成（R1），速战卡生成完成（R2）`)
  consoleReady.value = true
}

onMounted(() => { playAssembly() })
</script>

<style scoped>
.knowledge-previsit { display: flex; flex-direction: column; gap: 14px; }
.task-header { background: #eef2ff; border: 1px solid #c7d2fe; border-radius: 10px; padding: 14px 16px; }
.task-title { display: flex; align-items: center; gap: 8px; }
.task-badge { font-family: monospace; font-size: 11px; color: #4338ca; background: #fff; border: 1px solid #c7d2fe; padding: 2px 6px; border-radius: 4px; }
.task-name { font-weight: 700; color: #1a1a2e; }
.task-objective { margin: 8px 0 0; color: #374151; font-size: 13px; }
.task-mapping { margin: 4px 0 0; color: #888; font-size: 12px; }
.ki-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.ki-block { border: 1px solid #e5e7eb; border-radius: 10px; padding: 12px 14px; background: #fafbfc; }
.ki-title { margin: 0 0 8px; font-size: 14px; color: #1a1a2e; display: flex; align-items: center; gap: 8px; }
.ki-id { font-family: monospace; font-size: 11px; color: #4338ca; background: #eef2ff; padding: 1px 6px; border-radius: 4px; }
.ki-body { font-size: 13px; color: #374151; }
.kv { display: flex; gap: 10px; padding: 2px 0; }
.k { color: #888; min-width: 64px; }
.v { color: #1a1a2e; }
.ki-sub { font-size: 12px; color: #888; margin: 6px 0 2px; }
.ki-note { color: #aaa; font-size: 12px; }
.strategy { line-height: 1.6; }
ul { margin: 4px 0; padding-left: 18px; }
li { margin: 2px 0; }
.product { border-top: 1px dashed #e5e7eb; padding: 6px 0; }
.product-name { font-weight: 600; margin: 0; }
.amount { color: #166534; font-size: 12px; }
.product-reason, .product-term { margin: 2px 0; color: #555; font-size: 12px; }
.battle-card { border: 2px solid #1e3a8a; border-radius: 10px; padding: 14px 16px; background: #f8fafc; }
.bc-title { margin: 0; font-size: 15px; color: #1e3a8a; display: flex; gap: 8px; align-items: center; }
.bc-id { font-family: monospace; font-size: 11px; color: #fff; background: #1e3a8a; padding: 1px 6px; border-radius: 4px; }
.bc-meta { margin: 6px 0; color: #374151; font-size: 13px; }
.bc-tier { color: #888; font-size: 12px; }
.bc-section { margin: 8px 0; }
.bc-sub { font-size: 12px; color: #888; margin: 0 0 2px; }
.bc-bottom { margin: 8px 0 0; font-weight: 600; color: #b91c1c; }
.ki-supplychain .ki-body { display: flex; flex-direction: column; gap: 5px; }
.sc-row { display: flex; align-items: baseline; gap: 8px; font-size: 13px; }
.sc-badge { font-size: 10px; color: #fff; padding: 1px 6px; border-radius: 4px; flex: 0 0 auto; }
.sc-up { background: #166534; }
.sc-mid { background: #7c3aed; }
.sc-down { background: #b45309; }
.sc-note { background: #6b7280; }
.sc-name { font-weight: 600; color: #1a1a2e; }
.sc-attrs { color: #4b5563; }
.dbg-console { border: 1px solid #333; border-radius: 10px; background: #0f172a; color: #d1d5db; font-family: ui-monospace, monospace; overflow: hidden; }
.dbg-head { display: flex; justify-content: space-between; align-items: center; padding: 6px 12px; background: #1e293b; font-size: 12px; color: #e2e8f0; }
.dbg-body { max-height: 300px; overflow-y: auto; padding: 8px 12px; font-size: 12px; }
.dbg-line { display: flex; gap: 8px; line-height: 1.6; }
.dbg-time { color: #64748b; flex: 0 0 auto; }
.dbg-icon { flex: 0 0 auto; }
.dbg-text { color: #e2e8f0; }
.dbg-empty { color: #64748b; }
</style>
