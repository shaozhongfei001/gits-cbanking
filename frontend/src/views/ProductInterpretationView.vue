<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import {
  NAlert,
  NCard,
  NCollapse,
  NCollapseItem,
  NDescriptions,
  NDescriptionsItem,
  NEmpty,
  NFlex,
  NList,
  NListItem,
  NSpace,
  NSpin,
  NTabPane,
  NTabs,
  NTag,
  NText,
  NTooltip,
} from 'naive-ui'
import ObjectHeader from '../components/shell/ObjectHeader.vue'
import PageState from '../components/shell/PageState.vue'
import {
  fetchProductCards,
  fetchProductCardDetail,
  fetchInterpretation,
  ProductKnowledgeError,
  type ProductCardDetail,
  type ProductCardSummary,
  type InterpretationResponse,
  type InterpretationView,
  type KnowledgeState,
} from '../api/productKnowledge'
import { deriveResourceStatus } from '../composables/useResourceStatus'
import { usePageReferenceStore } from '../stores/pageReference'

const PAGE_ID = 'P38'
const OBJECT_TYPE = '产品知识（对公产品全景）'

/** 产品族显示顺序。 */
const FAMILY_ORDER = ['流动资金融资', '贸易融资', '结算服务', '现金管理', '跨境金融', '投资银行']

/** fieldPath → 人类可读中文标签（对齐 CTR-PK-TAX-001 分类法）。 */
const FIELD_LABELS: Record<string, string> = {
  'identity.productCode': '产品代码',
  'compliance.regulatoryBasis': '监管依据',
  'eligibility.customerSegment': '适用客户分层',
  'eligibility.minAccountBalance': '最低留存余额',
  'eligibility.prerequisiteProducts': '前置产品',
  'pricing.serviceFee': '服务费',
}

const VIEW_TABS: Array<{ value: InterpretationView; label: string }> = [
  { value: 'OVERVIEW', label: '概览' },
  { value: 'ELIGIBILITY', label: '准入' },
  { value: 'PRICING', label: '定价' },
]

const stateTagType = (state: KnowledgeState) => {
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
}

const stateLabel = (state: KnowledgeState) => {
  switch (state) {
    case 'SUPPORTED':
      return '有证据支撑'
    case 'UNKNOWN':
      return '未复核（不补值）'
    case 'CONFLICT':
      return '存在冲突'
    case 'NOT_APPLICABLE':
      return '不适用'
    default:
      return '已过期'
  }
}

const authorityLabel = (level: string) => {
  switch (level) {
    case 'INTERNAL_POLICY':
      return '行内制度'
    case 'REGULATORY':
      return '监管法规'
    case 'PUBLIC_PRICE_DISCLOSURE':
      return '公开价目'
    case 'PUBLIC_MARKETING':
      return '公开营销'
    default:
      return level
  }
}

const pageRefs = usePageReferenceStore()
const cards = ref<ProductCardSummary[]>([])
const detail = ref<ProductCardDetail | null>(null)
const selectedId = ref<string>('')
const loading = ref(false)
const error = ref('')
const requested = ref(false)

// KERT 三视图解读（仅 interpretable 产品）
const activeView = ref<InterpretationView>('ELIGIBILITY')
const interpretation = ref<InterpretationResponse | null>(null)
const interpLoading = ref(false)
const interpError = ref('')

const status = computed(() =>
  deriveResourceStatus({
    loading: loading.value,
    error: error.value,
    hasData: requested.value,
    requested: requested.value,
  }),
)

const grouped = computed(() => {
  const groups: Array<{ familyName: string; items: ProductCardSummary[] }> = []
  for (const fam of FAMILY_ORDER) {
    const items = cards.value.filter((c) => c.familyName === fam)
    if (items.length > 0) groups.push({ familyName: fam, items })
  }
  const known = new Set(FAMILY_ORDER)
  const others = cards.value.filter((c) => !known.has(c.familyName))
  if (others.length > 0) groups.push({ familyName: '其他', items: others })
  return groups
})

function persistReference() {
  pageRefs.capture(PAGE_ID, {
    objectType: OBJECT_TYPE,
    recordId: selectedId.value || 'catalog',
    viewId: 'product_interpretation',
    scrollAnchor: typeof window !== 'undefined' ? window.scrollY : 0,
  })
}

async function loadCatalog() {
  loading.value = true
  error.value = ''
  requested.value = true
  try {
    cards.value = await fetchProductCards()
    if (!selectedId.value && cards.value.length > 0) {
      await selectProduct(cards.value[0].productId)
    }
  } catch (e) {
    error.value = e instanceof Error ? e.message : '产品目录加载失败'
    cards.value = []
  } finally {
    loading.value = false
  }
}

