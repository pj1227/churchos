<!--
  app/pages/contact.vue — Contact page (route: /contact)

  What it does:
    Renders a contact form (name, email, message) alongside church address,
    phone, and service time info. Form submission is a client-side no-op
    for Phase 2 — actual email/API wiring happens in Phase 3+.

  Why it exists at this layer:
    The contact form is the visitor's primary engagement pathway. The static
    structure and accessibility semantics need to be locked in and tested
    before the submission logic is added.

  How it connects:
    - Rendered inside app/layouts/default.vue
    - Uses @churchos/ui CoFormInput and CoButton for consistent form styling
    - Textarea is a raw <textarea> wrapped with the .form-input token class
      (CoFormInput wraps <input> elements only — textarea needs manual styling)
-->

<script setup lang="ts">
import { ref } from 'vue'
import { CoFormInput, CoButton, CoContainer, CoSection } from '@churchos/ui'

useSeoMeta({
  title: 'Contact — Libby Church of the Nazarene',
  description: 'Get in touch with Libby Church of the Nazarene. We\'d love to hear from you.',
})

const form = ref({
  name: '',
  email: '',
  message: '',
})

const submitted = ref(false)
const submitting = ref(false)

async function handleSubmit() {
  // Phase 2 stub — real submission wired in Phase 3
  submitting.value = true
  await new Promise(resolve => setTimeout(resolve, 800))
  submitting.value = false
  submitted.value = true
}
</script>

<template>
  <!-- Page header -->
  <CoSection class="bg-forest-600 dark:bg-charcoal-900 py-16">
    <CoContainer>
      <h1
        style="font-family: var(--font-display)"
        class="text-4xl md:text-5xl font-bold text-white mb-3"
      >
        Contact Us
      </h1>
      <p
        style="font-family: var(--font-body)"
        class="text-white/70 text-lg max-w-xl"
      >
        We'd love to hear from you. Reach out with questions, prayer requests,
        or just to say hello.
      </p>
    </CoContainer>
  </CoSection>

  <!-- Content -->
  <CoSection>
    <CoContainer>
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-12">

        <!-- Contact form -->
        <div>
          <!-- Success state -->
          <div
            v-if="submitted"
            class="co-card border-forest-300 dark:border-forest-700 text-center py-10"
          >
            <p
              style="font-family: var(--font-display)"
              class="text-2xl font-semibold text-forest-600 dark:text-forest-300 mb-3"
            >
              Message Sent!
            </p>
            <p style="font-family: var(--font-body)" class="text-charcoal-900/70 dark:text-stone-300">
              Thank you for reaching out. We'll be in touch soon.
            </p>
          </div>

          <!-- Form -->
          <form
            v-else
            class="flex flex-col gap-5"
            novalidate
            @submit.prevent="handleSubmit"
          >
            <CoFormInput
              id="name"
              v-model="form.name"
              label="Full name"
              placeholder="Jane Smith"
              required
            />

            <CoFormInput
              id="email"
              v-model="form.email"
              label="Email address"
              type="email"
              placeholder="jane@example.com"
              required
            />

            <!-- Textarea — styled with form token classes -->
            <div class="flex flex-col gap-1">
              <label
                for="message"
                class="form-label"
                style="font-family: var(--font-ui)"
              >
                Message
              </label>
              <textarea
                id="message"
                v-model="form.message"
                name="message"
                rows="5"
                placeholder="How can we help?"
                class="form-input resize-y"
                style="font-family: var(--font-body)"
                required
              />
            </div>

            <CoButton
              variant="primary"
              tag="button"
              type="submit"
              class="self-start !px-8"
              :disabled="submitting"
            >
              {{ submitting ? 'Sending…' : 'Send Message' }}
            </CoButton>
          </form>
        </div>

        <!-- Church info sidebar -->
        <div data-testid="church-address" class="flex flex-col gap-6">
          <div>
            <p
              style="font-family: var(--font-display)"
              class="text-lg font-semibold text-charcoal-900 dark:text-stone-50 mb-2"
            >
              Find Us
            </p>
            <address
              style="font-family: var(--font-ui)"
              class="not-italic text-charcoal-900/70 dark:text-stone-300 leading-relaxed"
            >
              409 Louisiana Ave<br>
              Libby, MT 59923
            </address>
            <p style="font-family: var(--font-ui)" class="mt-2">
              <a
                href="tel:+14062932931"
                class="text-forest-500 hover:text-forest-600 dark:text-forest-300 transition-colors"
              >
                (406) 293-2931
              </a>
            </p>
          </div>

          <div>
            <p
              style="font-family: var(--font-display)"
              class="text-lg font-semibold text-charcoal-900 dark:text-stone-50 mb-2"
            >
              Service Times
            </p>
            <ul style="font-family: var(--font-ui)" class="list-none m-0 p-0 text-charcoal-900/70 dark:text-stone-300 space-y-1">
              <li>Sunday School — 9:30 AM</li>
              <li>Morning Worship — 10:45 AM</li>
              <li>Wednesday Prayer — 6:30 PM</li>
            </ul>
          </div>

          <div>
            <p
              style="font-family: var(--font-display)"
              class="text-lg font-semibold text-charcoal-900 dark:text-stone-50 mb-2"
            >
              Pastor
            </p>
            <p style="font-family: var(--font-ui)" class="text-charcoal-900/70 dark:text-stone-300">
              Pastor John Smith<br>
              <a
                href="mailto:pastor@libbychurch.org"
                class="text-forest-500 hover:text-forest-600 dark:text-forest-300 transition-colors"
              >
                pastor@libbychurch.org
              </a>
            </p>
          </div>
        </div>

      </div>
    </CoContainer>
  </CoSection>
</template>
