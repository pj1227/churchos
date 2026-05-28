/**
 * tests/pages/SermonEditPage.test.ts
 *
 * Contract:
 *   - Renders an "Edit Sermon" heading
 *   - Populates form fields (title, speaker_name, series, date) from fetched data
 *   - Submits a PATCH to /sermons/:id with only changed fields
 *   - Shows a success message after a successful save
 *   - Shows an error message when the PATCH fails
 *   - Publish toggle reflects the current is_published value
 *   - "Back to sermons" link points to /sermons
 */

import { mount, flushPromises } from '@vue/test-utils'
import { setActivePinia, createPinia } from 'pinia'
import { describe, it, expect, beforeEach, vi } from 'vitest'
import SermonEditPage from '~/pages/sermons/[id]/edit.vue'

// Nuxt auto-injects useRoute as a global; override the default setup.ts stub
// so every test in this suite sees params: { id: 'sermon-001' }.

const MOCK_SERMON = {
  id:               'sermon-001',
  title:            'Grace Abounding',
  speaker_name:     'Pastor John',
  series:           'Romans',
  date:             '2026-05-25',
  is_published:     true,
  duration_seconds: 2700,
  thumbnail_url:    null,
  description:      'A sermon on grace.',
  scripture_reference: 'Romans 5:20',
  notes:            null,
}

function mountPage() {
  return mount(SermonEditPage, {
    global: {
      stubs: {
        NuxtLink: { template: '<a :href="to"><slot /></a>', props: ['to'] },
      },
    },
  })
}

describe('SermonEditPage', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.stubGlobal('$fetch', vi.fn())
    vi.stubGlobal('useRoute', () => ({ params: { id: 'sermon-001' } }))
  })

  it('renders the Edit Sermon heading', async () => {
    vi.mocked($fetch).mockResolvedValueOnce(MOCK_SERMON)
    const wrapper = mountPage()
    await flushPromises()
    expect(wrapper.text()).toContain('Edit Sermon')
  })

  it('pre-fills the title input from fetched data', async () => {
    vi.mocked($fetch).mockResolvedValueOnce(MOCK_SERMON)
    const wrapper = mountPage()
    await flushPromises()
    const titleInput = wrapper.find('input[name="title"]')
    expect((titleInput.element as HTMLInputElement).value).toBe('Grace Abounding')
  })

  it('pre-fills the speaker_name input', async () => {
    vi.mocked($fetch).mockResolvedValueOnce(MOCK_SERMON)
    const wrapper = mountPage()
    await flushPromises()
    const speakerInput = wrapper.find('input[name="speaker_name"]')
    expect((speakerInput.element as HTMLInputElement).value).toBe('Pastor John')
  })

  it('pre-fills the series input', async () => {
    vi.mocked($fetch).mockResolvedValueOnce(MOCK_SERMON)
    const wrapper = mountPage()
    await flushPromises()
    const seriesInput = wrapper.find('input[name="series"]')
    expect((seriesInput.element as HTMLInputElement).value).toBe('Romans')
  })

  it('pre-fills the date input', async () => {
    vi.mocked($fetch).mockResolvedValueOnce(MOCK_SERMON)
    const wrapper = mountPage()
    await flushPromises()
    const dateInput = wrapper.find('input[name="date"]')
    expect((dateInput.element as HTMLInputElement).value).toBe('2026-05-25')
  })

  it('reflects the current is_published state in the toggle', async () => {
    vi.mocked($fetch).mockResolvedValueOnce(MOCK_SERMON)
    const wrapper = mountPage()
    await flushPromises()
    const toggle = wrapper.find('input[name="is_published"]')
    expect((toggle.element as HTMLInputElement).checked).toBe(true)
  })

  it('shows a Back link to /sermons', async () => {
    vi.mocked($fetch).mockResolvedValueOnce(MOCK_SERMON)
    const wrapper = mountPage()
    await flushPromises()
    const links = wrapper.findAll('a')
    const back = links.find(l => l.attributes('href') === '/sermons')
    expect(back).toBeDefined()
  })

  it('calls PATCH /sermons/:id on save', async () => {
    // First call: GET (load), second call: PATCH (save)
    vi.mocked($fetch)
      .mockResolvedValueOnce(MOCK_SERMON)
      .mockResolvedValueOnce({ ...MOCK_SERMON, title: 'Updated Title' })

    const wrapper = mountPage()
    await flushPromises()

    // Change the title
    const titleInput = wrapper.find('input[name="title"]')
    await titleInput.setValue('Updated Title')

    // Submit the form
    await wrapper.find('form').trigger('submit')
    await flushPromises()

    // Second $fetch call should be the PATCH
    expect(vi.mocked($fetch)).toHaveBeenCalledTimes(2)
    const [url, opts] = vi.mocked($fetch).mock.calls[1] as [string, Record<string, unknown>]
    expect(url).toBe('/sermons/sermon-001')
    expect(opts.method).toBe('PATCH')
  })

  it('shows a success message after saving', async () => {
    vi.mocked($fetch)
      .mockResolvedValueOnce(MOCK_SERMON)
      .mockResolvedValueOnce({ ...MOCK_SERMON })

    const wrapper = mountPage()
    await flushPromises()

    await wrapper.find('form').trigger('submit')
    await flushPromises()

    expect(wrapper.text()).toContain('Saved')
  })

  it('shows an error message when save fails', async () => {
    vi.mocked($fetch)
      .mockResolvedValueOnce(MOCK_SERMON)
      .mockRejectedValueOnce(new Error('Network error'))

    const wrapper = mountPage()
    await flushPromises()

    await wrapper.find('form').trigger('submit')
    await flushPromises()

    expect(wrapper.text()).toContain('Failed')
  })
})
