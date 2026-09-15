<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import MobileDegradeFrame from '../components/shell/MobileDegradeFrame.vue'
import PageState from '../components/shell/PageState.vue'
import DisabledAction from '../components/shell/DisabledAction.vue'
import {
  firstOnlineDeepLink,
  loadTodayActions,
  MOBILE_DEGRADE_PAGES,
  type TodayActionItem,
} from '../composables/mobileDegrade'
import { deriveResourceStatus } from '../composables/useResourceStatus'
import { usePageReferenceStore } from '../stores/pageReference'

const page = MOBILE_DEGRADE_PAGES.P41
const pageRefs = usePageReferenceStore()
const loading = ref(true)
const error = ref('')
const requested = ref(false)
const items = ref<TodayActionItem[]>([])

const status = computed(() =>
  deriveResourceStatus({
    loading: loading.value,
    error: error.value,
    hasData: requested.value,
    requested: requested.value,
  }),
)

const openFirstTo = computed(() => firstOnlineDeepLink(items.value))

function persistReference() {
  pageRefs.capture(page.pageId, {
    objectType: page.objectType,
    viewId: 'mobile_today',
    scrollAnchor: typeof window !== 'undefined' ? window.scrollY : 0,
  })
}

async function load() {
  loading.value = true
  error.value = ''
  requested.value = true
  try {
    items.value = await loadTodayActions()
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : '无法加载今日在线行动'
    items.value = []
  } finally {
    loading.value = false
  }
}

onMounted(load)
onBeforeUnmount(persistReference)
</script>

<template>
  <MobileDegradeFrame
    :page-id="page.pageId"
    :title="page.title"
    :object-type="page.objectType"
    :object-status="page.objectStatus"
    :test-id="page.testId"
    :hint="page.hint"
  >
    <template #toolbar>
      <RouterLink class="open-first" data-testid="p41-open-first" :to="openFirstTo">打开首项</RouterLink>
      <DisabledAction
        v-for="action in page.disabledActions"
        :key="action.label"
        :label="action.label"
        :disabled="true"
        :reason="action.reason"
        :unlock-path="action.unlockPath"
      />
    </template>
    <PageState :status="status" :error="error" :idle-description="page.idleDescription" @retry="load">
      <ul v-if="items.length" class="item-list" data-testid="p41-today-queue">
        <li v-for="item in items" :key="item.customerId">
          <RouterLink :to="item.onlinePath">{{ item.customerName }}</RouterLink>
          <span class="meta">在线深链（非正式任务）</span>
        </li>
      </ul>
      <p v-else class="empty" data-testid="p41-mobile-today-empty">{{ page.emptyText }}</p>
    </PageState>
  </MobileDegradeFrame>
</template>

<style scoped>
.open-first {
  display: inline-flex;
  align-items: center;
  height: 32px;
  padding: 0 12px;
  border: 1px solid var(--border-normal);
  border-radius: 6px;
  background: var(--bg-surface);
  color: var(--brand-primary);
  text-decoration: none;
  font-size: 13px;
  font-weight: 600;
}
.item-list {
  list-style: none;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.item-list li {
  display: flex;
  justify-content: space-between;
  gap: 8px;
  padding: 12px 14px;
  background: var(--bg-surface);
  border: 1px solid var(--border-light);
  border-radius: 8px;
  font-size: 13px;
}
.meta,
.empty {
  color: var(--text-tertiary);
  font-size: 13px;
}
</style>
