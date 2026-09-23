<script setup lang="ts">
/**
 * 企业金融产品中心 — 产品解读页（REQ-PI-01 / Loop PC1）。
 *
 * 结构：顶部环境条 + 三栏（左：产品目录 / 中：产品首屏 + 章节导航 + 八章 / 右：知识治理）。
 *
 * 硬边界（需求 01 §3.2）：
 * - 以产品为主语，不选择客户，不读取客户画像 / 账户 / 交易 / 授信 / 商机；
 * - 不计算适配度、推荐分、排名、赢单概率，不输出「适合某客户」的结论；
 * - 不承诺额度、期限、利率、费用、担保方式、办理时效与审批结果；
 * - 数据缺失显示「待核验」，无有效版本显示受控状态，不以示意内容填充。
 *
 * 数据来源：CTR-PKC-API-001（families / products / products/{productId}）。
 */
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NAlert, NSpin } from 'naive-ui'
import ProductEnvironmentBanner from '../components/product-center/ProductEnvironmentBanner.vue'
import ProductCatalog from '../components/product-center/ProductCatalog.vue'
import ProductHero from '../components/product-center/ProductHero.vue'
import ProductSectionNav from '../components/product-center/ProductSectionNav.vue'
import ProductChapterStack from '../components/product-center/ProductChapterStack.vue'
import ProductInheritedChapters from '../components/product-center/ProductInheritedChapters.vue'
import ProductSourceMaterial from '../components/product-center/ProductSourceMaterial.vue'
import ProductGovernancePanel from '../components/product-center/ProductGovernancePanel.vue'
import { fetchProductCardDetail, type ProductCardDetail } from '../api/productKnowledge'
import { IMMUTABLE_VERSION_CHAPTER, findCardSection } from '../utils/cardChapter'
import {
  extractErrorCode,
  fetchProductCenterDetail,
  fetchProductCenterFamilies,
  fetchProductCenterProducts,
  type ProductCenterDetail,
  type ProductCenterFamily,
  type ProductCenterProductEntry
} from '../api/productCenter'

const route = useRoute()
const router = useRouter()

const families = ref<ProductCenterFamily[]>([])
const products = ref<ProductCenterProductEntry[]>([])
const detail = ref<ProductCenterDetail | null>(null)
const catalogLoading = ref(false)
const detailLoading = ref(false)
const catalogErrorCode = ref<string | null>(null)
const detailErrorCode = ref<string | null>(null)
const keyword = ref('')
const selectedProductId = ref<string | null>(null)

/**
 * 产品卡详情（PC-i1 章级承接数据源）：供「C6/C9 独立承接区」与「C11 版本语义」使用。
 * 取自既有合同 CTR-PK-INT-001（只读复用，不改 P38 代码）；失败 ⇒ null，由各区块**具名**标注缺失。
 */
const cardDetail = ref<ProductCardDetail | null>(null)

const cardSections = computed(() => cardDetail.value?.sections ?? [])
const cardSourceFile = computed(() => cardDetail.value?.sourceFile ?? null)
/** C11：产品卡第 11 节（不可变版本语义）原文；定位不到 ⇒ null（版本区具名标注）。 */
const immutableVersionSection = computed(() => {
  const section = findCardSection(cardDetail.value?.sections ?? [], IMMUTABLE_VERSION_CHAPTER)
  return section ? { title: section.title, content: section.content } : null
})

async function loadCardDetail(productId: string | null) {
  cardDetail.value = null
  if (!productId) {
    return
  }
  try {
    cardDetail.value = await fetchProductCardDetail(productId)
  } catch {
    // 如实：不伪造来源；承接区/版本区会分别显示"来源标识不可得""未包含该节原文"
    cardDetail.value = null
  }
}

const environment = computed(
  () => detail.value?.version.environment ?? products.value[0]?.environment ?? 'DEMO'
)
const isDemo = computed(() => detail.value?.version.isDemo ?? products.value[0]?.isDemo ?? true)
const knowledgeAsOf = computed(() => detail.value?.version.knowledgeAsOf ?? null)

/** 身份服务未接入（PC2）：显式说明，不以假身份填充（PI-FR-004 缺口登记）。 */
const identityNote = '当前用户：身份服务未接入（PC2）'

const catalogErrorMessage = computed(() => {
  if (catalogErrorCode.value === 'SOURCES_UNAVAILABLE') {
    return '分类骨架或产品卡源当前不可读：目录已停止呈现（fail-closed），未做任何本地兜底。'
  }
  return catalogErrorCode.value ? '产品目录加载失败。' : null
})

