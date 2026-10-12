import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import TimelineItem from '../TimelineItem.vue'

describe('TimelineItem', () => {
  it('renders title', () => {
    const wrapper = mount(TimelineItem, {
      props: { title: '客户拜访' },
    })
    expect(wrapper.find('.timeline-title').text()).toBe('客户拜访')
  })

  it('renders subtitle when provided', () => {
    const wrapper = mount(TimelineItem, {
      props: { title: '客户拜访', subtitle: '与CEO会面' },
    })
    expect(wrapper.find('.timeline-subtitle').text()).toBe('与CEO会面')
  })

  it('does not render subtitle element when not provided', () => {
    const wrapper = mount(TimelineItem, {
      props: { title: '客户拜访' },
    })
    expect(wrapper.find('.timeline-subtitle').exists()).toBe(false)
  })

  it('renders formatted time', () => {
    const wrapper = mount(TimelineItem, {
      props: { title: '客户拜访', time: '2025-06-15T14:30:00Z' },
    })
    const timeEl = wrapper.find('.timeline-time')
    expect(timeEl.exists()).toBe(true)
    expect(timeEl.text().length).toBeGreaterThan(0)
  })

  it('does not render time when not provided', () => {
    const wrapper = mount(TimelineItem, {
      props: { title: '客户拜访' },
    })
    const timeEl = wrapper.find('.timeline-time')
    expect(timeEl.text()).toBe('')
  })

  it('starts in collapsed state by default', () => {
    const wrapper = mount(TimelineItem, {
      props: { title: '客户拜访' },
    })
    expect(wrapper.find('.timeline-detail').exists()).toBe(false)
    expect(wrapper.find('.timeline-item').classes()).not.toContain('timeline-expanded')
  })

  it('expands detail on header click', async () => {
    const wrapper = mount(TimelineItem, {
      props: { title: '客户拜访' },
      slots: { default: '<div class="detail-content">详细信息</div>' },
    })
    await wrapper.find('.timeline-header').trigger('click')
    expect(wrapper.find('.timeline-detail').exists()).toBe(true)
    expect(wrapper.find('.timeline-item').classes()).toContain('timeline-expanded')
    expect(wrapper.find('.detail-content').exists()).toBe(true)
  })

  it('collapses detail on second click', async () => {
    const wrapper = mount(TimelineItem, {
      props: { title: '客户拜访' },
      slots: { default: '<div>详细信息</div>' },
    })
    // Click to expand
    await wrapper.find('.timeline-header').trigger('click')
    expect(wrapper.find('.timeline-detail').exists()).toBe(true)
    // Click again to collapse
    await wrapper.find('.timeline-header').trigger('click')
    expect(wrapper.find('.timeline-detail').exists()).toBe(false)
  })

  it('renders slot content in detail area', async () => {
    const wrapper = mount(TimelineItem, {
      props: { title: '客户拜访' },
      slots: { default: '<p class="custom-detail">自定义详情内容</p>' },
    })
    await wrapper.find('.timeline-header').trigger('click')
    expect(wrapper.find('.custom-detail').text()).toBe('自定义详情内容')
  })

  it('applies custom dot color', () => {
    const wrapper = mount(TimelineItem, {
      props: { title: '客户拜访', color: '#ff0000' },
    })
    const dot = wrapper.find('.timeline-dot')
    expect(dot.attributes('style')).toContain('background')
    expect(dot.attributes('style')).toContain('#ff0000')
  })

  it('uses default dot color when color not provided', () => {
    const wrapper = mount(TimelineItem, {
      props: { title: '客户拜访' },
    })
    const dot = wrapper.find('.timeline-dot')
    expect(dot.attributes('style')).toContain('background')
    expect(dot.attributes('style')).toContain('#1976D2')
  })
})
