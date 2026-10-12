import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import DisabledAction from '../DisabledAction.vue'

const stubs = {
  NButton: {
    props: ['disabled'],
    template: '<button class="n-button" :disabled="disabled" data-testid="gated-action"><slot /></button>',
  },
  NTooltip: { template: '<div><slot name="trigger" /><slot /></div>' },
}

describe('DisabledAction', () => {
  it('shows reason and unlock path when disabled', () => {
    const wrapper = mount(DisabledAction, {
      props: {
        label: '批量调整分层',
        disabled: true,
        reason: '分层拖动写回为 C2，待合同批准',
        unlockPath: 'CCC 完成 CC2 后授权',
      },
      global: { stubs },
    })
    const button = wrapper.get('[data-testid="gated-action"]')
    expect((button.element as HTMLButtonElement).disabled).toBe(true)
    expect(wrapper.get('[data-testid="disabled-reason"]').text()).toContain('C2')
    expect(wrapper.text()).toContain('解除路径')
    expect(wrapper.text()).toContain('CCC 完成 CC2 后授权')
  })
})