const detailErrorMessage = computed(() => {
  switch (detailErrorCode.value) {
    case 'PRODUCT_NOT_FOUND':
      return '该产品未在受控分类法中登记。'
    case 'SOURCES_UNAVAILABLE':
      return '知识源当前不可读，产品解读已停止呈现（fail-closed）。'
    case null:
      return null
    case 'NO_PUBLISHED_VERSION':
      // 「无有效版本」不是错误，而是受控状态：由专用分支呈现（AT-009），
      // 不得落入通用错误文案。
      return null
    default:
      return '产品解读加载失败。'
  }
})

const detailHasNoVersion = computed(() => detailErrorCode.value === 'NO_PUBLISHED_VERSION')

async function loadCatalog() {
  catalogLoading.value = true
  catalogErrorCode.value = null
  try {
    const [familyList, productList] = await Promise.all([
      fetchProductCenterFamilies(),
      fetchProductCenterProducts(keyword.value ? { keyword: keyword.value } : {})
    ])
    families.value = familyList
    products.value = productList
  } catch (error) {
    catalogErrorCode.value = extractErrorCode(error) ?? 'UNKNOWN_ERROR'
    families.value = []
    products.value = []
  } finally {
    catalogLoading.value = false
  }
}

async function loadDetail(productId: string) {
  detailLoading.value = true
  detailErrorCode.value = null
  detail.value = null
  try {
    detail.value = await fetchProductCenterDetail(productId)
  } catch (error) {
    detailErrorCode.value = extractErrorCode(error) ?? 'UNKNOWN_ERROR'
  } finally {
    detailLoading.value = false
  }
}

/**
 * 选择产品：产品标识以 URL 承载（可分享、可回退）。
 * 默认落点 = 目录首项（受控分类法顺序），**不是**推荐或排序结果。
 */
function selectProduct(productId: string) {
  if (productId === selectedProductId.value) {
    return
  }
  selectedProductId.value = productId
  void router.replace({ name: 'ProductCenter', params: { productId } })
  void loadDetail(productId)
}

function syncFromRoute() {
  const fromRoute = (route.params.productId as string | undefined) ?? null
  if (fromRoute) {
    selectedProductId.value = fromRoute
    void loadDetail(fromRoute)
    return
  }
  detail.value = null
  detailErrorCode.value = null
  if (products.value.length > 0) {
    selectProduct(products.value[0].productId)
  }
}

onMounted(async () => {
  await loadCatalog()
  syncFromRoute()
})

watch(keyword, () => {
  void loadCatalog()
})

watch(
  () => route.params.productId,
  (next) => {
    const nextId = (next as string | undefined) ?? null
    if (nextId && nextId !== selectedProductId.value) {
      selectedProductId.value = nextId
      void loadDetail(nextId)
    }
  }
)

// 章级承接区与版本语义的数据源（随选中产品变化重取；失败在区块内具名标注）
watch(selectedProductId, (productId) => {
  void loadCardDetail(productId)
})
</script>

