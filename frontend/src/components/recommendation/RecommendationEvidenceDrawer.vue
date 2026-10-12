<script setup lang="ts">
import { computed } from 'vue'
import {
  NDrawer,
  NDrawerContent,
  NDescriptions,
  NDescriptionsItem,
  NTag,
  NEmpty,
  NAlert,
  NDivider,
} from 'naive-ui'
import {
  ELIGIBILITY_LABELS,
  RULE_RESULT_LABELS,
  type EligibilityResult,
  type EligibilityStatus,
  type EvidenceBundle,
  type CustomerFactSource,
  type ExclusionReason,
  type RuleResultStatus,
} from './types'

/**
 * 推荐证据反查抽屉（只读）。
 *
 * 状态块：CANDIDATE / FROZEN=NO / IMPLEMENTED=NO（WP5-3）。
 *
 * 从任一候选（产品/理由）反查证据链：产品版本、规则命中（ruleId/ruleVersion/reasonCode）、
 * 客户事实来源、EvidenceBundle（skillId/版本/哈希/traceId）、排除原因。
 * 无权查看客户事实来源原文时，只显示“证据存在 + 权限说明”，不泄露原文。
 */
const props = defineProps<{
  show: boolean
  candidate: EligibilityResult | null
  evidenceBundle: EvidenceBundle | null
  factSources: CustomerFactSource[]
  exclusionReasons: ExclusionReason[]
}>()

const emit = defineEmits<{
  (e: 'update:show', value: boolean): void
}>()

const eligibilityLabel = computed(() => {
  if (!props.candidate) return ''
  return ELIGIBILITY_LABELS[props.candidate.eligibility as EligibilityStatus] || props.candidate.eligibility
})

const eligibilityType = computed(() => {
  switch (props.candidate?.eligibility) {
    case 'ELIGIBLE':
      return 'success'
    case 'INELIGIBLE':
      return 'error'
    case 'UNKNOWN':
      return 'warning'
    case 'REVIEW_REQUIRED':
      return 'info'
    default:
      return 'default'
  }
})

function ruleResultType(result: RuleResultStatus) {
  switch (result) {
    case 'PASS':
      return 'success'
    case 'FAIL':
      return 'error'
    case 'UNKNOWN':
      return 'warning'
    case 'REVIEW_REQUIRED':
      return 'info'
    default:
      return 'default'
  }
}

function handleClose() {
  emit('update:show', false)
}
</script>

