<template>
  <div class="supply-chain-graph">
    <div v-if="loading" class="graph-loading">
      <n-spin size="small" />
      <span>加载图谱数据...</span>
    </div>

    <div v-else-if="error" class="graph-error">
      <n-empty description="图谱数据加载失败">
        <template #extra>
          <n-button size="small" @click="generateGraph">重新生成</n-button>
        </template>
      </n-empty>
    </div>

    <div v-else-if="!graphData" class="graph-empty">
      <n-empty description="暂无集团关系图谱数据">
        <template #extra>
          <n-button size="small" type="primary" @click="generateGraph" :loading="generating">
            生成图谱
          </n-button>
        </template>
      </n-empty>
    </div>

    <div v-else class="graph-content">
      <!-- 图谱统计 -->
      <div class="graph-stats">
        <div class="stat-item">
          <span class="stat-value">{{ graphData.result?.nodes?.length || 0 }}</span>
          <span class="stat-label">关联企业</span>
        </div>
        <div class="stat-item">
          <span class="stat-value">{{ graphData.result?.edges?.length || 0 }}</span>
          <span class="stat-label">关联关系</span>
        </div>
        <div class="stat-item">
          <span class="stat-value">{{ graphData.result?.interpretation?.riskLevel || '-' }}</span>
          <span class="stat-label">风险等级</span>
        </div>
      </div>

      <!-- 节点列表 -->
      <div v-if="graphData.result?.nodes?.length" class="nodes-section">
        <h4 class="sub-title">关联企业</h4>
        <div class="nodes-list">
          <n-card v-for="node in graphData.result.nodes" :key="node.id" size="small" class="node-card">
            <div class="node-header">
              <span class="node-name">{{ node.name }}</span>
              <n-tag v-if="node.type" size="tiny" :type="nodeTypeColor(node.type)">{{ node.type }}</n-tag>
            </div>
            <div class="node-meta">
              <span v-if="node.industry">行业: {{ node.industry }}</span>
              <span v-if="node.share != null">持股: {{ node.share }}%</span>
              <span v-if="node.annualAmount != null">年交易额: {{ formatAmount(node.annualAmount) }}</span>
            </div>
          </n-card>
        </div>
      </div>

      <!-- 关系列表 -->
      <div v-if="graphData.result?.edges?.length" class="edges-section">
        <h4 class="sub-title">关联关系</h4>
        <div class="edges-list">
          <div v-for="(edge, idx) in graphData.result.edges" :key="idx" class="edge-item">
            <span class="edge-source">{{ getNodeName(edge.source) }}</span>
            <span class="edge-relation">{{ edge.relation }}</span>
            <span class="edge-target">{{ getNodeName(edge.target) }}</span>
            <span v-if="edge.annualAmount" class="edge-amount">{{ formatAmount(edge.annualAmount) }}</span>
          </div>
        </div>
      </div>

      <!-- 解读 -->
      <div v-if="graphData.result?.interpretation" class="interpretation-section">
        <h4 class="sub-title">图谱解读</h4>
        <div class="interpretation-content">
          <p v-if="graphData.result.interpretation.summary">{{ graphData.result.interpretation.summary }}</p>
          <div v-if="graphData.result.interpretation.riskFactors?.length" class="risk-factors">
            <span class="risk-label">风险因素:</span>
            <n-tag v-for="factor in graphData.result.interpretation.riskFactors" :key="factor" size="small" type="warning">{{ factor }}</n-tag>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { NSpin, NButton, NEmpty, NCard, NTag } from 'naive-ui'
import { rootApi } from '../api/engagement'

interface GraphNode {
  id: string
  name: string
  layer?: string
  type?: string
  industry?: string
  annualAmount?: number
  share?: number
  trend?: string
  dataSource?: string
  verifyStatus?: string
}

interface GraphEdge {
  source: string
  target: string
  relation: string
  direction?: string
  annualAmount?: number
  share?: number
  settlement?: string
}

interface GraphInterpretation {
  summary?: string
  riskLevel?: string
  riskFactors?: string[]
  opportunities?: string[]
}

interface GraphResult {
  schemaVersion?: string
  buildStatus?: string
  nodes: GraphNode[]
  edges: GraphEdge[]
  interpretation?: GraphInterpretation
}

