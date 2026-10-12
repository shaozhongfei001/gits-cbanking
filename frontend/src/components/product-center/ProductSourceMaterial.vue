<script setup lang="ts">
/**
 * 附：产品原始材料（PC1.5 补丁）。
 *
 * 背景（为什么需要它）：产品中心的八个章节要求「内容来自受控知识契约」，
 * 而当前 KERT 尚未产出已发布 Release，若只呈现八章占位，页面在**业务信息量上会低于**
 * 既有 P38「产品解读与知识」页（该页直接铺产品卡原文全文）。
 * 产品卡原文是**真实权威材料**，不属于"示意数据"，因此按原始材料区只读呈现，
 * 并与受控知识版本严格区分。
 *
 * 硬约束：
 * - 来源为既有合同 CTR-PK-INT-001（`/api/v1/product-knowledge/cards/{id}`），只读复用，不改 P38 代码；
 * - 只呈现**相对路径**（源文件标识），不拼接、不暴露本机绝对路径（P38 现状缺陷 F-P38-01）；
 * - 必须常驻警示：未受控知识版本、仅供内部阅读、不得对客引用、条款口径以受控解读为准。
 */
import { ref, watch } from 'vue'
import { NCollapse, NCollapseItem, NSpin } from 'naive-ui'
import { fetchProductCardDetail, type ProductCardDetail } from '../../api/productKnowledge'

const props = defineProps<{ productId: string }>()

const detail = ref<ProductCardDetail | null>(null)
const loading = ref(false)
const error = ref<string | null>(null)

async function load(productId: string) {
  if (!productId) {
    return
  }
  loading.value = true
  error.value = null
  detail.value = null
  try {
    detail.value = await fetchProductCardDetail(productId)
  } catch {
    error.value = '该产品暂无原始材料可供呈现'
  } finally {
    loading.value = false
  }
}

watch(() => props.productId, load, { immediate: true })
</script>

<template>
  <section class="pc-source" data-testid="pc-source-material">
    <header class="pc-source-head">
      <h2 class="pc-source-title">附：产品原始材料</h2>
      <span v-if="detail" class="pc-source-file" data-testid="pc-source-file">{{ detail.sourceFile }}</span>
    </header>

    <p class="pc-source-warning" data-testid="pc-source-warning">
      <strong>模拟（DEMO）数据，非真实银行规则。</strong>
      以下内容来自演示用产品卡：尚未形成受控知识版本、未经审核与证据绑定；
      依 CTR-PK-TAX-001 登记（D-4），其权威材料目录为空、源材料全部为 PENDING_SOURCE、
      内容哈希为占位值。仅供内部阅读参考，<strong>不得对客引用</strong>，
      不得进入生产正式版本；对客口径以受控产品解读与最终批复、协议为准。
    </p>

    <p v-if="loading" class="pc-source-state"><NSpin size="small" /> 原始材料加载中…</p>
    <p v-else-if="error" class="pc-source-state" data-testid="pc-source-error">{{ error }}</p>
    <p v-else-if="!detail || detail.sections.length === 0" class="pc-source-state" data-testid="pc-source-empty">
      该产品卡未包含可呈现的正文章节。
    </p>

    <NCollapse v-else :default-expanded-names="detail.sections[0] ? [detail.sections[0].title] : []">
      <NCollapseItem
        v-for="section in detail.sections"
        :key="section.title"
        :title="section.title"
        :name="section.title"
        data-testid="pc-source-section"
      >
        <pre class="pc-source-content">{{ section.content }}</pre>
      </NCollapseItem>
    </NCollapse>
  </section>
</template>

<style scoped>
.pc-source {
  padding: 14px 16px;
  background: var(--bg-surface, #fff);
  border: 1px dashed var(--border-strong, #b0bac9);
  border-radius: 13px;
}

.pc-source-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 10px;
}

.pc-source-title {
  margin: 0;
  font-size: 15px;
  font-weight: 700;
  color: var(--gits-navy-800);
}

.pc-source-file {
  font-size: 11px;
  color: var(--gits-muted);
  word-break: break-all;
}

.pc-source-warning {
  margin: 8px 0 10px;
  padding: 8px 10px;
  font-size: 12px;
  line-height: 1.6;
  color: var(--color-warning, #7a4b00);
  background: var(--color-warning-bg, #fff6e5);
  border-left: 3px solid var(--gits-amber-400);
  border-radius: 8px;
}

.pc-source-state {
  margin: 0;
  font-size: 12px;
  color: var(--gits-muted);
}

.pc-source-content {
  margin: 0;
  white-space: pre-wrap;
  font-size: 13px;
  line-height: 1.7;
  color: var(--gits-text);
  font-family: inherit;
}
</style>
