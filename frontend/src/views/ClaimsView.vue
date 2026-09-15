<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import ObjectHeader from '../components/shell/ObjectHeader.vue'
import PageState from '../components/shell/PageState.vue'
import DisabledAction from '../components/shell/DisabledAction.vue'
import { listClaims, type Claim } from '../api/engagement'
import { fetchEvidenceVersions, type EvidenceVersion } from '../api/v11'
import { deriveResourceStatus } from '../composables/useResourceStatus'
import { usePageReferenceStore } from '../stores/pageReference'

const PAGE_ID = 'P37'
const OBJECT_TYPE = 'Claim'

const CLAIM_UNLOCK = '待证据登记/冲突处置写 API 纳入合同后由独立 Loop 启用'

const pageRefs = usePageReferenceStore()
const claims = ref<Claim[]>([])
const versionsByEvidence = ref<Record<string, EvidenceVersion[]>>({})
const loading = ref(true)
const error = ref('')
const requested = ref(false)

const status = computed(() =>
  deriveResourceStatus({
    loading: loading.value,
    error: error.value,
    hasData: requested.value,
    requested: requested.value,
  }),
)

function persistReference() {
  pageRefs.capture(PAGE_ID, {
    objectType: OBJECT_TYPE,
    viewId: 'claim_evidence_center',
    scrollAnchor: typeof window !== 'undefined' ? window.scrollY : 0,
  })
}

function evidenceIdsOf(claim: Claim): string[] {
  const ids: string[] = []
  if (claim.evidenceRef) {
    ids.push(claim.evidenceRef)
  }
  if (claim.evidenceRefs?.length) {
    ids.push(...claim.evidenceRefs)
  }
  return [...new Set(ids.filter(Boolean))]
}

async function load() {
  loading.value = true
  error.value = ''
  requested.value = true
  versionsByEvidence.value = {}
  try {
    const rows = await listClaims()
    claims.value = rows
    const evidenceIds = [...new Set(rows.flatMap(evidenceIdsOf))]
    const pairs = await Promise.all(
      evidenceIds.map(async id => {
        const versions = await fetchEvidenceVersions(id)
        return [id, versions] as const
      }),
    )
    versionsByEvidence.value = Object.fromEntries(pairs)
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : '无法加载 Claim'
    claims.value = []
  } finally {
    loading.value = false
  }
}

onMounted(load)
onBeforeUnmount(persistReference)
</script>

<template>
  <div class="claims" data-testid="p37-claims">
    <ObjectHeader
      :page-id="PAGE_ID"
      :object-type="OBJECT_TYPE"
      object-status="只读"
      title="Claim / Evidence 中心"
    />
    <div class="toolbar">
      <DisabledAction
        label="登记证据"
        :disabled="true"
        reason="无证据登记写 API，禁止从前端登记证据"
        :unlock-path="CLAIM_UNLOCK"
      />
      <DisabledAction
        label="处理冲突"
        :disabled="true"
        reason="无冲突处置写 API，禁止从前端处理冲突"
        :unlock-path="CLAIM_UNLOCK"
      />
    </div>
    <p class="hint">只读消费 listClaims。主键为 claimId。有 evidenceRef / evidenceRefs 时才查询证据版本。</p>
    <PageState :status="status" :error="error" idle-description="尚未加载 Claim" @retry="load">
      <p v-if="!claims.length" class="empty" data-testid="p37-empty">暂无 Claim。</p>
      <ul v-else class="claim-list" data-testid="p37-claim-list">
        <li v-for="claim in claims" :key="claim.claimId" class="claim-item" :data-testid="`p37-claim-${claim.claimId}`">
          <div class="claim-head">
            <span class="claim-id">{{ claim.claimId }}</span>
            <span>{{ claim.claimType }}</span>
            <span>{{ claim.status }}</span>
          </div>
          <p class="content">{{ claim.content }}</p>
          <div v-for="evidenceId in evidenceIdsOf(claim)" :key="evidenceId" class="evidence">
            <p class="evidence-id">证据 {{ evidenceId }}</p>
            <ul v-if="versionsByEvidence[evidenceId]?.length" class="versions">
              <li v-for="version in versionsByEvidence[evidenceId]" :key="version.versionId">
                v{{ version.version }} · {{ version.versionId }}
              </li>
            </ul>
          </div>
        </li>
      </ul>
    </PageState>
  </div>
</template>

<style scoped>
.toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: flex-start;
  margin-bottom: 16px;
}
.hint,
.empty {
  color: var(--text-tertiary);
  font-size: 13px;
}
.claim-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.claim-item {
  padding: 12px 14px;
  background: var(--bg-surface);
  border: 1px solid var(--border-light);
  border-radius: 8px;
}
.claim-head {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  font-size: 13px;
}
.claim-id {
  font-family: ui-monospace, monospace;
  font-weight: 600;
}
.content {
  margin: 8px 0 0;
  font-size: 14px;
}
.evidence {
  margin-top: 8px;
  font-size: 12px;
  color: var(--text-secondary);
}
.versions {
  margin: 4px 0 0;
  padding-left: 18px;
}
</style>
