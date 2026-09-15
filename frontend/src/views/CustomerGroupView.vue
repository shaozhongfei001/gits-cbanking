<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import ObjectHeader from '../components/shell/ObjectHeader.vue'
import PageState from '../components/shell/PageState.vue'
import DisabledAction from '../components/shell/DisabledAction.vue'
import CustomerRecordTabs from '../components/shell/CustomerRecordTabs.vue'
import SupplyChainForceGraph from '../components/SupplyChainForceGraph.vue'
import {
  executeSupplyChainGraph,
  fetchOperatingView,
  type Customer,
  type CreditFacilityRead,
  type SupplyChainGraphEdge,
  type SupplyChainGraphNode,
  type SupplyChainGraphReport,
} from '../api/engagement'
import { LAYER_LABEL } from '../utils/supplyChainFormat'
import { deriveResourceStatus } from '../composables/useResourceStatus'
import { usePageReferenceStore } from '../stores/pageReference'

const PAGE_ID = 'P05'
const OBJECT_TYPE = '客户 Account'

const route = useRoute()
const pageRefs = usePageReferenceStore()

const customerId = computed(() => String(route.params.id || ''))
const customer = ref<Customer | null>(null)
const facilities = ref<CreditFacilityRead[]>([])
const graphReport = ref<SupplyChainGraphReport | null>(null)
const graphError = ref('')
const loading = ref(true)
const error = ref('')
const requested = ref(false)
const selectedNode = ref<SupplyChainGraphNode | null>(null)

const nodes = computed<SupplyChainGraphNode[]>(() => graphReport.value?.result?.nodes || [])
const edges = computed<SupplyChainGraphEdge[]>(() => graphReport.value?.result?.edges || [])
const memberCount = computed(() => nodes.value.length)
const upstreamCount = computed(() => nodes.value.filter(n => n.layer === 'supplier').length)
const downstreamCount = computed(() => nodes.value.filter(n => n.layer === 'customer').length)

const status = computed(() =>
  deriveResourceStatus({
    loading: loading.value,
    error: error.value,
    hasData: customer.value != null,
    requested: requested.value,
  }),
)

const title = computed(() => customer.value?.customerName
  ? `${customer.value.customerName} · 集团关系`
  : '客户记录·集团关系')

function persistReference() {
  pageRefs.capture(PAGE_ID, {
    objectType: OBJECT_TYPE,
    recordId: customerId.value,
    viewId: 'group_graph',
    subtab: selectedNode.value?.id || 'group',
    scrollAnchor: typeof window !== 'undefined' ? window.scrollY : 0,
  })
}

async function loadRecord() {
  loading.value = true
  error.value = ''
  graphError.value = ''
  requested.value = true
  graphReport.value = null
  selectedNode.value = null
  try {
    const view = await fetchOperatingView(customerId.value)
    customer.value = view.customer
    facilities.value = view.creditFacilities || []
    try {
      graphReport.value = await executeSupplyChainGraph(customerId.value)
    } catch (e: unknown) {
      graphError.value = e instanceof Error ? e.message : 'DKWS 未返回'
      graphReport.value = null
    }
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : '无法获取客户记录'
    customer.value = null
    facilities.value = []
  } finally {
    loading.value = false
  }
}

onMounted(loadRecord)
watch(customerId, loadRecord)
onBeforeUnmount(persistReference)
</script>

