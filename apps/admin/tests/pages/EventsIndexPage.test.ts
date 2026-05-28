/**
 * tests/pages/EventsIndexPage.test.ts
 *
 * Contract:
 *   - Renders an "Events" heading
 *   - Shows event titles after data loads
 *   - Shows the event date for each row
 *   - Each row has an edit link to /events/:id/edit
 *   - Shows an empty-state message when the list is empty
 *   - Shows a Published badge for is_published: true
 *   - Shows a Draft badge for is_published: false
 */

import { mount, flushPromises } from '@vue/test-utils'
import { setActivePinia, createPinia } from 'pinia'
import { describe, it, expect, beforeEach, vi } from 'vitest'
import EventsPage from '~/pages/events/index.vue'

const MOCK_EVENTS = [
  {
    id:                   'event-001',
    title:                'Sunday Worship Service',
    description:          'Weekly gathering',
    start_at:             '2026-06-01T10:00:00Z',
    end_at:               '2026-06-01T11:30:00Z',
    all_day:              false,
    location:             'Main Sanctuary',
    is_virtual:           false,
    virtual_url:          null,
    category:             'worship',
    recurrence:           'weekly',
    image_url:            null,
    registration_required: false,
    registration_url:     null,
    is_published:         true,
    church_id:            'church-001',
    created_by:           'user-001',
  },
  {
    id:                   'event-002',
    title:                'Youth Camp',
    description:          'Summer youth retreat',
    start_at:             '2026-07-14T08:00:00Z',
    end_at:               '2026-07-17T17:00:00Z',
    all_day:              false,
    location:             'Camp Kootenai',
    is_virtual:           false,
    virtual_url:          null,
    category:             'youth',
    recurrence:           'none',
    image_url:            null,
    registration_required: true,
    registration_url:     'https://example.com/register',
    is_published:         false,
    church_id:            'church-001',
    created_by:           'user-001',
  },
]

function mountPage() {
  return mount(EventsPage, {
    global: {
      stubs: {
        NuxtLink: { template: '<a :href="to"><slot /></a>', props: ['to'] },
      },
    },
  })
}

describe('EventsIndexPage', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.stubGlobal('$fetch', vi.fn())
  })

  it('renders the Events heading', async () => {
    vi.mocked($fetch).mockResolvedValue([])
    const wrapper = mountPage()
    await flushPromises()
    expect(wrapper.text()).toContain('Events')
  })

  it('shows event titles after data loads', async () => {
    vi.mocked($fetch).mockResolvedValue(MOCK_EVENTS)
    const wrapper = mountPage()
    await flushPromises()
    expect(wrapper.text()).toContain('Sunday Worship Service')
    expect(wrapper.text()).toContain('Youth Camp')
  })

  it('shows the start date for each event', async () => {
    vi.mocked($fetch).mockResolvedValue(MOCK_EVENTS)
    const wrapper = mountPage()
    await flushPromises()
    // ISO string or formatted — just confirm the year appears
    expect(wrapper.text()).toContain('2026')
  })

  it('shows an edit link for each event', async () => {
    vi.mocked($fetch).mockResolvedValue(MOCK_EVENTS)
    const wrapper = mountPage()
    await flushPromises()
    const links = wrapper.findAll('a')
    const editLink = links.find(l => l.attributes('href') === '/events/event-001/edit')
    expect(editLink).toBeDefined()
  })

  it('shows empty state when no events', async () => {
    vi.mocked($fetch).mockResolvedValue([])
    const wrapper = mountPage()
    await flushPromises()
    expect(wrapper.text()).toContain('No events')
  })

  it('shows a Published badge for published events', async () => {
    vi.mocked($fetch).mockResolvedValue(MOCK_EVENTS)
    const wrapper = mountPage()
    await flushPromises()
    expect(wrapper.text()).toContain('Published')
  })

  it('shows a Draft badge for unpublished events', async () => {
    vi.mocked($fetch).mockResolvedValue(MOCK_EVENTS)
    const wrapper = mountPage()
    await flushPromises()
    expect(wrapper.text()).toContain('Draft')
  })
})
