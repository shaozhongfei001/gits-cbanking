import { describe, expect, it } from 'vitest'
import {
  detectChapterBase,
  draftParagraphs,
  normalizeChapterCode,
  splitProposalDraft,
} from '../proposalDraft'

/**
 * 夹具：SP-20 真实输出（RUN-PROPOSAL-20260925）的标题骨架，
 * 含三处真实异常形态：
 *  - `# 第一章 …`（层级上的章）与 `# CH04 …`（章代码标记）混用；
 *  - CH07 用无编号的 `## 产品推荐与适配` 开启，其子标题改用中文序号 `### 一、…`；
 *  - CH08 用 `## CH08 实施路径`（层级在 ## 但带章代码）。
 */
const REAL_SHAPED_DRAFT = [
  '# 华东精工装备集团有限公司综合金融服务建议书',
  '',
  '> 类型：INITIAL ｜ 阶段：FIRST_CONTACT ｜ runId：RUN-PROPOSAL-20260925055314',
  '',
  '# 第一章 企业概况与经营现状',
  '',
  '## 1.1 基本信息',
  '',
  '华东精工装备集团有限公司为制造业企业，成立于 2005 年 3 月 15 日。',
  '',
  '## 1.4 经营现状',
  '',
  '### 1.4.1 授信使用情况',
  '',
  '公司当前授信总额度为 1.5 亿元人民币。',
  '',
  '### 1.4.2 交易规模',
  '',
  '公司月均交易量为 2.8 亿元人民币。',
  '',
  '## 1.5 小结',
  '',
  '公司成立时间较早。',
  '',
  '# 第二章 行业与竞争分析',
  '',
  '## 2.1 行业定位与产业链位置',
  '',
  '公司处于装备制造业中游。',
  '',
  '# 第三章 财务状况与经营能力分析',
  '',
  '## 3.1 数据可得性说明',
  '',
  '财务汇总数据为空。',
  '',
  '# CH04 风险分析与预警',
  '',
  '## 4.4 操作风险分析',
  '',
  '### 操作风险红旗',
  '',
  '未提供操作风险明细。',
  '',
  '# CH05 客户需求识别与优先级排序',
  '',
  '## 5.4 隐性需求推断（均为推断，标签 C）',
  '',
  '### 推断 1：可能存在增量融资需求',
  '',
  '依据授信使用率推断。',
  '',
  '# CH06 服务方案设计',
  '',
  '## 6.1 设计依据与边界',
  '',
  '本章为方案设计稿。',
  '',
  '## 6.7 审批状态',
  '',
  '尚未进入 G3 审批。',
  '',
  '## 产品推荐与适配',
  '',
  '> 说明：本次上下文未传入 ProductRecommendationProposalVersion。',
  '',
  '### 一、本章定位与数据来源说明',
  '',
  '本章基于客户画像做适配判断。',
  '',
  '### 二、客户基础画像（用于适配判断的输入）',
  '',
  '客户为制造业企业。',
  '',
  '## CH08 实施路径',
  '',
  '### 一、总体节奏',
  '',
  '分三阶段推进。',
  '',
  '### 二、30 天计划（验证期）',
  '',
  '- 完成数据接入。',
  '- 完成试点场景选取。',
].join('\n')

/** 夹具：人工中文序号草稿（无 Markdown 层级）。 */
const ORDINAL_DRAFT = [
  '一、客户概况',
  '华东精工装备集团是一家制造企业。',
  '二、需求分析',
  '客户有资金周转需求。',
].join('\n')

