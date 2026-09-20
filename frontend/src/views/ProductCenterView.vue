<script setup lang="ts">
/**
 * 企业金融产品中心 — PC0（基线与契约）骨架占位页。
 *
 * 边界（REQ-PI-01 / 需求包 01 §3.2）：
 * - 以产品为主语，不读取客户画像、账户、交易、授信、商机数据；
 * - 不计算客户适配分，不输出推荐 / 授信结论；
 * - PC0 仅交付路由、菜单与静态骨架，不发起任何业务数据请求；
 *   产品目录、首屏、八章正文与右侧知识治理栏由 PC1–PC5 按合同分批交付。
 */
import { NAlert, NCard, NTag } from 'naive-ui'

/** 八个固定章节：顺序为受控契约，PC1 起改由产品中心合同配置驱动（PI-FR-026）。 */
const SECTION_KEYS = [
  '60 秒读懂',
  '核心条款',
  '适用边界',
  '办理流程',
  '申请材料',
  '价格与协议',
  '同类产品比较',
  '常见问题',
] as const
</script>

<template>
  <div class="product-center" data-testid="product-center-shell">
    <n-card :bordered="true" class="pc-hero" data-testid="product-center-hero">
      <template #header>
        <span class="pc-title">企业金融产品中心</span>
      </template>
      <template #header-extra>
        <n-tag size="small" :bordered="true">PC0 骨架</n-tag>
      </template>
      <p class="pc-sub">
        产品目录 → 选择产品 → 阅读客观产品解读 → 条款 / 流程 / 材料 / 价格 / 协议 / 比较 / 证据 →
        受控产品知识版本 → 供客户体检与受控推荐按版本引用。
      </p>
      <n-alert type="info" :show-icon="true" class="pc-note" data-testid="product-center-skeleton-note">
        本页为 PC0 交付的路由与骨架占位：左侧产品目录、产品首屏、八个章节正文与右侧知识治理栏
        将按 CTR-PK-CENTER-* 合同分批交付；当前不发起任何业务数据请求。
      </n-alert>
    </n-card>

    <n-card
      :bordered="true"
      class="pc-sections"
      data-testid="product-center-sections"
      title="固定章节（PC1 起由合同驱动）"
    >
      <ul class="pc-section-list">
        <li v-for="(section, index) in SECTION_KEYS" :key="section" class="pc-section-item">
          <span class="pc-section-no">{{ String(index + 1).padStart(2, '0') }}</span>
          <span class="pc-section-name">{{ section }}</span>
        </li>
      </ul>
    </n-card>
  </div>
</template>

<style scoped>
.product-center {
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-width: 1700px;
  margin: 0 auto;
  padding: 20px 24px;
}

.pc-title {
  font-size: 20px;
  font-weight: 800;
  color: var(--gits-navy-800);
}

.pc-sub {
  margin: 0;
  font-size: 13px;
  line-height: 1.6;
  color: var(--gits-muted);
}

.pc-note {
  margin-top: 12px;
}

.pc-section-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 8px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.pc-section-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 10px;
  border: 1px solid var(--gits-line);
  border-radius: 8px;
  background: var(--gits-page);
}

.pc-section-no {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 26px;
  height: 20px;
  border-radius: 4px;
  background: #eaf4fc;
  color: var(--gits-blue-600);
  font-size: 11px;
  font-weight: 700;
}

.pc-section-name {
  font-size: 13px;
  color: var(--gits-text);
}
</style>
