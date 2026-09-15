<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import MobileDegradeFrame from '../components/shell/MobileDegradeFrame.vue'
import PageState from '../components/shell/PageState.vue'
import DisabledAction from '../components/shell/DisabledAction.vue'
import { loadMobileDegradeShell, MOBILE_DEGRADE_PAGES } from '../composables/mobileDegrade'
import { deriveResourceStatus } from '../composables/useResourceStatus'
import { usePageReferenceStore } from '../stores/pageReference'

const page = MOBILE_DEGRADE_PAGES.P43
const pageRefs = usePageReferenceStore()
const loading = ref(true)
const error = ref('')
const requested = ref(false)

const status = computed(() =>
  deriveResourceStatus({
    loading: loading.value,
    error: error.value,
    hasData: requested.value,
    requested: requested.value,
  }),
)

function persistReference() {
  pageRefs.capture(page.pageId, {
    objectType: page.objectType,
    viewId: 'mobile_notes',
    scrollAnchor: typeof window !== 'undefined' ? window.scrollY : 0,
  })
}

async function load() {
  loading.value = true
  error.value = ''
  requested.value = true
  try {
    await loadMobileDegradeShell()
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : '无法装配会中速记降级壳层'
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
      <DisabledAction
        v-for="action in page.disabledActions"
        :key="action.label"
        :label="action.label"
        :disabled="true"
        :reason="action.reason"
        :unlock-path="action.unlockPath"
      />
      <RouterLink class="desktop-link" data-testid="p43-desktop-meeting" to="/in-meeting">
        查看桌面会中工作区（只读）
      </RouterLink>
    </template>
    <PageState :status="status" :error="error" :idle-description="page.idleDescription" @retry="load">
      <p class="empty" data-testid="p43-mobile-notes-empty">
        {{ page.emptyText }}草稿不得当成正式 Claim。
      </p>
    </PageState>
  </MobileDegradeFrame>
</template>

<style scoped>
.desktop-link {
  display: inline-flex;
  align-items: center;
  height: 32px;
  padding: 0 12px;
  color: var(--brand-primary);
  text-decoration: none;
  font-size: 13px;
}
.empty {
  color: var(--text-tertiary);
  font-size: 13px;
}
</style>
