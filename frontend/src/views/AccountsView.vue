<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NInput, NButton, NSkeleton, NRadioGroup, NRadioButton } from 'naive-ui'
import ObjectHeader from '../components/shell/ObjectHeader.vue'
import DisabledAction from '../components/shell/DisabledAction.vue'
import CustomerCard from '../components/CustomerCard.vue'
import { fetchCustomers, type Customer, RISK_LEVEL_LABELS, CUSTOMER_TIER_LABELS } from '../api/engagement'
import { usePageReferenceStore } from '../stores/pageReference'

const PAGE_ID = 'P02'
const OBJECT_TYPE = '客户 Account'

const route = useRoute()
const router = useRouter()
const pageRefs = usePageReferenceStore()

const customers = ref<Customer[]>([])
const loading = ref(true)
const error = ref('')
const requested = ref(false)
const filter = ref('')
const viewMode = ref<'card' | 'table'>('card')

const visibleCustomers = computed(() => {
  const q = filter.value.trim()
  if (!q) return customers.value
  return customers.value.filter(item => item.customerName.includes(q) || item.customerId.includes(q))
})

function persistReference() {
  pageRefs.capture(PAGE_ID, {
    objectType: OBJECT_TYPE,
    viewId: 'object_list',
    filter: filter.value,
    subtab: viewMode.value,
    scrollAnchor: typeof window !== 'undefined' ? window.scrollY : 0,
  })
}

async function loadCustomers() {
  loading.value = true
  error.value = ''
  requested.value = true
  try {
    customers.value = await fetchCustomers()
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : '无法获取客户列表'
  } finally {
    loading.value = false
  }
}

function openCustomer(id: string) {
  persistReference()
  router.push({ name: 'CustomerOperatingView', params: { id } })
}

onMounted(() => {
  const restored = pageRefs.restore(PAGE_ID, OBJECT_TYPE)
  filter.value = String(route.query.q || restored.filter || '')
  viewMode.value = (restored.subtab as 'card' | 'table') ?? 'card'
  loadCustomers()
})

onBeforeUnmount(persistReference)
</script>

<template>
  <div class="accounts" data-testid="p02-accounts">
    <ObjectHeader
      :page-id="PAGE_ID"
      :object-type="OBJECT_TYPE"
      object-status="列表"
      title="客户组合"
    />

    <div class="toolbar">
      <n-input
        v-model:value="filter"
        data-testid="p02-filter"
        placeholder="搜索客户名称或 ID"
        aria-label="搜索客户"
        style="max-width: 280px"
        clearable
        @update:value="persistReference"
      />
      <n-radio-group v-model:value="viewMode" size="small" @update:value="persistReference">
        <n-radio-button value="card">卡片</n-radio-button>
        <n-radio-button value="table">列表</n-radio-button>
      </n-radio-group>
      <DisabledAction
        label="导入名单"
        :disabled="true"
        reason="导入名单为写操作，P30 仅授权只读切片"
        unlockPath="待合同批准与后续 Loop 授权既有写 Action"
      />
      <router-link class="related-link" to="/accounts/portfolio" data-testid="p02-open-portfolio">
        组合看板
      </router-link>
    </div>

    <!-- 筛选结果计数 -->
    <div v-if="!loading && requested" class="filter-summary">
      <span v-if="filter.trim()">筛选结果：{{ visibleCustomers.length }} / {{ customers.length }} 位客户</span>
      <span v-else>共 {{ customers.length }} 位客户</span>
    </div>

    <!-- Loading 骨架 -->
    <div v-if="loading" class="skeleton-grid" data-testid="loading-state" aria-busy="true" aria-label="加载中">
      <div v-for="i in 6" :key="i" class="skeleton-card">
        <n-skeleton text :width="120" style="margin-bottom: 10px" />
        <n-skeleton text :width="80" />
        <n-skeleton text :width="160" style="margin-top: 8px" />
      </div>
    </div>

    <!-- Error 状态 -->
    <div v-else-if="error" class="error-block" data-testid="p02-error">
      <p class="error-text">加载失败：{{ error }}</p>
      <n-button size="small" @click="loadCustomers">重试</n-button>
    </div>

    <!-- 卡片视图 -->
    <template v-else-if="viewMode === 'card'">
      <div v-if="visibleCustomers.length" class="customer-grid" data-testid="p02-customer-grid">
        <CustomerCard
          v-for="customer in visibleCustomers"
          :key="customer.customerId"
          :customer="customer"
          @click="openCustomer(customer.customerId)"
        />
      </div>
      <div v-else class="empty-state" data-testid="p02-empty">
        <p class="empty-title">{{ filter.trim() ? '没有匹配的客户' : '暂无客户数据' }}</p>
        <p class="empty-desc">{{ filter.trim() ? '尝试调整搜索条件' : '客户组合为空，请前往经营总览查看待办事项。' }}</p>
        <n-button v-if="filter.trim()" size="small" @click="filter = ''">清除筛选</n-button>
        <n-button v-else size="small" @click="router.push('/workbench')">前往经营总览</n-button>
      </div>
    </template>

    <!-- 列表视图 -->
    <template v-else>
      <div v-if="visibleCustomers.length" class="customer-table" data-testid="p02-customer-table">
        <div class="table-header">
          <span class="col-name">客户名称</span>
          <span class="col-tier">层级</span>
          <span class="col-risk">风险</span>
          <span class="col-action">下一步</span>
        </div>
        <div
          v-for="customer in visibleCustomers"
          :key="customer.customerId"
          class="table-row"
          tabindex="0"
          role="link"
          :aria-label="`查看 ${customer.customerName} 详情`"
          @click="openCustomer(customer.customerId)"
          @keydown.enter="openCustomer(customer.customerId)"
        >
          <span class="col-name">
            <button type="button" class="customer-link" @click.stop="openCustomer(customer.customerId)">{{ customer.customerName }}</button>
          </span>
          <span class="col-tier">{{ customer.customerTier ? CUSTOMER_TIER_LABELS[customer.customerTier as keyof typeof CUSTOMER_TIER_LABELS] : '-' }}</span>
          <span class="col-risk">{{ customer.riskLevel ? RISK_LEVEL_LABELS[customer.riskLevel as keyof typeof RISK_LEVEL_LABELS] : '-' }}</span>
          <span class="col-action">{{ customer.riskLevel === 'HIGH' ? '风险跟进' : customer.customerTier === 'STRATEGIC' ? '经营检视' : '常规维护' }}</span>
        </div>
      </div>
      <div v-else class="empty-state" data-testid="p02-empty">
        <p class="empty-title">{{ filter.trim() ? '没有匹配的客户' : '暂无客户数据' }}</p>
        <p class="empty-desc">{{ filter.trim() ? '尝试调整搜索条件' : '客户组合为空。' }}</p>
        <n-button v-if="filter.trim()" size="small" @click="filter = ''">清除筛选</n-button>
      </div>
    </template>
  </div>
