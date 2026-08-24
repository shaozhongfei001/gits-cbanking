<template>
  <div class="sc-graph" :class="{ compact: compact }">
    <div class="gbar">
      <button type="button" @click="clearSelection">取消选中</button>
      <button type="button" @click="fitView">复位视图</button>
    </div>
    <div class="legend">
      <span><i style="background:#4d9fff"></i>上游供应商</span>
      <span><i style="background:#ef476f"></i>本企业</span>
      <span><i style="background:#2dd4a7"></i>下游客户</span>
      <span>边标签：关系 + 金额（选中/悬停显示）</span>
    </div>
    <div ref="host" class="gnet" />
  </div>
</template>

<script setup lang="ts">
import { Network, DataSet } from 'vis-network/standalone'
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import type { SupplyChainGraphEdge, SupplyChainGraphNode } from '../api/engagement'
import { formatAmountYuan, LAYER_COLOR, RELATION_LABEL } from '../utils/supplyChainFormat'

const props = defineProps<{
  nodes: SupplyChainGraphNode[]
  edges: SupplyChainGraphEdge[]
  compact?: boolean
}>()

const compact = computed(() => !!props.compact)
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

function hexA(h: string, a: number) {
  const hex = h.replace('#', '')
  const r = parseInt(hex.slice(0, 2), 16)
  const g = parseInt(hex.slice(2, 4), 16)
  const b = parseInt(hex.slice(4, 6), 16)
  return `rgba(${r},${g},${b},${a})`
}

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
  const showAll = network.getScale() >= 0.55
  const selected = new Set(network.getSelectedNodes().map(String))
  const upd: Array<{ id: string; label: string }> = []
  for (const n of props.nodes) {
    if (!n.id) continue
    const want = n.layer === 'enterprise' || showAll || selected.has(n.id) || hovered === n.id
    const cur = dsNodes.get(n.id) as { label?: string } | null
    const label = want ? (n.name || '') : ''
    if ((cur?.label || '') !== label) upd.push({ id: n.id, label })
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
    const color = LAYER_COLOR[n.layer || ''] || '#94a3b8'
    return {
      id: n.id as string,
      label: n.layer === 'enterprise' ? (n.name || '') : '',
      color: {
        background: color,
        border: '#fff',
        highlight: { background: '#ffd166', border: '#fff' },
        hover: { background: color, border: '#fff' },
      },
      font: { color: '#fff', size: 12, face: 'Noto Sans SC, Microsoft YaHei, sans-serif' },
      shadow: { enabled: true, color: hexA(color, 0.55), size: 16, x: 0, y: 0 },
      shape: 'dot',
      size: n.layer === 'enterprise' ? 32 : 26,
      opacity: 1,
    }
  }) as never) as VisDataSet
  dsEdges = new DataSet(edgeList.map((e, i) => ({
    id: `e${i}`,
    from: e.source as string,
    to: e.target as string,
    rel: e.relation,
    amount: e.annualAmount,
    color: { color: '#4a5d85', highlight: '#ffd166', hover: '#9db8e8' },
    arrows: { to: { enabled: true, scaleFactor: 0.6 } },
    width: 1,
    hoverWidth: 2,
    selectionWidth: 2,
    smooth: { enabled: true, type: 'continuous' },
    label: '',
    font: { color: '#a8b8d8', size: 10, face: 'Noto Sans SC, Microsoft YaHei, sans-serif' },
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
    nodes: { borderWidth: 1.5, borderWidthSelected: 3, opacity: 1, font: { color: '#fff', size: 12 } },
    edges: { selectionWidth: 2, hoverWidth: 2, width: 1 },
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
.gnet { width: 100%; height: 520px; background: #0d1728; border-radius: 8px; }
.sc-graph.compact .gnet { height: 380px; }
.gbar { position: absolute; right: 8px; top: 0; z-index: 2; display: flex; gap: 6px; }
.gbar button {
  background: #16233f; color: #cbd5e1; border: 1px solid #2a3f68;
  border-radius: 6px; padding: 3px 10px; font-size: 11px; cursor: pointer;
}
.gbar button:hover { border-color: #fbbf24; color: #fbbf24; }
.legend { display: flex; gap: 14px; font-size: 11px; color: #94a3b8; padding: 28px 8px 6px; flex-wrap: wrap; }
.legend i { width: 9px; height: 9px; border-radius: 50%; display: inline-block; margin-right: 4px; }
</style>
