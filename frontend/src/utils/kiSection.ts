/** DKWS R1 `data.sections` 对位：按 heading 中的 KI 编号或稳定中文标题取正文。 */

export interface SkillSection {
  heading?: string
  content?: string
}

const ALIASES: Record<string, string[]> = {
  'KI-009': ['KI-009', '企业客户基本信息', '客户概况', '客户基本信息'],
  'KI-FRONT-001': ['KI-FRONT-001', '供应链图谱', '公司供应链'],
  'KI-FRONT-002': ['KI-FRONT-002', '八维', '产业链八维'],
  'KI-FRONT-003': ['KI-FRONT-003', '行内变动', '变动行为'],
  'KI-FRONT-004': ['KI-FRONT-004', '事实承诺', '沟通话术', '承诺事项'],
  'KI-FRONT-005': ['KI-FRONT-005', 'KYC'],
  'KI-FRONT-006': ['KI-FRONT-006', '产品候选', '产品组合'],
}

export function sectionContent(sections: SkillSection[] | undefined, kiId: string): string {
  if (!sections?.length) {
    return ''
  }
  const aliases = ALIASES[kiId] ?? [kiId]
  for (const section of sections) {
    const heading = section.heading || ''
    const content = (section.content || '').trim()
    if (!content) {
      continue
    }
    if (aliases.some((alias) => heading.includes(alias))) {
      return content
    }
  }
  return ''
}
