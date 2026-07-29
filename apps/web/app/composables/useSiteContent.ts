/**
 * composables/useSiteContent.ts — public CMS content for the site.
 *
 * What it does:
 *   Fetches GET {apiBase}/site-config/public once (module-level singleton
 *   promise, shared across every page during a client session — apps/web
 *   is client-routed after the initial load, so this avoids one fetch per
 *   page) and returns a reactive object of church name/address/contact/
 *   page-copy fields.
 *
 * Why fallback defaults:
 *   apps/web is statically generated (`nuxt generate`) for Cloudflare
 *   Pages. Until an admin fills in the Site Content page (apps/admin
 *   /content), GET /site-config/public won't have most of these keys set.
 *   Every field defaults to the church's current copy so nothing regresses
 *   — the page renders the same content it does today, and each field
 *   only changes once an admin explicitly sets it.
 *
 * How it connects:
 *   - apps/admin app/pages/content/index.vue writes these same keys via
 *     PUT /site-config/{key} with is_public=true.
 *   - app/routers/site_config.py GET /site-config/public is the read side.
 */

import { ref } from 'vue'

export interface SiteContent {
  church_name: string
  church_logo_url: string

  church_address_line1: string
  church_city: string
  church_state: string
  church_zip: string

  church_phone: string
  church_office_email: string
  church_pastor_name: string
  church_office_hours: string

  service_time_1_label: string
  service_time_1_time: string
  service_time_2_label: string
  service_time_2_time: string
  service_time_3_label: string
  service_time_3_time: string

  home_tagline: string
  home_welcome_message: string
  home_new_here_heading: string
  home_new_here_tagline: string
  home_scripture_ref: string
  home_scripture_text: string

  about_tagline: string
  about_mission_statement: string
  about_what_we_believe: string
  about_scripture_ref: string
  about_scripture_text: string

  sermons_tagline: string
  sermons_display_count: string

  giving_header: string
  giving_tagline: string
}

const DEFAULTS: SiteContent = {
  church_name:     'Libby Church of the Nazarene',
  church_logo_url: '',

  church_address_line1: '409 Louisiana Ave',
  church_city:  'Libby',
  church_state: 'MT',
  church_zip:   '59923',

  church_phone:        '(406) 293-2931',
  church_office_email: 'pastor@libbychurch.org',
  church_pastor_name:  'Pastor John Smith',
  church_office_hours: '',

  service_time_1_label: 'Sunday School',
  service_time_1_time:  '9:30 AM',
  service_time_2_label: 'Morning Worship',
  service_time_2_time:  '10:45 AM',
  service_time_3_label: 'Wednesday Prayer',
  service_time_3_time:  '6:30 PM',

  home_tagline:           'A Place to Know God and Be Known',
  home_welcome_message:   'Join us every Sunday morning for worship, teaching from God\'s Word, and a community that walks alongside you.',
  home_new_here_heading:  'New Here? We\'d Love to Meet You.',
  home_new_here_tagline:  'Whether you\'re exploring faith for the first time or looking for a church home in Libby, you\'re welcome here. Reach out — we\'ll be in touch.',
  home_scripture_ref:     'Matthew 22:37–39',
  home_scripture_text:    'Love the Lord your God with all your heart and with all your soul and with all your mind. This is the first and greatest commandment. And the second is like it: Love your neighbor as yourself.',

  about_tagline:            'A community of believers in Libby, Montana — loving God and loving our neighbors since 1910.',
  about_mission_statement:  'We exist to make Christlike disciples in the nations — beginning right here in Libby, Montana. That means gathering together in worship, growing in the knowledge of God\'s Word, and going into our community with the love and hope of Jesus.\n\nAs part of the Church of the Nazarene, we stand in the Wesleyan-Holiness tradition — believing that God\'s grace is available to all, that real transformation is possible, and that love is the mark of the Kingdom.',
  about_what_we_believe:    'We believe in one God — Father, Son, and Holy Spirit. We believe the Bible is the inspired Word of God, the sufficient rule of faith and practice. We believe that all people are fallen and in need of God\'s grace, and that through Jesus Christ\'s atoning death and resurrection, salvation is freely offered to all who believe.\n\nWe believe the Holy Spirit sanctifies believers — setting them apart and empowering them to love God and neighbor fully. We look forward to the return of Christ and the resurrection of the dead.',
  about_scripture_ref:      'Micah 6:8',
  about_scripture_text:     'He has shown you, O mortal, what is good. And what does the LORD require of you? To act justly and to love mercy and to walk humbly with your God.',

  sermons_tagline:       'Teaching from God\'s Word every Sunday morning. Listen online or join us in person.',
  sermons_display_count: '6',

  giving_header:  'Give',
  giving_tagline: 'Online giving is coming soon. In the meantime, you can give in person during any Sunday service, or mail a check to the church office.',
}

const state = ref<SiteContent>({ ...DEFAULTS })
let fetchPromise: Promise<void> | null = null

export function useSiteContent() {
  if (!fetchPromise) {
    const apiBase = useRuntimeConfig().public.apiBase
    fetchPromise = $fetch(`${apiBase}/site-config/public`)
      .then((data) => {
        Object.assign(state.value, data as Partial<SiteContent>)
      })
      .catch(() => {
        // Network/API failure — keep defaults, never break page rendering.
      })
  }
  return state
}
