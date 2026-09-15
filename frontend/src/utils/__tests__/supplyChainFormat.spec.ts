import { describe, expect, it } from 'vitest'
import {
  formatAmountYuan,
  formatConfidence,
  formatShare,
  graphInsightStrips,
  isPartialBuild,
  LAYER_COLOR,
} from '../supplyChainFormat'

describe('supplyChainFormat', () => {
  it('formats yuan as 万/亿', () => {
    expect(formatAmountYuan(12000000)).toBe('1200.0 万')
    expect(formatAmountYuan(250000000)).toBe('2.50 亿')
    expect(formatAmountYuan(800)).toBe('800')
    expect(formatAmountYuan(null)).toBe('—')
  })

  it('formats share as percent', () => {
    expect(formatShare(0.35)).toBe('35.0%')
    expect(formatShare(1)).toBe('100.0%')
    expect(formatShare(undefined)).toBe('—')
  })

  it('formats confidence object without inventing keys', () => {
    expect(formatConfidence({ position: 'high', changes: 'low' })).toBe('position=high；changes=low')
    expect(formatConfidence('medium')).toBe('medium')
  })

  it('detects partial buildStatus', () => {
    expect(isPartialBuild('partial')).toBe(true)
    expect(isPartialBuild('complete')).toBe(false)
  })

  it('uses V3.2 layer colors from the 05 group-relationship template', () => {
    expect(LAYER_COLOR.enterprise).toBe('#1976d2')
    expect(LAYER_COLOR.supplier).toBe('#12a7a0')
    expect(LAYER_COLOR.customer).toBe('#48a7e8')
  })

  it('builds insight strips only from returned Skill fields', () => {
    expect(graphInsightStrips(null)).toEqual([])
    expect(graphInsightStrips({ overallAssessment: ' 位置稳  ', followUpQuestions: ['问账期'] })).toEqual([
      { tone: 'blue', label: '关键判断', text: '位置稳' },
      { tone: 'teal', label: '建议动作', text: '问账期' },
    ])
  })
})
