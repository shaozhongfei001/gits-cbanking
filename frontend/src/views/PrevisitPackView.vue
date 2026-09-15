<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { NButton, NTooltip } from 'naive-ui'
import ObjectHeader from '../components/shell/ObjectHeader.vue'
import PageState from '../components/shell/PageState.vue'
import StagePath from '../components/shell/StagePath.vue'
import type { StagePathStage } from '../components/shell/StagePath.vue'
import KnowledgePrevisitReport from '../components/KnowledgePrevisitReport.vue'
import { deriveResourceStatus } from '../composables/useResourceStatus'
import { useEngagementContext } from '../composables/useEngagementContext'
import { usePageReferenceStore } from '../stores/pageReference'
import { usePrevisitStore } from '../stores/previsit'

const PAGE_ID = 'P14'
const OBJECT_TYPE = '互动 Interaction'

const router = useRouter()
const pageRefs = usePageReferenceStore()
const previsitStore = usePrevisitStore()
const { customerId, journeyId, operatingCaseId, rmId } = useEngagementContext()

const requested = ref(true)

// 访前向导步骤（3.2 向导步骤条风格）
const stages: StagePathStage[] = [
  { key: 'gaps', label: '访前目标' },
  { key: 'evidence', label: '证据装配' },
  { key: 'pack', label: '访前包预览' },
  { key: 'meeting', label: '会中工作区' },
]
const completedKeys = computed(() => ['gaps', 'evidence'])
const currentKey = 'pack'

// 本页只读消费 store 的一键访前结果；不调用 executePrevisit（消除 KERT 重复调用）。
const status = computed(() =>
  deriveResourceStatus({
    loading: previsitStore.loading,
    error: previsitStore.error,
    hasData: previsitStore.previsitDone || requested.value,
    requested: requested.value,
  }),
)

const objectStatus = computed(() => (journeyId.value || '缺对象'))
const canComplete = computed(() => Boolean(journeyId.value && customerId.value && previsitStore.previsitDone))

const outR = computed(() => previsitStore.previsitResult?.outreachScript || null)
const meetR = computed(() => previsitStore.previsitResult?.meetingScript || null)

function channelLabel(channel?: string): string {
  const labels: Record<string, string> = { PHONE: '电话', WECHAT: '微信', EMAIL: '邮件', FACE_TO_FACE: '面谈' }
  return channel ? (labels[channel] || channel) : ''
}

function persistReference() {
  pageRefs.capture(PAGE_ID, {
    objectType: OBJECT_TYPE,
    customerId: customerId.value || undefined,
    recordId: journeyId.value || undefined,
    viewId: 'previsit_pack',
    scrollAnchor: typeof window !== 'undefined' ? window.scrollY : 0,
  })
}

function goMeeting() {
  persistReference()
  if (journeyId.value) {
    router.push({ name: 'InMeetingAssistant', params: { id: journeyId.value }, query: {
      ...(customerId.value ? { customerId: customerId.value } : {}),
      ...(journeyId.value ? { journeyId: journeyId.value } : {}),
      ...(operatingCaseId.value ? { operatingCaseId: operatingCaseId.value } : {}),
      ...(rmId.value ? { rmId: rmId.value } : {}),
    } })
  }
}

function goEvidence() {
  persistReference()
  router.push({ name: 'PrevisitEvidence', query: {
    ...(customerId.value ? { customerId: customerId.value } : {}),
    ...(journeyId.value ? { journeyId: journeyId.value } : {}),
    ...(operatingCaseId.value ? { operatingCaseId: operatingCaseId.value } : {}),
    ...(rmId.value ? { rmId: rmId.value } : {}),
  } })
}

onMounted(() => {
  requested.value = true
  previsitStore.setContext({
    journeyId: journeyId.value,
    operatingCaseId: operatingCaseId.value,
    customerId: customerId.value,
    rmId: rmId.value,
  })
})
onBeforeUnmount(persistReference)
</script>

