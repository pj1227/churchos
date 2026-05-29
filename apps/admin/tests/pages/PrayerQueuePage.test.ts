/**
 * tests/pages/PrayerQueuePage.test.ts — TDD tests for the prayer moderation queue
 *
 * What it does:
 *   Verifies the staff prayer moderation queue page renders pending requests,
 *   allows approving and rejecting submissions, and handles empty/error states.
 *
 * Why it exists at this layer:
 *   The moderation queue is the staff-facing side of Phase 5. Tests lock in
 *   the required UI structure and moderation actions before implementation.
 *
 * How it connects:
 *   Component under test: app/pages/prayer/index.vue
 *   API calls: GET /prayer-requests/pending, PATCH /prayer-requests/{id}
 *   (both stubbed via vi.stubGlobal('$fetch'))
 */

import { mount, flushPromises } from '@vue/test-utils'
import { setActivePinia, createPinia } from 'pinia'
import { describe, it, expect, beforeEach, vi } from 'vitest'
import PrayerQueuePage from '~/pages/prayer/index.vue'

const MOCK_PENDING = [
  {
    id:           'prayer-001',
    church_id:    'default',
    name:         'Jane Doe',
    email:        null,
    body:         'Please pray for healing.',
    is_anonymous: false,
    status:       'pending',
    ai_score:     0.92,
    ai_reason:    null,
    prayer_count: 0,
    submitted_at: '2026-05-28T10:00:00Z',
    moderated_at: null,
    moderated_by: null,
    is_answered:  false,
    expires_at:   null,
    created_at:   '2026-05-28T10:00:00Z',
    updated_at:   '2026-05-28T10:00:00Z',
  },
  {
    id:           'prayer-002',
    church_id:    'default',
    name:         null,
    email:        null,
    body:         'Pray for my family.',
    is_anonymous: true,
    status:       'pending',
    ai_score:     0.88,
    ai_reason:    null,
    prayer_count: 0,
    submitted_at: '2026-05-28T11:00:00Z',
    moderated_at: null,
    moderated_by: null,
    is_answered:  false,
    expires_at:   null,
    created_at:   '2026-05-28T11:00:00Z',
    updated_at:   '2026-05-28T11:00:00Z',
  },
]

function mountPage() {
  return mount(PrayerQueuePage, {
    global: {
      stubs: {
        NuxtLink: { template: '<a :href="to"><slot /></a>', props: ['to'] },
      },
    },
  })
}

beforeEach(() => {
  setActivePinia(createPinia())
  vi.stubGlobal('$fetch', vi.fn().mockResolvedValue(MOCK_PENDING))
})

describe('PrayerQueuePage', () => {
  it('renders a "Prayer Queue" heading', async () => {
    const wrapper = mountPage()
    await flushPromises()
    expect(wrapper.text()).toMatch(/prayer queue|prayer requests/i)
  })

  it('shows a loading state before data arrives', () => {
    vi.stubGlobal('$fetch', vi.fn(() => new Promise(() => {})))
    const wrapper = mountPage()
    expect(wrapper.text()).toMatch(/loading/i)
  })

  it('renders a row for each pending request', async () => {
    const wrapper = mountPage()
    await flushPromises()
    const rows = wrapper.findAll('[data-testid="prayer-row"]')
    expect(rows).toHaveLength(2)
  })

  it('shows the prayer body in each row', async () => {
    const wrapper = mountPage()
    await flushPromises()
    expect(wrapper.text()).toContain('Please pray for healing.')
    expect(wrapper.text()).toContain('Pray for my family.')
  })

  it('shows submitter name when not anonymous', async () => {
    const wrapper = mountPage()
    await flushPromises()
    expect(wrapper.text()).toContain('Jane Doe')
  })

  it('shows "Anonymous" when is_anonymous is true', async () => {
    const wrapper = mountPage()
    await flushPromises()
    expect(wrapper.text()).toMatch(/anonymous/i)
  })

  it('each row has an Approve button', async () => {
    const wrapper = mountPage()
    await flushPromises()
    const approveBtns = wrapper.findAll('[data-testid="btn-approve"]')
    expect(approveBtns).toHaveLength(2)
  })

  it('each row has a Reject button', async () => {
    const wrapper = mountPage()
    await flushPromises()
    const rejectBtns = wrapper.findAll('[data-testid="btn-reject"]')
    expect(rejectBtns).toHaveLength(2)
  })

  it('calls PATCH with status=approved when Approve is clicked', async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(MOCK_PENDING)   // initial GET
      .mockResolvedValueOnce({ ...MOCK_PENDING[0], status: 'approved' }) // PATCH
    vi.stubGlobal('$fetch', fetchMock)

    const wrapper = mountPage()
    await flushPromises()

    await wrapper.findAll('[data-testid="btn-approve"]')[0].trigger('click')
    await flushPromises()

    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('prayer-001'),
      expect.objectContaining({ method: 'PATCH', body: expect.objectContaining({ status: 'approved' }) }),
    )
  })

  it('calls PATCH with status=rejected when Reject is clicked', async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(MOCK_PENDING)
      .mockResolvedValueOnce({ ...MOCK_PENDING[0], status: 'rejected' })
    vi.stubGlobal('$fetch', fetchMock)

    const wrapper = mountPage()
    await flushPromises()

    await wrapper.findAll('[data-testid="btn-reject"]')[0].trigger('click')
    await flushPromises()

    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('prayer-001'),
      expect.objectContaining({ method: 'PATCH', body: expect.objectContaining({ status: 'rejected' }) }),
    )
  })

  it('removes the row after moderation action', async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(MOCK_PENDING)
      .mockResolvedValueOnce({ ...MOCK_PENDING[0], status: 'approved' })
    vi.stubGlobal('$fetch', fetchMock)

    const wrapper = mountPage()
    await flushPromises()
    expect(wrapper.findAll('[data-testid="prayer-row"]')).toHaveLength(2)

    await wrapper.findAll('[data-testid="btn-approve"]')[0].trigger('click')
    await flushPromises()

    expect(wrapper.findAll('[data-testid="prayer-row"]')).toHaveLength(1)
  })

  it('shows empty state when queue is empty', async () => {
    vi.stubGlobal('$fetch', vi.fn().mockResolvedValue([]))
    const wrapper = mountPage()
    await flushPromises()
    expect(wrapper.text()).toMatch(/no pending|queue is empty|all caught up/i)
  })
})
