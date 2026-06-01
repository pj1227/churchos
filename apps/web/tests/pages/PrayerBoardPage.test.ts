/**
 * tests/pages/PrayerBoardPage.test.ts — TDD tests for the public prayer board
 *
 * What it does:
 *   Verifies the public prayer board page displays approved community prayer
 *   requests and links to the submission form.
 *
 * How it connects:
 *   Component under test: app/pages/prayer/board.vue
 *   API call: GET {apiBase}/prayer-requests/public (no auth required —
 *   returns approved prayers with email and moderation fields stripped)
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import PrayerBoardPage from '../../app/pages/prayer/board.vue'

const stubs = {
  NuxtLink: { template: '<a :href="to"><slot /></a>', props: ['to'] },
  CoContainer: { template: '<div><slot /></div>' },
  CoSection: { template: '<section><slot /></section>' },
}

const MOCK_PRAYERS = [
  {
    id:           'prayer-001',
    name:         'Jane Doe',
    body:         'Please pray for healing.',
    is_anonymous: false,
    status:       'approved',
    prayer_count: 3,
    submitted_at: '2026-05-28T10:00:00Z',
    is_answered:  false,
  },
  {
    id:           'prayer-002',
    name:         null,
    body:         'Pray for my family.',
    is_anonymous: true,
    status:       'approved',
    prayer_count: 1,
    submitted_at: '2026-05-28T11:00:00Z',
    is_answered:  false,
  },
]

beforeEach(() => {
  vi.stubGlobal('$fetch', vi.fn().mockResolvedValue(MOCK_PRAYERS))
})

describe('PrayerBoardPage', () => {
  it('renders a heading containing "Prayer"', async () => {
    const wrapper = mount(PrayerBoardPage, { global: { stubs } })
    await flushPromises()
    expect(wrapper.find('h1').text()).toMatch(/prayer/i)
  })

  it('shows a loading state before data arrives', () => {
    vi.stubGlobal('$fetch', vi.fn(() => new Promise(() => {})))
    const wrapper = mount(PrayerBoardPage, { global: { stubs } })
    expect(wrapper.text()).toMatch(/loading/i)
  })

  it('renders a card for each approved prayer', async () => {
    const wrapper = mount(PrayerBoardPage, { global: { stubs } })
    await flushPromises()
    const cards = wrapper.findAll('[data-testid="prayer-card"]')
    expect(cards).toHaveLength(2)
  })

  it('shows the prayer body in each card', async () => {
    const wrapper = mount(PrayerBoardPage, { global: { stubs } })
    await flushPromises()
    expect(wrapper.text()).toContain('Please pray for healing.')
    expect(wrapper.text()).toContain('Pray for my family.')
  })

  it('shows submitter name when not anonymous', async () => {
    const wrapper = mount(PrayerBoardPage, { global: { stubs } })
    await flushPromises()
    expect(wrapper.text()).toContain('Jane Doe')
  })

  it('shows "Anonymous" when is_anonymous is true', async () => {
    const wrapper = mount(PrayerBoardPage, { global: { stubs } })
    await flushPromises()
    expect(wrapper.text()).toMatch(/anonymous/i)
  })

  it('shows empty state when no approved prayers', async () => {
    vi.stubGlobal('$fetch', vi.fn().mockResolvedValue([]))
    const wrapper = mount(PrayerBoardPage, { global: { stubs } })
    await flushPromises()
    expect(wrapper.text()).toMatch(/no prayer|be the first/i)
  })

  it('has a link to submit a prayer request', async () => {
    const wrapper = mount(PrayerBoardPage, { global: { stubs } })
    await flushPromises()
    const link = wrapper.find('a[href="/prayer"]')
    expect(link.exists()).toBe(true)
  })
})
