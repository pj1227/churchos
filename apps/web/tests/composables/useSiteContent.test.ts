/**
 * tests/composables/useSiteContent.test.ts — TDD tests for useSiteContent()
 *
 * What it does:
 *   Verifies the composable exposes the current hardcoded copy as fallback
 *   defaults immediately, fetches GET /site-config/public exactly once
 *   (shared across repeated calls within a session — apps/web is
 *   client-navigated after the static build, so this avoids refetching
 *   per page), merges the response over the defaults, and never throws or
 *   replaces defaults when the fetch fails.
 *
 * How it connects:
 *   Composable under test: app/composables/useSiteContent.ts
 *   API call: GET {apiBase}/site-config/public
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'

async function freshImport() {
  vi.resetModules()
  const mod = await import('../../app/composables/useSiteContent')
  return mod.useSiteContent
}

function flushMicrotasks() {
  return new Promise(resolve => setTimeout(resolve, 0))
}

beforeEach(() => {
  vi.stubGlobal('$fetch', vi.fn().mockResolvedValue({}))
  vi.stubGlobal('useRuntimeConfig', () => ({ public: { apiBase: 'https://api.test' } }))
})

describe('useSiteContent', () => {
  it('returns fallback defaults synchronously before the fetch resolves', async () => {
    const useSiteContent = await freshImport()
    const content = useSiteContent()
    expect(content.value.church_name).toBe('Libby Church of the Nazarene')
  })

  it('fetches GET {apiBase}/site-config/public', async () => {
    const fetchMock = vi.fn().mockResolvedValue({})
    vi.stubGlobal('$fetch', fetchMock)

    const useSiteContent = await freshImport()
    useSiteContent()
    await flushMicrotasks()

    expect(fetchMock).toHaveBeenCalledWith('https://api.test/site-config/public')
  })

  it('merges fetched values over the defaults', async () => {
    vi.stubGlobal('$fetch', vi.fn().mockResolvedValue({ church_name: 'Grace Chapel', church_phone: '555-1234' }))

    const useSiteContent = await freshImport()
    const content = useSiteContent()
    await flushMicrotasks()

    expect(content.value.church_name).toBe('Grace Chapel')
    expect(content.value.church_phone).toBe('555-1234')
    // Keys not present in the response keep their default
    expect(content.value.giving_header).toBe('Give')
  })

  it('keeps defaults if the fetch fails', async () => {
    vi.stubGlobal('$fetch', vi.fn().mockRejectedValue(new Error('network error')))

    const useSiteContent = await freshImport()
    const content = useSiteContent()
    await flushMicrotasks()

    expect(content.value.church_name).toBe('Libby Church of the Nazarene')
  })

  it('only fetches once across repeated calls (shared state)', async () => {
    const fetchMock = vi.fn().mockResolvedValue({})
    vi.stubGlobal('$fetch', fetchMock)

    const useSiteContent = await freshImport()
    useSiteContent()
    useSiteContent()
    useSiteContent()
    await flushMicrotasks()

    expect(fetchMock).toHaveBeenCalledTimes(1)
  })

  it('returns the same reactive instance across repeated calls', async () => {
    const useSiteContent = await freshImport()
    const a = useSiteContent()
    const b = useSiteContent()
    expect(a).toBe(b)
  })
})
