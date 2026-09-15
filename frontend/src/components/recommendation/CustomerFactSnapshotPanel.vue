<script setup lang="ts">
import { computed } from 'vue'
import type { ProductRecommendationRun } from '../../api/productRecommendation'

const props = defineProps<{
  run: ProductRecommendationRun | null
}>()

const snapshotEntries = computed<Array<[string, string]>>(() => {
  const refs = props.run?.snapshotRefs
  if (!refs) {
    return []
  }
  return Object.entries(refs)
})

function formatTime(value?: string): string {
  if (!value) {
    return '—'
  }
  return value
}
</script>

<template>
  <section class="fact-snapshot" data-testid="customer-fact-snapshot">
    <h2>客户事实快照</h2>
    <dl v-if="run" class="facts">
      <div>
        <dt>客户</dt>
        <dd>{{ run.customerId }}</dd>
      </div>
      <div>
        <dt>业务时点（asOf）</dt>
        <dd>{{ formatTime(run.asOf) }}</dd>
      </div>
      <div>
        <dt>推荐目的</dt>
        <dd>{{ run.recommendationObjective || '—' }}</dd>
      </div>
      <div>
        <dt>Need 版本引用</dt>
        <dd data-testid="fact-snapshot-needs">
          <span v-if="run.needVersionIds?.length">{{ run.needVersionIds.join('、') }}</span>
          <span v-else class="empty">—</span>
        </dd>
      </div>
      <div>
        <dt>请求产品域</dt>
        <dd>
          <span v-if="run.requestedProductDomains?.length">{{ run.requestedProductDomains.join('、') }}</span>
          <span v-else class="empty">未限定</span>
        </dd>
      </div>
      <div v-if="snapshotEntries.length">
        <dt>快照引用</dt>
        <dd>
          <ul class="refs" data-testid="fact-snapshot-refs">
            <li v-for="[key, value] in snapshotEntries" :key="key">
              <span class="key">{{ key }}</span>
              <span class="value">{{ value }}</span>
            </li>
          </ul>
        </dd>
      </div>
    </dl>
    <p v-else class="empty">尚未加载客户事实快照</p>
  </section>
</template>

<style scoped>
.fact-snapshot h2 {
  font-size: 16px;
  margin: 0 0 12px;
}
.facts {
  display: grid;
  gap: 10px;
  margin: 0;
}
.facts div {
  padding: 10px 12px;
  background: var(--bg-surface);
  border: 1px solid var(--border-light);
  border-radius: 8px;
}
dt {
  font-size: 12px;
  color: var(--text-tertiary);
}
dd {
  margin: 4px 0 0;
  font-size: 13px;
}
.refs {
  list-style: none;
  margin: 4px 0 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.refs li {
  display: grid;
  grid-template-columns: 0.8fr 1.2fr;
  gap: 8px;
  font-size: 12px;
}
.key {
  color: var(--text-tertiary);
  font-family: monospace;
  overflow-wrap: anywhere;
}
.value {
  font-family: monospace;
  overflow-wrap: anywhere;
}
.empty {
  color: var(--text-tertiary);
  font-size: 13px;
}
</style>
