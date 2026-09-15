<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink, useRoute } from 'vue-router'

const route = useRoute()

const onSignals = computed(() => route.path.startsWith('/signals'))
const onInteractions = computed(() =>
  route.path === '/engagements' || route.path.startsWith('/engagements/'),
)
const onJourney = computed(() =>
  !onSignals.value
  && !onInteractions.value
  && (
    route.path.startsWith('/engagement')
    || route.path.startsWith('/in-meeting')
    || route.path.startsWith('/journeys')
  ),
)
</script>

<template>
  <nav class="slice-tabs" data-testid="signals-domain-tabs" aria-label="信号与互动域页签">
    <RouterLink
      to="/engagement"
      data-testid="signals-tab-p11"
      :class="{ active: onJourney }"
    >
      经营旅程
    </RouterLink>
    <RouterLink
      to="/signals"
      data-testid="signals-tab-p08"
      :class="{ active: onSignals }"
    >
      经营信号
    </RouterLink>
    <RouterLink
      to="/engagements"
      data-testid="signals-tab-p10"
      :class="{ active: onInteractions }"
    >
      互动对象
    </RouterLink>
  </nav>
</template>

<style scoped>
.slice-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-bottom: 16px;
  border-bottom: 1px solid var(--gits-line, #d9e2ec);
}
.slice-tabs a {
  height: 36px;
  padding: 0 14px;
  display: inline-flex;
  align-items: center;
  color: var(--gits-muted, #5b708b);
  text-decoration: none;
  font-size: 13px;
  font-weight: 600;
  border-bottom: 2px solid transparent;
}
.slice-tabs a.active {
  color: var(--gits-blue-600, #1976d2);
  border-bottom-color: var(--gits-blue-600, #1976d2);
}
</style>
