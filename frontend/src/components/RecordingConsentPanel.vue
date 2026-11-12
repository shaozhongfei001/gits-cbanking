<template>
  <div class="consent-panel">
    <div class="panel-header">
      <h4>录音授权</h4>
      <RecordingConsentBadge :status="latestConsent?.consentStatus || 'PENDING'" />
    </div>
    <div v-if="consents.length === 0" class="empty-state">暂无录音授权记录</div>
    <div v-else class="consent-timeline">
      <div v-for="c in consents" :key="c.consentId" class="consent-item">
        <div class="consent-info">
          <RecordingConsentBadge :status="c.consentStatus" />
          <span class="consent-method" v-if="c.consentMethod">{{ c.consentMethod }}</span>
        </div>
        <div v-if="c.recordingPurpose" class="consent-purpose">{{ c.recordingPurpose }}</div>
        <div class="consent-time">
          <span v-if="c.grantedAt">授权: {{ formatTime(c.grantedAt) }}</span>
          <span v-if="c.revokedAt">撤销: {{ formatTime(c.revokedAt) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { RecordingConsent } from '../api/v11'
import RecordingConsentBadge from './RecordingConsentBadge.vue'

const props = defineProps<{
  consents: RecordingConsent[]
}>()

const latestConsent = computed(() =>
  props.consents.length > 0 ? props.consents[0] : null
)

function formatTime(ts: string) {
  try { return new Date(ts).toLocaleString('zh-CN') }
  catch { return ts }
}
</script>

<style scoped>
.consent-panel {
  padding: 12px 16px;
  border-radius: 8px;
  border: 1px solid #e8ecf4;
  background: #fff;
}
.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
.panel-header h4 { font-size: 14px; color: #1a2438; margin: 0; }
.empty-state { text-align: center; padding: 16px; color: #7a8899; font-size: 13px; }
.consent-timeline { display: flex; flex-direction: column; gap: 8px; }
.consent-item {
  padding: 8px;
  border-radius: 4px;
  background: #f7f9fd;
}
.consent-info {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}
.consent-method {
  font-size: 12px;
  color: #666;
}
.consent-purpose {
  font-size: 13px;
  color: #333;
  margin-bottom: 4px;
}
.consent-time {
  font-size: 11px;
  color: #999;
  display: flex;
  gap: 12px;
}
</style>
