<script setup lang="ts">
/**
 * 左侧产品目录（需求 02 §6-2 / PI-FR-009、010、011、012、014）。
 *
 * 边界：目录只呈现产品族与产品；**不得**出现客户、商机或推荐排序。
 * 计数口径来自后端（按已登记产品与可呈现版本计算），前端不自行排序或增删。
 */
import { computed, ref } from 'vue'
import { NTag } from 'naive-ui'
import type { ProductCenterFamily, ProductCenterProductEntry } from '../../api/productCenter'

const props = defineProps<{
  families: ProductCenterFamily[]
  products: ProductCenterProductEntry[]
  selectedProductId: string | null
  loading: boolean
}>()

const emit = defineEmits<{
  (e: 'select', productId: string): void
}>()

const collapsed = ref<Record<string, boolean>>({})

const productsByFamily = computed(() => {
  const map = new Map<string, ProductCenterProductEntry[]>()
  for (const product of props.products) {
    const list = map.get(product.familyId) ?? []
    list.push(product)
    map.set(product.familyId, list)
  }
  return map
})

function toggle(familyId: string) {
  collapsed.value = { ...collapsed.value, [familyId]: !collapsed.value[familyId] }
}

function isCollapsed(familyId: string) {
  return collapsed.value[familyId] === true
}

function countIn(familyId: string) {
  return (productsByFamily.value.get(familyId) ?? []).length
}
</script>

<template>
  <nav class="pc-catalog" data-testid="pc-catalog" aria-label="产品目录">
    <div class="pc-catalog-head">
      <span class="pc-catalog-title">产品目录</span>
      <span class="pc-catalog-total" data-testid="pc-catalog-total">
        共 {{ products.length }} 个产品 · {{ families.length }} 个产品族
      </span>
    </div>

    <p v-if="loading" class="pc-catalog-state" data-testid="pc-catalog-loading">目录加载中…</p>
    <p v-else-if="families.length === 0" class="pc-catalog-state" data-testid="pc-catalog-empty">
      暂无可呈现的产品目录
    </p>

    <ul v-else class="pc-family-list">
      <li
        v-for="family in families"
        :key="family.familyId"
        class="pc-family"
        data-testid="pc-catalog-family"
        :data-family-id="family.familyId"
      >
        <button
          type="button"
          class="pc-family-head"
          :aria-expanded="!isCollapsed(family.familyId)"
          @click="toggle(family.familyId)"
        >
          <span class="pc-family-caret">{{ isCollapsed(family.familyId) ? '▸' : '▾' }}</span>
          <span class="pc-family-name">{{ family.familyName }}</span>
          <span class="pc-family-domain">{{ family.domainName }}</span>
          <span class="pc-family-count" data-testid="pc-family-count">
            {{ countIn(family.familyId) }}
          </span>
        </button>

        <p v-if="family.unclassifiedCount > 0" class="pc-family-warn">
          {{ family.unclassifiedCount }} 个产品待维护内容
        </p>

        <ul v-show="!isCollapsed(family.familyId)" class="pc-product-list">
          <li
            v-for="product in productsByFamily.get(family.familyId) ?? []"
            :key="product.productId"
            class="pc-product"
            data-testid="pc-catalog-product"
            :data-product-id="product.productId"
          >
            <button
              type="button"
              class="pc-product-btn"
              :class="{ 'is-active': product.productId === selectedProductId }"
              :aria-current="product.productId === selectedProductId ? 'true' : undefined"
              @click="emit('select', product.productId)"
            >
              <span class="pc-product-name">{{ product.productName }}</span>
              <span class="pc-product-id">{{ product.productId }}</span>
              <n-tag v-if="!product.hasPublishedVersion" size="tiny" :bordered="true" type="warning">
                无有效版本
              </n-tag>
            </button>
          </li>
        </ul>
      </li>
    </ul>
  </nav>
</template>

<style scoped>
.pc-catalog {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 12px;
  background: var(--bg-surface, #fff);
  border: 1px solid var(--border-light, #d8e2ec);
  border-radius: 13px;
}

.pc-catalog-head {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.pc-catalog-title {
  font-size: 13px;
  font-weight: 700;
  color: var(--gits-navy-800);
}

.pc-catalog-total {
  font-size: 11px;
  color: var(--gits-muted);
}

.pc-catalog-state {
  margin: 6px 0 0;
  font-size: 12px;
  color: var(--gits-muted);
}

.pc-family-list,
.pc-product-list {
  margin: 0;
  padding: 0;
  list-style: none;
}

.pc-family + .pc-family {
  margin-top: 6px;
}

.pc-family-head {
  display: flex;
  align-items: center;
  gap: 6px;
  width: 100%;
  padding: 6px 6px;
  background: transparent;
  border: 0;
  border-radius: 8px;
  cursor: pointer;
  text-align: left;
}

.pc-family-head:hover {
  background: var(--bg-hover, #eff3fb);
}

.pc-family-caret {
  color: var(--gits-muted);
  font-size: 11px;
}

.pc-family-name {
  font-size: 13px;
  font-weight: 600;
  color: var(--gits-text);
}

.pc-family-domain,
.pc-family-count {
  font-size: 11px;
  color: var(--gits-muted);
}

.pc-family-count {
  margin-left: auto;
  padding: 0 6px;
  border-radius: 8px;
  background: var(--gits-page);
}

.pc-family-warn {
  margin: 2px 0 4px 22px;
  font-size: 11px;
  color: var(--color-warning, #7a4b00);
}

.pc-product-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  width: 100%;
  padding: 6px 8px 6px 22px;
  background: transparent;
  border: 0;
  border-radius: 8px;
  cursor: pointer;
  text-align: left;
}

.pc-product-btn:hover {
  background: var(--bg-hover, #eff3fb);
}

.pc-product-btn.is-active {
  background: var(--brand-primary-lighter, #eaf4fe);
  box-shadow: inset 2px 0 0 var(--gits-blue-600);
}

.pc-product-name {
  font-size: 12.5px;
  color: var(--gits-text);
}

.pc-product-id {
  font-size: 11px;
  color: var(--gits-muted);
  margin-left: auto;
}
</style>
