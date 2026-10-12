/** 前端 PageReference：仅本地 UI 状态，不是 OpenAPI 字段。 */
export interface PageReference {
  objectType: string
  recordId?: string
  customerId?: string
  workspaceTabId?: string
  viewId?: string
  filter?: string
  sort?: string
  subtab?: string
  scrollAnchor?: number
  draftId?: string
}

export const PAGE_REFERENCE_STORAGE_KEY = 'gits-bank-page-reference'
