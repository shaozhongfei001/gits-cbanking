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
        <span v-if="skillExecutiveSummary"> · {{ skillExecutiveSummary }}</span>
      </p>
      <p class="task-mapping">
        知识地图任务映射：DKWS 按 customerId 取 KI；本页只展示 Skill 返回正文。装配轨迹为 Debug。
      </p>
    </div>

    <!-- 知识区：按 KI 分组 -->
    <div class="ki-grid">
      <!-- KI-009 企业客户基本信息 -->
      <section class="ki-block" :class="kiClass('KI-009')" data-ki="KI-009">
        <h3 class="ki-title"><span class="ki-id">KI-009</span> 企业客户基本信息</h3>
        <div class="ki-body" v-if="sectionOf('KI-009')">
          <p class="ki-skill">{{ sectionOf('KI-009') }}</p>
        </div>
        <div class="ki-body" v-else>
          <p class="ki-note">{{ emptyHint('KI-009') }}</p>
        </div>
      </section>

      <!-- KI-FRONT-001 公司供应链图谱（SK-FRONT-002 力导向，不解析 DKWS HTML） -->
      <section class="ki-block ki-supplychain" :class="kiClass('KI-FRONT-001')" data-ki="KI-FRONT-001">
        <h3 class="ki-title">
          <span class="ki-id">KI-FRONT-001</span> 公司供应链图谱
          <span v-if="graphPartial" class="sc-partial">部分降级，仅供参考</span>
          <a v-if="fullReportPath" class="sc-full" :href="fullReportPath" @click.prevent="openFull">完整报告页</a>
        </h3>
        <div v-if="supplyChainLoading" class="ki-note">正在生成三段式力导向图谱…</div>
        <div v-else-if="graphNodes.length" class="sc-viz">
          <SupplyChainForceGraph :nodes="graphNodes" :edges="graphEdges" compact />
        </div>
        <div v-else-if="sectionOf('KI-FRONT-001')" class="ki-body">
          <p class="ki-skill">{{ sectionOf('KI-FRONT-001') }}</p>
        </div>
        <div class="ki-body" v-else>
          <p class="ki-note">{{ emptyHint('KI-FRONT-001') }}</p>
        </div>
      </section>

      <section class="ki-block" :class="kiClass('KI-FRONT-002')" data-ki="KI-FRONT-002">
        <h3 class="ki-title"><span class="ki-id">KI-FRONT-002</span> 产业链八维研判</h3>
        <div class="ki-body">
          <p class="ki-skill" v-if="sectionOf('KI-FRONT-002')">{{ sectionOf('KI-FRONT-002') }}</p>
          <p class="ki-note" v-else>{{ emptyHint('KI-FRONT-002') }}</p>
        </div>
      </section>

      <section class="ki-block" :class="kiClass('KI-FRONT-003')" data-ki="KI-FRONT-003">
        <h3 class="ki-title"><span class="ki-id">KI-FRONT-003</span> 行内变动行为</h3>
        <div class="ki-body">
          <p class="ki-skill" v-if="sectionOf('KI-FRONT-003')">{{ sectionOf('KI-FRONT-003') }}</p>
          <p class="ki-note" v-else>{{ emptyHint('KI-FRONT-003') }}</p>
        </div>
      </section>

      <section class="ki-block" :class="kiClass('KI-FRONT-004')" data-ki="KI-FRONT-004">
        <h3 class="ki-title"><span class="ki-id">KI-FRONT-004</span> 事实承诺事项 / 沟通话术</h3>
        <div class="ki-body">
          <p class="ki-skill" v-if="sectionOf('KI-FRONT-004')">{{ sectionOf('KI-FRONT-004') }}</p>
          <p class="ki-note" v-else>{{ emptyHint('KI-FRONT-004') }}</p>
        </div>
      </section>

      <section class="ki-block" :class="kiClass('KI-FRONT-005')" data-ki="KI-FRONT-005">
        <h3 class="ki-title"><span class="ki-id">KI-FRONT-005</span> KYC信息缺口</h3>
        <div class="ki-body">
          <p class="ki-skill" v-if="sectionOf('KI-FRONT-005')">{{ sectionOf('KI-FRONT-005') }}</p>
          <p class="ki-note" v-else>{{ emptyHint('KI-FRONT-005') }}</p>
        </div>
      </section>

      <section class="ki-block" :class="kiClass('KI-FRONT-006')" data-ki="KI-FRONT-006">
        <h3 class="ki-title"><span class="ki-id">KI-FRONT-006</span> 产品候选组合</h3>
        <div class="ki-body">
          <p class="ki-skill" v-if="sectionOf('KI-FRONT-006')">{{ sectionOf('KI-FRONT-006') }}</p>
          <p class="ki-note" v-else>{{ emptyHint('KI-FRONT-006') }}</p>
        </div>
      </section>
    </div>

    <!-- 速战卡（R2）按知识条目标注；Skill 无章节时仍展示区块，不整卡隐藏 -->
    <div class="battle-card" v-if="battleCard">
      <h3 class="bc-title">60秒速战卡 <span class="bc-id">R2</span></h3>
      <p class="bc-meta">{{ battleCard.customerName }} · {{ battleCard.visitObjective }}
        <span class="bc-tier">{{ battleCard.customerTier }} · {{ battleCard.riskLevel }}</span></p>
      <template v-if="battleCardFilled">
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
      </template>
      <p v-else class="ki-note">DKWS 未返回速战卡</p>
    </div>

    <!-- 知识组装模拟控制台：实时滚动，逐 KI 打印组装轨迹 -->
    <section class="dbg-console">
      <div class="dbg-head">
        <span>{{ consoleTitle }}</span>
        <n-tag size="tiny" :type="consoleReady ? 'success' : 'info'">{{ consoleReady ? '已完成' : '组装中…' }}</n-tag>
      </div>
      <div class="dbg-body">
        <div v-for="(ln, i) in consoleLines" :key="i" class="dbg-line" :class="{ 'dbg-ki-line': !!ln.kiId, 'dbg-skip': ln.status === 'skipped' }">
          <span class="dbg-time">{{ ln.time }}</span>
          <span class="dbg-icon">{{ ln.icon }}</span>
          <span v-if="ln.kiId" class="dbg-ki">{{ ln.kiId }}</span>
          <span class="dbg-text">{{ ln.text }}</span>
        </div>
        <div v-if="consoleReady && !consoleLines.length" class="dbg-empty">（无轨迹输出）</div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import type { AssemblyTraceStep, SkillReportSection, SupplyChainGraphReport } from '../api/engagement'
