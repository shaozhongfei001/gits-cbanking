<script setup lang="ts">
/** 右侧门禁面板：下一步与门禁 / 业务规则 / 异常降级 / 契约使用 + 动作插槽。 */
defineProps<{
  nextStep: string
  businessRule?: string
  exception?: string
  contractUsage?: string
}>()
</script>

<template>
  <aside class="guidance-panel" data-testid="guidance-panel">
    <section class="gp-block">
      <h4 class="gp-title">下一步与门禁</h4>
      <p class="gp-next">{{ nextStep }}</p>
    </section>
    <section v-if="businessRule" class="gp-block">
      <h4 class="gp-title">业务规则</h4>
      <p class="gp-text">{{ businessRule }}</p>
    </section>
    <section v-if="exception" class="gp-block">
      <h4 class="gp-title">异常 / 降级</h4>
      <p class="gp-text">{{ exception }}</p>
    </section>
    <section v-if="contractUsage" class="gp-block">
      <h4 class="gp-title">契约使用</h4>
      <p class="gp-mono">{{ contractUsage }}</p>
    </section>
    <div class="gp-actions">
      <slot />
    </div>
  </aside>
</template>

<style scoped>
.guidance-panel {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 16px;
  background: var(--bg-surface);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-md);
  position: sticky;
  top: 16px;
}
.gp-block {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.gp-title {
  margin: 0;
  font-size: 12px;
  font-weight: 700;
  color: var(--gits-navy-800, #0b2e4f);
  letter-spacing: 0.02em;
}
.gp-next {
  margin: 0;
  font-size: 13px;
  color: var(--brand-primary);
  font-weight: 500;
}
.gp-text {
  margin: 0;
  font-size: 12px;
  color: var(--text-secondary);
  line-height: 1.5;
}
.gp-mono {
  margin: 0;
  font-size: 11px;
  color: var(--text-tertiary);
  font-family: var(--font-mono);
  line-height: 1.5;
}
.gp-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding-top: 4px;
}
</style>