<template>
  <div class="pc-page" data-testid="product-center-shell">
    <ProductEnvironmentBanner
      :environment="environment"
      :is-demo="isDemo"
      :knowledge-as-of="knowledgeAsOf"
      :keyword="keyword"
      :identity-note="identityNote"
      @update:keyword="keyword = $event"
    />

    <div class="pc-layout">
      <!-- 左：产品目录（<1180px 时成为全宽侧板，字段不消失） -->
      <div class="pc-col pc-col-left" data-testid="pc-col-left">
        <ProductCatalog
          :families="families"
          :products="products"
          :selected-product-id="selectedProductId"
          :loading="catalogLoading"
          @select="selectProduct"
        />
        <NAlert v-if="catalogErrorMessage" type="error" :show-icon="true" data-testid="pc-catalog-error">
          <p class="pc-alert-body">{{ catalogErrorMessage }}</p>
          <p class="pc-code">错误码：{{ catalogErrorCode }}</p>
        </NAlert>
      </div>

      <!-- 中：产品首屏 + 章节导航 + 八章 -->
      <main class="pc-col pc-col-main" data-testid="pc-col-main">
        <div v-if="detailLoading" class="pc-state" data-testid="pc-detail-loading">
          <NSpin size="small" />
          <span class="pc-state-body">产品解读加载中…</span>
        </div>

        <section v-else-if="detailErrorMessage" class="pc-state pc-state-error" data-testid="pc-detail-error">
          <p class="pc-state-title">无法呈现产品解读</p>
          <p class="pc-state-body">{{ detailErrorMessage }}</p>
          <p class="pc-code">错误码：{{ detailErrorCode }}</p>
        </section>

        <section v-else-if="detailHasNoVersion" class="pc-state" data-testid="pc-no-published-version">
          <p class="pc-state-title">暂无有效发布版本</p>
          <p class="pc-state-body">
            该产品已在受控分类法中登记，但当前没有可呈现的受控知识版本。
            产品知识责任人完成编制并发布后，本页将按发布版本呈现；本页不展示草稿或示意内容。
          </p>
        </section>

        <template v-else-if="detail">
          <ProductHero :detail="detail" />
          <ProductSectionNav />
          <ProductChapterStack :detail="detail" />
          <!-- PC-i1 · W1-a/b：R2 映射记为「无任何对应区块」的章节（C6/C9）原样落位 -->
          <ProductInheritedChapters
            :sections="cardSections"
            :source-file="cardSourceFile"
            :sales-boundaries="detail.salesBoundaries"
            :version-status="detail.version.versionStatus"
            :version-label="detail.version.versionLabel"
            :effective-from="detail.version.effectiveFrom"
          />
          <!-- PC1.5：八章契约未接入期间，保留产品卡原始材料（真实材料，非示意数据） -->
          <ProductSourceMaterial :product-id="detail.productId" />
        </template>

        <section v-else class="pc-state" data-testid="pc-no-selection">
          <p class="pc-state-title">请从左侧目录选择产品</p>
          <p class="pc-state-body">产品中心以产品为主语：先选产品，再阅读客观产品解读。</p>
        </section>
      </main>

      <!-- 右：知识治理（<1180px 时成为全宽侧板，字段不消失） -->
      <div class="pc-col pc-col-right" data-testid="pc-col-right">
        <ProductGovernancePanel
          v-if="detail"
          :detail="detail"
          :immutable-version="immutableVersionSection"
          :card-source-file="cardSourceFile"
        />
        <div v-else class="pc-gov-placeholder" data-testid="pc-governance-placeholder">
          知识治理栏随产品选择呈现。
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.pc-page {
  min-height: 100%;
  background: var(--bg-page, #f3f6f9);
}

.pc-layout {
  display: grid;
  grid-template-columns: 246px minmax(680px, 1fr) 310px;
  gap: 14px;
  max-width: 1700px;
  margin: 0 auto;
  padding: 14px 20px 40px;
  align-items: start;
}

.pc-col-left,
.pc-col-right {
  position: sticky;
  top: 62px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.pc-col-main {
  display: flex;
  flex-direction: column;
  gap: 12px;
  min-width: 0;
}

.pc-state {
  padding: 20px;
  background: var(--bg-surface, #fff);
  border: 1px solid var(--border-light, #d8e2ec);
  border-radius: 13px;
}

.pc-state-title {
  margin: 0 0 6px;
  font-size: 15px;
  font-weight: 700;
  color: var(--gits-navy-800);
}

.pc-state-body {
  margin: 0;
  font-size: 13px;
  line-height: 1.7;
  color: var(--gits-muted);
}

.pc-state-error {
  border-left: 3px solid var(--color-danger, #dc2626);
}

.pc-code {
  margin: 8px 0 0;
  font-size: 11px;
  color: var(--gits-muted);
}

.pc-alert-body {
  margin: 0;
  font-size: 12.5px;
  line-height: 1.6;
}

.pc-gov-placeholder {
  padding: 14px;
  font-size: 12px;
  color: var(--gits-muted);
  background: var(--bg-surface, #fff);
  border: 1px dashed var(--border-light, #d8e2ec);
  border-radius: 13px;
}

/* 1440：保持三栏，左右栏略收 */
@media (max-width: 1439px) {
  .pc-layout {
    grid-template-columns: 220px minmax(0, 1fr) 280px;
  }
}

/* 1280：左右栏压缩（流程两行等正文适配随 PC2 内容接入） */
@media (max-width: 1279px) {
  .pc-layout {
    grid-template-columns: 200px minmax(0, 1fr) 250px;
    gap: 10px;
  }
}

/* <1180：左右栏变为全宽侧板（核心字段不消失；受控抽屉交互由 PC2 补齐） */
@media (max-width: 1179px) {
  .pc-layout {
    grid-template-columns: minmax(0, 1fr);
  }

  .pc-col-left,
  .pc-col-right {
    position: static;
  }
}
</style>
