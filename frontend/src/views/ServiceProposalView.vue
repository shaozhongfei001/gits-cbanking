<template>
  <div class="spv">
    <div class="spv-header">
      <h1>SP-20 服务建议书</h1>
      <p>DKWS v1.4 集成 · 内部版 / 对客版 · 闸门 G0-G5</p>
    </div>

    <!-- 客户与操作 -->
    <div class="spv-bar">
      <span>客户：<n-tag v-if="customerId" type="info">{{ customerId }}</n-tag><em v-else>未选择</em></span>
      <span class="spv-bar-r">
        <n-input v-model:value="customerId" placeholder="客户ID" style="width: 220px" size="small" />
        <n-button size="small" :loading="genLd" @click="generate">生成建议书</n-button>
        <n-button size="small" :loading="stateLd" @click="loadGateState">闸门状态</n-button>
        <n-button size="small" type="warning" @click="extractMemories">SP-21 记忆抽取</n-button>
      </span>
    </div>

    <n-alert v-if="errorMsg" type="error" :show-icon="true" class="spv-err" closable @close="errorMsg=''">
      {{ errorMsg }}
    </n-alert>

    <!-- 建议书内容 -->
    <template v-if="proposal">
      <div class="spv-meta">
        <n-tag :type="proposal.status === 'SUCCESS' ? 'success' : 'warning'">{{ proposal.status }}</n-tag>
        <n-tag>runId: {{ proposal.runId }}</n-tag>
        <n-tag>schema: {{ proposal.schemaVersion }}</n-tag>
        <n-tag v-if="proposal.ruleViolations.length > 0" type="error">
          {{ proposal.ruleViolations.length }} 条规则违规
        </n-tag>
        <n-tag :type="releaseReady() ? 'success' : 'default'">
          {{ releaseReady() ? '对客版可放行' : '对客版未放行' }}
        </n-tag>
      </div>

      <n-tabs type="line" animated>
        <!-- 内部版 -->
        <n-tab-pane name="internal" tab="内部版">
          <n-card title="内部版（含事实标签）" size="small">
            <div class="spv-version-note">
              <n-tag v-for="(label, fid) in proposal.content.internalVersion?.factLabels || {}" :key="fid" size="small">
                {{ fid }}: {{ label }}
              </n-tag>
            </div>
            <pre class="spv-markdown">{{ proposal.content.internalVersion?.content || '(空)' }}</pre>
          </n-card>
        </n-tab-pane>

        <!-- 对客版 -->
        <n-tab-pane name="customer" tab="对客版">
          <n-card title="对客版（仅 F/A 事实）" size="small">
            <template #header-extra>
              <n-tag v-if="releaseReady()" type="success">已放行</n-tag>
              <n-tag v-else type="warning">放行受阻</n-tag>
            </template>
            <div v-if="proposal.content.customerVersion?.filteringNotes?.length" class="spv-version-note">
              <n-tag v-for="(n, i) in proposal.content.customerVersion.filteringNotes" :key="i" size="small" type="info">{{ n }}</n-tag>
            </div>
            <pre class="spv-markdown">{{ proposal.content.customerVersion?.content || '(空)' }}</pre>
            <div class="spv-version-note" v-if="proposal.content.customerVersionNote">
              <em>说明：{{ proposal.content.customerVersionNote }}</em>
            </div>
          </n-card>
        </n-tab-pane>

        <!-- 引用与待确认 -->
        <n-tab-pane name="citations" tab="引用 / 待确认">
          <n-card title="引用清单" size="small">
            <n-table size="small" :bordered="false">
              <thead>
                <tr><th>ID</th><th>事实标签</th><th>引用内容</th><th>来源</th><th>章节</th></tr>
              </thead>
              <tbody>
                <tr v-for="c in proposal.citations" :key="c.id">
                  <td>{{ c.id }}</td><td><n-tag size="small">{{ c.factLabel }}</n-tag></td>
                  <td>{{ c.claim }}</td><td>{{ c.source }}</td><td>{{ c.chapterRef }}</td>
                </tr>
              </tbody>
            </n-table>
          </n-card>
          <n-card title="待确认项" size="small" class="spv-card-gap">
            <n-empty v-if="proposal.unknowns.length === 0" description="无待确认项" />
            <ul v-else class="spv-unknowns">
              <li v-for="u in proposal.unknowns" :key="u.id">
                <b>{{ u.id }}</b> {{ u.description }} — 建议：{{ u.suggestedAction }}（{{ u.relatedChapter }}）
              </li>
            </ul>
          </n-card>
        </n-tab-pane>
      </n-tabs>
    </template>
    <n-empty v-else description="尚未生成建议书" class="spv-empty" />

    <!-- 闸门状态 -->
    <div v-if="gateState" class="spv-gates">
      <h3>闸门状态（GITS 权威）</h3>
      <div class="spv-gates-bar">
        <n-tag type="info">当前闸门: {{ gateState.currentGate }}</n-tag>
        <n-tag v-if="gateState.releaseReady" type="success">放行条件已满足 (G1/G2/G3)</n-tag>
        <n-tag v-else type="warning">放行条件未满足</n-tag>
      </div>
      <n-table size="small" :bordered="false">
        <thead>
          <tr><th>闸门</th><th>状态</th><th>证据/操作人</th></tr>
        </thead>
        <tbody>
          <tr v-for="item in gateState.checklist" :key="item.gate">
            <td>{{ item.gate }}</td>
            <td>
              <n-tag :type="item.state === 'PASSED' ? 'success' : item.state === 'BLOCKED' ? 'error' : 'default'">
                {{ item.state }}
              </n-tag>
            </td>
            <td>{{ item.evidence.join(' / ') || '-' }}</td>
          </tr>
        </tbody>
      </n-table>
    </div>

    <!-- SP-21 记忆抽取结果 -->
    <div v-if="memoryResult" class="spv-memory">
      <h3>SP-21 交互记忆抽取</h3>
      <n-alert v-if="memoryResult.status !== 'SUCCESS'" type="warning" :show-icon="true">
        {{ memoryResult.ruleViolations.length }} 条规则违规
      </n-alert>
      <n-card title="候选记忆" size="small">
        <n-empty v-if="memoryResult.candidateMemories.length === 0" description="无候选记忆" />
        <ul v-else class="spv-memory-list">
          <li v-for="m in memoryResult.candidateMemories" :key="m.memoryId">
            <b>[{{ m.category }}]</b> {{ m.content }}
            <span class="spv-memory-meta">置信度 {{ m.confidence }} · 衰减 {{ m.suggestedDecayRule }}</span>
            <div v-if="m.evidenceQuote" class="spv-memory-quote">证据：{{ m.evidenceQuote }}</div>
          </li>
        </ul>
      </n-card>
      <n-card title="强化 / 取代" size="small" class="spv-card-gap">
        <div v-if="memoryResult.memoryUpdates.length">强化：
          <n-tag v-for="u in memoryResult.memoryUpdates" :key="u.memoryId" size="small">
            {{ u.memoryId }} +{{ u.confidenceDelta }}
          </n-tag>
        </div>
        <div v-if="memoryResult.memorySupersessions.length">取代：
          <n-tag v-for="s in memoryResult.memorySupersessions" :key="s.supersededMemoryId" size="small" type="warning">
            {{ s.supersededMemoryId }} → {{ s.newMemoryId }}
          </n-tag>
        </div>
      </n-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRoute } from 'vue-router'
