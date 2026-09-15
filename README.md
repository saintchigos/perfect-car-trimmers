# Perfect Car Trimmers — Booking Platform

A Django implementation of the "Automated Online Booking & Customer
Acquisition Platform" proposal, built for the auto upholstery / car roof
lining repair shop (Midrand).

**The business name is just a placeholder in `SHOP_NAME`** — it's easy to
swap for whatever the client finally settles on. Change it once in
`carecare_booking/settings.py` and it updates everywhere (nav, footer, page
titles, WhatsApp messages).

## Design

The site uses a warm, energetic craftsmanship look — deep espresso-brown
base, punchy sunset-orange for calls to action, and gold for trust/rating
accents — built to feel inviting to a customer rather than a spec sheet.
A recurring "stitch-line" dashed motif (a nod to literal leather stitching)
is used sparingly as a signature device, and shows up in the logo itself:
a car roofline traced with a gold stitch line (`static/img/logo-mark.svg`,
also used as the favicon — it's one SVG file, easy to swap for a real logo
later without touching any template). Fonts: Poppins (headings/buttons),
Inter (body). All tokens live at the top of `static/css/site.css` — change
the CSS variables there to retheme the whole site in one place. Tested with
no horizontal overflow from 375px (phone) through 1440px (desktop), plus a
sticky mobile call/book bar since most visitors from ads will land on a
phone.

### Editing homepage content (no code needed)
Go to `/admin/` → **Site Content** to edit, without touching any code:
- The hero headline, sub-line, and an optional hero background photo
- The Google rating badge (score + review count) shown on the homepage —
  update this whenever the shop's Google rating changes
- The "Our Story" / about section heading, text, and photo

Gallery before/after photos and fabric swatches are still managed under
**Gallery Items** and **Fabric Options** in the same admin.

## What's built (maps to the proposal)

| Proposal feature | Where it lives |
|---|---|
| Time-Slot Scheduling | `bookings.TimeSlot` model + slot picker on the booking form |
| Booking confirmations | `Booking` model + confirmation page |
| 1-Click WhatsApp Direct | Confirmation page generates a `wa.me` link pre-filled with the customer's name, vehicle, slot and damage notes, sent to the shop's real WhatsApp number |
| Deposit / upfront payment option | `deposit_required` / `deposit_paid` fields on `Booking` (checkbox at booking time; actual payment collection is a Phase 2 item — see below) |
| Mobile / On-site repair requests | `service_mode` choice on `Booking` (drop-off / pick-up / on-site) + free-text location field |
| Fabric & Style Customizer | `FabricOption` model, selectable at booking time |
| Before & After Gallery | `GalleryItem` model + `/gallery/` page — pre-loaded with 12 real completed-work photos supplied by the client |
| Shop management (admin) | Django admin at `/admin/` — full control: slots, bookings, fabric options, gallery |
| **Staff activity dashboard** | `/staff/` — a simpler, non-technical view for workers: today's schedule, pending/confirmed counts, deposit status, and one-click status updates without touching the Django admin |

### Real business details wired in
- WhatsApp / phone: `+27 81 855 1252`
- Facebook: linked in the footer
- Location: Google Maps link in the footer ("📍 Find Us")

All of these live in `carecare_booking/settings.py` under `SHOP_*` — change them there if any detail changes.

### Staff Dashboard (`/staff/`)
A separate, simplified view for whoever is running the shop floor — no need to learn the full Django admin:
- Stats: pending bookings, confirmed today, deposits outstanding, total upcoming
- Today's Schedule and Upcoming Bookings tables
- Filter by status
- Inline dropdown to update a booking's status (and mark a deposit as paid) without leaving the page

Access is restricted to staff accounts (`is_staff=True`). Create one with:
```bash
python3 manage.py createsuperuser
```
Then log in at `/admin/login/` — it'll redirect you into `/staff/` if you were trying to reach it, and a "Staff Dashboard" link appears in the nav bar once logged in.

### Not yet automated (flagged for Phase 2)
The proposal mentions *automated* SMS/WhatsApp sending and a full local-SEO push. Those need external services this scaffold doesn't wire up yet:
- **Automated WhatsApp/SMS confirmations** — currently the customer taps a
  button to send WhatsApp themselves (zero cost, no API needed). Fully
  automatic sending requires the WhatsApp Business API or a provider like
  Twilio.
