/**
 * tests/pages/DashboardPage.test.ts — TDD anchor for the admin home page.
 *
 * What we are testing:
 *   app/pages/index.vue — the dashboard landing page shown after login.
 *
 * Contract:
 *   - Renders a welcome heading
 *   - Shows quick-nav cards for Sermons and Events
 *   - Each card links to the correct route
 */

import { mount } from '@vue/test-utils'
import { setActivePinia, createPinia } from 'pinia'
import { describe, it, expect, beforeEach } from 'vitest'
import { useAuthStore } from '~/stores/auth'
import DashboardPage from '~/pages/index.vue'

const MOCK_PROFILE = {
  id:           '550e8400-e29b-41d4-a716-446655440000',
  email:        'joel@libbynaz.org',
  display_name: 'Joel',
  role:         'admin' as const,
  church_slug:  'libby-naz',
}

function mountPage() {
  return mount(DashboardPage, {
    global: {
      stubs: {
        NuxtLink: {
          template: '<a :href="to"><slot /></a>',
          props: ['to'],
        },
      },
    },
  })
}

describe('DashboardPage', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    const store = useAuthStore()
    store.setProfile(MOCK_PROFILE)
  })

  it('renders a welcome heading', () => {
    const wrapper = mountPage()
    expect(wrapper.text()).toContain('Welcome')
  })

  it('shows a Sermons quick-nav card linking to /sermons', () => {
    const wrapper = mountPage()
    const links = wrapper.findAll('a')
    const link = links.find(l => l.attributes('href') === '/sermons')
    expect(link).toBeDefined()
    expect(wrapper.text()).toContain('Sermons')
  })

  it('shows an Events quick-nav card linking to /events', () => {
    const wrapper = mountPage()
    const links = wrapper.findAll('a')
    const link = links.find(l => l.attributes('href') === '/events')
    expect(link).toBeDefined()
    expect(wrapper.text()).toContain('Events')
  })
})
