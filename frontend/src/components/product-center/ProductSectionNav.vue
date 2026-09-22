<script setup lang="ts">
/**
 * 章节导航（需求 02 §6-4 / PI-FR-027、028、029）。
 *
 * 要求：吸顶、滚动同步激活、URL 深链接（hash）、键盘可操作。
 * 位置恢复（PI-FR-029 的持久化部分）由 PC2 接入受控存储后启用。
 */
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { PRODUCT_SECTIONS, type ProductSectionKey } from './sections'

const activeKey = ref<ProductSectionKey>('OVERVIEW')
let observer: IntersectionObserver | null = null

function onVisible(entries: IntersectionObserverEntry[]) {
  const visible = entries
    .filter((entry) => entry.isIntersecting)
    .sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top)
  const key = visible[0]?.target.getAttribute('data-section-key') as ProductSectionKey | null
  if (key) {
    activeKey.value = key
  }
}

onMounted(() => {
  const targets = PRODUCT_SECTIONS
    .map((section) => document.getElementById(section.anchor))
    .filter((element): element is HTMLElement => element !== null)
  if (targets.length === 0 || typeof IntersectionObserver === 'undefined') {
    return
  }
  observer = new IntersectionObserver(onVisible, { rootMargin: '-96px 0px -70% 0px', threshold: [0, 1] })
  targets.forEach((target) => observer?.observe(target))
})

onBeforeUnmount(() => observer?.disconnect())
</script>

<template>
  <nav class="pc-secnav" data-testid="pc-section-nav" aria-label="章节导航">
    <a
      v-for="section in PRODUCT_SECTIONS"
      :key="section.key"
      class="pc-secnav-link"
      :class="{ 'is-active': section.key === activeKey }"
      :href="`#${section.anchor}`"
      :data-section-key="section.key"
      data-testid="pc-section-link"
    >
      {{ section.title }}
    </a>
  </nav>
</template>

<style scoped>
.pc-secnav {
  position: sticky;
  top: 49px;
  z-index: 10;
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  padding: 8px 10px;
  background: var(--bg-surface, #fff);
  border: 1px solid var(--border-light, #d8e2ec);
  border-radius: 12px;
}

.pc-secnav-link {
  padding: 5px 10px;
  font-size: 12.5px;
  color: var(--gits-muted);
  text-decoration: none;
  border-radius: 8px;
}

.pc-secnav-link:hover {
  background: var(--bg-hover, #eff3fb);
  color: var(--gits-text);
}

.pc-secnav-link:focus-visible {
  outline: 2px solid var(--gits-blue-600);
  outline-offset: 1px;
}

.pc-secnav-link.is-active {
  color: var(--gits-blue-600);
  background: var(--brand-primary-lighter, #eaf4fe);
  font-weight: 600;
}
</style>
