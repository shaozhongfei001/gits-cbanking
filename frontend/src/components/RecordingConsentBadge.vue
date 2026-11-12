<template>
  <span class="consent-badge" :class="`consent-${statusClass}`">
    {{ statusLabel }}
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { RecordingConsentStatus } from '../api/v11'
import { RECORDING_CONSENT_STATUS_LABELS } from '../api/v11'

const props = defineProps<{
  status: RecordingConsentStatus
}>()

const statusLabel = computed(() =>
  RECORDING_CONSENT_STATUS_LABELS[props.status] || props.status
)
const statusClass = computed(() => props.status.toLowerCase())
</script>

<style scoped>
.consent-badge {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: 500;
}
.consent-granted { background: #eef9f6; color: #18a890; }
.consent-denied { background: #fdf3f1; color: #c0392b; }
.consent-pending { background: #fff8ec; color: #f39c12; }
.consent-revoked { background: #f7f9fd; color: #999; }
</style>
