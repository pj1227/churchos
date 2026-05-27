/**
 * tests/pages/EventEditPage.test.ts
 *
 * Contract:
 *   - Renders an "Edit Event" heading
 *   - Pre-fills title, location, and is_published from fetched data
 *   - Submits a PATCH to /events/:id with the form body
 *   - Shows a success message after a successful save
 *   - Shows an error message when the PATCH fails
 *   - "Back to events" link points to /events
 */

import { mount, flushPromises } from '@vue/test-utils'
import { setActivePinia, createPinia } from 'pinia'
import { describe, it, expect, beforeEach, vi } from 'vitest'
import EventEditPage from '~/pages/events/[id]/edit.vue'

const MOCK_EVENT = {
  id:                   'event-001',
  title:                'Sunday Worship Service',
  description:          'Weekly gathering',
  start_at:             '2026-06-01T10:00:00',
  end_at:               '2026-06-01T11:30:00',
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
}

function mountPage() {
  return mount(EventEditPage, {
    global: {
      stubs: {
        NuxtLink: { template: '<a :href="to"><slot /></a>', props: ['to'] },
      },
    },
  })
}

describe('EventEditPage', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.stubGlobal('$fetch', vi.fn())
    vi.stubGlobal('useRoute', () => ({ params: { id: 'event-001' } }))
  })

  it('renders the Edit Event heading', async () => {
    vi.mocked($fetch).mockResolvedValueOnce(MOCK_EVENT)
    const wrapper = mountPage()
    await flushPromises()
    expect(wrapper.text()).toContain('Edit Event')
  })

  it('pre-fills the title input from fetched data', async () => {
    vi.mocked($fetch).mockResolvedValueOnce(MOCK_EVENT)
    const wrapper = mountPage()
    await flushPromises()
    const input = wrapper.find('input[name="title"]')
    expect((input.element as HTMLInputElement).value).toBe('Sunday Worship Service')
  })

  it('pre-fills the location input', async () => {
    vi.mocked($fetch).mockResolvedValueOnce(MOCK_EVENT)
    const wrapper = mountPage()
    await flushPromises()
    const input = wrapper.find('input[name="location"]')
    expect((input.element as HTMLInputElement).value).toBe('Main Sanctuary')
  })

  it('reflects current is_published state in the toggle', async () => {
    vi.mocked($fetch).mockResolvedValueOnce(MOCK_EVENT)
    const wrapper = mountPage()
    await flushPromises()
    const toggle = wrapper.find('input[name="is_published"]')
    expect((toggle.element as HTMLInputElement).checked).toBe(true)
  })

  it('shows a Back link to /events', async () => {
    vi.mocked($fetch).mockResolvedValueOnce(MOCK_EVENT)
    const wrapper = mountPage()
    await flushPromises()
    const links = wrapper.findAll('a')
    const back = links.find(l => l.attributes('href') === '/events')
    expect(back).toBeDefined()
  })

  it('calls PATCH /events/:id on save', async () => {
    vi.mocked($fetch)
      .mockResolvedValueOnce(MOCK_EVENT)
      .mockResolvedValueOnce({ ...MOCK_EVENT, title: 'Updated Title' })

    const wrapper = mountPage()
    await flushPromises()

    await wrapper.find('input[name="title"]').setValue('Updated Title')
    await wrapper.find('form').trigger('submit')
    await flushPromises()

    expect(vi.mocked($fetch)).toHaveBeenCalledTimes(2)
    const [url, opts] = vi.mocked($fetch).mock.calls[1] as [string, Record<string, unknown>]
    expect(url).toBe('/events/event-001')
    expect(opts.method).toBe('PATCH')
  })

  it('shows a success message after saving', async () => {
    vi.mocked($fetch)
      .mockResolvedValueOnce(MOCK_EVENT)
      .mockResolvedValueOnce({ ...MOCK_EVENT })

    const wrapper = mountPage()
    await flushPromises()
    await wrapper.find('form').trigger('submit')
    await flushPromises()

    expect(wrapper.text()).toContain('Saved')
  })

  it('shows an error message when save fails', async () => {
    vi.mocked($fetch)
      .mockResolvedValueOnce(MOCK_EVENT)
      .mockRejectedValueOnce(new Error('Server error'))

    const wrapper = mountPage()
    await flushPromises()
    await wrapper.find('form').trigger('submit')
    await flushPromises()

    expect(wrapper.text()).toContain('Failed')
  })
})
