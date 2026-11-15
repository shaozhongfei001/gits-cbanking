<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import {
  NLayout, NLayoutContent, NLayoutSider, NCard, NTabs, NTabPane,
  NSpace, NTag, NButton, NInput, NBadge, NDivider, NEmpty, NTooltip,
} from 'naive-ui'
import {
  type HumanGate, type CrmWritebackCommand, type GateDecision,
  GATE_TYPE_LABELS, fetchHumanGates, fetchCrmWritebackCommands,
} from '../api/v11'
import { useHumanGate, useCrmWriteback } from '../composables/useHumanGate'
import { deriveResourceStatus } from '../composables/useResourceStatus'
import { useEngagementContext } from '../composables/useEngagementContext'
import StagePath from '../components/shell/StagePath.vue'
import type { StagePathStage } from '../components/shell/StagePath.vue'
import { usePageReferenceStore } from '../stores/pageReference'
import ObjectHeader from '../components/shell/ObjectHeader.vue'
import PageState from '../components/shell/PageState.vue'
import HumanGateDialog from '../components/HumanGateDialog.vue'
import CrmWritebackApproval from '../components/CrmWritebackApproval.vue'

const PAGE_ID = 'P15'
const OBJECT_TYPE = '互动 Interaction'

/** 会中对话的一轮发言（纯前端演示样例，不是后端 API 响应字段）。 */
interface MeetingTurn {
  id: string
  speaker: 'RM' | 'CUSTOMER'
  speakerLabel: string
  at: string
  text: string
}

/**
 * 预生成的客户经理 ↔ 客户对话交互记录。
 * 演示数据在页面加载时即存在，无需等待后端；界面显式标注「演示样例」，
 * 不冒充真实客户会话，也不涉及额度/利率/时效等承诺性表述。
 */
const MEETING_DIALOGUE: readonly MeetingTurn[] = [
  { id: 't01', speaker: 'RM', speakerLabel: '客户经理', at: '09:30', text: '您好，今天主要想对齐贵司下半年的结算与资金归集安排，先不谈具体方案。' },
  { id: 't02', speaker: 'CUSTOMER', speakerLabel: '客户', at: '09:31', text: '可以。我们几家子公司的回款账户比较分散，对账压力确实比较大。' },
  { id: 't03', speaker: 'RM', speakerLabel: '客户经理', at: '09:32', text: '明白。访前包里已整理近两个季度的账户分布，我们先核对一下口径。' },
  { id: 't04', speaker: 'CUSTOMER', speakerLabel: '客户', at: '09:33', text: '口径没问题，不过跨主体归集这块要看内部授权流程。' },
  { id: 't05', speaker: 'RM', speakerLabel: '客户经理', at: '09:34', text: '这属于需要确认的边界，我会记录为待核验项，不在会上给结论。' },
  { id: 't06', speaker: 'CUSTOMER', speakerLabel: '客户', at: '09:36', text: '另外想了解一下票据和日常支付能不能放在同一套流程里。' },
  { id: 't07', speaker: 'RM', speakerLabel: '客户经理', at: '09:38', text: '可以一并梳理。具体额度、期限、费用与办理时效以最终批复和协议为准，这里先只记录诉求。' },
  { id: 't08', speaker: 'CUSTOMER', speakerLabel: '客户', at: '09:39', text: '好，那麻烦把需要我方准备的材料列一下。' },
  { id: 't09', speaker: 'RM', speakerLabel: '客户经理', at: '09:41', text: '会后在访后事实对账里形成清单，并走 HumanGate 审批，正式结论以审批后为准。' },
  { id: 't10', speaker: 'CUSTOMER', speakerLabel: '客户', at: '09:42', text: '可以，先按这个节奏推进。' },
]

const router = useRouter()
const pageRefs = usePageReferenceStore()
const { journeyId } = useEngagementContext()

