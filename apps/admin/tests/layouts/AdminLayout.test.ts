/**
 * tests/layouts/AdminLayout.test.ts — TDD anchor for the admin layout shell.
 *
 * Written BEFORE the layout exists. Tests will fail with "Cannot find module
 * '~/layouts/default.vue'" until the file is created. That is expected.
 *
 * What we are testing:
 *   app/layouts/default.vue — the persistent shell around every admin page.
 *
 * Contract enforced here:
 *   - Navigation links to /sermons and /events are present
 *   - ChurchOS brand wordmark renders in the sidebar
 *   - Version badge renders with "v0.1.0"
 *   - Signed-in user's display name (or email) appears in the topbar
 *   - Sign-out button calls auth.signOut()
 *   - The <slot /> renders slotted content
 *
 * How it connects:
 *   - app/layouts/default.vue: the component under test
 *   - app/stores/auth.ts: provides isAuthenticated, profile, signOut
 *   - tests/setup.ts: stubs navigateTo and other Nuxt globals
 */

import { mount } from '@vue/test-utils'
import { setActivePinia, createPinia } from 'pinia'
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useAuthStore } from '~/stores/auth'
import AdminLayout from '~/layouts/default.vue'

const MOCK_PROFILE = {
  id:           '550e8400-e29b-41d4-a716-446655440000',
  email:        'joel@libbynaz.org',
  display_name: 'Joel',
  role:         'admin' as const,
  church_slug:  'libby-naz',
}

function mountLayout(slotContent = '<p id="slot-content">Page content</p>') {
  return mount(AdminLayout, {
    slots: { default: slotContent },
    global: {
      stubs: {
        // Stub NuxtLink so href assertions work without a router
        NuxtLink: {
          template: '<a :href="to"><slot /></a>',
          props: ['to'],
        },
      },
    },
  })
}

describe('AdminLayout', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  // ── Brand & navigation ───────────────────────────────────────────────────

  it('renders the ChurchOS wordmark', () => {
    const store = useAuthStore()
    store.setProfile(MOCK_PROFILE)
    const wrapper = mountLayout()
    expect(wrapper.text()).toContain('ChurchOS')
  })

  it('renders a link to /sermons', () => {
    const store = useAuthStore()
    store.setProfile(MOCK_PROFILE)
    const wrapper = mountLayout()
    const links = wrapper.findAll('a')
    const sermonLink = links.find(l => l.attributes('href') === '/sermons')
    expect(sermonLink).toBeDefined()
  })

  it('renders a link to /events', () => {
    const store = useAuthStore()
    store.setProfile(MOCK_PROFILE)
    const wrapper = mountLayout()
    const links = wrapper.findAll('a')
    const eventLink = links.find(l => l.attributes('href') === '/events')
    expect(eventLink).toBeDefined()
  })

  // ── Version badge ────────────────────────────────────────────────────────

  it('renders the version badge', () => {
    const store = useAuthStore()
    store.setProfile(MOCK_PROFILE)
    const wrapper = mountLayout()
    expect(wrapper.text()).toContain('v0.1.0')
  })

  // ── User identity ────────────────────────────────────────────────────────

  it('displays the signed-in user display name', () => {
    const store = useAuthStore()
    store.setProfile(MOCK_PROFILE)
    const wrapper = mountLayout()
    expect(wrapper.text()).toContain('Joel')
  })

  it('falls back to email when display_name is null', () => {
    const store = useAuthStore()
    store.setProfile({ ...MOCK_PROFILE, display_name: null })
    const wrapper = mountLayout()
    expect(wrapper.text()).toContain('joel@libbynaz.org')
  })

  // ── Sign-out ─────────────────────────────────────────────────────────────

  it('calls auth.signOut when sign-out button is clicked', async () => {
    const store = useAuthStore()
    store.setProfile(MOCK_PROFILE)
    const signOutSpy = vi.spyOn(store, 'signOut').mockResolvedValue()
    const wrapper = mountLayout()

    const signOutBtn = wrapper.find('[data-testid="sign-out-btn"]')
    expect(signOutBtn.exists()).toBe(true)
    await signOutBtn.trigger('click')
    expect(signOutSpy).toHaveBeenCalledOnce()
  })

  // ── Slot ─────────────────────────────────────────────────────────────────

  it('renders slotted page content', () => {
    const store = useAuthStore()
    store.setProfile(MOCK_PROFILE)
    const wrapper = mountLayout()
    expect(wrapper.find('#slot-content').exists()).toBe(true)
  })
})
