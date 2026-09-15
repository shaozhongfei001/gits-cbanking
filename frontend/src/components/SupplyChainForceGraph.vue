<template>
  <div class="sc-graph" :class="{ compact: compact }">
    <div class="gbar">
      <button type="button" @click="clearSelection">取消选中</button>
      <button type="button" @click="fitView">复位视图</button>
    </div>
    <div class="legend">
      <span v-for="item in legendItems" :key="item.layer">
        <i :style="{ borderColor: item.color, background: item.fill }"></i>{{ item.label }}
      </span>
      <span>边标签：关系 + 金额（选中/悬停显示）</span>
    </div>
    <div ref="host" class="gnet" />
    <div v-if="strips.length" class="sc-insights" data-testid="sc-insights">
      <article v-for="s in strips" :key="s.label" :class="'strip-' + s.tone">
        <span>{{ s.label }}</span>
        <p>{{ s.text }}</p>
      </article>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Network, DataSet } from 'vis-network/standalone'
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import type { SupplyChainGraphEdge, SupplyChainGraphInterpretation, SupplyChainGraphNode } from '../api/engagement'
import {
  formatAmountYuan,
  graphInsightStrips,
  LAYER_COLOR,
  LAYER_FILL,
  LAYER_LABEL,
  RELATION_LABEL,
} from '../utils/supplyChainFormat'

const props = defineProps<{
  nodes: SupplyChainGraphNode[]
  edges: SupplyChainGraphEdge[]
  compact?: boolean
  interpretation?: SupplyChainGraphInterpretation | null
}>()

const compact = computed(() => !!props.compact)
const strips = computed(() => graphInsightStrips(props.interpretation))
const legendItems = [
  { layer: 'supplier', label: LAYER_LABEL.supplier, color: LAYER_COLOR.supplier, fill: LAYER_FILL.supplier },
  { layer: 'enterprise', label: LAYER_LABEL.enterprise, color: LAYER_COLOR.enterprise, fill: LAYER_FILL.enterprise },
  { layer: 'customer', label: LAYER_LABEL.customer, color: LAYER_COLOR.customer, fill: LAYER_FILL.customer },
]
const emit = defineEmits<{
  select: [node: SupplyChainGraphNode | null]
}>()

type VisDataSet = {
  get: (id: string | number) => Record<string, unknown> | null
  update: (data: Record<string, unknown> | Record<string, unknown>[]) => void
}

const host = ref<HTMLElement | null>(null)
let network: InstanceType<typeof Network> | null = null
let dsNodes: VisDataSet | null = null
let dsEdges: VisDataSet | null = null
let hovered: string | null = null

function neighbors(): Map<string, Set<string>> {
  const map = new Map<string, Set<string>>()
  for (const n of props.nodes) {
    if (n.id) map.set(n.id, new Set())
  }
  for (const e of props.edges) {
    if (e.source && map.has(e.source) && e.target) map.get(e.source)!.add(e.target)
    if (e.target && map.has(e.target) && e.source) map.get(e.target)!.add(e.source)
  }
  return map
}

function byId(): Map<string, SupplyChainGraphNode> {
  return new Map(props.nodes.filter(n => n.id).map(n => [n.id as string, n]))
}

function applyLabels() {
  if (!network || !dsNodes) return
  const upd: Array<{ id: string; label: string }> = []
  for (const n of props.nodes) {
    if (!n.id) continue
    const want = n.name || ''
    const cur = dsNodes.get(n.id) as { label?: string } | null
    if ((cur?.label || '') !== want) upd.push({ id: n.id, label: want })
  }
  if (upd.length) dsNodes.update(upd)
}

function setDim(keep: Set<string>) {
  if (!dsNodes) return
  const upd: Array<{ id: string; opacity: number }> = []
  for (const n of props.nodes) {
    if (!n.id) continue
    const op = keep.has(n.id) ? 1 : 0.12
    upd.push({ id: n.id, opacity: op })
  }
  dsNodes.update(upd)
}

function edgeLabel(id: string | number, on: boolean) {
  if (!dsEdges) return
  const e = dsEdges.get(id) as { rel?: string; amount?: number; label?: string } | null
  if (!e) return
  const rel = RELATION_LABEL[e.rel || ''] || e.rel || ''
  const amt = e.amount ? formatAmountYuan(e.amount) : ''
  const want = on ? `${rel} ${amt}`.trim() : ''
  if (e.label !== want) dsEdges.update({ id, label: want })
}

function destroy() {
  network?.destroy()
  network = null
  dsNodes = null
  dsEdges = null
}

