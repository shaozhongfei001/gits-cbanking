<script setup lang="ts">
import { computed, ref } from 'vue'
import {
  NAlert,
  NButton,
  NCard,
  NCollapse,
  NCollapseItem,
  NDescriptions,
  NDescriptionsItem,
  NDivider,
  NEmpty,
  NFlex,
  NSelect,
  NSkeleton,
  NSpace,
  NTabPane,
  NTabs,
  NTag,
  NText,
  NTooltip,
} from 'naive-ui'
import {
  fetchInterpretation,
  ProductKnowledgeError,
  type InterpretationPurpose,
  type InterpretationResponse,
  type InterpretationView,
  type KnowledgeState,
} from '../api/productKnowledge'

/** 场景剧本：把业务可发生的路径做成可一键触发的演示入口。 */
interface Scenario {
  key: string
  label: string
  description: string
  productId: string
  view: InterpretationView
  purpose: InterpretationPurpose
}

const SCENARIOS: Scenario[] = [
  {
    key: 'happy',
    label: '正常解读（概览）',
    description: '已发布 Release，解读用途，返回 OVERVIEW 两字段（均为 Owner 裁决的 NOT_APPLICABLE）。',
    productId: 'PROD-CM-001',
    view: 'OVERVIEW',
    purpose: 'INTERPRETATION',
  },
  {
    key: 'eligibility',
    label: '准入视图（有支撑值）',
    description: 'minAccountBalance 为 SUPPORTED=50 万元，带证据回链；其余未复核字段显示 UNKNOWN。',
    productId: 'PROD-CM-001',
    view: 'ELIGIBILITY',
    purpose: 'INTERPRETATION',
  },
  {
    key: 'pricing',
    label: '定价视图（OQ-C 未裁决）',
    description: 'pricing.serviceFee 因 Owner 未裁决公开价目问题，保持 UNKNOWN，不补值。',
    productId: 'PROD-CM-001',
    view: 'PRICING',
    purpose: 'INTERPRETATION',
  },
  {
    key: 'recommendation',
    label: '推荐用途被拒（422）',
    description: 'DEMO 派生知识不得进入 RECOMMENDATION_READY（INV-RLS-09）。',
    productId: 'PROD-CM-001',
    view: 'ELIGIBILITY',
    purpose: 'RECOMMENDATION',
  },
  {
    key: 'not-published',
    label: '产品无已发布 Release（404）',
    description: '未发布的知识不得呈现，返回 PRODUCT_KNOWLEDGE_NOT_PUBLISHED。',
    productId: 'PROD-CM-999',
    view: 'OVERVIEW',
    purpose: 'INTERPRETATION',
  },
  {
    key: 'bad-param',
    label: '非法参数（400）',
    description: 'productId 不符合 PROD-XX-NNN 格式，返回 BAD_REQUEST 与统一错误体。',
    productId: 'BAD-ID',
    view: 'OVERVIEW',
    purpose: 'INTERPRETATION',
  },
]

/** 受控失败需运维侧改变后端环境，前端无法自行触发，故以命令形式给出。 */
const FAILED_CLOSED_HINT =
  '将后端 --gits.product-knowledge.snapshot-dir 指向空目录后重启，' +
  '再请求同一端点，应返回 503 FAILED_CLOSED 且响应体不含任何结论字段。'

const activeScenarioKey = ref<string>('eligibility')
const view = ref<InterpretationView>('ELIGIBILITY')
const data = ref<InterpretationResponse | null>(null)
const error = ref<ProductKnowledgeError | null>(null)
const isLoading = ref(false)
const hasRequested = ref(false)

const activeScenario = computed(
  () => SCENARIOS.find((item) => item.key === activeScenarioKey.value) ?? SCENARIOS[0]
)

const stateTagType = computed(() => (state: KnowledgeState) => {
  switch (state) {
    case 'SUPPORTED':
      return 'success' as const
    case 'CONFLICT':
      return 'error' as const
    case 'STALE':
      return 'warning' as const
    case 'NOT_APPLICABLE':
      return 'info' as const
    default:
      return 'default' as const
  }
})