describe('splitProposalDraft · SP-20 真实形态', () => {
  const outline = splitProposalDraft(REAL_SHAPED_DRAFT)

  it('抽出文档标题与引用块元信息', () => {
    expect(outline.docTitle).toBe('华东精工装备集团有限公司综合金融服务建议书')
    expect(outline.meta).toContain('类型：INITIAL')
    expect(outline.meta).toContain('runId：RUN-PROPOSAL-20260925055314')
  })

  it('识别 8 个章（含 CH04 代码标记、无编号 CH07、## 层 CH08）', () => {
    expect(outline.chapters).toHaveLength(8)
    expect(outline.chapters.map(c => c.title)).toEqual([
      '企业概况与经营现状',
      '行业与竞争分析',
      '财务状况与经营能力分析',
      '风险分析与预警',
      '客户需求识别与优先级排序',
      '服务方案设计',
      '产品推荐与适配',
      '实施路径',
    ])
  })

  it('章代码与 citations/unknowns 的 chapterRef 口径一致（CH01…CH08）', () => {
    expect(outline.chapters.map(c => c.code)).toEqual([
      'CH01', 'CH02', 'CH03', 'CH04', 'CH05', 'CH06', 'CH07', 'CH08',
    ])
  })

  it('保留章标记原样（第一章 / CH04 / CH08）', () => {
    expect(outline.chapters[0].marker).toBe('第一章')
    expect(outline.chapters[3].marker).toBe('CH04')
    expect(outline.chapters[7].marker).toBe('CH08')
    expect(outline.chapters[6].marker).toBe('')
  })

  it('把 `### 1.4.1` 归为 1.4 的小节，不另起一章', () => {
    const chapter1 = outline.chapters[0]
    expect(chapter1.sections.map(s => s.heading)).toEqual(['1.1 基本信息', '1.4 经营现状', '1.5 小结'])
    const sec14 = chapter1.sections[1]
    expect(sec14.children.map(s => s.heading)).toEqual(['1.4.1 授信使用情况', '1.4.2 交易规模'])
    expect(sec14.children[0].paragraphs.join('')).toContain('1.5 亿元人民币')
  })

  it('## 产品推荐与适配 独立成章，其 `### 一、` 子标题归入该章', () => {
    const chapter7 = outline.chapters[6]
    expect(chapter7.sections.map(s => s.heading)).toEqual(['一、本章定位与数据来源说明', '二、客户基础画像（用于适配判断的输入）'])
    expect(chapter7.paragraphs.join('')).toContain('ProductRecommendationProposalVersion')
  })

  it('CH08 下 `### 一、总体节奏` 升格为节，列表行原样保留', () => {
    const chapter8 = outline.chapters[7]
    expect(chapter8.sections.map(s => s.heading)).toEqual(['一、总体节奏', '二、30 天计划（验证期）'])
    expect(chapter8.sections[1].paragraphs.join('\n')).toContain('- 完成数据接入。')
  })

  it('不丢内容：所有正文句子都能在结构里找到', () => {
    const flat = JSON.stringify(outline.chapters)
    for (const sentence of [
      '华东精工装备集团有限公司为制造业企业',
      '公司当前授信总额度为 1.5 亿元人民币',
      '公司月均交易量为 2.8 亿元人民币',
      '公司成立时间较早',
      '公司处于装备制造业中游',
      '财务汇总数据为空',
      '未提供操作风险明细',
      '依据授信使用率推断',
      '本章为方案设计稿',
      '尚未进入 G3 审批',
      '本章基于客户画像做适配判断',
      '客户为制造业企业',
      '分三阶段推进',
      '- 完成试点场景选取。',
    ]) {
      expect(flat, `正文丢失：${sentence}`).toContain(sentence)
    }
  })

  it('不把 `1. 近三年营业收入` 这类列表项误判为节或章', () => {
    const draft = ['# 第一章 数据', '', '## 1.1 清单', '', '1. 近三年营业收入；', '2. 流动资产；'].join('\n')
    const result = splitProposalDraft(draft)
    expect(result.chapters).toHaveLength(1)
    expect(result.chapters[0].sections).toHaveLength(1)
    expect(result.chapters[0].sections[0].paragraphs.join('\n')).toContain('1. 近三年营业收入；')
    expect(result.chapters[0].sections[0].paragraphs.join('\n')).toContain('2. 流动资产；')
  })
})