// 访前向导步骤（3.2 向导步骤条风格；会中为第 4 步）
const stages: StagePathStage[] = [
  { key: 'gaps', label: '访前目标' },
  { key: 'evidence', label: '证据装配' },
  { key: 'pack', label: '访前包预览' },
  { key: 'meeting', label: '会中工作区' },
]
const completedKeys = computed<string[]>(() => ['gaps', 'evidence', 'pack'])
const currentKey = 'meeting'

const { gates: pendingGates, error: gatesError, loadGates, decide: decideGate } = useHumanGate()
const { commands: crmCommands, error: crmError, loadCommands, decideCommand } = useCrmWriteback()

const showGateDialog = ref(false)
const selectedGate = ref<HumanGate | null>(null)
const showCrmDialog = ref(false)
const selectedCrmCommand = ref<CrmWritebackCommand | null>(null)
const meetingNotes = ref('')
const isInterpreting = ref(false)
const deciding = ref(false)
const requested = ref(false)
/** 四态只由「首次加载 / 手动重试」驱动；后台轮询不得让整页重新 loading。 */
const initialLoading = ref(false)
const initialError = ref('')
const refreshFailed = ref(false)

let pollTimer: ReturnType<typeof setInterval> | null = null
let refreshing = false

const status = computed(() =>
  deriveResourceStatus({
    loading: initialLoading.value,
    error: initialError.value,
    hasData: requested.value,
    requested: requested.value,
  }),
)

const objectStatus = computed(() => journeyId.value || '缺对象')
const pendingGateCount = computed(() => pendingGates.value.length)
const pendingCrmCount = computed(() => crmCommands.value.filter(c => c.status === 'PENDING').length)

function persistReference() {
  pageRefs.capture(PAGE_ID, {
    objectType: OBJECT_TYPE,
    recordId: journeyId.value || undefined,
    viewId: 'in_meeting',
    draftId: meetingNotes.value || undefined,
    scrollAnchor: typeof window !== 'undefined' ? window.scrollY : 0,
  })
}

function startPolling() {
  if (pollTimer) return
  // 后台刷新走静默通道：不触发全页四态切换，避免每 5s 卸载/重建三栏与输入框。
  pollTimer = setInterval(() => {
    void refreshWorkspace()
  }, 5000)
}

function stopPolling() {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
}

async function loadWorkspace() {
  requested.value = true
  initialLoading.value = true
  initialError.value = ''
  try {
    await Promise.all([
      loadGates({ status: 'PENDING', journeyId: journeyId.value || undefined }),
      loadCommands({ journeyId: journeyId.value || undefined }),
    ])
    initialError.value = gatesError.value || crmError.value || ''
  } catch {
    initialError.value = gatesError.value || crmError.value || '加载会中工作区失败'
  } finally {
    initialLoading.value = false
  }
}

/**
 * 静默刷新：直接取数写回 composable 暴露的列表 ref，不经过 loadGates/loadCommands，
 * 因此不会置 loading、不会让 PageState 把整页切回 spinner；防重入避免慢响应堆积。
 * 失败时保留上次成功结果并显式提示，不静默吞掉。
 */
async function refreshWorkspace() {
  if (refreshing) return
  refreshing = true
  try {
    const [gates, commands] = await Promise.all([
      fetchHumanGates({ status: 'PENDING', journeyId: journeyId.value || undefined }),
      fetchCrmWritebackCommands({ journeyId: journeyId.value || undefined }),
    ])
    pendingGates.value = gates
    crmCommands.value = commands
    refreshFailed.value = false
  } catch {
    refreshFailed.value = true
  } finally {
    refreshing = false
  }
}

function openGate(gate: HumanGate) {
  selectedGate.value = gate
  showGateDialog.value = true
}

function openCrmCommand(cmd: CrmWritebackCommand) {
  selectedCrmCommand.value = cmd
  showCrmDialog.value = true
}

function goCapture() {
  if (!journeyId.value) return
  persistReference()
  router.push({ name: 'MeetingCapture', params: { id: journeyId.value } })
}