import { NTag, NInput, NButton, NAlert, NCard, NTabPane, NTabs, NTable, NEmpty, useMessage } from 'naive-ui'
import {
  generateServiceProposal,
  fetchGateState,
  extractInteractionMemories,
  type ServiceProposal,
  type GateSnapshot,
  type InteractionMemoryExtraction
} from '../api/v14'

const msg = useMessage()
const route = useRoute()
const customerId = ref(String(route.query.customerId || ''))
const proposal = ref<ServiceProposal | null>(null)
const gateState = ref<GateSnapshot | null>(null)
const memoryResult = ref<InteractionMemoryExtraction | null>(null)
const genLd = ref(false)
const stateLd = ref(false)
const errorMsg = ref('')

const releaseReady = () => {
  if (!proposal.value) return false
  if (gateState.value) return gateState.value.releaseReady
  const rbu = proposal.value.content.customerVersion?.releaseBlockedUntil || []
  return rbu.length === 0
}

async function generate() {
  if (!customerId.value) {
    msg.warning('请先输入客户ID')
    return
  }
  genLd.value = true
  errorMsg.value = ''
  try {
    proposal.value = await generateServiceProposal(`V14-${Date.now()}`, customerId.value, {
      enterpriseData: { customerId: customerId.value },
      customerVersionLabel: '内部'
    })
    msg.success('服务建议书已生成')
  } catch (e: any) {
    errorMsg.value = e.response?.data?.message || e.message || '生成失败'
  } finally {
    genLd.value = false
  }
}

async function loadGateState() {
  if (!customerId.value) {
    msg.warning('请先输入客户ID')
    return
  }
  stateLd.value = true
  errorMsg.value = ''
  try {
    gateState.value = await fetchGateState(customerId.value)
    msg.success('闸门状态已加载')
  } catch (e: any) {
    errorMsg.value = e.response?.data?.message || e.message || '闸门状态加载失败'
  } finally {
    stateLd.value = false
  }
}

async function extractMemories() {
  if (!customerId.value) {
    msg.warning('请先输入客户ID')
    return
  }
  try {
    memoryResult.value = await extractInteractionMemories(
      `INT-${Date.now()}`,
      customerId.value,
      '客户：下月提供担保函；供应链融资方案不变。'
    )
    msg.success('记忆抽取完成')
  } catch (e: any) {
    errorMsg.value = e.response?.data?.message || e.message || '记忆抽取失败'
  }
}
</script>

<style scoped>
.spv { padding: 16px; max-width: 1200px; margin: 0 auto; }
.spv-header h1 { margin: 0 0 4px; }
.spv-header p { margin: 0 0 12px; color: #888; font-size: 13px; }
.spv-bar { display: flex; gap: 12px; align-items: center; margin-bottom: 12px; flex-wrap: wrap; }
.spv-bar-r { margin-left: auto; display: flex; gap: 8px; align-items: center; flex-wrap: wrap; }
.spv-err { margin-bottom: 12px; }
.spv-meta { display: flex; gap: 8px; margin-bottom: 12px; flex-wrap: wrap; }
.spv-markdown { white-space: pre-wrap; font-family: inherit; font-size: 14px; line-height: 1.7; margin: 8px 0 0; }
.spv-version-note { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 6px; }
.spv-card-gap { margin-top: 12px; }
.spv-unknowns li, .spv-memory-list li { margin-bottom: 8px; line-height: 1.6; }
.spv-empty { margin-top: 24px; }
.spv-gates, .spv-memory { margin-top: 20px; }
.spv-gates h3, .spv-memory h3 { margin: 0 0 10px; }
.spv-gates-bar { display: flex; gap: 8px; margin-bottom: 10px; }
.spv-memory-meta { color: #888; font-size: 12px; margin-left: 8px; }
.spv-memory-quote { color: #666; font-size: 12px; font-style: italic; margin-top: 2px; }
</style>
