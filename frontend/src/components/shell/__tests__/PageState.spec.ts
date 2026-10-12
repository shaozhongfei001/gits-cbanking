import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import PageState from '../PageState.vue'

const stubs = {
  NSpin: { template: '<div class="n-spin" />' },
  NResult: { template: '<div class="n-result"><slot name="footer" /></div>' },
  NButton: { template: '<button class="n-button" v-bind="$attrs" @click="$emit(\'click\')"><slot /></button>' },
  NEmpty: { template: '<div class="n-empty"><slot /></div>' },
}

describe('PageState', () => {
  it('renders idle, loading, success and error states', async () => {
    const idle = mount(PageState, { props: { status: 'idle' }, global: { stubs } })
    expect(idle.find('[data-testid="idle-state"]').exists()).toBe(true)

    const loading = mount(PageState, { props: { status: 'loading' }, global: { stubs } })
    expect(loading.find('[data-testid="loading-state"]').exists()).toBe(true)

    const success = mount(PageState, {
      props: { status: 'success' },
      slots: { default: '<p>ok</p>' },
      global: { stubs },
    })
    expect(success.find('[data-testid="success-state"]').exists()).toBe(true)
    expect(success.text()).toContain('ok')

    const error = mount(PageState, { props: { status: 'error', error: 'boom' }, global: { stubs } })
    expect(error.find('[data-testid="error-state"]').exists()).toBe(true)
    await error.get('[data-testid="retry-action"]').trigger('click')
    expect(error.emitted('retry')).toBeTruthy()
  })
})
