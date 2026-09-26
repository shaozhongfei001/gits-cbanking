/**
 * 建议书草稿结构解析（P24 / P25 卡片式展示的底座）。
 *
 * 职责边界（诚实性）：
 * - 本模块只做**结构切分**：把 KERT SP-20 返回的 Markdown 草稿拆成「章 → 节 → 小节 → 段落」；
 * - **不新增、不改写、不省略**任何正文文字；无法识别的行一律按正文保留；
 * - 不做业务判断（不评估章节内容对错、不补默认文案、不改写事实标签）。
 *
 * 切分规则（按 SP-20 实际输出实测，夹具见 __tests__/proposalDraft.spec.ts）：
 * 1. 显式章标记优先：`第X章 …` 与 `CH0N …`（SP-20 存在 `# 第一章 …` / `# CH04 …` 混用）；
 * 2. 其余按「相对当前章层级」判定：层级 ≤ 章层级 ⇒ 新章；= 章层级+1 ⇒ 节；> 章层级+1 ⇒ 小节；
 *    （SP-20 的 CH07/CH08 的章标题落在 `##` 层，其子标题 `###` 仍应算「节」，故不以文档全局层级为准）
 * 3. 「无编号的（章层级+1）标题 ⇒ 新章」：SP-20 在 CH06 之后用 `## 产品推荐与适配`（无编号）
 *    开启 CH07，其子标题改用中文序号 `### 一、…`；当本章已出现十进制编号节时判定为新章；
 * 4. 无 Markdown 结构的人工草稿：`一、客户概况` / `1、客户概况` 即章（`1. xxx` 视为列表，不作章）；
 * 5. 正文行（`- `、`1. ` 列表与 `> ` 引用块）一律原样保留。
 */

export interface DraftBlock {
  key: string
  /** 节标题（如 `1.1 基本信息`）；空串表示无标题块 */
  heading: string
  paragraphs: string[]
  children: DraftBlock[]
}

export interface DraftChapter {
  index: number
  /** 章标记：`第一章` / `CH04` / `一` / `1`；无显式标记时为空串 */
  marker: string
  /** 章代码（由章序号推导），与 citations/unknowns 的 chapterRef 口径一致 */
  code: string
  title: string
  /** 首个节之前的引言段落 */
  paragraphs: string[]
  sections: DraftBlock[]
  anchor: string
}

export interface DraftOutline {
  docTitle: string
  /** 引用块元信息（如 `类型：INITIAL ｜ 阶段：FIRST_CONTACT`） */
  meta: string
  chapters: DraftChapter[]
}

