<template>
  <div class="event-monitor">
    <div class="page-header">
      <h1>外部事件监控</h1>
      <p class="subtitle">追踪外部事件对客户经营的影响</p>
    </div>

    <div class="stats-bar">
      <div class="stat-item">
        <span class="stat-value">{{ eventStore.events.length }}</span>
        <span class="stat-label">事件总数</span>
      </div>
      <div class="stat-item">
        <span class="stat-value">{{ eventStore.highConfidenceEvents.length }}</span>
        <span class="stat-label">高置信度</span>
      </div>
      <div class="stat-item">
        <span class="stat-value">{{ eventStore.bankUsableEvents.length }}</span>
        <span class="stat-label">可用于银行业务</span>
      </div>
    </div>

    <div class="monitor-grid">
      <section class="section main-section">
        <h2>近期事件</h2>
        <ExternalEventList
          :events="eventStore.events"
          :loading="eventStore.loading"
          title=""
          @select="onEventSelect"
        />
      </section>

      <aside class="section side-section">
        <h2>产品知识更新</h2>
        <ProductKnowledgeCard
          v-for="v in recentKnowledge"
          :key="v.versionId"
          :version="v"
        />
        <div v-if="recentKnowledge.length === 0" class="empty-state">暂无产品知识更新</div>
      </aside>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useExternalEventStore } from '../stores/externalEvent'
import ExternalEventList from '../components/ExternalEventList.vue'
import ProductKnowledgeCard from '../components/ProductKnowledgeCard.vue'
import { fetchRecentProductKnowledge } from '../api/v11'
import type { ExternalEvent, ProductKnowledgeVersion } from '../api/v11'

const eventStore = useExternalEventStore()
const recentKnowledge = ref<ProductKnowledgeVersion[]>([])

onMounted(async () => {
  await Promise.all([
    eventStore.loadEvents(),
    eventStore.loadRecentEvents(20),
    loadKnowledge()
  ])
})

async function loadKnowledge() {
  try {
    recentKnowledge.value = await fetchRecentProductKnowledge(5)
  } catch (e) {
    console.error('加载产品知识失败:', e)
  }
}

function onEventSelect(e: ExternalEvent) {
  console.log('Selected event:', e.eventId)
}
</script>

<style scoped>
.event-monitor {
  max-width: 1240px;
  padding: 32px 34px 48px;
}
.page-header { margin-bottom: var(--space-6); }
.page-header h1 { font-size: var(--text-2xl); color: var(--text-primary); margin: 0 0 var(--space-1); font-weight: 600; }
.subtitle { color: var(--v8-nav-text); font-size: var(--text-sm); margin: 0; }
.stats-bar {
  display: flex;
  gap: var(--space-6);
  margin-bottom: var(--space-6);
  padding: var(--space-5) var(--space-6);
  background: linear-gradient(135deg, var(--brand-primary), var(--brand-primary-light));
  border-radius: var(--radius-lg);
  color: var(--text-inverse);
  box-shadow: var(--shadow-md);
}
.stat-item { display: flex; flex-direction: column; align-items: center; min-width: 80px; }
.stat-value { font-size: var(--text-3xl); font-weight: 700; }
.stat-label { font-size: var(--text-xs); opacity: 0.85; margin-top: 2px; }
.monitor-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: var(--space-6);
}
.section { }
.section h2 { font-size: var(--text-lg); color: var(--text-primary); margin: 0 0 var(--space-3); font-weight: 600; }
.side-section {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}
.empty-state { text-align: center; padding: var(--space-6); color: var(--v8-nav-text); font-size: var(--text-sm); }
</style>
