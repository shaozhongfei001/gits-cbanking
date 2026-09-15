import { describe, expect, it } from 'vitest'
import { sectionContent } from '../kiSection'

describe('sectionContent', () => {
  const sections = [
    { heading: 'KI-009 企业客户基本信息', content: '行业：制造' },
    { heading: '产业链八维研判', content: '中游集成' },
    { heading: '客户概况', content: '不应抢 KI-009，因已有编号节' },
  ]

  it('prefers KI id in heading', () => {
    expect(sectionContent(sections, 'KI-009')).toBe('行业：制造')
  })

  it('matches stable Chinese title when KI id absent', () => {
    expect(sectionContent(sections, 'KI-FRONT-002')).toBe('中游集成')
  })

  it('returns empty when DKWS omitted the KI', () => {
    expect(sectionContent(sections, 'KI-FRONT-005')).toBe('')
    expect(sectionContent([], 'KI-009')).toBe('')
  })
})