- **Online deposit payments** — the checkbox just flags intent; taking real
  money needs a gateway (PayFast, Yoco, or Paystack are common in South
  Africa).
- **Local SEO** — this is meta tags/content, not code; happy to help with
  page copy once you're ready.

## Before you launch this for real

1. Double check `SHOP_WHATSAPP_NUMBER`, `SHOP_FACEBOOK_URL`, and `SHOP_MAPS_URL`
   in `carecare_booking/settings.py` match exactly what was supplied.
2. Add/replace gallery photos and fabric swatches via `/admin/` as the
   client sends more, and fill in **Site Content** (hero text, about text,
   Google rating) with the real copy.
3. Create a staff login for whoever will run the front desk — don't give
   them the superuser account; a plain staff account (`is_staff=True`,
   `is_superuser=False`) is enough for `/staff/` and keeps them out of
   the full admin.
4. **Security — do this before the site is public:**
   - Copy `.env.example` to `.env` and fill in every value — a real
     `DJANGO_SECRET_KEY` (command to generate one is right there in the
     file), `DJANGO_DEBUG=False`, and `DJANGO_ALLOWED_HOSTS` set to your
     real domain. Never commit `.env`.
   - Set `DJANGO_ADMIN_URL` in `.env` to something private instead of the
     default `admin/`, e.g. `roofline-team/`.
   - Run `python3 manage.py check --deploy` with your real `.env` loaded —
     it should come back clean.
   - Use a strong, unique password for the superuser account, and only
     ever access `/admin/` (or your custom admin path) over HTTPS.
   - Once `DEBUG=False`, run `python3 manage.py collectstatic` before
     deploying — WhiteNoise serves the compressed static files from there.
   - What's already handled for you: HTTPS redirect + HSTS, secure/HttpOnly
     cookies, clickjacking protection, a 5MB cap on every image upload
     (damage photos, gallery, fabric swatches, site content), server-side
     validation that uploaded "images" are actually images, and a honeypot
     field on the public booking form to cut down on bot spam.
5. Set up a real database backup (even a scheduled copy of `db.sqlite3`
   somewhere safe) before it's holding real customer bookings.
6. **Keep time slots topped up.** `seed_demo_data` only creates slots for the
   14 days *from the moment you run it* — it does not run itself. If it
   isn't re-run, every slot eventually falls into the past and the booking
   page will look empty with nothing to pick ("no bugs", just no future
   slots left). Re-run it periodically — e.g. a weekly cron job:
   `0 6 * * 1 cd /path/to/project && venv/bin/python manage.py seed_demo_data`
   — or add slots manually any time under **Time Slots** in `/admin/`.
   Running it repeatedly is always safe; it only adds new slots and never
   duplicates or removes existing ones.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env             # then edit .env — see "Before you launch" below
python3 manage.py migrate
python3 manage.py seed_demo_data      # sample fabric options + rolling 14 days of slots
python3 manage.py seed_gallery_photos # loads the 12 real completed-work photos
python3 manage.py createsuperuser     # for /admin/ and /staff/
python3 manage.py runserver
```

Visit `http://127.0.0.1:8000/` for the site, `/admin/` for full shop management, `/staff/` for the simplified activity dashboard (log in first).

For local development you can skip `.env` entirely — the project falls back to safe development defaults (`DEBUG=True`, `localhost`/`127.0.0.1` allowed). The `.env` file only becomes required once `DJANGO_DEBUG=False`.

## Project layout

```
carecare_booking/    # project settings, root urls
bookings/            # the whole app: models, views, forms, admin, templates
  models.py          # FabricOption, TimeSlot, GalleryItem, Booking
  forms.py           # BookingForm (hides full slots, validates availability)
  views.py           # home, gallery, book, confirmation, staff_dashboard, update_booking_status
  admin.py            # full shop-facing management screens
  context_processors.py  # injects shop name/phone/Facebook/Maps into every template
  seed_assets/gallery/   # the 12 real photos supplied by the client
  templates/bookings/
    staff_dashboard.html, _booking_table.html   # the staff activity view
  management/commands/
    seed_demo_data.py       # fabric options + sample time slots
    seed_gallery_photos.py  # loads the real photos into the gallery
```

