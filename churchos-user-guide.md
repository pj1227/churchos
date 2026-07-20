# ChurchOS User Guide

**Version:** 0.1.0 pre-release ("Kootenai")
**Last updated:** Phase 7 — Gloo AI Integration

> This guide is a living document. A new section is added after each phase is completed.

---

## Welcome to ChurchOS

ChurchOS is your church's website and management system — all in one place. It gives your congregation a beautiful, fast public website and gives your staff a clean dashboard to manage content, moderate prayer requests, track giving, and maintain a member directory.

**What makes ChurchOS different:**
- Your church owns its own data — it lives in infrastructure you control.
- It's free (or nearly free) to run for a small congregation.
- It's designed around how churches actually work.
- It can be customized to match your church's identity without hiring a developer.

---

## Table of Contents

- [Part 1 — Getting Your Site Online](#part-1--getting-your-site-online)
- [Part 2 — Managing Your Website](#part-2--managing-your-website)
- [Part 3 — Prayer Board](#part-3--prayer-board)
- [Part 4 — Settings & Configuration](#part-4--settings--configuration)
- [Part 5 — User Accounts & Roles](#part-5--user-accounts--roles)
- [Part 6 — Online Giving](#part-6--online-giving) *(coming in Phase 8)*
- [Part 7 — Member Directory](#part-7--member-directory) *(coming in Phase 9)*
- [Part 8 — Maintenance & Updates](#part-8--maintenance--updates)
- [Appendix A — Glossary](#appendix-a--glossary)
- [Appendix B — Getting Help](#appendix-b--getting-help)

---

## Part 1 — Getting Your Site Online

### What you'll need before starting

Before deploying ChurchOS, gather accounts at these free services. Each takes about 5 minutes to create:

| Service | What it does | Cost |
|---|---|---|
| [GitHub](https://github.com) | Stores your code | Free |
| [Supabase](https://supabase.com) | Your database and user logins | Free |
| [Railway](https://railway.app) | Runs your backend server | Free tier |
| [Cloudflare](https://cloudflare.com) | Hosts your website + protects it | Free |
| [Upstash](https://upstash.com) | Prevents prayer form spam | Free |
| [Backblaze B2](https://backblaze.com/b2) | Stores sermon audio/video | Free for first 10 GB |
| A domain name | e.g. yourdomain.com | ~$12/year (Namecheap) |

You will also need someone comfortable running commands in a terminal (a developer or technically-minded volunteer). If that's not you, this guide will tell you exactly what to hand to them.

---

### Step 1 — Set up your database (Supabase)

1. Go to [supabase.com](https://supabase.com) and create a free account.
2. Click **New Project**.
3. Give it a name like `churchos-yourchurchname`.
4. Choose the region closest to your congregation. For churches in the Northwest U.S., choose **US West (North California)**.
5. Set a strong database password. Write it down somewhere safe.
6. Wait about 2 minutes for the project to be ready.
7. Go to **Settings → API** in your project.
8. Copy these four values and give them to your developer:

| Value | Where to find it |
|---|---|
| Project URL | Settings → API → Project URL |
| Publishable key (anon) | Settings → API → Project API keys → `publishable` |
| Secret key | Settings → API → Project API keys → `secret` |
| JWT Secret | Settings → API → JWT Settings |

> ⚠️ **Keep the secret key private.** It has full access to your database. Never share it publicly or post it anywhere online.

> **Note on Supabase key names:** Supabase renamed their API keys in 2025. What was called "anon key" is now "publishable key." What was called "service role key" is now "secret key." ChurchOS documentation uses the new names.

---

### Step 2 — Configure authentication settings

Still in your Supabase project:

1. Go to **Authentication → URL Configuration**.
2. Set **Site URL** to your church's domain: `https://yourdomain.com`
3. Under **Redirect URLs**, add:
   - `https://admin.yourdomain.com/**`
   - `http://localhost:3001/**` (for your developer's local testing)
4. Click Save.

---

### Step 3 — Create your first admin account

1. In Supabase, go to **Authentication → Users**.
2. Click **Add User**.
3. Enter your email address and a strong password.
4. Your developer will then run a command to give your account admin access.

After that's done, you'll be able to log in at `https://admin.yourdomain.com` using that email and password.

---

### Step 4 — Point your domain to Cloudflare

This step puts your website behind Cloudflare, which makes it load faster worldwide and protects it from attacks — for free.

1. Go to [cloudflare.com](https://cloudflare.com) and log in.
2. Click **Add a Site** and enter your domain name.
3. Choose the free plan.
4. Cloudflare will give you two nameserver addresses (they look like `brad.ns.cloudflare.com`).
5. Log in to wherever you bought your domain (e.g. Namecheap).
6. Find the nameserver settings and replace them with the two Cloudflare nameservers.
7. Save. DNS changes can take a few hours to take effect worldwide.

---

### Step 5 — Verify everything is working

Once your developer has finished the deployment, run through this checklist:

- [ ] Your website loads at `https://yourdomain.com`
- [ ] The site loads over HTTPS (padlock in browser)
- [ ] Service times and address display correctly
- [ ] The map shows the right location
- [ ] The contact form submits without error
- [ ] You can log in at `https://admin.yourdomain.com`
- [ ] Dark mode toggle works
- [ ] You can visit `https://api.yourdomain.com/health` and see `"status": "ok"`

---

## Part 2 — Managing Your Website

### Logging in to the admin panel

Go to `https://admin.yourdomain.com` and sign in with your email and password.

If you forget your password, click **Forgot Password** on the login page. You'll receive a reset email at the address you registered with.

Once you're in, you'll see the sidebar on the left with navigation links: **Sermons**, **Events**, **Prayer**, and **Settings**. Your name (or email) and a **Sign out** button are in the top-right corner. The ChurchOS version appears at the bottom of the sidebar — useful when reporting an issue.

---

### Managing sermons

The sermon archive is one of the most-visited parts of your website. Keeping it up to date helps people find messages they've missed and introduces your church to new visitors.

#### Viewing the sermon list

Click **Sermons** in the sidebar. You'll see a table of all sermons with their title, speaker, series, and date. Each row has an **Edit** link.

#### Editing a sermon

Click the **Edit** link next to any sermon to open its edit form. From here you can update the title, speaker, series, date, and description. Click **Save** to apply your changes. A green confirmation message will appear briefly when the save succeeds.

> **Current limitation:** Sermon creation from the admin panel is not yet available in this version — sermons are currently managed through direct database access. A full Create/Delete interface is planned for a future update.

---

### Managing events

Events appear on the homepage and on a dedicated events page.

#### Viewing the event list

Click **Events** in the sidebar. You'll see a table of all events with their title, date, location, and status. Each row has an **Edit** link.

Status badges indicate:
- **Upcoming** (green) — event is in the future
- **Past** (grey) — event date has passed

#### Editing an event

Click **Edit** next to any event to update its title, date, time, location, and description. Click **Save** to apply your changes.

> **Current limitation:** Like sermons, event creation from the admin panel is in development. Events are currently managed via direct database access.

---

## Part 3 — Prayer Board

The prayer board allows your congregation and visitors to submit prayer requests. Every request is reviewed before appearing publicly — nothing goes live without your approval.

### How it works — the full flow

1. A visitor fills out the prayer request form at `yourdomain.com/prayer`.
2. The system automatically checks the submission rate (limit: 3 submissions per hour per visitor, to prevent spam).
3. An AI system (Grok by default; configurable to Gloo AI in Settings) reviews the content for appropriateness.
4. The request is stored with a status of either `pending` or `rejected` based on the AI review.
5. You review pending requests in the admin panel and approve or reject them.
6. Approved requests appear on the public prayer board at `yourdomain.com/prayer/board` (no personal contact info is shown).
7. When you approve a request, an email notification is sent to your configured prayer chain address (see Settings).

### The submission form

The public form at `/prayer` has three fields:
- **Prayer request** (required) — the text of the request.
- **Your name** (optional) — submitters can leave this blank or check "Submit anonymously."
- **Email** (optional) — for follow-up only; never shown publicly.

Submitters always see a success message, even if the AI moderation rejected their submission. This is intentional — it preserves dignity and doesn't give bad actors information about the moderation system.

### Moderating prayer requests

1. In the admin panel, click **Prayer Board** in the sidebar.
2. You'll see two tabs: **Pending** and **Active**.

**Pending tab** shows new submissions waiting for your decision. For each request you'll see the submitter's name (or "Anonymous"), the full text of the request, and **Approve** / **Reject** buttons.

Click **Approve** to publish the request to the public board and trigger a prayer chain email notification. Click **Reject** to decline it. Rejected requests are not deleted — they remain in the database visible only to staff, in case you need to review your decisions later.

**Active tab** shows currently approved, unanswered requests. From here you can mark a request as **Answered** — this flags it visually and moves it to an archived state so the board stays focused on active needs.

### Notes on privacy

- Submitters' email addresses are stored securely in your database but are **never shown** on the public prayer board.
- The name or identifying details a submitter includes in their prayer text is their own choice.
- Approved requests appear on the public board at `/prayer/board`. No login is required to view the board, but no contact information is ever included in what's shown.

---

## Part 4 — Settings & Configuration

The Settings page (click **Settings** in the sidebar) manages three areas.

### Prayer Board — Prayer Chain Email

This is the email address that receives a notification each time you approve a prayer request. Set it to your prayer team's group email or your pastor's address.

1. In Settings, find the **Prayer Board** section.
2. Enter an email address in the **Prayer Chain Email** field.
3. Click **Save Prayer Settings**.

Leave this blank if you don't want email notifications when approving requests.

---

### Email Connector

ChurchOS sends email notifications using one of two providers. You choose which one in Settings.

**SMTP** (default) — works with any email provider that supports SMTP. Works with Gmail, Office 365, Fastmail, and others. Configured via environment variables set during deployment — contact your developer to update these.

**Microsoft 365** — uses the Microsoft Graph API to send email from a licensed Microsoft 365 mailbox. Better for churches already using Microsoft 365 for email.

#### Setting up Microsoft 365

1. In Settings, find the **Email Connector** section.
2. Change the provider dropdown from **SMTP** to **Microsoft 365**.
3. Fill in:
   - **Tenant ID** — your Azure tenant ID (found in Azure Active Directory)
   - **Client ID** — the App Registration client ID
   - **Client Secret** — the App Registration secret value
   - **Sender** — the licensed Microsoft 365 mailbox address to send from
4. Click **Save Connector Settings**.

If any of the Microsoft 365 fields are incomplete, ChurchOS will automatically fall back to SMTP without failing.

> For help obtaining Azure credentials, ask your developer or IT contact. They will need to register an application in Azure Active Directory and grant it Mail.Send permissions.

---

### AI Moderation

Controls which AI system reviews prayer request submissions.

**Grok** (default) — xAI's Grok model. Used automatically with the deployment-level API key.

**Gloo AI** — an AI platform designed specifically for faith communities. Supports theological tradition settings to make moderation sensitive to your church's context.

To switch to Gloo AI:
1. In the **AI Moderation** section of Settings, change the provider to **Gloo**.
2. Enter your **Client ID**, **Client Secret**, and select your **Theological Tradition**.
3. Click **Save AI Settings**.

If Gloo credentials are missing or Gloo is unavailable, ChurchOS automatically falls back to Grok. If Grok is also unavailable, submissions are approved and queued for manual review — the system never silently drops a prayer request.

---

## Part 5 — User Accounts & Roles

ChurchOS uses a five-level role system to control who can see and do what.

| Role | Who it's for | What they can do |
|---|---|---|
| **Superadmin** | ChurchOS system administrator | Everything, including changing admin roles |
| **Admin** | Church administrator or pastor | Full access to all content, settings, members, and giving records |
| **Staff** | Office staff, worship leaders | Manage sermons, events, and moderate the prayer board |
| **Member** | Verified church members | Access the member directory (when live) and their own giving history |
| **Guest** | Everyone else | View public pages and submit prayer requests |

### Creating accounts

New users sign in via the admin panel at `https://admin.yourdomain.com`. On first sign-in, Supabase creates their account. By default, new accounts are assigned the **Guest** role.

To grant a user staff or admin access, your developer can update their role directly in the Supabase database (Authentication → Users, then update their row in `public.profiles`). A role management UI is planned for a future update.

### Removing access

To revoke someone's admin access: change their role to **Guest** in the database. They will still have an account but will only see public pages.

---

## Part 6 — Online Giving

> **Coming in Phase 8.** ChurchOS will integrate with Stripe to accept online donations securely. Your church receives funds directly in your Stripe account. No card data will ever touch ChurchOS servers — Stripe handles all payment processing.

When available, this section will cover setting up your Stripe account, creating and managing giving funds (General Fund, Building Fund, Missions, etc.), viewing giving records in the admin panel, and exporting year-end giving summaries for your treasurer.

---

## Part 7 — Member Directory

> **Coming in Phase 9.** The member directory will be a consent-based, members-only contact list. It will never be publicly accessible. Each member will control exactly what information they share (email, phone, address, photo).

---

## Part 8 — Maintenance & Updates

### Checking your current version

Your ChurchOS version appears in:
- The bottom-left corner of every admin panel page
- By visiting `https://api.yourdomain.com/health` in a browser (shows `"version"` and `"codename"`)

### Updating ChurchOS

ChurchOS is updated by your developer pushing changes through the standard GitHub workflow. When a new version is released:

1. Your developer pulls the latest code from GitHub.
2. They test it on a staging environment first.
3. After confirming everything works, they deploy to production.

### Backups

Your database is backed up automatically by Supabase every day. The free tier retains 7 days of backups. If you ever need to restore from a backup, contact your developer.

### Checking the API is healthy

Visit `https://api.yourdomain.com/health` in your browser at any time. You should see:

```json
{
  "status": "ok",
  "version": "0.1.0",
  "codename": "Kootenai"
}
```

If you see an error or the page doesn't load, your backend server may be down. Contact your developer.

---

## Appendix A — Glossary

| Term | What it means |
|---|---|
| **Admin panel** | The staff-only area at `admin.yourdomain.com` where you manage your site |
| **Supabase** | The service that stores your church's data (database + user logins) |
| **Cloudflare** | The service that hosts your website and protects it from attacks |
| **Railway** | The service that runs your backend server (the API) |
| **Upstash** | The service that tracks submission counts for rate limiting (prevents spam) |
| **RLS** | Row Level Security — a database feature ensuring members can only see their own records |
| **JWT** | A secure token that proves you're logged in; stored in memory, never on disk |
| **Stripe** | The payment service used for online giving (Phase 8) |
| **Gloo AI** | An AI platform built for faith communities, used to moderate prayer requests |
| **Grok** | xAI's language model; the default AI moderator in ChurchOS |
| **SMTP** | A standard protocol for sending email; used by Gmail, Office 365, and most providers |
| **Connector** | A pluggable integration (e.g., email provider, AI provider) that can be swapped without code changes |
| **Slug** | A URL-friendly version of a name, e.g., `my-sermon-title` |
| **Monorepo** | A single code repository containing all parts of the application |
| **Turborepo** | The tool that manages building and testing the monorepo |
| **Alembic** | The tool that manages database schema changes (migrations) |
| **CI/CD** | Continuous Integration / Continuous Deployment — automated testing and deployment |

---

## Appendix B — Getting Help

### Community

ChurchOS is open source. You can find documentation, report issues, and connect with other users on GitHub: [github.com/pj1227/churchos](https://github.com/pj1227/churchos)

### Security issues

If you discover a security vulnerability, **do not** open a public GitHub issue. Email: `security@churchos.dev`

We respond within 48 hours.

### Reporting bugs

Open an issue on GitHub with:
1. What you were trying to do
2. What you expected to happen
3. What actually happened
4. Your ChurchOS version (check the admin sidebar footer or `GET /health`)

---

*ChurchOS User Guide — updated with each phase release.*
*Current version: 0.1.0 pre-release | Phase 7 — Gloo AI Integration | Codename: "Kootenai"*
