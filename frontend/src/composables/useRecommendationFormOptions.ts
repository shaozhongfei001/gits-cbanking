import { ref, computed } from 'vue'
import { fetchCustomers, type Customer } from '../api/engagement'
import { fetchOpportunities, fetchRecentProductKnowledge, type Opportunity, type ProductKnowledgeVersion } from '../api/v11'

/** 下拉选项统一结构（对齐 Naive UI NSelect options 约定）。 */
export interface SelectOption {
  label: string
  value: string
  description?: string
}

/** 需求（Need）候选项 —— 派生自商机，非后端 NeedVersion 权威对象。 */
export interface NeedCandidate extends SelectOption {
  customerId: string
  operatingCaseId?: string
}

const RM_ID_ALL = 'ALL'
const PRODUCT_KNOWLEDGE_LIMIT = 50

/** 产品域中文标签。键为后端 product_knowledge_version.category 取值。 */
export const PRODUCT_DOMAIN_LABELS: Record<string, string> = {
  FINANCING: '融资',
  SETTLEMENT: '结算',
  CASH_MANAGEMENT: '现金管理',
  TRADE_FINANCE: '贸易金融',
  CROSS_BORDER: '跨境金融',
  INVESTMENT_BANKING: '投资银行',
}

function shortId(id: string): string {
  return id.length > 8 ? `${id.slice(0, 8)}…` : id
}

/**
 * 产品推荐工作区表单的选项数据源。
 *
 * 数据来源均为后端真实端点，不使用本地假数据：
 * - 客户：GET /api/v1/engagement/customer?rmId=ALL
 * - 经营案例 / 商机：GET /api/v1/opportunities
 * - 需求候选：由商机派生（后端暂无 NeedVersion 列表端点，标记为派生项）
 * - 产品域：GET /api/v1/product-knowledge/recent 的 category 去重
 */
export function useRecommendationFormOptions() {
  const customers = ref<Customer[]>([])
  const opportunities = ref<Opportunity[]>([])
  const productKnowledge = ref<ProductKnowledgeVersion[]>([])

  const loading = ref(false)
  const loaded = ref(false)
  const error = ref('')

  const customerOptions = computed<SelectOption[]>(() =>
    customers.value.map((c) => ({
      label: `${c.customerName}（${c.customerId}）`,
      value: c.customerId,
      description: [c.industry, c.customerTier].filter(Boolean).join(' · '),
    })),
  )

  /** 经营案例选项：按 operatingCaseId 去重，标签取该案例下首个商机的描述。 */
  const operatingCaseOptions = computed<SelectOption[]>(() => {
    const seen = new Map<string, Opportunity>()
    for (const opp of opportunities.value) {
      const caseId = opp.operatingCaseId
      if (caseId && !seen.has(caseId)) {
        seen.set(caseId, opp)
      }
    }
    return Array.from(seen.entries()).map(([caseId, opp]) => ({
      label: opp.description ? `${opp.description}（案例 ${shortId(caseId)}）` : `经营案例 ${shortId(caseId)}`,
      value: caseId,
      description: opp.customerId,
    }))
  })

  /** 需求候选：由商机派生，label 明确标注派生来源，避免与权威 NeedVersion 混淆。 */
  const needCandidates = computed<NeedCandidate[]>(() =>
    opportunities.value.map((opp) => ({
      label: opp.productName
        ? `${opp.productName} — ${opp.description ?? ''}`.trim()
        : (opp.description ?? opp.opportunityId),
      value: opp.opportunityId,
      description: `派生自商机 ${shortId(opp.opportunityId)}`,
      customerId: opp.customerId,
      operatingCaseId: opp.operatingCaseId,
    })),
  )

  /** 产品域选项：取产品知识版本的 category 去重，label 附带该域下产品数量。 */
  const productDomainOptions = computed<SelectOption[]>(() => {
    const grouped = new Map<string, string[]>()
    for (const pk of productKnowledge.value) {
      const domain = pk.category
      if (!domain) continue
      const names = grouped.get(domain) ?? []
      names.push(pk.productName)
      grouped.set(domain, names)
    }
    return Array.from(grouped.entries()).map(([domain, names]) => ({
      label: `${PRODUCT_DOMAIN_LABELS[domain] ?? domain}（${names.length} 个产品）`,
      value: domain,
      description: names.slice(0, 3).join('、'),
    }))
  })

  /** 按客户过滤经营案例，供客户切换时联动。 */
  function operatingCasesOf(customerId: string): SelectOption[] {
    return operatingCaseOptions.value.filter((opt) => opt.description === customerId)
  }

  /** 按客户过滤需求候选，供客户切换时联动。 */
  function needCandidatesOf(customerId: string): NeedCandidate[] {
    return needCandidates.value.filter((n) => n.customerId === customerId)
  }

  async function load(): Promise<void> {
    loading.value = true
    error.value = ''
    try {
      const [customerList, opportunityList, productKnowledgeList] = await Promise.all([
        fetchCustomers(RM_ID_ALL),
        fetchOpportunities({}),
        fetchRecentProductKnowledge(PRODUCT_KNOWLEDGE_LIMIT),
      ])
      customers.value = Array.isArray(customerList) ? customerList : []
      opportunities.value = Array.isArray(opportunityList) ? opportunityList : []
      productKnowledge.value = Array.isArray(productKnowledgeList) ? productKnowledgeList : []
      loaded.value = true
    } catch (e) {
      error.value = e instanceof Error ? e.message : '加载表单选项失败'
    } finally {
      loading.value = false
    }
  }

  return {
    loading,
    loaded,
    error,
    customerOptions,
    operatingCaseOptions,
    needCandidates,
    productDomainOptions,
    operatingCasesOf,
    needCandidatesOf,
    load,
  }
}
