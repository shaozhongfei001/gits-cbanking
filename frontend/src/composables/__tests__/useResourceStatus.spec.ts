import { describe, it, expect } from 'vitest'
import { deriveResourceStatus } from '../useResourceStatus'

describe('deriveResourceStatus', () => {
  it('covers idle loading success and error', () => {
    expect(deriveResourceStatus({ loading: false, error: '', hasData: false, requested: false })).toBe('idle')
    expect(deriveResourceStatus({ loading: true, error: '', hasData: false, requested: true })).toBe('loading')
    expect(deriveResourceStatus({ loading: false, error: 'x', hasData: false, requested: true })).toBe('error')
    expect(deriveResourceStatus({ loading: false, error: '', hasData: true, requested: true })).toBe('success')
  })
})
