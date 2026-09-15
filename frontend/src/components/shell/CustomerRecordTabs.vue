<script setup lang="ts">
import { RouterLink, useRoute } from 'vue-router'

const props = defineProps<{
  customerId: string
}>()

const route = useRoute()
</script>

<template>
  <nav class="slice-tabs" data-testid="customer-slice-tabs" aria-label="客户记录页签">
    <RouterLink
      :to="{ name: 'CustomerOperatingView', params: { id: props.customerId } }"
      data-testid="tab-p04"
      :class="{ active: route.name === 'CustomerOperatingView' }"
    >
      经营总览
    </RouterLink>
    <RouterLink
      :to="{ name: 'CustomerGroupView', params: { id: props.customerId } }"
      data-testid="tab-p05"
      :class="{ active: route.name === 'CustomerGroupView' }"
    >
      集团关系
    </RouterLink>
    <RouterLink
      :to="{ name: 'CustomerFundsView', params: { id: props.customerId } }"
      data-testid="tab-p06"
      :class="{ active: route.name === 'CustomerFundsView' }"
    >
      业务资金
    </RouterLink>
    <RouterLink
      :to="{ name: 'CustomerPartiesView', params: { id: props.customerId } }"
      data-testid="tab-p07"
      :class="{ active: route.name === 'CustomerPartiesView' }"
    >
      关系人情报
    </RouterLink>
  </nav>
</template>

<style scoped>
.slice-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-bottom: 16px;
  border-bottom: 1px solid var(--gits-line);
}
.slice-tabs a {
  height: 36px;
  padding: 0 14px;
  display: inline-flex;
  align-items: center;
  color: var(--gits-muted);
  text-decoration: none;
  font-size: 13px;
  font-weight: 600;
  border-bottom: 2px solid transparent;
}
.slice-tabs a.active,
.slice-tabs a.router-link-exact-active {
  color: var(--gits-blue-600);
  border-bottom-color: var(--gits-blue-600);
}
</style>
