import { describe, expect, it } from 'vitest'
import {
  formatAmountYuan,
  formatConfidence,
  formatShare,
  isPartialBuild,
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
})