interface GraphReport {
  requestId: string
  customerId: string
  customerName?: string
  generatedAt?: string
  status: string
  reportUrl?: string
  result?: GraphResult
}

const props = defineProps<{
  customerId: string
}>()

const graphData = ref<GraphReport | null>(null)
const loading = ref(true)
const generating = ref(false)
const error = ref(false)
const nodeMap = ref<Map<string, string>>(new Map())

function getNodeName(id: string): string {
  return nodeMap.value.get(id) || id
}

function nodeTypeColor(type: string): 'info' | 'success' | 'warning' | 'default' {
  switch (type) {
    case 'CORE': return 'info'
    case 'SUBSIDIARY': return 'success'
    case 'SUPPLIER': return 'warning'
    default: return 'default'
  }
}

function formatAmount(amount: number): string {
  if (amount >= 100000000) return `${(amount / 100000000).toFixed(1)}亿`
  if (amount >= 10000) return `${(amount / 10000).toFixed(0)}万`
  return `${amount.toFixed(0)}元`
}

async function generateGraph() {
  generating.value = true
  error.value = false
  try {
    const { data } = await rootApi.post('/api/v1/engagement/supply-chain-graph', {
      customerId: props.customerId
    })
    graphData.value = data
    updateNodeMap()
  } catch (e) {
    console.error('Failed to generate graph:', e)
    error.value = true
  } finally {
    generating.value = false
  }
}

function updateNodeMap() {
  const map = new Map<string, string>()
  graphData.value?.result?.nodes?.forEach(n => map.set(n.id, n.name))
  nodeMap.value = map
}

onMounted(async () => {
  try {
    // 先尝试获取已有的图谱数据
    const { data } = await rootApi.get(`/api/v1/engagement/customer/${props.customerId}/knowledge-map`)
    if (data?.result?.nodes?.length) {
      graphData.value = { requestId: '', customerId: props.customerId, status: 'COMPLETED', result: data.result }
      updateNodeMap()
    }
  } catch {
    // 知识图谱不可用，不设置error，让用户手动生成
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.supply-chain-graph {
  min-height: 200px;
}
.graph-loading {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-6) 0;
  justify-content: center;
  color: var(--text-secondary);
}
.graph-error, .graph-empty {
  padding: var(--space-4) 0;
}
.graph-content {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}
.graph-stats {
  display: flex;
  gap: var(--space-6);
  padding: var(--space-3) var(--space-4);
  background: var(--bg-surface);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-light);
}
.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-1);
}
.stat-value {
  font-size: var(--text-xl);
  font-weight: 600;
  color: var(--brand-primary);
}
.stat-label {
  font-size: var(--text-xs);
  color: var(--text-tertiary);
}
.sub-title {
  font-size: var(--text-base);
  color: var(--text-primary);
  margin: 0 0 var(--space-2);
  font-weight: 600;
}
.nodes-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: var(--space-2);
}
.node-card {
  border-left: 3px solid var(--brand-primary);
}
.node-header {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  margin-bottom: var(--space-1);
}
.node-name {
  font-weight: 600;
  font-size: var(--text-sm);
  color: var(--text-primary);
}
.node-meta {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-3);
  font-size: var(--text-xs);
  color: var(--text-secondary);
}
.edges-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}
.edge-item {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-3);
  background: var(--bg-surface);
  border-radius: var(--radius-sm);
  border: 1px solid var(--border-light);
  font-size: var(--text-sm);
}
.edge-source, .edge-target {
  font-weight: 600;
  color: var(--text-primary);
}
.edge-relation {
  color: var(--brand-primary);
  font-size: var(--text-xs);
  padding: 0 var(--space-1);
  background: rgba(0, 102, 204, 0.08);
  border-radius: var(--radius-sm);
}
.edge-amount {
  margin-left: auto;
  color: var(--text-secondary);
  font-size: var(--text-xs);
}
.interpretation-content {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  line-height: var(--leading-relaxed);
}
.risk-factors {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  margin-top: var(--space-2);
  flex-wrap: wrap;
}
.risk-label {
  font-size: var(--text-xs);
  color: var(--text-tertiary);
}
</style>