<template>
  <div class="group-view" data-testid="p05-group">
    <ObjectHeader
      :page-id="PAGE_ID"
      :object-type="OBJECT_TYPE"
      object-status="关系图谱"
      :title="title"
    />
    <p class="page-subtitle">集团架构、上下游与知识图谱来自 DKWS Skill（bank-front-supply-chain-graph）。DKWS 未返回时不使用本地种子拼图。</p>
    <CustomerRecordTabs :customer-id="customerId" />
    <div class="toolbar">
      <DisabledAction
        label="新增关系"
        :disabled="true"
        button-test-id="gated-add-relation"
        reason="C2：新增集团关系写无本波合同"
        unlockPath="待集团关系核验合同批准后由后续 Loop 启用"
      />
      <DisabledAction
        label="发起核验"
        :disabled="true"
        reason="C2：集团关系核验写操作无本 Loop 合同；变更只形成候选事实"
        unlockPath="待合同批准后由后续 Loop 启用核验 Action"
      />
    </div>
    <PageState :status="status" :error="error" idle-description="尚未请求集团关系" @retry="loadRecord">
      <div class="metrics" data-testid="p05-metrics">
        <article class="metric metric-blue">
          <span>图谱节点</span>
          <strong>{{ memberCount }}</strong>
        </article>
        <article class="metric metric-teal">
          <span>上游</span>
          <strong>{{ upstreamCount }}</strong>
        </article>
        <article class="metric metric-blue">
          <span>下游</span>
          <strong>{{ downstreamCount }}</strong>
        </article>
        <article class="metric metric-amber">
          <span>我行授信</span>
          <strong>{{ facilities.length }}</strong>
          <em>CreditFacility 只读</em>
        </article>
      </div>

      <div class="panorama">
        <section class="graph-panel">
          <header class="panel-head">
            <h2>集团 / 供应链知识图谱</h2>
            <p>数据：DKWS <code>bank-front-supply-chain-graph</code>。空图表示平台未返回，不是本地假节点。</p>
          </header>
          <div v-if="nodes.length" data-testid="p05-group-graph">
            <SupplyChainForceGraph
              :nodes="nodes"
              :edges="edges"
              :interpretation="graphReport?.result?.interpretation"
              compact
              @select="selectedNode = $event"
            />
          </div>
          <p v-else class="empty" data-testid="p05-empty-graph">{{ graphError || 'DKWS 未返回知识图谱' }}</p>
        </section>

        <aside class="gate-panel" data-testid="p05-gate-panel">
          <h2>下一步与门禁</h2>
          <p class="gate-lead">操作目的、条件与可追溯结果</p>
          <div class="recommend">
            <p>推荐主动作</p>
            <strong>发起核验</strong>
            <span>关系变更只形成候选事实</span>
          </div>
          <p class="gate-label pill pill-blue">当前业务规则</p>
          <p>图谱只读展示 DKWS Skill 结果；核验写仍无本波合同。</p>
          <p class="gate-label pill pill-amber">异常与降级</p>
          <p>DKWS 不可达时保持空态，不回填 H2 种子边。</p>
          <div v-if="selectedNode" class="selected-card" data-testid="p05-selected-node">
            <h3>{{ selectedNode.name || selectedNode.id }}</h3>
            <dl>
              <div><dt>层级</dt><dd>{{ LAYER_LABEL[selectedNode.layer || ''] || selectedNode.layer || '-' }}</dd></div>
              <div><dt>类型</dt><dd>{{ selectedNode.type || '-' }}</dd></div>
              <div><dt>数据源</dt><dd>{{ selectedNode.dataSource || 'DKWS' }}</dd></div>
              <div><dt>核验</dt><dd>{{ selectedNode.verifyStatus || '-' }}</dd></div>
            </dl>
          </div>
          <div class="gate-chips">
            <span class="pill pill-amber">人工确认</span>
            <span class="pill pill-teal">证据可追溯</span>
            <span class="pill pill-blue">DKWS Skill</span>
          </div>
        </aside>
      </div>

      <section class="member-table-wrap">
        <h2>图谱节点</h2>
        <table v-if="nodes.length" class="member-table" data-testid="p05-member-table">
          <thead>
            <tr>
              <th>名称</th>
              <th>层级</th>
              <th>类型</th>
              <th>数据源</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="row in nodes"
              :key="row.id || row.name"
              :class="{ current: row.id === selectedNode?.id }"
              @click="selectedNode = row"
            >
              <td>{{ row.name || row.id }}</td>
              <td>{{ LAYER_LABEL[row.layer || ''] || row.layer || '-' }}</td>
              <td>{{ row.type || '-' }}</td>
              <td>{{ row.dataSource || 'DKWS' }}</td>
            </tr>
          </tbody>
        </table>
        <p v-else class="empty">DKWS 未返回图谱节点</p>
        <p v-if="facilities.length" class="facility-note">
          我行授信覆盖 {{ facilities.length }} 笔（CreditFacility.borrowerEntity 只读）：
          {{ facilities.map(item => item.borrowerEntity || item.facilityId).join('、') }}
        </p>
      </section>
    </PageState>
  </div>