import SupplyChainForceGraph from './SupplyChainForceGraph.vue'
import { isPartialBuild } from '../utils/supplyChainFormat'
import { sectionContent } from '../utils/kiSection'

interface PrevisitReport {
  reportId?: string
  visitObjective?: string
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
const props = defineProps<{
  report: PrevisitReport
  battleCard?: BattleCard
  assemblyTrace?: AssemblyTraceStep[]
  skillSections?: SkillReportSection[]
  skillExecutiveSummary?: string
  supplyChainReport?: SupplyChainGraphReport | null
  supplyChainLoading?: boolean
}>()

const router = useRouter()
const graphNodes = computed(() => props.supplyChainReport?.result.nodes || [])
const graphEdges = computed(() => props.supplyChainReport?.result.edges || [])
const graphPartial = computed(() => isPartialBuild(props.supplyChainReport?.result.buildStatus))
const fullReportPath = computed(() =>
  props.supplyChainReport?.requestId ? `/supply-chain-report/${props.supplyChainReport.requestId}` : '')

function openFull() {
  if (props.supplyChainReport?.requestId) {
    router.push({ name: 'SupplyChainGraphReport', params: { requestId: props.supplyChainReport.requestId } })
  }
}

function sectionOf(kiId: string): string {
  return sectionContent(props.skillSections, kiId)
}

function emptyHint(kiId: string): string {
  const status = kiOutcome.value[kiId]
  if (status === 'skipped') return 'DKWS 未取到该条目（平台知识库未命中）'
  if (status === 'failed') return 'DKWS 取数失败'
  return 'DKWS 未返回该条目'
}

const battleCardFilled = computed(() => {
  const card = props.battleCard
  if (!card) return false
  return Boolean(
    (card.keyPoints && card.keyPoints.length)
    || (card.productHints && card.productHints.length)
    || (card.dontForget && card.dontForget.length)
    || (card.bottomLine && card.bottomLine.trim()),
  )
})

function kiClass(id: string) {
  return {
    'ki-active': activeKiId.value === id,
    'ki-hit': kiOutcome.value[id] === 'ok',
    'ki-skip': kiOutcome.value[id] === 'skipped' || kiOutcome.value[id] === 'failed',
  }
}

type ConsoleLine = { time: string; icon: string; text: string; kiId?: string; status?: string }
const consoleLines = ref<ConsoleLine[]>([])
const consoleReady = ref(false)
const activeKiId = ref('')
const kiOutcome = ref<Record<string, string>>({})

const consoleTitle = computed(() =>
  (props.assemblyTrace && props.assemblyTrace.length > 0)
    ? '🖥️ DSH Skill 装配轨迹（Debug）'
    : '🖥️ 知识组装控制台（Debug）'
)

const PHASE_ICON: Record<string, string> = {
  resolve: '🧭',
  idempotency: '🔁',
  evidence: '📎',
  validate: '🔎',
  dkws: '📚',
  model: '🤖',
  parse: '🧩',
  compose: '🏁',
}

const ts = () => new Date().toLocaleTimeString('zh-CN', { hour12: false })

function push(icon: string, text: string, extra: { kiId?: string; status?: string } = {}) {
  consoleLines.value.push({ time: ts(), icon, text, kiId: extra.kiId, status: extra.status })
}

function delay(ms: number) { return new Promise(r => setTimeout(r, ms)) }

async function playAssembly() {
  consoleReady.value = false
  consoleLines.value = []
  activeKiId.value = ''
  kiOutcome.value = {}
  const steps = props.assemblyTrace || []
  if (steps.length === 0) {
    push('⚠️', '未收到 DSH assemblyTrace（DKWS 未返回轨迹）')
    consoleReady.value = true
    return
  }
  push('🛰️', `skill-customer-previsit-report · ${steps.length} 步 · ok=平台库取到该 KI`)
  await delay(120)
  for (const step of steps) {
    if (step.kiId) {
      activeKiId.value = step.kiId
      kiOutcome.value = { ...kiOutcome.value, [step.kiId]: step.status }
      document.querySelector(`[data-ki="${step.kiId}"]`)?.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
    }
    push(PHASE_ICON[step.phase] || '•', `[${step.phase}/${step.status}] ${step.message}`, {
      kiId: step.kiId,
      status: step.status,
    })
    await delay(160)
  }
  activeKiId.value = ''
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
.ki-supplychain { grid-column: 1 / -1; }
.ki-title .sc-partial { margin-left: auto; font-size: 11px; color: #b45309; background: #fef3c7; padding: 1px 8px; border-radius: 10px; font-weight: 600; }
.ki-title .sc-full { font-size: 12px; color: #4338ca; font-weight: 500; }
.sc-viz { background: #0b1322; border-radius: 10px; padding: 8px 10px 12px; min-height: 360px; }
.ki-block { border: 1px solid #e5e7eb; border-radius: 10px; padding: 12px 14px; background: #fafbfc; transition: box-shadow .15s, border-color .15s, background .15s; }
.ki-block.ki-active { outline: 2px solid #4338ca; box-shadow: 0 0 0 3px #c7d2fe; }
.ki-block.ki-hit { border-color: #86efac; background: #f0fdf4; }
.ki-block.ki-skip { border-color: #fcd34d; background: #fffbeb; }
.ki-block.ki-hit .ki-id { background: #dcfce7; color: #166534; }
.ki-block.ki-skip .ki-id { background: #fef3c7; color: #92400e; }
.ki-title { margin: 0 0 8px; font-size: 14px; color: #1a1a2e; display: flex; align-items: center; gap: 8px; }
.ki-id { font-family: monospace; font-size: 11px; color: #4338ca; background: #eef2ff; padding: 1px 6px; border-radius: 4px; }
.ki-body { font-size: 13px; color: #374151; }
.kv { display: flex; gap: 10px; padding: 2px 0; }
.k { color: #888; min-width: 64px; }
.v { color: #1a1a2e; }
.ki-sub { font-size: 12px; color: #888; margin: 6px 0 2px; }
.ki-note { color: #aaa; font-size: 12px; }
.ki-skill { margin: 0; white-space: pre-wrap; line-height: 1.6; }
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
.dbg-line { display: flex; gap: 8px; line-height: 1.6; align-items: baseline; }
.dbg-ki { font-size: 10px; color: #c7d2fe; background: #312e81; padding: 0 5px; border-radius: 3px; flex: 0 0 auto; }
.dbg-skip .dbg-text { color: #fbbf24; }
.dbg-ki-line { background: rgba(67, 56, 202, 0.12); }
.dbg-time { color: #64748b; flex: 0 0 auto; }
.dbg-icon { flex: 0 0 auto; }
.dbg-text { color: #e2e8f0; }
.dbg-empty { color: #64748b; }
</style>