function build() {
  destroy()
  if (!host.value) return
  const nodeList = props.nodes.filter(n => n.id)
  const edgeList = props.edges.filter(e => e.source && e.target)
  dsNodes = new DataSet(nodeList.map((n) => {
    const border = LAYER_COLOR[n.layer || ''] || '#596779'
    const fill = LAYER_FILL[n.layer || ''] || '#ffffff'
    const isEnt = n.layer === 'enterprise'
    return {
      id: n.id as string,
      label: n.name || '',
      color: {
        background: fill,
        border,
        highlight: { background: fill, border: '#08233b' },
        hover: { background: fill, border },
      },
      font: { color: '#1b2632', size: isEnt ? 13 : 12, face: 'Noto Sans SC, Microsoft YaHei, sans-serif' },
      borderWidth: isEnt ? 3 : 2,
      shape: 'dot',
      size: isEnt ? 34 : 24,
      shadow: { enabled: true, color: 'rgba(8, 35, 59, 0.12)', size: 10, x: 0, y: 2 },
      opacity: 1,
    }
  }) as never) as VisDataSet
  dsEdges = new DataSet(edgeList.map((e, i) => ({
    id: `e${i}`,
    from: e.source as string,
    to: e.target as string,
    rel: e.relation,
    amount: e.annualAmount,
    color: { color: '#12a7a0', highlight: '#1976d2', hover: '#48a7e8' },
    arrows: { to: { enabled: true, scaleFactor: 0.55 } },
    width: 1.2,
    hoverWidth: 2,
    selectionWidth: 2,
    smooth: { enabled: true, type: 'continuous' },
    label: '',
    font: { color: '#596779', size: 10, face: 'Noto Sans SC, Microsoft YaHei, sans-serif' },
  })) as never) as VisDataSet
  network = new Network(host.value, { nodes: dsNodes as never, edges: dsEdges as never }, {
    autoResize: true,
    interaction: {
      hover: true,
      tooltipDelay: 120,
      selectConnectedEdges: true,
      hoverConnectedEdges: true,
      dragView: true,
      zoomView: true,
      dragNodes: true,
      keyboard: false,
    },
    nodes: { borderWidth: 2, borderWidthSelected: 3, opacity: 1, font: { color: '#1b2632', size: 12 } },
    edges: { selectionWidth: 2, hoverWidth: 2, width: 1.2 },
    physics: {
      enabled: true,
      stabilization: { iterations: 260, updateInterval: 20, fit: true },
      barnesHut: {
        gravitationalConstant: -4200,
        centralGravity: 0.05,
        springLength: 110,
        springConstant: 0.04,
        damping: 0.4,
      },
      minVelocity: 0.8,
      maxVelocity: 40,
    },
  })
  const nei = neighbors()
  const lookup = byId()
  network.on('zoom', applyLabels)
  network.on('animationFinished', applyLabels)
  network.on('stabilizationIterationsDone', () => {
    applyLabels()
    network?.fit({ animation: false })
  })
  network.on('hoverNode', (p: { node: string }) => {
    hovered = String(p.node)
    const n = lookup.get(hovered)
    if (n && dsNodes) dsNodes.update({ id: hovered, label: n.name || '' })
  })
  network.on('blurNode', () => {
    hovered = null
    applyLabels()
  })
  network.on('selectNode', (p: { nodes: Array<string | number> }) => {
    const id = p.nodes[0] != null ? String(p.nodes[0]) : ''
    if (!id) return
    const keep = new Set<string>([id, ...(nei.get(id) || [])])
    setDim(keep)
    applyLabels()
    emit('select', lookup.get(id) || null)
  })
  network.on('deselectNode', () => {
    setDim(new Set(nodeList.map(n => n.id as string)))
    applyLabels()
    emit('select', null)
  })
  network.on('hoverEdge', (p: { edge: string | number }) => edgeLabel(p.edge, true))
  network.on('blurEdge', (p: { edge: string | number }) => edgeLabel(p.edge, false))
  network.on('selectEdge', (p: { edges: Array<string | number> }) => p.edges.forEach(id => edgeLabel(id, true)))
  network.on('deselectEdge', (p: { edges: Array<string | number> }) => p.edges.forEach(id => edgeLabel(id, false)))
  network.on('doubleClick', (p: { nodes: Array<string | number> }) => {
    const id = p.nodes[0]
    if (id != null) network?.focus(id, { scale: 1.15, animation: { duration: 350, easingFunction: 'easeInOutQuad' } })
  })
}

function fitView() {
  network?.fit({ animation: { duration: 400, easingFunction: 'easeInOutQuad' } })
}

function clearSelection() {
  network?.unselectAll()
  setDim(new Set(props.nodes.filter(n => n.id).map(n => n.id as string)))
  emit('select', null)
  applyLabels()
}

onMounted(build)
watch(() => [props.nodes, props.edges], build, { deep: true })
onBeforeUnmount(destroy)
</script>

<style scoped>
.sc-graph { position: relative; }
.gnet {
  width: 100%;
  height: 520px;
  background: #f3f6f9;
  border: 1px solid #d8e2ec;
  border-radius: 6px;
}
.sc-graph.compact .gnet { height: 380px; }
.gbar { position: absolute; right: 8px; top: 0; z-index: 2; display: flex; gap: 6px; }
.gbar button {
  background: #fff;
  color: #1b2632;
  border: 1px solid #d8e2ec;
  border-radius: 6px;
  padding: 3px 10px;
  font-size: 11px;
  cursor: pointer;
}
.gbar button:hover { border-color: #1976d2; color: #1976d2; }
.legend {
  display: flex;
  gap: 14px;
  font-size: 11px;
  color: #596779;
  padding: 28px 8px 8px;
  flex-wrap: wrap;
}
.legend i {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  display: inline-block;
  margin-right: 4px;
  border-width: 2px;
  border-style: solid;
  vertical-align: -1px;
  box-sizing: border-box;
}
.sc-insights {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
  margin-top: 10px;
}
.sc-insights article {
  border: 1px solid #d8e2ec;
  border-radius: 5px;
  padding: 10px 12px;
  min-height: 72px;
}
.sc-insights span {
  display: block;
  font-size: 11px;
  font-weight: 600;
  margin-bottom: 6px;
}
.sc-insights p {
  margin: 0;
  font-size: 12px;
  color: #1b2632;
  line-height: 1.5;
}
.strip-blue { background: #eaf4fe; }
.strip-blue span { color: #1976d2; }
.strip-amber { background: #fff5dc; }
.strip-amber span { color: #7a4b00; }
.strip-teal { background: #e8f8f6; }
.strip-teal span { color: #087771; }
@media (max-width: 900px) {
  .sc-insights { grid-template-columns: 1fr; }
}
</style>