function goCheckout() {
  if (!journeyId.value) return
  persistReference()
  router.push({ name: 'MeetingCheckout', params: { id: journeyId.value } })
}

async function handleGateDecide(gateId: string, decision: GateDecision,
                                 modification?: Record<string, unknown>, reason?: string) {
  deciding.value = true
  try {
    await decideGate(gateId, decision, modification, reason)
    showGateDialog.value = false
  } finally {
    deciding.value = false
  }
}

async function handleCrmDecide(commandId: string, decision: GateDecision,
                                modifications?: Record<string, unknown>[] | undefined, reason?: string) {
  deciding.value = true
  try {
    await decideCommand(commandId, { decision, modifications, reason: reason || '', actorId: 'current-user' })
    showCrmDialog.value = false
  } finally {
    deciding.value = false
  }
}

onMounted(() => {
  const restored = pageRefs.restore(PAGE_ID, OBJECT_TYPE)
  meetingNotes.value = restored.draftId ?? ''
  loadWorkspace()
  startPolling()
})

onBeforeUnmount(persistReference)

onUnmounted(() => {
  stopPolling()
})
</script>

<template>
  <div class="in-meeting" data-testid="p15-in-meeting">
    <ObjectHeader
      :page-id="PAGE_ID"
      :object-type="OBJECT_TYPE"
      :object-status="objectStatus"
      title="互动记录·会中工作区"
    >
      <template #actions>
        <n-button size="small" :disabled="!journeyId" data-testid="p15-go-capture" @click="goCapture">
          进入实时捕获
        </n-button>
        <n-button size="small" type="primary" :disabled="!journeyId" data-testid="p15-go-checkout" @click="goCheckout">
          结束会谈 →
        </n-button>
        <n-tooltip>
          <template #trigger>
            <span>
              <n-button size="small" disabled>记为正式 Claim</n-button>
            </span>
          </template>
          会中记录仅为草稿，须经 HumanGate 审批后才能形成正式 Claim/Evidence
        </n-tooltip>
      </template>
    </ObjectHeader>

    <StagePath :stages="stages" :current-key="currentKey" :completed-keys="completedKeys" />

    <PageState :status="status" :error="gatesError || crmError || ''" idle-description="尚未加载会中工作区" @retry="loadWorkspace">
      <NLayout has-sider>
        <NLayoutSider bordered width="320" content-style="padding: 16px;">
          <NTag v-if="refreshFailed" type="warning" size="small" data-testid="p15-refresh-failed">
            数据刷新失败 · 当前显示上次结果
          </NTag>
          <h3>
            <NBadge :value="pendingGateCount" :max="99">待审批门禁</NBadge>
          </h3>
          <NEmpty v-if="!pendingGates.length" description="暂无待审批门禁" />
          <NSpace v-else vertical :size="8">
            <NCard
              v-for="gate in pendingGates"
              :key="gate.gateId"
              size="small"
              hoverable
              style="cursor: pointer"
              @click="openGate(gate)"
            >
              <template #header>
                <NTag size="small" type="warning">{{ GATE_TYPE_LABELS[gate.gateType] }}</NTag>
              </template>
              <div>{{ gate.subject }}</div>
            </NCard>
          </NSpace>

          <NDivider />

          <h3>
            <NBadge :value="pendingCrmCount" :max="99">CRM写回</NBadge>
          </h3>
          <NEmpty v-if="!crmCommands.filter(c => c.status === 'PENDING').length" description="暂无写回命令" />
          <NSpace v-else vertical :size="8">
            <NCard
              v-for="cmd in crmCommands.filter(c => c.status === 'PENDING')"
              :key="cmd.commandId"
              size="small"
              hoverable
              style="cursor: pointer"
              @click="openCrmCommand(cmd)"
            >
              <template #header>
                <NTag size="small" type="info">{{ cmd.operation }}</NTag>
              </template>
              <div>{{ cmd.targetEntity }}</div>
            </NCard>
          </NSpace>
        </NLayoutSider>

        <NLayoutContent content-style="padding: 24px;">
          <NCard title="会中助手">
            <template #header-extra>
              <NSpace>
                <NTag :type="isInterpreting ? 'success' : 'default'" data-testid="p15-interpret-status">
                  {{ isInterpreting ? '解读中' : '未解读' }}
                </NTag>
                <NButton size="small" data-testid="p15-interpret-toggle" @click="isInterpreting = !isInterpreting">
                  {{ isInterpreting ? '停止解读' : '开始解读' }}
                </NButton>
              </NSpace>
            </template>
            <NTabs type="line">
              <NTabPane name="notes" tab="会议记录">
                <NSpace vertical :size="12">
                  <NSpace align="center" :size="8">
                    <NTag size="small" type="info">演示样例 · 预生成对话</NTag>
                    <span class="dialogue-hint">客户经理 ↔ 客户，共 {{ MEETING_DIALOGUE.length }} 轮</span>
                    <NTag size="small" :type="isInterpreting ? 'success' : 'default'">
                      {{ isInterpreting ? '正在解读对话' : '对话待解读' }}
                    </NTag>
                  </NSpace>
                  <ul class="dialogue-list" data-testid="p15-meeting-dialogue">
                    <li
                      v-for="turn in MEETING_DIALOGUE"
                      :key="turn.id"
                      class="dialogue-turn"
                      :class="{ 'is-rm': turn.speaker === 'RM', 'is-customer': turn.speaker === 'CUSTOMER' }"
                      :data-testid="`p15-turn-${turn.id}`"
                    >
                      <div class="dialogue-meta">
                        <span class="dialogue-speaker">{{ turn.speakerLabel }}</span>
                        <span class="dialogue-time">{{ turn.at }}</span>
                      </div>
                      <p class="dialogue-text">{{ turn.text }}</p>
                    </li>
                  </ul>
                  <NInput
                    v-model:value="meetingNotes"
                    type="textarea"
                    placeholder="在此追加会议要点（候选草稿，非正式 Claim）"
                    :rows="5"
                  />
                </NSpace>
              </NTabPane>
              <NTabPane name="actions" tab="待办事项">
                <NEmpty description="暂无待办事项" />
              </NTabPane>
              <NTabPane name="evidence" tab="证据收集">
                <NEmpty description="暂无证据" />
              </NTabPane>
            </NTabs>
          </NCard>
        </NLayoutContent>
      </NLayout>
    </PageState>

    <HumanGateDialog
      v-model:show="showGateDialog"
      :gate="selectedGate"
      :loading="deciding"
      @decide="handleGateDecide"
    />
    <CrmWritebackApproval
      v-model:show="showCrmDialog"
      :command="selectedCrmCommand"
      :loading="deciding"
      @decide="handleCrmDecide"
    />
  </div>
</template>

<style scoped>
.in-meeting {
  max-width: 1240px;
  padding: 32px 34px 48px;
}
h3 {
  margin: 0 0 12px;
}
.dialogue-hint {
  color: var(--text-tertiary);
  font-size: var(--text-sm);
}
.dialogue-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-height: 300px;
  margin: 0;
  padding: 0;
  overflow-y: auto;
  list-style: none;
}
.dialogue-turn {
  padding: 10px 12px;
  border: 1px solid var(--border-light);
  border-radius: 10px;
  background: var(--bg-surface-soft);
}
.dialogue-turn.is-rm {
  border-color: var(--border-normal);
  background: var(--bg-active);
}
.dialogue-meta {
  display: flex;
  justify-content: space-between;
  margin-bottom: 6px;
  color: var(--text-secondary);
  font-size: var(--text-xs);
}
.dialogue-speaker {
  color: var(--text-primary);
  font-weight: 600;
}
.dialogue-text {
  margin: 0;
  color: var(--text-primary);
  font-size: var(--text-base);
  line-height: 1.6;
}
</style>
