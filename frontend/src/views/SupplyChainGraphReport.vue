<template>
  <div class="sc-page">
    <div v-if="loading" class="sc-state">正在加载供应链图谱报告…</div>
    <div v-else-if="expired" class="sc-state sc-expired">
      <p>报告已过期，请重新执行</p>
      <p class="hint">缓存约 10 分钟，过期后需再次调用 Skill。</p>
      <button type="button" class="retry" @click="retry">返回工作台重新执行</button>
    </div>
    <div v-else-if="error" class="sc-state">
      <p>{{ error }}</p>
      <button type="button" class="retry" @click="load">重试</button>
    </div>
    <template v-else-if="report">
      <header>
        <h1>供应链图谱分析报告 <small>SK-FRONT-002 · bank-front-supply-chain-graph</small></h1>
        <div class="meta">
          <span>客户：<b>{{ report.customerName || '—' }}</b></span>
          <span>客户ID：{{ report.customerId }}</span>
          <span>生成时间：{{ report.generatedAt }}</span>
          <span class="badge" :class="partial ? 'b-partial' : 'b-complete'">
            {{ partial ? 'partial · 部分降级，仅供参考' : (report.result.buildStatus || 'complete') }}
          </span>
          <span>请求ID：{{ report.requestId }}</span>
        </div>
      </header>
      <div class="wrap">
        <div class="cards">
          <div class="card"><div class="card-v">{{ stats.nodeCount }}</div><div class="card-k">节点总数</div></div>
          <div class="card"><div class="card-v">{{ stats.edgeCount }}</div><div class="card-k">关系边</div></div>
          <div class="card"><div class="card-v">{{ stats.suppliers }}</div><div class="card-k">上游供应商</div></div>
          <div class="card"><div class="card-v">{{ stats.customers }}</div><div class="card-k">下游客户</div></div>
          <div class="card"><div class="card-v">{{ enterpriseName }}</div><div class="card-k">本企业</div></div>
          <div class="card"><div class="card-v">{{ formatConfidence(interp?.confidence) }}</div><div class="card-k">置信度</div></div>
        </div>
        <div class="gcard">
          <h2>三段式供应链图谱 <span>滚轮缩放 · 拖拽平移 · 双击聚焦 · 点击高亮 1 跳邻居</span></h2>
          <SupplyChainForceGraph
            :nodes="nodes"
            :edges="edges"
            @select="selected = $event"
          />
          <aside v-if="selected" class="panel">
            <h3>节点详情</h3>
            <div class="kv"><span>名称</span><b>{{ selected.name || '—' }}</b></div>
            <div class="kv"><span>ID</span><b>{{ selected.id || '—' }}</b></div>
            <div class="kv"><span>层级</span><b>{{ LAYER_LABEL[selected.layer || ''] || selected.layer || '—' }}</b></div>
            <div class="kv"><span>金额</span><b>{{ formatAmountYuan(selected.annualAmount) }}</b></div>
            <div class="kv"><span>占比</span><b>{{ formatShare(selected.share) }}</b></div>
            <div class="kv"><span>趋势</span><b>{{ TREND_LABEL[selected.trend || ''] || selected.trend || '—' }}</b></div>
            <div class="kv"><span>核验状态</span><b>{{ selected.verifyStatus || '—' }}</b></div>
            <div class="kv"><span>数据源</span><b>{{ selected.dataSource || '—' }}</b></div>
          </aside>
        </div>
        <section class="isec"><h3>供应链位置</h3><p>{{ interp?.supplyChainPosition || '—' }}</p></section>
        <section class="isec"><h3>议价能力</h3><p>{{ interp?.bargainingPower || '—' }}</p></section>
        <section class="isec">
          <h3>集中度风险</h3>
          <ul v-if="interp?.concentrationRisk?.length">
            <li v-for="(item, i) in interp.concentrationRisk" :key="i">{{ item }}</li>
          </ul>
          <p v-else>—</p>
        </section>
        <section class="isec"><h3>关键变动</h3><p>{{ interp?.keyChanges || '—' }}</p></section>
        <section class="isec"><h3>综合研判</h3><p>{{ interp?.overallAssessment || '—' }}</p></section>
        <section class="isec">
          <h3>访前必问事项</h3>
          <ul v-if="interp?.followUpQuestions?.length">
            <li v-for="(q, i) in interp.followUpQuestions" :key="i">{{ q }}</li>
          </ul>
          <p v-else>—</p>
        </section>
        <details open>
          <summary>节点明细（{{ nodes.length }}）</summary>
          <div class="tblwrap">
            <table>
              <thead><tr><th>名称</th><th>层级</th><th>年金额</th><th>占比</th><th>趋势</th><th>核验</th><th>数据源</th></tr></thead>
              <tbody>
                <tr v-for="n in nodes" :key="n.id">
                  <td>{{ n.name }}</td>
                  <td><span class="tag" :class="'t-'+(n.layer||'')">{{ LAYER_LABEL[n.layer || ''] || n.layer }}</span></td>
                  <td>{{ formatAmountYuan(n.annualAmount) }}</td>
                  <td>{{ formatShare(n.share) }}</td>
                  <td>{{ TREND_LABEL[n.trend || ''] || n.trend || '—' }}</td>
                  <td>{{ n.verifyStatus || '—' }}</td>
                  <td>{{ n.dataSource || '—' }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </details>
        <details>
          <summary>关系边明细（{{ edges.length }}）</summary>
          <div class="tblwrap">
            <table>
              <thead><tr><th>来源</th><th></th><th>目标</th><th>关系</th><th>年金额</th><th>占比</th><th>结算/账期</th></tr></thead>
              <tbody>
                <tr v-for="(e, i) in edges" :key="i">
                  <td>{{ nameOf(e.source) }}</td>
                  <td>→</td>
                  <td>{{ nameOf(e.target) }}</td>
                  <td>{{ RELATION_LABEL[e.relation || ''] || e.relation || '—' }}</td>
                  <td>{{ formatAmountYuan(e.annualAmount) }}</td>
                  <td>{{ formatShare(e.share) }}</td>
                  <td>{{ e.settlement || '—' }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </details>
      </div>
    </template>
    <div v-else class="sc-state">尚未请求报告。</div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import {
  fetchSupplyChainGraphReport,
  type SupplyChainGraphNode,
  type SupplyChainGraphReport,
} from '../api/engagement'
import SupplyChainForceGraph from '../components/SupplyChainForceGraph.vue'
import {
  formatAmountYuan,
  formatConfidence,
  formatShare,
  isPartialBuild,
  LAYER_LABEL,
  RELATION_LABEL,
  TREND_LABEL,
} from '../utils/supplyChainFormat'

const route = useRoute()
const router = useRouter()
const loading = ref(true)
const expired = ref(false)
const error = ref('')
const report = ref<SupplyChainGraphReport | null>(null)
const selected = ref<SupplyChainGraphNode | null>(null)

const nodes = computed(() => report.value?.result.nodes || [])
const edges = computed(() => report.value?.result.edges || [])
const interp = computed(() => report.value?.result.interpretation)
const partial = computed(() => isPartialBuild(report.value?.result.buildStatus))
const enterpriseName = computed(() =>
  nodes.value.find(n => n.layer === 'enterprise')?.name || report.value?.customerName || '—')
const stats = computed(() => ({
  nodeCount: nodes.value.length,
  edgeCount: edges.value.length,
  suppliers: nodes.value.filter(n => n.layer === 'supplier').length,
  customers: nodes.value.filter(n => n.layer === 'customer').length,
}))

function nameOf(id?: string) {
  return nodes.value.find(n => n.id === id)?.name || id || '—'
}

function isExpiredStatus(status?: number, message?: string) {
  return status === 404 || message === '报告已过期，请重新执行'
}

function errorPayload(e: unknown): { status?: number; message?: string } {
  if (axios.isAxiosError(e)) {
    return { status: e.response?.status, message: e.response?.data?.message as string | undefined }
  }
  if (e && typeof e === 'object' && 'response' in e) {
    const response = (e as { response?: { status?: number; data?: { message?: string } } }).response
    return { status: response?.status, message: response?.data?.message }
  }
  return {}
}

async function load() {
  const requestId = String(route.params.requestId || '')
  loading.value = true
  expired.value = false
  error.value = ''
  report.value = null
  selected.value = null
  if (!requestId) {
    loading.value = false
    error.value = '缺少 requestId'
    return
  }
  try {
    report.value = await fetchSupplyChainGraphReport(requestId)
  } catch (e: unknown) {
    const payload = errorPayload(e)
    if (isExpiredStatus(payload.status, payload.message)) {
      expired.value = true
    } else {
      error.value = payload.message || (e instanceof Error ? e.message : '加载失败')
    }
  } finally {
    loading.value = false
  }
}

function retry() {
  router.push({ name: 'EngagementWorkspace' })
}

onMounted(load)
</script>

<style scoped>
.sc-page {
  min-height: 100%;
  background: #0b1322;
  color: #e2e8f0;
  font-family: "Noto Sans SC", "Microsoft YaHei", system-ui, sans-serif;
}
header { padding: 18px 26px; background: linear-gradient(135deg, #101c33, #0e1630); border-bottom: 1px solid #1c2f52; }
header h1 { margin: 0; font-size: 19px; color: #f1f5f9; }
header h1 small { color: #7c9bd1; font-weight: 400; font-size: 13px; margin-left: 10px; }
.meta { margin-top: 8px; font-size: 12px; color: #8ba3c7; display: flex; gap: 18px; flex-wrap: wrap; }
.badge { display: inline-block; padding: 2px 10px; border-radius: 20px; font-size: 11px; font-weight: 600; }
.b-complete { background: rgba(45, 212, 167, .15); color: #2dd4a7; border: 1px solid rgba(45, 212, 167, .4); }
.b-partial { background: rgba(251, 191, 36, .15); color: #fbbf24; border: 1px solid rgba(251, 191, 36, .4); }
.wrap { padding: 20px 26px; max-width: 1400px; margin: 0 auto; }
.cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 12px; margin-bottom: 18px; }
.card { background: #0f1b33; border: 1px solid #1e2f55; border-radius: 10px; padding: 12px 14px; }
.card-v { font-size: 17px; font-weight: 700; color: #fbbf24; word-break: break-all; }
.card-k { font-size: 11px; color: #8ba3c7; margin-top: 3px; }
.gcard { background: #0d1728; border: 1px solid #1e2f55; border-radius: 12px; padding: 12px; margin-bottom: 18px; position: relative; }
.gcard h2 { margin: 4px 8px 8px; font-size: 14px; color: #cbd5e1; }
.gcard h2 span { color: #64748b; font-weight: 400; font-size: 12px; margin-left: 8px; }
.panel {
  position: absolute; left: 16px; bottom: 16px; width: 280px;
  background: rgba(15, 27, 51, .94); border: 1px solid #1e2f55; border-radius: 8px; padding: 10px 12px;
}
.panel h3 { margin: 0 0 8px; font-size: 13px; color: #ffd166; }
.panel .kv { display: flex; justify-content: space-between; gap: 8px; font-size: 12px; padding: 3px 0; }
.panel .kv span { color: #8ba3c7; }
.panel .kv b { color: #e2e8f0; font-weight: 600; text-align: right; }
.isec { background: #0f1b33; border: 1px solid #1e2f55; border-left: 3px solid #4d9fff; border-radius: 8px; padding: 12px 16px; margin-bottom: 12px; }
.isec:nth-child(odd) { border-left-color: #2dd4a7; }
.isec h3 { margin: 0 0 8px; font-size: 14px; color: #ffd166; }
.isec p, .isec ul { margin: 6px 0; line-height: 1.7; font-size: 13px; color: #dbe4f3; }
.isec ul { padding-left: 20px; }
details { background: #0f1b33; border: 1px solid #1e2f55; border-radius: 8px; margin-bottom: 12px; }
summary { padding: 10px 16px; cursor: pointer; color: #cbd5e1; font-size: 13px; }
.tblwrap { overflow: auto; max-height: 360px; padding: 0 12px 12px; }
table { border-collapse: collapse; width: 100%; font-size: 12px; }
th, td { border: 1px solid #1e2f55; padding: 6px 9px; text-align: left; white-space: nowrap; }
th { background: #132242; color: #8ba3c7; position: sticky; top: 0; }
td { color: #dbe4f3; }
.tag { padding: 1px 8px; border-radius: 12px; font-size: 11px; }
.t-supplier { background: rgba(77, 159, 255, .15); color: #7db4ff; }
.t-enterprise { background: rgba(239, 71, 111, .15); color: #ff8fa5; }
.t-customer { background: rgba(45, 212, 167, .15); color: #5ce0b8; }
.sc-state { padding: 80px 24px; text-align: center; color: #cbd5e1; }
.sc-expired p { font-size: 18px; color: #fbbf24; }
.hint { color: #8ba3c7 !important; font-size: 13px !important; }
.retry {
  margin-top: 16px; background: #16233f; color: #fbbf24; border: 1px solid #fbbf24;
  border-radius: 8px; padding: 8px 16px; cursor: pointer;
}
</style>
