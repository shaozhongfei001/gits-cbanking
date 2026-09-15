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
            :interpretation="interp"
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
  background: #f3f6f9;
  color: #1b2632;
  font-family: "Noto Sans SC", "Microsoft YaHei", system-ui, sans-serif;
}
header {
  padding: 18px 26px;
  background: #fff;
  border-bottom: 1px solid #d8e2ec;
}
header h1 { margin: 0; font-size: 19px; color: #0b2e4f; }
header h1 small { color: #596779; font-weight: 400; font-size: 13px; margin-left: 10px; }
.meta { margin-top: 8px; font-size: 12px; color: #596779; display: flex; gap: 18px; flex-wrap: wrap; }
.badge { display: inline-block; padding: 2px 10px; border-radius: 20px; font-size: 11px; font-weight: 600; }
.b-complete { background: #e8f8f6; color: #087771; border: 1px solid #12a7a0; }
.b-partial { background: #fff5dc; color: #7a4b00; border: 1px solid #f2b84b; }
.wrap { padding: 20px 26px; max-width: 1400px; margin: 0 auto; }
.cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; margin-bottom: 18px; }
.card {
  position: relative;
  background: #fff;
  border: 1px solid #d8e2ec;
  border-radius: 6px;
  padding: 12px 14px 12px 18px;
}
.card::before {
  content: '';
  position: absolute;
  left: 0; top: 0; bottom: 0;
  width: 3px;
  border-radius: 6px 0 0 6px;
  background: #1976d2;
}
.card:nth-child(2)::before { background: #12a7a0; }
.card:nth-child(3)::before { background: #12a7a0; }
.card:nth-child(4)::before { background: #48a7e8; }
.card:nth-child(5)::before { background: #1976d2; }
.card:nth-child(6)::before { background: #f2b84b; }
.card-v { font-size: 17px; font-weight: 700; color: #0b2e4f; word-break: break-all; }
.card-k { font-size: 11px; color: #596779; margin-top: 3px; }
.gcard {
  background: #fff;
  border: 1px solid #d8e2ec;
  border-radius: 6px;
  padding: 12px 16px 16px;
  margin-bottom: 18px;
  position: relative;
}
.gcard h2 { margin: 4px 0 8px; font-size: 14px; color: #0b2e4f; }
.gcard h2 span { color: #596779; font-weight: 400; font-size: 12px; margin-left: 8px; }
.panel {
  position: absolute; left: 16px; top: 56px; width: 280px;
  background: #fff; border: 1px solid #d8e2ec; border-radius: 6px; padding: 10px 12px;
  box-shadow: 0 4px 12px rgba(8, 35, 59, 0.08);
}
.panel h3 { margin: 0 0 8px; font-size: 13px; color: #1976d2; }
.panel .kv { display: flex; justify-content: space-between; gap: 8px; font-size: 12px; padding: 3px 0; }
.panel .kv span { color: #596779; }
.panel .kv b { color: #1b2632; font-weight: 600; text-align: right; }
.isec {
  background: #fff;
  border: 1px solid #d8e2ec;
  border-left: 3px solid #1976d2;
  border-radius: 6px;
  padding: 12px 16px;
  margin-bottom: 12px;
}
.isec:nth-child(odd) { border-left-color: #12a7a0; }
.isec h3 { margin: 0 0 8px; font-size: 14px; color: #0b2e4f; }
.isec p, .isec ul { margin: 6px 0; line-height: 1.7; font-size: 13px; color: #1b2632; }
.isec ul { padding-left: 20px; }
details { background: #fff; border: 1px solid #d8e2ec; border-radius: 6px; margin-bottom: 12px; }
summary { padding: 10px 16px; cursor: pointer; color: #0b2e4f; font-size: 13px; }
.tblwrap { overflow: auto; max-height: 360px; padding: 0 12px 12px; }
table { border-collapse: collapse; width: 100%; font-size: 12px; }
th, td { border: 1px solid #d8e2ec; padding: 6px 9px; text-align: left; white-space: nowrap; }
th { background: #f3f6f9; color: #596779; position: sticky; top: 0; }
td { color: #1b2632; }
.tag { padding: 1px 8px; border-radius: 12px; font-size: 11px; }
.t-supplier { background: #e8f8f6; color: #087771; }
.t-enterprise { background: #eaf4fe; color: #1976d2; }
.t-customer { background: #eaf4fe; color: #0b2e4f; }
.sc-state { padding: 80px 24px; text-align: center; color: #596779; }
.sc-expired p { font-size: 18px; color: #7a4b00; }
.hint { color: #596779 !important; font-size: 13px !important; }
.retry {
  margin-top: 16px; background: #fff; color: #1976d2; border: 1px solid #1976d2;
  border-radius: 6px; padding: 8px 16px; cursor: pointer;
}
</style>