describe('splitProposalDraft · 章号跳号（SP-20 实际输出形态）', () => {
  it('章代码跟随显式标记：CH06 后直接 CH08，不得把 CH08 的内容归到 CH07', () => {
    const draft = [
      '# 标题',
      '',
      '# 第一章 概况',
      '',
      '## 1.1 基本信息',
      '',
      '正文一。',
      '',
      '# CH06 服务方案设计',
      '',
      '## 7. 产品推荐与适配',
      '',
      '第 7 章内容被写在 CH06 之下。',
      '',
      '# CH08 实施路径',
      '',
      '## 1. 实施总览',
      '',
      '实施路径正文。',
    ].join('\n')
    const outline = splitProposalDraft(draft)
    expect(outline.chapters.map(c => c.marker)).toEqual(['第一章', 'CH06', 'CH08'])
    expect(outline.chapters.map(c => c.code)).toEqual(['CH01', 'CH06', 'CH08'])
    // 第三章缺失时不得把 CH08 降级成 CH03
    expect(outline.chapters[2].sections.map(s => s.heading)).toEqual(['1. 实施总览'])
  })
})

describe('splitProposalDraft · 人工中文序号草稿', () => {
  const outline = splitProposalDraft(ORDINAL_DRAFT)

  it('`一、` `二、` 识别为两章', () => {
    expect(outline.chapters).toHaveLength(2)
    expect(outline.chapters.map(c => c.title)).toEqual(['客户概况', '需求分析'])
    expect(outline.chapters.map(c => c.marker)).toEqual(['一', '二'])
  })

  it('正文挂在各自章下', () => {
    expect(outline.chapters[0].paragraphs.join('')).toContain('华东精工装备集团是一家制造企业。')
    expect(outline.chapters[1].paragraphs.join('')).toContain('客户有资金周转需求。')
  })
})

describe('splitProposalDraft · 空草稿与边界', () => {
  it('空草稿返回 0 章（不编造章节）', () => {
    expect(splitProposalDraft('').chapters).toHaveLength(0)
    expect(splitProposalDraft('   \n  \n').chapters).toHaveLength(0)
    expect(splitProposalDraft('').docTitle).toBe('')
  })

  it('无 Markdown 层级时 base 回退为 1 且标记为非结构化', () => {
    expect(detectChapterBase(ORDINAL_DRAFT.split('\n'))).toEqual({ level: 1, markdownStructured: false })
  })

  it('有显式 Markdown 章标题时按标题层级定 base', () => {
    expect(detectChapterBase(REAL_SHAPED_DRAFT.split('\n'))).toEqual({ level: 1, markdownStructured: true })
    const h2Draft = ['# 标题', '', '## 第一章 概况', '', '### 1.1 基本信息', '', '正文'].join('\n')
    expect(detectChapterBase(h2Draft.split('\n'))).toEqual({ level: 2, markdownStructured: true })
    expect(splitProposalDraft(h2Draft).chapters).toHaveLength(1)
    expect(splitProposalDraft(h2Draft).chapters[0].sections[0].heading).toBe('1.1 基本信息')
  })
})

describe('draftParagraphs · 段落切分', () => {
  it('按空行切段并剔除空段', () => {
    expect(draftParagraphs(['第一段。', '', '第二段第一行', '第二段第二行', '', '', '第三段。'])).toEqual([
      '第一段。',
      '第二段第一行\n第二段第二行',
      '第三段。',
    ])
  })

  it('空输入返回空数组', () => {
    expect(draftParagraphs([])).toEqual([])
    expect(draftParagraphs(['', '  '])).toEqual([])
  })
})

describe('normalizeChapterCode', () => {
  it('归一 CH06 / ch6 / 6 为 CH06', () => {
    expect(normalizeChapterCode('CH06')).toBe('CH06')
    expect(normalizeChapterCode('ch6')).toBe('CH06')
    expect(normalizeChapterCode('6')).toBe('CH06')
    expect(normalizeChapterCode('CH012')).toBe('CH012')
  })

  it('无法解析时返回 null（不猜章）', () => {
    expect(normalizeChapterCode('')).toBeNull()
    expect(normalizeChapterCode(null)).toBeNull()
    expect(normalizeChapterCode(undefined)).toBeNull()
    expect(normalizeChapterCode('CH-')).toBeNull()
  })
})
