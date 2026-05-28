/**
 * tests/pages/SermonsIndexPage.test.ts
 *
 * Contract:
 *   - Renders a heading "Sermons"
 *   - Shows a list of sermon rows when data loads
 *   - Each row contains the sermon title and speaker
 *   - Each row has a link to /sermons/:id/edit
 *   - Shows an empty-state message when the list is empty
 *   - Shows a loading indicator while fetching
 */

import { mount, flushPromises } from '@vue/test-utils'
import { setActivePinia, createPinia } from 'pinia'
import { describe, it, expect, beforeEach, vi } from 'vitest'
import SermonsPage from '~/pages/sermons/index.vue'

const MOCK_SERMONS = [
  {
    id:              'sermon-001',
    title:           'Grace Abounding',
    speaker_name:    'Pastor John',
    series:          'Romans',
    date:            '2026-05-25',
    is_published:    true,
    duration_seconds: 2700,
    thumbnail_url:   null,
  },
  {
    id:              'sermon-002',
    title:           'The Good Shepherd',
    speaker_name:    'Pastor Jane',
    series:          null,
    date:            '2026-05-18',
    is_published:    false,
    duration_seconds: null,
    thumbnail_url:   null,
  },
]

function mountPage() {
  return mount(SermonsPage, {
    global: {
      stubs: {
        NuxtLink: { template: '<a :href="to"><slot /></a>', props: ['to'] },
      },
    },
  })
}

describe('SermonsIndexPage', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.stubGlobal('$fetch', vi.fn())
  })

  it('renders the Sermons heading', async () => {
    vi.mocked($fetch).mockResolvedValue([])
    const wrapper = mountPage()
    await flushPromises()
    expect(wrapper.text()).toContain('Sermons')
  })

  it('shows sermon titles after data loads', async () => {
    vi.mocked($fetch).mockResolvedValue(MOCK_SERMONS)
    const wrapper = mountPage()
    await flushPromises()
    expect(wrapper.text()).toContain('Grace Abounding')
    expect(wrapper.text()).toContain('The Good Shepherd')
  })

  it('shows speaker names', async () => {
    vi.mocked($fetch).mockResolvedValue(MOCK_SERMONS)
    const wrapper = mountPage()
    await flushPromises()
    expect(wrapper.text()).toContain('Pastor John')
  })

  it('shows an edit link for each sermon', async () => {
    vi.mocked($fetch).mockResolvedValue(MOCK_SERMONS)
    const wrapper = mountPage()
    await flushPromises()
    const links = wrapper.findAll('a')
    const editLink = links.find(l => l.attributes('href') === '/sermons/sermon-001/edit')
    expect(editLink).toBeDefined()
  })

  it('shows empty state when no sermons', async () => {
    vi.mocked($fetch).mockResolvedValue([])
    const wrapper = mountPage()
    await flushPromises()
    expect(wrapper.text()).toContain('No sermons')
  })

  it('shows a published badge for published sermons', async () => {
    vi.mocked($fetch).mockResolvedValue(MOCK_SERMONS)
    const wrapper = mountPage()
    await flushPromises()
    expect(wrapper.text()).toContain('Published')
  })

  it('shows a draft badge for unpublished sermons', async () => {
    vi.mocked($fetch).mockResolvedValue(MOCK_SERMONS)
    const wrapper = mountPage()
    await flushPromises()
    expect(wrapper.text()).toContain('Draft')
  })
})
