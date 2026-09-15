<script setup lang="ts">
export interface MetricItem {
  label: string
  value: string
  tone?: 'blue' | 'teal' | 'amber'
}

defineProps<{ items: MetricItem[] }>()
</script>

<template>
  <div class="highlights" data-testid="highlights-metrics">
    <div v-for="(m, i) in items" :key="i" class="hl-card" :class="`hl-${m.tone || 'blue'}`">
      <span class="hl-value">{{ m.value }}</span>
      <span class="hl-label">{{ m.label }}</span>
    </div>
  </div>
</template>

<style scoped>
.highlights {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
  margin-bottom: 16px;
}
.hl-card {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 12px 16px;
  background: var(--bg-surface);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-md);
  position: relative;
  overflow: hidden;
}
.hl-card::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
}
.hl-blue::before {
  background: var(--brand-primary);
}
.hl-teal::before {
  background: var(--gits-teal-500, #12a7a0);
}
.hl-amber::before {
  background: var(--gits-amber-400, #f2b84b);
}
.hl-value {
  font-size: 22px;
  font-weight: 700;
  color: var(--gits-navy-800, #0b2e4f);
  line-height: 1.1;
}
.hl-label {
  font-size: 12px;
  color: var(--text-tertiary);
}
@media (max-width: 900px) {
  .highlights {
    grid-template-columns: 1fr 1fr;
  }
}
</style>
