<script setup lang="ts">
import { ref } from 'vue'
import { NButton, NTag, NEmpty, NAlert, NSpace } from 'naive-ui'
import { createTask, type Task, type TaskType } from '../../api/v11'
import { ELIGIBILITY_LABELS, type ReviewRequiredItem } from './types'

/**
 * REVIEW_REQUIRED / UNKNOWN 待处理面板 + “创建专家协同/待核实任务”入口。
 *
 * 状态块：CANDIDATE / FROZEN=NO / IMPLEMENTED=NO（WP5-3）。
 *
 * 展示三段式第一段中需要人工/专家介入的项（REVIEW_REQUIRED）与关键事实缺失项（UNKNOWN），
 * 并调用 createTask 创建任务（REVIEW / FOLLOW_UP），将任务关联到推荐运行 runId。
 * runId 同时写入任务 payload 顶层字段与 description 文本，避免后端字段裁剪时丢失关联。
 */
const props = withDefaults(defineProps<{
  items: ReviewRequiredItem[]
  runId: string
  customerId?: string
  operatingCaseId?: string
  assignedTo?: string
}>(), {
  customerId: '',
  operatingCaseId: '',
  assignedTo: '',
})

const emit = defineEmits<{
  (e: 'created', task: Task, item: ReviewRequiredItem): void
  (e: 'error', error: unknown): void
}>()

type CreateReviewTaskPayload = Partial<Task> & { runId?: string }

const creatingKey = ref<string | null>(null)
const createdKeys = ref<string[]>([])
const errorMessage = ref('')

function itemKey(item: ReviewRequiredItem): string {
  return `${item.eligibility}:${item.productId ?? ''}:${item.reasonCode ?? item.reason}`
}

function isCreating(item: ReviewRequiredItem): boolean {
  return creatingKey.value === itemKey(item)
}

function isCreated(item: ReviewRequiredItem): boolean {
  return createdKeys.value.includes(itemKey(item))
}

function taskTypeFor(item: ReviewRequiredItem): TaskType {
  return item.eligibility === 'REVIEW_REQUIRED' ? 'REVIEW' : 'FOLLOW_UP'
}

function buttonLabel(item: ReviewRequiredItem): string {
  return item.eligibility === 'REVIEW_REQUIRED' ? '创建专家协同任务' : '创建待核实任务'
}

function buildTitle(item: ReviewRequiredItem): string {
  const scope = item.productId ? `${item.productId}@${item.productVersion ?? '-'}` : '推荐运行'
  return item.eligibility === 'REVIEW_REQUIRED' ? `专家协同：${scope}` : `待核实：${scope}`
}

function buildDescription(item: ReviewRequiredItem): string {
  const parts = [`推荐运行 ${props.runId}`]
  if (item.productId) {
    parts.push(`产品 ${item.productId}@${item.productVersion ?? '-'}`)
  }
  parts.push(`原因：${item.reason}`)
  if (item.requiredExpertise) {
    parts.push(`所需专业：${item.requiredExpertise}`)
  }
  if (item.suggestedAction) {
    parts.push(`建议动作：${item.suggestedAction}`)
  }
  return parts.join('；')
}

async function handleCreate(item: ReviewRequiredItem) {
  const key = itemKey(item)
  creatingKey.value = key
  errorMessage.value = ''

  const payload: CreateReviewTaskPayload = {
    taskType: taskTypeFor(item),
    title: buildTitle(item),
    description: buildDescription(item),
    customerId: props.customerId || undefined,
    operatingCaseId: props.operatingCaseId || undefined,
    assignedTo: props.assignedTo || undefined,
    runId: props.runId,
  }

  try {
    const created = await createTask(payload)
    createdKeys.value = [...createdKeys.value, key]
    emit('created', created, item)
  } catch (e: unknown) {
    errorMessage.value = e instanceof Error ? e.message : '创建任务失败'
    emit('error', e)
  } finally {
    creatingKey.value = null
  }
}
</script>

<template>
  <div class="review-required-panel" data-testid="review-required-panel">
    <NAlert v-if="errorMessage" type="error" :title="errorMessage" style="margin-bottom: 12px" />

    <NEmpty
      v-if="items.length === 0"
      description="暂无需要复核或待核实的推荐项"
      data-testid="review-empty"
    />

    <div v-else class="review-list">
      <div
        v-for="item in items"
        :key="itemKey(item)"
        class="review-item"
        data-testid="review-item"
        :class="{ 'review-required': item.eligibility === 'REVIEW_REQUIRED' }"
      >
        <div class="review-header">
          <NTag
            :type="item.eligibility === 'REVIEW_REQUIRED' ? 'info' : 'warning'"
            size="small"
            data-testid="review-eligibility"
          >
            {{ ELIGIBILITY_LABELS[item.eligibility] }}
          </NTag>
          <span v-if="item.productId" class="review-product" data-testid="review-product">
            {{ item.productId }}<template v-if="item.productVersion">@{{ item.productVersion }}</template>
          </span>
        </div>

        <div class="review-reason" data-testid="review-reason">{{ item.reason }}</div>

        <div v-if="item.ruleId" class="review-rule" data-testid="review-rule">
          规则：{{ item.ruleId }}
        </div>
        <div v-if="item.requiredExpertise" class="review-expertise" data-testid="review-expertise">
          所需专业：{{ item.requiredExpertise }}
        </div>
        <div v-if="item.suggestedAction" class="review-action" data-testid="review-action">
          建议动作：{{ item.suggestedAction }}
        </div>

        <NSpace justify="end" style="margin-top: 8px">
          <NButton
            size="small"
            :type="item.eligibility === 'REVIEW_REQUIRED' ? 'info' : 'warning'"
            :loading="isCreating(item)"
            :disabled="isCreated(item)"
            data-testid="create-task-button"
            @click="handleCreate(item)"
          >
            {{ isCreated(item) ? '已创建任务' : buttonLabel(item) }}
          </NButton>
        </NSpace>
      </div>
    </div>
  </div>
</template>

<style scoped>
.review-required-panel {
  padding: 8px 0;
  font-size: 14px;
  color: #333;
}

.review-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.review-item {
  padding: 12px 16px;
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  background: #fff;
}

.review-item.review-required {
  border-left: 3px solid #2080f0;
}

.review-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.review-product {
  font-weight: 600;
  color: #003366;
}

.review-reason {
  font-size: 13px;
  color: #333;
  line-height: 1.5;
  margin-bottom: 4px;
}

.review-rule,
.review-expertise,
.review-action {
  font-size: 12px;
  color: #8c8c8c;
  margin-top: 4px;
}
</style>
