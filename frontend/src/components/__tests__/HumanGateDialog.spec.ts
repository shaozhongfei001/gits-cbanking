import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import HumanGateDialog from '../HumanGateDialog.vue'
import type { HumanGate } from '../../api/v11'

// naive-ui 组件 `name` 选项不带 N 前缀（如 NButton → Button），stubs 需按 name 匹配。
const stubs = {
  Modal: { template: '<div class="modal-stub"><slot /><slot name="footer" /></div>' },
  Spin: { template: '<div class="spin-stub"><slot /></div>' },
  Alert: { props: ['title'], template: '<div class="alert-stub">{{ title }}<slot /></div>' },
  Descriptions: { template: '<div class="desc-stub"><slot /></div>' },
  DescriptionsItem: { template: '<div class="desc-item-stub"><slot /></div>' },
  Tag: { template: '<span class="tag-stub"><slot /></span>' },
  Divider: { template: '<div class="divider-stub"><slot /></div>' },
  Space: { template: '<div class="space-stub"><slot /></div>' },
  Button: {
    props: ['loading', 'disabled'],
    template: '<button class="button-stub" :disabled="disabled" @click="$emit(\'click\')"><slot /></button>',
  },
  Input: { template: '<div class="input-stub"><slot /></div>' },
}

function d01Gate(): HumanGate {
  return {
    gateId: 'HG-D01',
    gateType: 'D01_PRODUCT_RECOMMEND',
    status: 'PENDING',
    subject: '产品推荐人工决定',
    proposal: {
      runId: 'run-1',
      proposalVersionId: 'V1',
      currentVersionId: 'V1',
    },
    createdAt: '2026-08-31T00:00:00Z',
  }
}

function mountDialog(gate: HumanGate) {
  return mount(HumanGateDialog, {
    props: { show: true, gate },
    global: { stubs },
  })
}

describe('HumanGateDialog D01 结构化决定面板', () => {
  it('D01 显示结构化决定面板，不再编辑原始 JSON', async () => {
    const wrapper = mountDialog(d01Gate())

    expect(wrapper.find('[data-testid="d01-decision-buttons"]').exists()).toBe(true)
    expect(wrapper.text()).toContain('采纳')
    expect(wrapper.text()).toContain('修改后采纳')
    expect(wrapper.text()).toContain('驳回')
    expect(wrapper.text()).toContain('暂缓')

    await wrapper.get('[data-testid="d01-decision-modify"]').trigger('click')

    // 结构化修改项表单（kind 下拉 + 字段输入），而非原始 JSON 文本域
    expect(wrapper.find('[data-testid="d01-modify-builder"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="d01-mod-kind"]').exists()).toBe(true)
    expect(wrapper.text()).not.toContain('JSON格式')
  })

  it('非 D01 门禁不显示 D01 结构化面板', () => {
    const wrapper = mountDialog({
      gateId: 'gate-1',
      gateType: 'C02_REPORT_APPROVE',
      status: 'PENDING',
      subject: '报告审批',
      createdAt: '2026-08-31T00:00:00Z',
    })

    expect(wrapper.find('[data-testid="d01-decision-buttons"]').exists()).toBe(false)
    expect(wrapper.find('[data-testid="d01-decision-modify"]').exists()).toBe(false)
  })

  it('修改后采纳缺少结构化修改项时显式失败，不发决定', async () => {
    const wrapper = mountDialog(d01Gate())

    await wrapper.get('[data-testid="d01-decision-modify"]').trigger('click')
    await wrapper.get('[data-testid="d01-submit"]').trigger('click')

    expect(wrapper.text()).toContain('修改后采纳需至少一条结构化修改项')
    expect(wrapper.emitted('decide-structured')).toBeUndefined()
  })

  it('非法修改（REORDER 缺位置）显式失败，不发决定', async () => {
    const wrapper = mountDialog(d01Gate())

    await wrapper.get('[data-testid="d01-decision-modify"]').trigger('click')
    await wrapper.get('[data-testid="d01-mod-kind"]').setValue('REORDER_CANDIDATE')
    await wrapper.get('[data-testid="d01-mod-product-id"]').setValue('PROD-1')
    await wrapper.get('[data-testid="d01-mod-add"]').trigger('click')
    await wrapper.get('[data-testid="d01-submit"]').trigger('click')

    expect(wrapper.text()).toContain('调整顺序需填写原位置与新位置')
    expect(wrapper.emitted('decide-structured')).toBeUndefined()
  })

  it('合法修改后采纳发出结构化 decide-structured 载荷', async () => {
    const wrapper = mountDialog(d01Gate())

    await wrapper.get('[data-testid="d01-decision-modify"]').trigger('click')
    await wrapper.get('[data-testid="d01-mod-kind"]').setValue('ADD_CONFIRMED_FACT')
    await wrapper.get('[data-testid="d01-mod-value"]').setValue('客户已确认经营数据')
    await wrapper.get('[data-testid="d01-mod-add"]').trigger('click')
    expect(wrapper.find('[data-testid="d01-mod-list"]').exists()).toBe(true)
    await wrapper.get('[data-testid="d01-submit"]').trigger('click')

    const emitted = wrapper.emitted('decide-structured')
    expect(emitted).toBeDefined()
    const payload = emitted?.[0]?.[0] as {
      runId: string
      proposalVersionId: string
      expectedVersion?: string
      decision: string
      modifications?: Array<{ kind: string; value?: string }>
      reason?: string
    }
    expect(payload.decision).toBe('MODIFY')
    expect(payload.runId).toBe('run-1')
    expect(payload.proposalVersionId).toBe('V1')
    expect(payload.expectedVersion).toBe('V1')
    expect(payload.modifications).toHaveLength(1)
    expect(payload.modifications?.[0]).toMatchObject({ kind: 'ADD_CONFIRMED_FACT', value: '客户已确认经营数据' })
  })
})