</template>

<style scoped>
.accounts {
  max-width: 1240px;
  padding: 32px 34px 48px;
}

.toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
  margin-bottom: 16px;
}

.related-link {
  color: var(--brand-primary);
  font-size: 13px;
  align-self: center;
}
.related-link:focus-visible {
  outline: 2px solid var(--v8-focus-on-light);
  outline-offset: 2px;
  border-radius: 4px;
}

.filter-summary {
  font-size: 13px;
  color: var(--v8-nav-text);
  margin-bottom: 12px;
}

/* 骨架 */
.skeleton-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}
.skeleton-card {
  padding: 18px;
  border: 1px solid var(--border-light);
  border-radius: 10px;
  background: var(--bg-surface);
}

/* 错误 */
.error-block {
  padding: 24px;
  background: var(--bg-surface);
  border: 1px solid var(--border-light);
  border-radius: 10px;
  text-align: center;
}
.error-text {
  color: var(--color-error, #C0392B);
  margin-bottom: 12px;
  font-size: 14px;
}

/* 卡片网格 */
.customer-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

/* 列表视图 */
.customer-table {
  border: 1px solid var(--border-light);
  border-radius: 10px;
  overflow: hidden;
}
.table-header {
  display: grid;
  grid-template-columns: 2fr 0.8fr 0.8fr 1fr;
  gap: 12px;
  padding: 10px 16px;
  background: rgba(17, 45, 64, 0.03);
  font-size: 12px;
  font-weight: 600;
  color: var(--v8-nav-text);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
.table-row {
  display: grid;
  grid-template-columns: 2fr 0.8fr 0.8fr 1fr;
  gap: 12px;
  padding: 12px 16px;
  border-top: 1px solid var(--border-light);
  font-size: 14px;
  cursor: pointer;
  transition: background 0.1s ease;
}
.table-row:hover {
  background: rgba(59, 88, 200, 0.03);
}
.table-row:focus-visible {
  outline: 2px solid var(--v8-focus-on-light);
  outline-offset: -2px;
}
.customer-link {
  border: 0;
  background: transparent;
  color: var(--brand-primary);
  cursor: pointer;
  font-weight: 600;
  font-size: 14px;
  text-align: left;
}
.customer-link:hover {
  color: var(--brand-primary-light);
}
.customer-link:focus-visible {
  outline: 2px solid var(--v8-focus-on-light);
  outline-offset: 2px;
  border-radius: 4px;
}
.col-tier, .col-risk, .col-action {
  color: var(--text-primary);
  font-size: 13px;
}
.col-action {
  color: var(--brand-primary);
  font-weight: 500;
}

/* 空态 */
.empty-state {
  padding: 40px 24px;
  text-align: center;
  background: var(--bg-surface);
  border: 1px solid var(--border-light);
  border-radius: 10px;
}
.empty-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
}
.empty-desc {
  font-size: 13px;
  color: var(--v8-nav-text);
  margin-bottom: 16px;
}

/* 中宽屏 */
@media (max-width: 1024px) {
  .accounts {
    padding: 24px 24px 40px;
  }
  .customer-grid {
    grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  }
}

/* 手机 */
@media (max-width: 640px) {
  .accounts {
    padding: 16px 16px 32px;
  }
  .customer-grid {
    grid-template-columns: 1fr;
  }
  .table-header, .table-row {
    grid-template-columns: 1fr;
    gap: 4px;
  }
}
</style>
