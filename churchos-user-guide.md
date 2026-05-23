# ChurchOS User Guide

**Version:** 0.1.0 (Pre-release)
**Last updated:** Phase 0 — Repo & Tooling

> This guide is a living document. A new section is added after each phase is completed. If a feature isn't documented here yet, it's planned for a future phase.

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
- [Part 4 — Online Giving](#part-4--online-giving)
- [Part 5 — Member Directory](#part-5--member-directory)
- [Part 6 — User Accounts & Roles](#part-6--user-accounts--roles)
- [Part 7 — Settings & Configuration](#part-7--settings--configuration)
- [Part 8 — Maintenance & Updates](#part-8--maintenance--updates)
- [Appendix A — Glossary](#appendix-a--glossary)
- [Appendix B — Getting Help](#appendix-b--getting-help)

---

## Part 1 — Getting Your Site Online

> **Phase availability:** This section will be completed after Phase 0–3.

### What you'll need before starting

Before deploying ChurchOS, gather accounts at these free services. Each takes about 5 minutes to create:

| Service | What it does | Cost |
|---|---|---|
| [GitHub](https://github.com) | Stores your code | Free |
| [Supabase](https://supabase.com) | Your database and user logins | Free |
| [Railway](https://railway.app) | Runs your backend server | Free tier |
| [Cloudflare](https://cloudflare.com) | Hosts your website + protects it | Free |
| [Upstash](https://upstash.com) | Prevents form spam | Free |
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
| Anon public key | Settings → API → Project API keys → `anon public` |
| Service role key | Settings → API → Project API keys → `service_role` |
| JWT Secret | Settings → API → JWT Settings |

> ⚠️ **Keep the service role key private.** It has full access to your database. Never share it publicly or post it anywhere online.

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

---

## Part 2 — Managing Your Website

> **Phase availability:** This section will be completed after Phase 4.

### Logging in to the admin panel

Go to `https://admin.yourdomain.com` and sign in with your email and password.

If you forget your password, click **Forgot Password** on the login page. You'll receive a reset email at the address you registered with.

---

### Managing sermons

The sermon archive is one of the most-visited parts of your website. Keeping it up to date helps people find messages they've missed and introduces your church to new visitors.

#### Adding a new sermon

1. In the admin panel, click **Sermons** in the left sidebar.
2. Click **+ New Sermon**.
3. Fill in the details:
   - **Title** — the sermon title as it will appear on the website.
   - **Speaker** — the person who preached (usually your pastor's name).
   - **Series** — if this sermon is part of a series, enter the series name. Sermons with the same series name are grouped together automatically.
   - **Date** — the date the sermon was preached.
   - **Description** — a brief summary (2–4 sentences). This shows in search results and on the sermon archive page.
4. Upload your audio or video file. Supported formats: MP3, M4A (audio), MP4 (video).
5. Click **Save**. The sermon will appear on the public website immediately.

#### Editing or deleting a sermon

1. Click **Sermons** in the sidebar.
2. Find the sermon in the list and click its title.
3. Make your changes and click **Save**, or click **Delete** to remove it.

> Deleting a sermon is permanent. If you're unsure, consider leaving the sermon unpublished instead.

---

### Managing events

Events appear on the homepage and on a dedicated events page.

#### Adding an event

1. Click **Events** in the sidebar.
2. Click **+ New Event**.
3. Fill in: title, date, time, location, and a short description.
4. Click **Save**.

Events past their date are automatically moved to the archive and no longer show on the main events listing.

---

### Updating church info

To change service times, your address, phone number, or other general information:

1. Click **Settings** in the sidebar.
2. Click **Church Info**.
3. Update the fields and click **Save**.

Changes take effect immediately on the public website.

---

## Part 3 — Prayer Board

> **Phase availability:** This section will be completed after Phase 5.

The prayer board allows your congregation and visitors to submit prayer requests. Every request is reviewed before appearing publicly — nothing goes live without approval.

### How it works

1. A visitor fills out the prayer request form on your website.
2. The system automatically reviews the request for appropriateness.
3. You review it in the admin panel and approve or reject it.
4. Approved requests appear on the public prayer board (without any personal contact information).

### Moderating prayer requests

1. In the admin panel, click **Prayer Board**.
2. New submissions appear under the **Pending** tab.
3. Click a request to read it in full.
4. Click **Approve** to publish it or **Reject** to remove it.

Rejected requests are not deleted — they are archived in case you need to review them later.

### Notes on privacy

- Submitters' email addresses are stored securely on your server but are **never shown** on the public prayer board.
- The name or identifying details a submitter chooses to include in their prayer text is their own choice.
- You can always edit the text of a request before approving it if needed.

---

## Part 4 — Online Giving

> **Phase availability:** This section will be completed after Phase 7.

ChurchOS integrates with Stripe to accept online donations securely. Your church receives funds directly in your Stripe account.

### Setting up giving

Before accepting online gifts, you'll need a free [Stripe](https://stripe.com) account. Your developer will connect Stripe to ChurchOS.

### Giving funds

You can create multiple giving funds (e.g., General Fund, Building Fund, Missions). Each fund appears as an option on the giving page. Donors choose which fund to give to.

To add or edit funds:
1. Go to **Settings → Giving**.
2. Add fund names under **Giving Funds**.
3. Click **Save**.

### Viewing giving records

1. Click **Giving** in the sidebar.
2. The overview shows:
   - Total given this month
   - Total given this year
   - Recent transactions

You can filter by date range, fund, or donor.

### Member giving history

Members can view their own giving history when logged in. They can access this from their profile page on the member portal.

Only you (as admin) can see giving records for other members.

### Exporting for taxes

At the end of the year, you can export giving records as a CSV file for your treasurer or accountant. Go to **Giving → Export → Year-End Summary**.

---

## Part 5 — Member Directory

> **Phase availability:** This section will be completed after Phase 8.

The member directory is only visible to logged-in members — it is never publicly accessible. Each member decides exactly what contact information to share.

### Adding members

1. Go to **Members** in the sidebar.
2. Click **+ Invite Member**.
3. Enter the person's email address. They'll receive an invitation email with a link to create their account.

### What members control

Once a member has an account, they can update their own profile and choose what to show in the directory:

- ✅ or ❌ Show my email address
- ✅ or ❌ Show my phone number
- ✅ or ❌ Show my home address
- Profile photo (optional)

If a member opts out of all three, they still appear in the directory with just their name, so the congregation knows they're part of the church — but no contact details are shared.

### Admin view

As an admin, you can see all member records regardless of their visibility settings. You can also update a member's role (see Part 6).

---

## Part 6 — User Accounts & Roles

> **Phase availability:** This section will be completed after Phase 3.

ChurchOS uses a simple role system to control who can do what.

| Role | Who it's for | What they can do |
|---|---|---|
| **Admin** | Church administrator or pastor | Everything — full access to all content, settings, members, and giving records |
| **Staff** | Office staff, worship leaders | Manage sermons, events, and prayer board moderation |
| **Member** | Verified church members | Access the member directory and their own giving history |
| **Guest** | Everyone else | View public pages and submit prayer requests |

### Changing someone's role

1. Go to **Members** in the sidebar.
2. Find the person and click their name.
3. Under **Role**, select the new role from the dropdown.
4. Click **Save**.

> Only admins can change roles. Be thoughtful about who receives admin access — admins can see all data including giving records.

### Removing access

To revoke someone's access to the admin panel or member area:
1. Go to **Members** and find the person.
2. Change their role to **Guest**.

They will still have an account but will only see public pages.

---

## Part 7 — Settings & Configuration

> **Phase availability:** This section will be completed after Phase 4.

### Church Information

Located at **Settings → Church Info**. Update:
- Church name
- Address
- Phone number
- Email address
- Service times (multiple services supported)
- Social media links

### Design & Branding

Located at **Settings → Appearance**. Update:
- Primary color (used for buttons and links)
- Secondary color (accents)
- Church logo

> More advanced design changes (fonts, layout) require your developer to update the design system configuration file.

### AI Settings (Prayer Moderation)

Located at **Settings → AI**. Shows:
- Which AI provider is currently active (Gloo or Anthropic)
- Your Gloo theological tradition setting
- Your Gloo publisher name (for the "Ask Our Church" feature)

You generally do not need to change these settings after initial setup.

---

## Part 8 — Maintenance & Updates

> **Phase availability:** This section will be completed after Phase 10.

### Checking your current version

Your ChurchOS version appears in:
- The bottom of every page on your public website
- The top-right corner of your admin panel
- By visiting `https://api.yourdomain.com/health` in a browser

### Updating ChurchOS

ChurchOS is updated by your developer pushing changes through the standard GitHub workflow. When a new version is released:

1. Your developer pulls the latest code.
2. They test it on a staging environment first.
3. After confirming everything works, they deploy to production.

For patch updates (bug fixes), this is routine. For major updates, your developer will follow the migration guide included in the release notes.

### Backups

Your database is backed up automatically by Supabase every day. Free tier retains 7 days of backups. If you ever need to restore from a backup, contact your developer.

### Monitoring uptime

If your website goes down, you'll want to know about it quickly. Ask your developer to set up uptime monitoring (Sentry and Better Uptime both have free tiers).

---

## Appendix A — Glossary

| Term | What it means |
|---|---|
| **Admin panel** | The staff-only area at `admin.yourdomain.com` where you manage your site |
| **Supabase** | The service that stores your church's data |
| **Cloudflare** | The service that hosts your website and protects it |
| **Railway** | The service that runs your backend server |
| **RLS** | Row Level Security — a database feature that ensures members can only see their own records |
| **JWT** | A secure token that proves you're logged in |
| **Stripe** | The payment service used for online giving |
| **Gloo AI** | An AI platform built specifically for faith communities, used to moderate prayer requests |
| **Slug** | A URL-friendly version of a title, e.g., `my-sermon-title` |
| **Monorepo** | A single code repository containing all parts of the application |
| **Turborepo** | The tool that manages building and testing the monorepo |
| **Alembic** | The tool that manages database changes (migrations) |
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
4. Your ChurchOS version (check the footer or admin topbar)

---

*ChurchOS User Guide — updated with each phase release.*
*Current version: 0.1.0 pre-release | Phase 0 — Repo & Tooling*