async function selectProduct(id: string) {
  selectedId.value = id
  detail.value = null
  interpretation.value = null
  interpError.value = ''
  try {
    detail.value = await fetchProductCardDetail(id)
  } catch (e) {
    detail.value = null
  }
  if (detail.value?.interpretable) {
    void loadInterpretation('ELIGIBILITY')
  }
}

async function loadInterpretation(nextView: InterpretationView) {
  if (nextView) activeView.value = nextView
  if (!detail.value?.interpretable) return
  interpLoading.value = true
  interpError.value = ''
  interpretation.value = null
  try {
    interpretation.value = await fetchInterpretation({
      productId: detail.value.productId,
      view: activeView.value,
      purpose: 'INTERPRETATION',
    })
  } catch (e) {
    interpError.value =
      e instanceof ProductKnowledgeError ? `${e.code}：${e.message}`
        : e instanceof Error ? e.message : '解读请求失败'
  } finally {
    interpLoading.value = false
  }
}

onMounted(loadCatalog)
onBeforeUnmount(persistReference)
</script>

<template>
  <div class="interpretation-page" data-testid="p38-product-interpretation">
    <ObjectHeader
      :page-id="PAGE_ID"
      :object-type="OBJECT_TYPE"
      object-status="只读"
      title="产品解读与知识"
    />

    <NAlert type="info" :show-icon="true" title="对公产品全景" class="notice">
      本页展示本行对公产品知识全景（源自 KERT 产品原始材料）。
      每个产品均含「产品摘要」与「深度解读」（原始产品文档全文），并提供原始文件路径。
      其中「现金池」额外具备 KERT 已发布 Release 的制度深度解读（三视图 + 依据原文）。
    </NAlert>

    <PageState :status="status" :error="error" idle-description="尚未加载产品目录" @retry="loadCatalog">
      <div class="layout">
        <aside class="catalog-panel">
          <NList hoverable clickable>
            <template v-for="group in grouped" :key="group.familyName">
              <div class="family-title">{{ group.familyName }}</div>
              <NListItem
                v-for="item in group.items"
                :key="item.productId"
                :class="{ active: item.productId === selectedId }"
                @click="selectProduct(item.productId)"
              >
                <div class="catalog-item">
                  <NText strong>{{ item.name }}</NText>
                  <NText depth="3" class="catalog-code">{{ item.productId }}</NText>
                </div>
                <template #suffix>
                  <NTag v-if="item.interpretable" type="success" size="small" :bordered="false">
                    制度解读
                  </NTag>
                </template>
              </NListItem>
            </template>
          </NList>
        </aside>

        <main class="detail-panel">
          <template v-if="detail">
            <!-- 产品摘要 -->
            <NCard size="small" :title="detail.name">
              <template #header-extra>
                <NFlex :gap="8" align="center">
                  <NTag :bordered="false">{{ detail.productId }}</NTag>
                  <NTag type="info" :bordered="false">{{ detail.familyName }}</NTag>
                </NFlex>
              </template>

              <NSpace vertical :size="12">
                <div>
                  <NText depth="3">产品摘要</NText>
                  <p class="summary">{{ detail.summary }}</p>
                </div>

                <NDescriptions bordered :column="1" size="small">
                  <NDescriptionsItem label="产品 Owner">{{ detail.owner || '—' }}</NDescriptionsItem>
                  <NDescriptionsItem label="产品原始文件">
                    <!-- S-2（Owner 2026-09-22 授权）：仅呈现相对源文件标识，不得暴露服务器绝对路径 -->
                    <code class="src-path">{{ detail.sourceFile }}</code>
                  </NDescriptionsItem>
                </NDescriptions>
              </NSpace>
            </NCard>

            <!-- 制度深度解读（仅现金池） -->
            <NCard v-if="detail.interpretable" size="small" title="制度深度解读（KERT 已发布 Release）" class="kert-card">
              <template #header-extra>
                <NTag type="success" size="small" :bordered="false">受控 Release</NTag>
              </template>

              <div v-if="interpLoading" class="interp-loading">
                <NSpin size="small" />
                <NText depth="3">加载制度解读…</NText>
              </div>
              <NAlert v-else-if="interpError" type="error" :show-icon="false">{{ interpError }}</NAlert>
              <template v-else-if="interpretation">
                <NDescriptions bordered :column="2" size="small" class="interp-meta">
                  <NDescriptionsItem label="Release">{{ interpretation.releaseId }}</NDescriptionsItem>
                  <NDescriptionsItem label="知识状态">{{ interpretation.isStale ? '已过期' : '新鲜可用' }}</NDescriptionsItem>
                </NDescriptions>
                <NTabs :value="activeView" type="line" @update:value="(v: string) => loadInterpretation(v as InterpretationView)">
                  <NTabPane v-for="tab in VIEW_TABS" :key="tab.value" :name="tab.value" :tab="tab.label">
                    <NSpace vertical :size="10" class="field-list">
                      <NEmpty v-if="interpretation.fields.length === 0" description="该视图暂无解读字段" />
                      <NCard
                        v-for="field in interpretation.fields"
                        :key="field.fieldPath"
                        size="small"
                        embedded
                        :title="FIELD_LABELS[field.fieldPath] ?? field.fieldPath"
                      >
                        <template #header-extra>
                          <NTooltip trigger="hover">
                            <template #trigger>
                              <NTag :type="stateTagType(field.knowledgeState)" size="small" :bordered="false">
                                {{ stateLabel(field.knowledgeState) }}
                              </NTag>
                            </template>
                            {{ field.fieldPath }}
                          </NTooltip>
                        </template>
                        <NSpace vertical :size="8">
                          <NFlex :gap="8" align="center">
                            <NText strong>结论：</NText>
                            <NText v-if="field.displayValue" strong>{{ field.displayValue }}</NText>
                            <NText v-else depth="3">—（{{ stateLabel(field.knowledgeState) }}）</NText>
                          </NFlex>
                          <NCollapse v-if="field.evidenceSummaries.length > 0">
                            <NCollapseItem :title="`依据原文（${field.evidenceSummaries.length} 条）`" :name="field.fieldPath">
                              <NSpace vertical :size="8">
                                <NCard v-for="ev in field.evidenceSummaries" :key="ev.evidenceId" size="small" embedded>
                                  <NSpace vertical :size="4">
                                    <NFlex :gap="8" align="center" wrap>
                                      <NTag size="small" :bordered="false">{{ authorityLabel(ev.authorityLevel) }}</NTag>
                                      <NText depth="3">{{ ev.sourceId }}</NText>
                                      <NText depth="3">{{ ev.locatorHint }}</NText>
                                    </NFlex>
                                    <NText>{{ ev.quoteExcerpt }}</NText>
                                  </NSpace>
                                </NCard>
                              </NSpace>
                            </NCollapseItem>
                          </NCollapse>
                        </NSpace>
                      </NCard>
                    </NSpace>
                  </NTabPane>
                </NTabs>
              </template>
            </NCard>

            <!-- 深度解读：原始产品文档全文 -->
            <NCard size="small" title="深度解读（原始产品文档）">
              <template #header-extra>
                <NText depth="3" style="font-size: 12px">{{ detail.sections.length }} 个章节</NText>
              </template>
              <NCollapse :default-expanded-names="detail.sections[0] ? [detail.sections[0].title] : []">
                <NCollapseItem
                  v-for="section in detail.sections"
                  :key="section.title"
                  :title="section.title"
                  :name="section.title"
                >
                  <pre class="section-content">{{ section.content }}</pre>
                </NCollapseItem>
              </NCollapse>
            </NCard>
          </template>
        </main>
      </div>
    </PageState>
  </div>