<template>
  <div class="slice-page" data-testid="p14-previsit-pack">
    <ObjectHeader
      :page-id="PAGE_ID"
      :object-type="OBJECT_TYPE"
      :object-status="objectStatus"
      title="访前包预览"
    >
      <template #actions>
        <n-button size="small" data-testid="p14-back-evidence" @click="goEvidence">
          ← 返回装配
        </n-button>
        <n-tooltip>
          <template #trigger>
            <span>
              <n-button size="small" disabled data-testid="p14-send-mobile">
                发送到移动端
              </n-button>
            </span>
          </template>
          移动端离线包发送为写操作且无本 Loop 合同
        </n-tooltip>
        <n-tooltip :disabled="canComplete">
          <template #trigger>
            <span>
              <n-button
                size="small"
                type="primary"
                data-testid="p14-complete"
                :disabled="!canComplete"
                @click="goMeeting"
              >
                完成准备，进入会中 →
              </n-button>
            </span>
          </template>
          需先在「访前知识证据装配」生成访前包
        </n-tooltip>
      </template>
    </ObjectHeader>

    <StagePath :stages="stages" :current-key="currentKey" :completed-keys="completedKeys" />

    <PageState :status="status" :error="previsitStore.error" idle-description="尚未预览访前包" @retry="goMeeting">
      <p v-if="!previsitStore.previsitDone" class="empty" data-testid="p14-empty">
        尚未生成访前包。请先在「访前知识证据装配」点击「生成访前包」（KERT 一键访前）。
      </p>
      <template v-else>
        <div class="pack-preview">
          <div v-if="outR" class="pack-card">
            <div class="pack-card-header">
              <span class="pack-card-icon">📞</span>
              <span>外联脚本</span>
              <span v-if="outR.channel" class="chip">{{ channelLabel(outR.channel) }}</span>
            </div>
            <div class="pack-card-body">
              <p v-if="outR.objective"><b>目标：</b>{{ outR.objective }}</p>
              <p v-if="outR.openingLine"><b>开场白：</b>{{ outR.openingLine }}</p>
              <p v-if="outR.talkingPoints?.length"><b>话题要点：</b>{{ outR.talkingPoints.length }} 条</p>
            </div>
          </div>

          <div v-if="meetR" class="pack-card">
            <div class="pack-card-header">
              <span class="pack-card-icon">🤝</span>
              <span>会面脚本</span>
            </div>
            <div class="pack-card-body">
              <p v-if="meetR.meetingObjective"><b>会面目标：</b>{{ meetR.meetingObjective }}</p>
              <p v-if="meetR.agendaItems?.length"><b>议程：</b>{{ meetR.agendaItems.length }} 项</p>
              <p v-if="meetR.kycQuestions?.length"><b>KYC 探查：</b>{{ meetR.kycQuestions.length }} 题</p>
            </div>
          </div>

          <div class="pack-card pack-card-report" data-testid="p14-pack-result">
            <div class="pack-card-header">
              <span class="pack-card-icon">📋</span>
              <span>R1 访前报告 & R2 速战卡</span>
            </div>
            <div class="pack-card-body">
              <KnowledgePrevisitReport
                :report="previsitStore.previsitResult!.previsitReport"
                :battle-card="previsitStore.previsitResult!.battleCard"
                :assembly-trace="previsitStore.previsitResult!.assemblyTrace || []"
                :skill-sections="previsitStore.previsitResult!.skillSections || []"
                :skill-executive-summary="previsitStore.previsitResult!.skillExecutiveSummary || ''"
                :supply-chain-report="previsitStore.supplyChainReport"
                :supply-chain-loading="false"
              />
            </div>
          </div>
        </div>
      </template>
    </PageState>
  </div>
</template>

<style scoped>
.empty {
  color: var(--text-tertiary);
  font-size: 13px;
}
.pack-preview {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.pack-card {
  border: 1px solid var(--border-light);
  border-radius: 8px;
  overflow: hidden;
  background: var(--bg-surface);
}
.pack-card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  background: var(--bg-surface-soft);
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
}
.pack-card-icon {
  font-size: 16px;
}
.chip {
  margin-left: auto;
  font-size: 11px;
  font-weight: 500;
  color: var(--text-secondary);
  background: var(--bg-hover);
  padding: 1px 8px;
  border-radius: 10px;
}
.pack-card-body {
  padding: 12px;
}
.pack-card-body p {
  margin: 0 0 4px;
  font-size: 13px;
}
</style>