const stateLabel = computed(() => (state: KnowledgeState) => {
  switch (state) {
    case 'SUPPORTED':
      return '有证据支撑'
    case 'UNKNOWN':
      return '未就绪·不补值'
    case 'CONFLICT':
      return '存在冲突'
    case 'NOT_APPLICABLE':
      return '不适用（已裁决）'
    default:
      return '已过期'
  }
})

const fieldCount = computed(() => data.value?.fields.length ?? 0)
const supportedCount = computed(
  () => data.value?.fields.filter((f) => f.knowledgeState === 'SUPPORTED').length ?? 0
)

async function runScenario(): Promise<void> {
  const scenario = activeScenario.value
  view.value = scenario.view
  isLoading.value = true
  hasRequested.value = true
  error.value = null
  data.value = null
  try {
    data.value = await fetchInterpretation({
      productId: scenario.productId,
      view: scenario.view,
      purpose: scenario.purpose,
    })
  } catch (err) {
    error.value = err instanceof ProductKnowledgeError ? err : null
    if (!error.value) {
      throw err
    }
  } finally {
    isLoading.value = false
  }
}

async function switchView(next: InterpretationView): Promise<void> {
  view.value = next
  if (activeScenarioKey.value === 'recommendation' || activeScenarioKey.value === 'not-published' || activeScenarioKey.value === 'bad-param') {
    return
  }
  isLoading.value = true
  error.value = null
  try {
    data.value = await fetchInterpretation({
      productId: activeScenario.value.productId,
      view: next,
      purpose: activeScenario.value.purpose,
    })
  } catch (err) {
    error.value = err instanceof ProductKnowledgeError ? err : null
    data.value = null
  } finally {
    isLoading.value = false
  }
}

void runScenario()
</script>