const RE_MD_HEADING = /^(#{1,6})\s+(.*)$/
const RE_META = /^>\s?(.*)$/
const RE_CHAPTER_CN = /^第[一二三四五六七八九十百千零〇\d]+[章节節部分]\s*[:：、.]?\s*(.*)$/
const RE_CH_CODE = /^CH\s*(\d+)\s*[:：、.\-]?\s*(.*)$/i
/** 十进制编号节：必须含至少一个 `.`，避免把 `1. 近三年营业收入` 这类列表项误判为节 */
const RE_SECTION_DOTTED = /^(\d+(?:\.\d+)+)\s*[、.．]?\s+(.*)$/
const RE_SECTION_DOTTED_TIGHT = /^(\d+(?:\.\d+)+)\s*[、.．]\s*(.*)$/
/** 中文序号（`一、总体节奏` / `（一）基本情况`） */
const RE_ORDINAL_CN = /^[（(]?([一二三四五六七八九十]+)[）)]?\s*[、.．]\s*(.*)$/
/** 阿拉伯序号仅认顿号（`1、客户概况`）；`1. xxx` 视为列表项 */
const RE_ORDINAL_ARABIC = /^[（(]?(\d+)[）)]?\s*、\s*(.*)$/

type LineKind = 'docTitle' | 'meta' | 'chapter' | 'section' | 'subSection' | 'content'

interface HeadingInfo {
  level: number
  /** 去 Markdown 前缀后的标题文本 */
  text: string
}

interface Classified {
  kind: LineKind
  /** 该行的 Markdown 标题层级；非标题行或非 Markdown 章为 0 */
  level: number
  marker: string
  title: string
  /** 原样保留的整行（正文分支使用） */
  text: string
}

export interface ChapterBase {
  level: number
  /** true ⇒ 文档存在显式 Markdown 章标题（`# 第一章` / `# CH04`） */
  markdownStructured: boolean
}

export interface ClassifyContext {
  /** 章基准层级（首个显式章标题所在层级；无显式章时为最浅标题层级或 1） */
  base: number
  /** 当前章所在层级（未进入章时等于 base） */
  chapterLevel: number
  hasChapter: boolean
  /** 当前章是否已出现十进制编号节（用于 §3 的新章判定） */
  numberedSectionSeen: boolean
  markdownStructured: boolean
}

function parseHeading(raw: string): HeadingInfo | null {
  const match = raw.match(RE_MD_HEADING)
  if (!match) return null
  return { level: match[1].length, text: match[2].trim() }
}

function stripEdge(source: string): string {
  return source.replace(/^[：:、.\s]+/, '').replace(/[：:、.\s]+$/, '').trim()
}

/** 判定文本是否可作「章标题」（`第X章` / `CH0N`）。 */
function asChapter(text: string): { marker: string; title: string } | null {
  const cn = text.match(RE_CHAPTER_CN)
  if (cn) {
    return { marker: text.slice(0, text.length - cn[1].length).trim(), title: stripEdge(cn[1]) || text }
  }
  const code = text.match(RE_CH_CODE)
  if (code) {
    return { marker: `CH${code[1].padStart(2, '0')}`, title: stripEdge(code[2]) || text }
  }
  return null
}

/** 判定文本是否可作「节标题」（十进制编号优先）。 */
function asNumberedSection(text: string): { marker: string; title: string } | null {
  const dotted = text.match(RE_SECTION_DOTTED) ?? text.match(RE_SECTION_DOTTED_TIGHT)
  if (dotted && dotted[2] && dotted[2].trim().length > 0) {
    return { marker: dotted[1], title: `${dotted[1]} ${dotted[2].trim()}` }
  }
  return null
}

/** 判定文本是否带序号（十进制 / 中文序号 / 阿拉伯顿号）。 */
function asOrdinalSection(text: string): { marker: string; title: string } | null {
  const dotted = asNumberedSection(text)
  if (dotted) return dotted
  const ordinal = text.match(RE_ORDINAL_CN) ?? text.match(RE_ORDINAL_ARABIC)
  if (ordinal && ordinal[2] && ordinal[2].trim().length > 0) {
    return { marker: ordinal[1], title: `${ordinal[1]}、${ordinal[2].trim()}` }
  }
  return null
}

/**
 * 预扫描：首个显式章标题（`第X章` / `CH0N`）所在层级。
 * 无显式章标题时：有 Markdown 标题则取最浅层级，否则视为无层级结构（level=1）。
 */
export function detectChapterBase(lines: string[]): ChapterBase {
  let shallowest = 0
  for (const raw of lines) {
    const heading = parseHeading(raw)
    const text = heading ? heading.text : raw.trim()
    if (!text) continue
    if (heading && (shallowest === 0 || heading.level < shallowest)) {
      shallowest = heading.level
    }
    if (asChapter(text)) {
      return { level: heading ? heading.level : 1, markdownStructured: true }
    }
  }
  if (shallowest > 0) {
    return { level: shallowest, markdownStructured: true }
  }
  return { level: 1, markdownStructured: false }
}

/** 判定单行归属（章 / 节 / 小节 / 文档标题 / 元信息 / 正文）。 */
export function classifyDraftLine(raw: string, ctx: ClassifyContext): Classified {
  const line = raw.replace(/\s+$/, '')
  if (line.trim().length === 0) {
    return { kind: 'content', level: 0, marker: '', title: '', text: '' }
  }

  const heading = parseHeading(line)

  if (!heading) {
    const text = line.trim()
    const meta = text.match(RE_META)
    if (meta && !ctx.hasChapter) {
      return { kind: 'meta', level: 0, marker: '', title: '', text: meta[1].trim() }
    }
    const chapter = asChapter(text)
    if (chapter) return { kind: 'chapter', level: 0, marker: chapter.marker, title: chapter.title, text }
    const dotted = asNumberedSection(text)
    if (dotted && ctx.hasChapter) {
      return { kind: 'section', level: 0, marker: dotted.marker, title: dotted.title, text }
    }
    if (ctx.markdownStructured) {
      // Markdown 结构文档中，非标题行不可能是节（避免把 `1. xxx` 列表项误判为节）
      return { kind: 'content', level: 0, marker: '', title: '', text: line }
    }
    const organic = text.match(RE_ORDINAL_CN) ?? text.match(RE_ORDINAL_ARABIC)
    if (organic && organic[2] && organic[2].trim().length > 0) {
      return { kind: 'chapter', level: 0, marker: organic[1], title: stripEdge(organic[2]), text }
    }
    return { kind: 'content', level: 0, marker: '', title: '', text: line }
  }

  const { level, text } = heading

  const chapter = asChapter(text)
  if (chapter) {
    return { kind: 'chapter', level, marker: chapter.marker, title: chapter.title, text }
  }

  if (!ctx.hasChapter) {
    // 首个无章标记的 Markdown 标题 = 文档标题
    return { kind: 'docTitle', level, marker: '', title: text, text }
  }

  if (level <= ctx.chapterLevel) {
    return { kind: 'chapter', level, marker: '', title: text, text }
  }

  if (level > ctx.chapterLevel + 1) {
    const sub = asOrdinalSection(text)
    return { kind: 'subSection', level, marker: sub?.marker ?? '', title: sub?.title ?? text, text }
  }

  // level === chapterLevel + 1
  const section = asOrdinalSection(text)
  if (section) {
    return { kind: 'section', level, marker: section.marker, title: section.title, text }
  }
  if (ctx.numberedSectionSeen && ctx.chapterLevel === ctx.base) {
    // 无编号顶层标题，且本章已有十进制编号节 ⇒ 新章（模块头 §3）
    return { kind: 'chapter', level, marker: '', title: text, text }
  }
  return { kind: 'section', level, marker: '', title: text, text }
}

/** 把草稿正文拆成「章 → 节 → 小节」结构；空草稿返回空章列表（不编造章节）。 */
export function splitProposalDraft(draft: string): DraftOutline {
  const outline: DraftOutline = { docTitle: '', meta: '', chapters: [] }
  const lines = (draft ?? '').replace(/\r\n?/g, '\n').split('\n')
  const { level: base, markdownStructured } = detectChapterBase(lines)

  let chapter: { marker: string; title: string; paragraphs: string[]; sections: DraftBlock[] } | null = null
  let chapterLevel = base
  let section: DraftBlock | null = null
  let subSection: DraftBlock | null = null
  let numberedSectionSeen = false

  const closeSub = () => {
    if (section && subSection) {
      section.children.push(subSection)
      subSection = null
    }
  }
  const closeSection = () => {
    closeSub()
    if (chapter && section) {
      chapter.sections.push(section)
      section = null
    }
  }
  const usedCodes = new Set<string>()
  const closeChapter = () => {
    closeSection()
    if (chapter) {
      const index = outline.chapters.length
      // 章代码优先取显式标记（SP-20 可能跳过章号，如 CH06 后直接 CH08）；
      // 无显式标记或代码重复时才回退为按序号派生。
      const explicit = normalizeChapterCode(chapter.marker)
      let code = explicit && !usedCodes.has(explicit) ? explicit : `CH${String(index + 1).padStart(2, '0')}`
      while (usedCodes.has(code)) {
        code = `${code}x`
      }
      usedCodes.add(code)
      outline.chapters.push({
        index,
        marker: chapter.marker,
        code,
        title: chapter.title,
        paragraphs: chapter.paragraphs,
        sections: chapter.sections,
        anchor: `proposal-chapter-${index}`,
      })
      chapter = null
    }
  }
  const pushParagraph = (text: string) => {
    if (subSection) subSection.paragraphs.push(text)
    else if (section) section.paragraphs.push(text)
    else if (chapter) chapter.paragraphs.push(text)
  }

  for (const raw of lines) {
    const line = raw.replace(/\s+$/, '')
    const cls = classifyDraftLine(line, {
      base,
      chapterLevel,
      hasChapter: chapter !== null,
      numberedSectionSeen,
      markdownStructured,
    })

    if (cls.kind === 'docTitle') {
      if (!outline.docTitle) outline.docTitle = cls.text
      continue
    }
    if (cls.kind === 'meta') {
      outline.meta = outline.meta ? `${outline.meta} ｜ ${cls.text}` : cls.text
      continue
    }
    if (cls.kind === 'chapter') {
      closeChapter()
      chapter = { marker: cls.marker, title: cls.title, paragraphs: [], sections: [] }
      chapterLevel = cls.level > 0 ? cls.level : 0
      numberedSectionSeen = false
      continue
    }
    if (cls.kind === 'section') {
      if (!chapter) {
        // 未进入章即出现节：升格为章，保证内容不丢
        chapter = { marker: cls.marker, title: cls.title, paragraphs: [], sections: [] }
        chapterLevel = cls.level > 0 ? cls.level : 0
        numberedSectionSeen = false
        continue
      }
      closeSection()
      section = { key: `sec-${chapter.sections.length}`, heading: cls.title, paragraphs: [], children: [] }
      if (asNumberedSection(cls.title)) numberedSectionSeen = true
      continue
    }
    if (cls.kind === 'subSection') {
      if (!chapter) {
        chapter = { marker: '', title: cls.title, paragraphs: [], sections: [] }
        chapterLevel = cls.level > 0 ? cls.level : 0
        continue
      }
      if (!section) {
        // 章下直接出现小节：升格为节
        section = { key: `sec-${chapter.sections.length}`, heading: cls.title, paragraphs: [], children: [] }
        continue
      }
      closeSub()
      subSection = {
        key: `${section.key}-sub-${section.children.length}`,
        heading: cls.title,
        paragraphs: [],
        children: [],
      }
      continue
    }

    if (line.trim().length > 0) {
      pushParagraph(line)
    } else if (subSection || section || chapter) {
      // 空行仅作分块边界（段落切分时统一处理）
      pushParagraph('')
    }
  }

  closeChapter()
  return outline
}

/** 正文分块：按空行切段，供卡片内逐段渲染（不合并、不裁剪段内文字）。 */
export function draftParagraphs(paragraphs: string[]): string[] {
  return paragraphs
    .join('\n')
    .split(/\n{2,}/)
    .map(block => block.replace(/^\s+|\s+$/g, ''))
    .filter(block => block.length > 0)
}

/** 章代码归一：`CH06` / `ch6` / `6` ⇒ `CH06`；无法解析返回 null（不猜章）。 */
export function normalizeChapterCode(ref: string | null | undefined): string | null {
  if (!ref) return null
  const digits = String(ref).match(/\d+/)
  if (!digits) return null
  return `CH${digits[0].padStart(2, '0')}`
}