</template>

<style scoped>
.page-subtitle {
  margin: -8px 0 12px;
  color: var(--gits-muted);
  font-size: 13px;
}
.toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 16px;
}
.metrics {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
  margin-bottom: 16px;
}
.metric {
  position: relative;
  background: #fff;
  border: 1px solid var(--gits-line);
  border-radius: 6px;
  padding: 10px 14px 10px 18px;
  min-height: 60px;
}
.metric::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  border-radius: 6px 0 0 6px;
}
.metric-blue::before { background: var(--gits-blue-600); }
.metric-teal::before { background: var(--gits-teal-500); }
.metric-amber::before { background: var(--gits-amber-400); }
.metric span,
.metric em {
  display: block;
  font-size: 11px;
  color: var(--gits-muted);
  font-style: normal;
}
.metric strong {
  display: block;
  margin-top: 4px;
  font-size: 20px;
  color: var(--gits-navy-800);
}
.panorama {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 322px;
  gap: 12px;
  align-items: start;
}
.graph-panel,
.gate-panel,
.member-table-wrap {
  background: #fff;
  border: 1px solid var(--gits-line);
  border-radius: 6px;
  padding: 16px;
}
.panel-head h2,
.gate-panel h2,
.member-table-wrap h2 {
  margin: 0;
  font-size: 14px;
  color: var(--gits-navy-800);
}
.panel-head p,
.gate-lead,
.gate-panel p,
.empty,
.facility-note {
  margin: 6px 0 12px;
  font-size: 12px;
  color: var(--gits-muted);
}
.insights {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
  margin-top: 12px;
}
.insights article {
  border: 1px solid var(--gits-line);
  border-radius: 5px;
  padding: 10px 12px;
}
.insights p {
  margin: 8px 0 0;
  font-size: 12px;
  color: var(--gits-text);
}
.pill {
  display: inline-flex;
  align-items: center;
  height: 20px;
  padding: 0 8px;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 600;
}
.pill-blue { background: #eaf4fe; color: var(--gits-blue-600); }
.pill-teal { background: #e8f8f6; color: var(--gits-teal-700); }
.pill-amber { background: #fff5dc; color: var(--gits-amber-800); }
.recommend {
  background: #f5f9fd;
  border: 1px solid var(--gits-line);
  border-radius: 5px;
  padding: 10px 12px;
  margin-bottom: 12px;
}
.recommend p,
.recommend span {
  margin: 0;
  font-size: 12px;
  color: var(--gits-muted);
}
.recommend strong {
  display: block;
  margin: 4px 0;
  color: var(--gits-navy-800);
}
.gate-label {
  margin: 10px 0 4px;
}
.selected-card {
  margin-top: 12px;
  padding: 10px;
  border: 1px solid var(--gits-line);
  border-radius: 5px;
  background: #f5f9fd;
}
.selected-card h3 {
  margin: 0 0 8px;
  font-size: 13px;
}
.selected-card dl {
  margin: 0;
  display: grid;
  gap: 4px;
}
.selected-card dt {
  font-size: 11px;
  color: var(--gits-muted);
}
.selected-card dd {
  margin: 0;
  font-size: 12px;
}
.entity-link {
  display: inline-block;
  margin-top: 8px;
  font-size: 12px;
  color: var(--gits-blue-600);
}
.gate-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px solid var(--gits-line);
}
.member-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}
.member-table th,
.member-table td {
  text-align: left;
  padding: 8px;
  border-bottom: 1px solid var(--gits-line);
}
.member-table tr.current {
  background: #eaf4fe;
}
.member-table tbody tr {
  cursor: pointer;
}
@media (max-width: 1100px) {
  .metrics,
  .panorama,
  .insights {
    grid-template-columns: 1fr;
  }
}
</style>