<template>
  <div class="interpretation-demo">
    <NAlert type="warning" :show-icon="true" title="演示数据来源声明" class="demo-notice">
      本页数据来自 <strong>DEMO 演示制度文本</strong>（Owner 决议 DECISION-20260906-01 路径 C），
      机构为虚构的 DEMO-BANK，<strong>不代表真实制度</strong>，不得用于真实业务、定价、授信或对外承诺。
      已发布 Release 的 <code>recommendationReady</code> 恒为 false。
    </NAlert>

    <NCard title="业务场景演示" size="small">
      <NSpace vertical :size="12">
        <NFlex :gap="12" align="center" wrap>
          <NSelect
            v-model:value="activeScenarioKey"
            :options="SCENARIOS.map((s) => ({ label: s.label, value: s.key }))"
            style="width: 280px"
          />
          <NButton type="primary" :loading="isLoading" @click="runScenario">运行场景</NButton>
        </NFlex>
        <NText depth="3">{{ activeScenario.description }}</NText>
      </NSpace>
    </NCard>

    <NCard title="解读结果" size="small">
      <!-- Loading -->
      <NSpace v-if="isLoading" vertical :size="8">
        <NSkeleton text :repeat="2" />
        <NSkeleton text style="width: 60%" />
      </NSpace>

      <!-- Error（受控失败统一呈现） -->
      <NAlert v-else-if="error" type="error" :title="`${error.status} ${error.code}`">
        {{ error.message }}
        <div class="error-meta">path: {{ error.path }} · timestamp: {{ error.timestamp }}</div>
      </NAlert>

      <!-- Empty -->
      <NEmpty v-else-if="hasRequested && !data" description="暂无解读结果" />

      <!-- Success -->
      <template v-else-if="data">
        <NDescriptions bordered :column="2" size="small">
          <NDescriptionsItem label="产品 ID">{{ data.productId }}</NDescriptionsItem>
          <NDescriptionsItem label="Release">{{ data.releaseId }}</NDescriptionsItem>
          <NDescriptionsItem label="用途">{{ data.purpose }}</NDescriptionsItem>
          <NDescriptionsItem label="Stale">{{ data.isStale ? '是' : '否' }}</NDescriptionsItem>
          <NDescriptionsItem label="字段数 / 有支撑">
            {{ fieldCount }} / {{ supportedCount }}
          </NDescriptionsItem>
          <NDescriptionsItem label="生成时间">{{ data.generatedAt }}</NDescriptionsItem>
        </NDescriptions>

        <NDivider />

        <NTabs :value="view" type="segment" @update:value="switchView">
          <NTabPane name="OVERVIEW" tab="概览" />
          <NTabPane name="ELIGIBILITY" tab="准入" />
          <NTabPane name="PRICING" tab="定价" />
        </NTabs>

        <NSpace vertical :size="12" class="field-list">
          <NCard
            v-for="field in data.fields"
            :key="field.fieldPath"
            size="small"
            :title="field.fieldPath"
          >
            <template #header-extra>
              <NTooltip trigger="hover">
                <template #trigger>
                  <NTag :type="stateTagType(field.knowledgeState)" size="small" :bordered="false">
                    {{ field.knowledgeState }}
                  </NTag>
                </template>
                {{ stateLabel(field.knowledgeState) }}
              </NTooltip>
            </template>

            <NSpace vertical :size="8">
              <NFlex :gap="8" align="center">
                <NText strong>呈现值：</NText>
                <NText v-if="field.displayValue">{{ field.displayValue }}</NText>
                <NText v-else depth="3">—（{{ stateLabel(field.knowledgeState) }}，禁止补齐）</NText>
              </NFlex>

              <NText v-if="field.conflictId" depth="3">
                冲突溯源：{{ field.conflictId }}（已由 Owner 裁决）
              </NText>

              <NCollapse v-if="field.evidenceSummaries.length > 0">
                <NCollapseItem
                  :title="`证据回链（${field.evidenceSummaries.length}）`"
                  :name="field.fieldPath"
                >
                  <NSpace vertical :size="10">
                    <NCard
                      v-for="evidence in field.evidenceSummaries"
                      :key="evidence.evidenceId"
                      size="small"
                      embedded
                    >
                      <NSpace vertical :size="4">
                        <NFlex :gap="8" align="center" wrap>
                          <NTag size="small" :bordered="false">{{ evidence.authorityLevel }}</NTag>
                          <NText depth="3">{{ evidence.sourceId }}</NText>
                          <NText depth="3">{{ evidence.locatorHint }}</NText>
                        </NFlex>
                        <NText>{{ evidence.quoteExcerpt }}</NText>
                        <NText depth="3" style="font-size: 12px">
                          {{ evidence.evidenceId }} · {{ evidence.sourceVersionId }}
                        </NText>
                      </NSpace>
                    </NCard>
                  </NSpace>
                </NCollapseItem>
              </NCollapse>

              <NText v-else depth="3">
                无证据回链（未复核结论不呈现证据，避免误导）
              </NText>
            </NSpace>
          </NCard>
        </NSpace>
      </template>
    </NCard>

    <NCard title="受控失败场景（503 FAILED_CLOSED）" size="small">
      <NSpace vertical :size="8">
        <NText>{{ FAILED_CLOSED_HINT }}</NText>
        <code class="cmd">
          ./mvnw -q -pl apps/api spring-boot:run -DskipTests
          -Dspring-boot.run.arguments="--gits.product-knowledge.snapshot-dir=/tmp/empty-snap
          --server.port=8080"
        </code>
      </NSpace>
    </NCard>
  </div>
</template>

<style scoped>
.interpretation-demo {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 16px;
}

.demo-notice :deep(.n-alert-body) {
  align-items: flex-start;
}

.field-list {
  margin-top: 12px;
}

.error-meta {
  margin-top: 6px;
  font-size: 12px;
  opacity: 0.75;
}

.cmd {
  display: block;
  padding: 8px;
  border-radius: 4px;
  background: rgba(127, 127, 127, 0.12);
  font-size: 12px;
  white-space: pre-wrap;
}
</style>