<template>
  <NDrawer :show="show" :width="480" placement="right" @update:show="handleClose">
    <NDrawerContent title="推荐证据反查" closable>
      <div class="evidence-drawer" data-testid="evidence-drawer">
        <NAlert
          type="info"
          title="只读反查"
          style="margin-bottom: 12px"
        >
          本抽屉为只读视图，用于从候选/理由反查证据链；不触发任何生成或决策。
        </NAlert>

        <NAlert v-if="!candidate" type="warning" title="未选择候选或理由" />

        <template v-else>
          <!-- 产品版本 -->
          <NDivider title-placement="left">产品版本</NDivider>
          <NDescriptions bordered :column="1" label-placement="left" size="small">
            <NDescriptionsItem label="产品ID" data-testid="product-id">
              {{ candidate.productId }}
            </NDescriptionsItem>
            <NDescriptionsItem label="产品版本" data-testid="product-version">
              {{ candidate.productVersion }}
            </NDescriptionsItem>
            <NDescriptionsItem label="资格状态" data-testid="eligibility">
              <NTag :type="eligibilityType" size="small">{{ eligibilityLabel }}</NTag>
            </NDescriptionsItem>
          </NDescriptions>

          <!-- 规则命中 -->
          <NDivider title-placement="left">规则命中</NDivider>
          <NEmpty
            v-if="!candidate.ruleResults || candidate.ruleResults.length === 0"
            description="无规则命中"
            data-testid="rule-empty"
          />
          <div v-else class="rule-list">
            <div
              v-for="rule in candidate.ruleResults"
              :key="rule.ruleId"
              class="rule-item"
              data-testid="rule-hit"
            >
              <div class="rule-line">
                <span class="rule-id" data-testid="rule-id">{{ rule.ruleId }}</span>
                <span class="rule-version" data-testid="rule-version">v{{ rule.ruleVersion }}</span>
                <NTag :type="ruleResultType(rule.result)" size="small">
                  {{ RULE_RESULT_LABELS[rule.result as RuleResultStatus] || rule.result }}
                </NTag>
              </div>
              <div class="reason-code" data-testid="reason-code">
                原因码：{{ rule.reasonCode }}
              </div>
              <div v-if="rule.inputFactRefs && rule.inputFactRefs.length" class="fact-refs">
                事实引用：{{ rule.inputFactRefs.join(', ') }}
              </div>
            </div>
          </div>

          <!-- 客户事实来源 -->
          <NDivider title-placement="left">客户事实来源</NDivider>
          <NEmpty
            v-if="factSources.length === 0"
            description="无事实来源"
            data-testid="fact-empty"
          />
          <div v-else class="fact-list">
            <div
              v-for="fact in factSources"
              :key="fact.ref"
              class="fact-item"
              data-testid="fact-source"
            >
              <div class="fact-ref" data-testid="fact-ref">{{ fact.ref }}</div>
              <div v-if="fact.canViewSource" class="fact-content" data-testid="fact-content">
                {{ fact.content || '-' }}
              </div>
              <div v-else class="fact-denied" data-testid="fact-denied">
                <span class="denied-badge">证据存在</span>
                <span class="permission-note">您无权查看该来源原文，如需核实请发起专家协同任务。</span>
              </div>
            </div>
          </div>

          <!-- EvidenceBundle -->
          <NDivider title-placement="left">证据包（EvidenceBundle）</NDivider>
          <NEmpty v-if="!evidenceBundle" description="无证据包" data-testid="bundle-empty" />
          <NDescriptions v-else bordered :column="1" label-placement="left" size="small">
            <NDescriptionsItem label="Skill ID" data-testid="bundle-skill-id">
              {{ evidenceBundle.skillId }}
            </NDescriptionsItem>
            <NDescriptionsItem label="Skill 版本" data-testid="bundle-skill-version">
              {{ evidenceBundle.skillVersion }}
            </NDescriptionsItem>
            <NDescriptionsItem label="内容哈希" data-testid="bundle-content-hash">
              {{ evidenceBundle.contentHash }}
            </NDescriptionsItem>
            <NDescriptionsItem label="Trace ID" data-testid="bundle-trace-id">
              {{ evidenceBundle.traceId }}
            </NDescriptionsItem>
            <NDescriptionsItem
              v-if="evidenceBundle.evidenceBundleId"
              label="证据包 ID"
              data-testid="bundle-id"
            >
              {{ evidenceBundle.evidenceBundleId }}
            </NDescriptionsItem>
          </NDescriptions>

          <!-- 排除原因 -->
          <NDivider title-placement="left">排除原因</NDivider>
          <NEmpty
            v-if="exclusionReasons.length === 0"
            description="无排除原因"
            data-testid="exclusion-empty"
          />
          <div v-else class="exclusion-list">
            <div
              v-for="(reason, idx) in exclusionReasons"
              :key="`${reason.reasonCode || 'reason'}-${idx}`"
              class="exclusion-item"
              data-testid="exclusion-reason"
            >
              <NTag v-if="reason.reasonCode" size="small" type="error">
                {{ reason.reasonCode }}
              </NTag>
              <span class="exclusion-text">{{ reason.text }}</span>
            </div>
          </div>
        </template>
      </div>
    </NDrawerContent>
  </NDrawer>
</template>

<style scoped>
.evidence-drawer {
  padding: 8px 4px;
  font-size: 14px;
  color: #333;
}

.rule-list,
.fact-list,
.exclusion-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.rule-item,
.fact-item,
.exclusion-item {
  padding: 10px 12px;
  border: 1px solid #e8e8e8;
  border-radius: 6px;
  background: #fff;
}

.rule-line {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.rule-id {
  font-weight: 600;
  color: #003366;
}

.rule-version {
  font-size: 12px;
  color: #8c8c8c;
}

.reason-code {
  font-size: 13px;
  color: #cf1322;
}

.fact-refs {
  margin-top: 4px;
  font-size: 12px;
  color: #8c8c8c;
}

.fact-ref {
  font-weight: 600;
  color: #003366;
  margin-bottom: 4px;
}

.fact-content {
  font-size: 13px;
  color: #333;
  white-space: pre-wrap;
  word-break: break-all;
}

.fact-denied {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.denied-badge {
  align-self: flex-start;
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 4px;
  background: #f5f5f5;
  color: #999;
}

.permission-note {
  font-size: 12px;
  color: #8c8c8c;
}

.exclusion-item {
  display: flex;
  align-items: flex-start;
  gap: 8px;
}

.exclusion-text {
  font-size: 13px;
  color: #333;
}
</style>
