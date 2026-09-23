#!/usr/bin/env python3
"""PC-i1 · 独立 QA 复验 · V-N1 变异复验夹具生成器（**只写 test-results/ 我自己的副本，绝不改仓内源**）

生成 4 组副本，**副本文件名刻意用 `.check.ts`（非 `*.spec.ts`）**，以免被仓内 `npx vitest run` 的默认收集规则
（`**/*.{test,spec}.?(c|m)[jt]s?(x)`）纳入 —— 独立 QA 制品不得影响被验门禁命令的判定。

仅改动「从仓内源复制来的目标行：
  baseline/      —— 原样副本（无变异）⇒ 期望全绿（证明夹具/运行环境有效）
  mutant-B1/     —— 标题回退为「登记章号」形式（复现 QA-B1 修前渲染）⇒ 期望判红
  mutant-B2/     —— 缺失文案/节号回退为「未包含第 <登记章号> 节 + 回落登记值」⇒ 期望判红
  mutant-util/   —— `actualSectionNo()` 未命中回落登记值 ⇒ 期望判红
"""
import pathlib
import shutil
import sys

REPO = pathlib.Path('/home/szf/dev/gits-cbanking')
FE = REPO / 'frontend'
SRC = FE / 'src'
MUT = FE / 'test-results/qa-reverify-pci1-20260923/mutant'

COMPONENT = SRC / 'components/product-center/ProductInheritedChapters.vue'
COMPONENT_SPEC = SRC / 'components/product-center/__tests__/ProductInheritedChapters.spec.ts'
UTIL = SRC / 'utils/cardChapter.ts'
UTIL_SPEC = SRC / 'utils/__tests__/cardChapter.spec.ts'

if MUT.exists():
    shutil.rmtree(MUT)
MUT.mkdir(parents=True)


def read(p):
    return p.read_text(encoding='utf-8')


def sub(text, old, new, label):
    if old not in text:
        sys.exit(f'FATAL: 变异锚点未找到（{label}）—— 实现已变更，须重新审读，禁止盲改')
    return text.replace(old, new, 1)


def wire_component(text):
    """把副本组件的 cardChapter 依赖指向**同目录副本**（不触及仓内源）。"""
    return sub(text, "} from '../../utils/cardChapter'", "} from './cardChapter'", 'component->cardChapter')


def wire_component_spec(text):
    return sub(text, "from '../ProductInheritedChapters.vue'", "from './ProductInheritedChapters.vue'", 'spec->component')


def wire_util_spec(text):
    return sub(text, "} from '../cardChapter'", "} from './cardChapter'", 'utlspec->cardChapter')


BASE_COMPONENT = wire_component(read(COMPONENT))
BASE_COMPONENT_SPEC = wire_component_spec(read(COMPONENT_SPEC))
BASE_UTIL = read(UTIL)
BASE_UTIL_SPEC = wire_util_spec(read(UTIL_SPEC))

# 修前渲染形态（QA-B1 正本所记录）
PREFIX_TITLE_OLD = """          {{ block.spec.title }}
          <span v-if="block.sectionNo !== null" class="pc-inherited-block-no">
            （卡内第 {{ block.sectionNo }} 节）
          </span>"""
PREFIX_TITLE_NEW = """          {{ block.spec.no }}. {{ block.spec.title }}"""

ABSENT_OLD = """function absentText(spec: CardChapterSpec): string {
  if (props.cardState === 'unavailable') {
    return `产品卡来源不可得 ⇒ 无法判定该卡是否包含「${spec.title}」节（R2 章号 ${spec.id}）原文 —— 如实标注，不以示意内容填充。`
  }
  if (props.cardState === 'loading') {
    return `产品卡原文加载中 ⇒ 暂不判定该卡是否包含「${spec.title}」节（R2 章号 ${spec.id}）原文 —— 不以示意内容填充。`
  }
  return `该产品卡未包含「${spec.title}」节（R2 章号 ${spec.id}）原文 —— 如实标注，不以示意内容填充。`
}"""
ABSENT_NEW = """function absentText(spec: CardChapterSpec): string {
  return `该产品卡未包含第 ${spec.no} 节（${spec.title}）原文 —— 如实标注，不以示意内容填充。`
}"""

NO_LABEL_OLD = """function sectionNoLabel(section: ProductCardSection | null, spec: CardChapterSpec): string {
  const no = actualSectionNo(section, spec)
  if (no !== null) {
    return `第 ${no} 节`
  }
  if (props.cardState === 'unavailable') {
    return '来源不可得 · 节号不可判'
  }
  if (props.cardState === 'loading') {
    return '原文加载中 · 节号待判'
  }
  return `本卡未含该节 · R2 章号 ${spec.id}`
}"""
NO_LABEL_NEW = """function sectionNoLabel(section: ProductCardSection | null, spec: CardChapterSpec): string {
  return `第 ${actualSectionNo(section, spec) ?? spec.no} 节`
}"""

UTIL_OLD = """  const matched = section?.title.match(/^(\\d+)\\./)
  return matched ? Number(matched[1]) : null"""
UTIL_NEW = """  const matched = section?.title.match(/^(\\d+)\\./)
  return matched ? Number(matched[1]) : _spec.no"""

MUT_B1_COMPONENT = sub(BASE_COMPONENT, PREFIX_TITLE_OLD, PREFIX_TITLE_NEW, 'B1 title prefix')
MUT_B2_COMPONENT = sub(sub(BASE_COMPONENT, ABSENT_OLD, ABSENT_NEW, 'B2 absent'), NO_LABEL_OLD, NO_LABEL_NEW, 'B2 sectionNoLabel')
MUT_UTIL = sub(BASE_UTIL, UTIL_OLD, UTIL_NEW, 'util fallback')

GROUPS = {
    'baseline': {'component': BASE_COMPONENT, 'util': BASE_UTIL},
    'mutant-B1': {'component': MUT_B1_COMPONENT, 'util': BASE_UTIL},
    'mutant-B2': {'component': MUT_B2_COMPONENT, 'util': BASE_UTIL},
    'mutant-util': {'component': BASE_COMPONENT, 'util': MUT_UTIL},
}

for name, g in GROUPS.items():
    d = MUT / name
    d.mkdir()
    (d / 'ProductInheritedChapters.vue').write_text(g['component'], encoding='utf-8')
    (d / 'ProductInheritedChapters.check.ts').write_text(BASE_COMPONENT_SPEC, encoding='utf-8')
    (d / 'cardChapter.ts').write_text(g['util'], encoding='utf-8')
    (d / 'cardChapter.check.ts').write_text(BASE_UTIL_SPEC, encoding='utf-8')

(MUT / 'vitest.mutant.config.ts').write_text(
    """import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'

// 独立 QA 变异复验专用配置（只覆盖 test-results/ 下的副本；不触碰仓内 vitest.config.ts）
export default defineConfig({
  plugins: [vue()],
  test: {
    environment: 'happy-dom',
    include: ['test-results/qa-reverify-pci1-20260923/mutant/**/*.check.ts'],
  },
})
""",
    encoding='utf-8',
)

print('generated:', ', '.join(GROUPS))
for name in GROUPS:
    print(name, sorted(p.name for p in (MUT / name).iterdir()))