</template>

<style scoped>
.interpretation-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.notice :deep(.n-alert-body) {
  align-items: flex-start;
}
.layout {
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 16px;
  align-items: start;
}
.catalog-panel {
  position: sticky;
  top: 16px;
}
.family-title {
  padding: 8px 12px 4px;
  font-size: 12px;
  color: var(--text-tertiary);
  letter-spacing: 0.04em;
}
.catalog-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.catalog-code {
  font-size: 12px;
}
.catalog-panel :deep(.n-list-item.active) {
  background: rgba(24, 160, 88, 0.08);
}
.detail-panel {
  display: flex;
  flex-direction: column;
  gap: 16px;
  min-width: 0;
}
.summary {
  margin: 6px 0 0;
  line-height: 1.7;
  color: var(--text-primary);
}
.src-path {
  font-size: 12px;
  word-break: break-all;
}
.kert-card {
  border-color: rgba(24, 160, 88, 0.35);
}
.interp-loading {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 16px 0;
}
.interp-meta {
  margin-bottom: 12px;
}
.field-list {
  padding-top: 8px;
}
.section-content {
  margin: 0;
  white-space: pre-wrap;
  font-size: 13px;
  line-height: 1.7;
  color: var(--text-primary);
  font-family: inherit;
}
</style>
