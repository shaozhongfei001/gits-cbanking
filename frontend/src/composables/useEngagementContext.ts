import { computed } from 'vue'
import { useRoute } from 'vue-router'

/** Query/path context for P11–P19. Not a new API field. */
export function useEngagementContext() {
  const route = useRoute()
  const customerId = computed(() => String(route.query.customerId || ''))
  const journeyId = computed(() => {
    const fromQuery = String(route.query.journeyId || '')
    if (fromQuery) {
      return fromQuery
    }
    return typeof route.params.id === 'string' ? route.params.id : ''
  })
  const operatingCaseId = computed(() => String(route.query.operatingCaseId || ''))
  const rmId = computed(() => String(route.query.rmId || ''))
  return { customerId, journeyId, operatingCaseId, rmId }
}

export function engagementQuery(ctx: {
  customerId?: string
  journeyId?: string
  operatingCaseId?: string
  rmId?: string
}): Record<string, string> {
  const query: Record<string, string> = {}
  if (ctx.customerId) query.customerId = ctx.customerId
  if (ctx.journeyId) query.journeyId = ctx.journeyId
  if (ctx.operatingCaseId) query.operatingCaseId = ctx.operatingCaseId
  if (ctx.rmId) query.rmId = ctx.rmId
  return query
}
