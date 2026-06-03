# MediMatch — Community Blood Coordination System

> Uganda's real-time platform connecting blood donors, community clinics, and blood banks.  
---

## Quick Start — 5 Commands

Open a terminal, navigate to the project folder, then run:

```bash
cd med/medimatch
# 1. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# 2. Install all dependencies
pip install -r requirements.txt

# 3. Run database migrations
python manage.py migrate

# 4. Populate the database with demo users and content
python manage.py seed_data

# 5. Start the server
python manage.py runserver
```

Open your browser: **http://127.0.0.1:8000**

> **Port busy?** Run `python manage.py runserver 8080` → open http://127.0.0.1:8080

---

## What Gets Seeded

Running `python manage.py seed_data` creates a fully populated database:

| Type | Count | Detail |
|------|-------|--------|
| Facilities | 5 | 3 clinics + 2 blood banks across Uganda |
| Staff accounts | 6 | 1 superadmin + 3 clinic admins + 2 bank admins |
| Donor accounts | 20 | All blood types, every status, 9 districts |
| Donation records | 10 | Historical donation history for key donors |
| Blood drive bulletins | 8 | Published drives, urgent appeals, awareness |
| SOS requests | 6 | Open / acknowledged / in_transit / resolved / cancelled |
| Transport requests | 5 | Pending / approved / completed |
| SOS status timelines | Full | Every SOS has its full audit trail |

---

## All Login Credentials

### Staff Accounts

| Role | Email | Password | Facility |
|------|-------|----------|----------|
| **Superadmin** | `admin@medimatch.ug` | `Admin1234!` | All facilities |
| **Clinic Admin** | `grace.nakato@medimatch.ug` | `Clinic1234!` | Mulago Community Health Centre |
| **Clinic Admin** | `robert.onen@medimatch.ug` | `Clinic1234!` | Kisenyi Health Centre IV |
| **Clinic Admin** | `sarah.akello@medimatch.ug` | `Clinic1234!` | Jinja Regional Referral Hospital |
| **Bank Admin** | `david.ssali@medimatch.ug` | `Bank1234!` | UBTS – Nakasero, Kampala |
| **Bank Admin** | `patricia.tumusiime@medimatch.ug` | `Bank1234!` | UBTS Regional Centre – Mbarara |

> **Admin panel:** http://127.0.0.1:8000/admin/ — login with `admin@medimatch.ug / Admin1234!`

---

### Donor Accounts — all passwords are `Donor1234!`

| Email | Blood Type | Status | District | Notes |
|-------|-----------|--------|----------|-------|
| `amina.nalumansi@donors.medimatch.ug` | O+ |  Approved | Kampala | 3 donations |
| `brian.okello@donors.medimatch.ug` | A+ |  Approved | Kampala | 7 donations |
| `catherine.achola@donors.medimatch.ug` | B+ |  Approved | Gulu | Needs transport |
| `daniel.mugisha@donors.medimatch.ug` | O- |  Approved | Mbarara | 12 donations |
| `esther.namukasa@donors.medimatch.ug` | AB+ |  Approved | Wakiso | New donor, 0 donations |
| `fred.wamala@donors.medimatch.ug` | A- |  Approved | Mbale | Needs transport |
| `grace.apio@donors.medimatch.ug` | B- | Approved | Lira | 4 donations |
| `henry.byaruhanga@donors.medimatch.ug` | O+ | Approved | Kabarole | 9 donations |
| `irene.atim@donors.medimatch.ug` | AB- |  Pending | Arua | New — awaiting review |
| `james.ssebulime@donors.medimatch.ug` | A+ |  Approved | Kampala | 6 donations |
| `kevin.opio@donors.medimatch.ug` | O+ |  Approved | Soroti | Needs transport |
| `lydia.nansubuga@donors.medimatch.ug` | B+ | Pending | Masaka | Needs transport |
| `moses.kato@donors.medimatch.ug` | O- |  Approved | Kampala | 15 donations — top donor |
| `norah.tumwine@donors.medimatch.ug` | A+ |  Approved | Kabale | 3 donations |
| `paul.lubega@donors.medimatch.ug` | AB+ |  Approved | Kampala | 1 donation |
| `rita.nabirye@donors.medimatch.ug` | A- |  Flagged | Mukono | Malaria in last 3 months |
| `sam.tugume@donors.medimatch.ug` | B+ |  Flagged | Kampala | Recent surgery + anticoagulants |
| `tina.akello@donors.medimatch.ug` | O+ |  Suspended | Kampala | HIV positive — disqualified |
| `umar.ssekandi@donors.medimatch.ug` | O- |  Pending | Kampala | New donor |
| `violet.nanteza@donors.medimatch.ug` | AB- |  Pending | Wakiso | Wheelchair user, needs accessible transport |

---

## Testing Workflows

Each workflow below can be tested independently. Start a fresh browser session per role.

---

### Workflow 1 — Register as a Brand New Donor

**Login required:** None (public)

1. Go to **http://127.0.0.1:8000/accounts/register/**
2. Click the ** Donor** role card → it highlights red
3. Fill in: first name, last name, email (e.g. `newdonor@test.com`), phone, password
4. Click **Create Account** → redirected to the 3-step donor registration wizard

**Wizard Step 1 — Personal Info:**
- Select blood type, date of birth (must be 18–65), gender
- Enter National ID (must be unique)
- Enter address and district → click **Next**

**Wizard Step 2 — Health Eligibility Checklist:**
- Answer all 13 Yes/No questions
- To test **auto-flagging**: answer **Yes** to "Have you had malaria in the last 3 months?"
- The system will automatically flag the profile — no staff action needed
- Answer all **No** for a clean profile → click **Next**

**Wizard Step 3 — Transport & Consent:**
- Tick **"I need transport assistance"** to expand transport notes field
- Tick the consent declaration (required)
- Click **✓ Complete Registration**

**Expected result:**
- Clean checklist → status = **Pending** (awaiting staff review)
- Any disqualifying answer → status = **Flagged** (shown in red on profile)
- Redirected to **My Donor Profile** page

---

### Workflow 2 — Clinic Admin Approves / Flags a Donor

**Login:** `grace.nakato@medimatch.ug` / `Clinic1234!`

1. Click **Find Donors** in the navbar → **http://127.0.0.1:8000/donors/**
2. You see the full donor registry table (20 seeded donors)

**Search & filter:**
- Filter by **Blood Type: O-** → shows Daniel Mugisha, Moses Kato, Umar Ssekandi
- Filter by **Status: Pending** → shows 4 donors awaiting review
- Filter by **Needs Transport: ✓** → shows 4 donors needing transport
- Filter by **District: Kampala** → shows Kampala-based donors only

**Approve a pending donor:**
1. Find **Irene Atim** (AB-, Pending) → click **View**
2. Review her profile, eligibility checklist, and personal details
3. Click **✓ Approve Donor** → status changes to Approved
4. An SMS + email notification is sent to the donor

**Flag a donor:**
1. Find any Approved donor → click **View**
2. Click **⚠ Flag** → status changes to Flagged
3. Use this to test the flagged state manually

---

### Workflow 3 — Explore Donor Profiles (All Statuses)

**Login:** Any clinic or bank admin

Visit these donors to see each status in action:

| What to see | Donor to visit |
|-------------|---------------|
| Approved, veteran donor | `moses.kato` — 15 donations, full history |
| Approved, transport needed | `catherine.achola` — Gulu, boda-boda note |
| Pending, new | `irene.atim` — AB-, no donations yet |
| Auto-flagged (malaria) | `rita.nabirye` — red flag badge, reason shown |
| Auto-flagged (surgery) | `sam.tugume` — two disqualifying conditions |
| Suspended | `tina.akello` — HIV positive, disqualified |
| Wheelchair / special needs | `violet.nanteza` — accessibility transport note |

---

### Workflow 4 — Post a Blood Drive Bulletin and Notify Donors

**Login:** `robert.onen@medimatch.ug` / `Clinic1234!`

1. Go to **Bulletins → + New Bulletin**
2. Fill in:
   - **Title:** e.g. "Emergency B- Drive — Kisenyi HC"
   - **Body:** describe the drive
   - **Category:** select **Urgent Blood Appeal**
   - **Blood types needed:** `B-, O-`
   - **Event date:** pick tomorrow's date
   - **Event time:** 08:00
   - **Event location:** "Kisenyi HC IV, Blood Collection Room"
   - **Status:** Published
3. Click **Save** → bulletin appears on the public board
4. On the bulletin detail page, click ** Send Notifications**
5. The system sends SMS to all approved donors matching the blood types
6. The notify button shows "Notifications sent" confirmation

**View public bulletins (no login):**
- Go to **http://127.0.0.1:8000/bulletins/**
- Filter by category or blood type using the bar at the top
- 8 seeded bulletins are already visible including urgent appeals

---

### Workflow 5 — Send an SOS Request (Clinic → Blood Bank)

**Login:** `sarah.akello@medimatch.ug` / `Clinic1234!` (Jinja clinic)

1. Go to **SOS Board → http://127.0.0.1:8000/sos/**
2. You see 6 seeded SOS requests in various states
3. Click **+ New SOS**
4. On the create page:
   - Click a **blood type tile** (e.g. AB-)
   - Click an **urgency tile** — Critical / Urgent / Standard
   - Set **Units needed** (e.g. 2)
   - Enter **patient condition** (brief clinical context only)
   - Select a **target blood bank** or leave blank to broadcast to all
5. Click **Send SOS** → blood bank admins notified by SMS

**Expected result:** SOS appears on the board with status **Open**, red pulse indicator, countdown to SLA deadline.

---

### Workflow 6 — Blood Bank Responds to an SOS

**Login:** `david.ssali@medimatch.ug` / `Bank1234!` (Nakasero)

1. Go to **SOS Board → http://127.0.0.1:8000/sos/**
2. You see all active SOS requests assigned to your bank
3. Find the **Open** SOS (post-partum haemorrhage, O-, Critical)
4. Click **View** → full detail page with patient context and timeline

**Acknowledge:**
- Click **Acknowledge** → status changes to **Acknowledged**
- A status update is logged in the audit trail below

**Dispatch blood:**
- Click **Mark In Transit** → status changes to **In Transit**
- Requesting clinic is notified

**Clinic resolves the SOS:**
- Switch to `grace.nakato@medimatch.ug` (Mulago clinic)
- Find the In Transit SOS → click **View**
- Enter resolution notes: e.g. "3 units received at 14:45. Patient stable."
- Click **Mark Resolved** → SOS closes with full audit trail

**Test overdue SOS:**
The seeded Critical SOS has a 1-hour deadline. If more than 1 hour passes without acknowledgement, it turns red and pulses. The board auto-refreshes every 30 seconds via HTMX.

---

### Workflow 7 — Manage Transport for a Donor

**Login:** `grace.nakato@medimatch.ug` / `Clinic1234!`

**View existing requests:**
1. Go to **http://127.0.0.1:8000/transport/**
2. Five seeded requests: 1 completed, 2 approved with vouchers, 2 pending

**Create a new transport request:**
1. Go to **Donors** → find `lydia.nansubuga` (B+, Pending, Masaka)
2. Click **View** → on her profile, click **+ Create Transport Request**
3. Fill in:
   - Pickup address: "Masaka Bus Park, opposite Centenary Bank"
   - Estimated cost: 20000
   - Funding source: NGO Partnership
4. Click **Save** → request created as Pending

**Approve the request:**
1. Go to **Transport** → find Lydia's request
2. Click **Approve** → a voucher code is generated (e.g. `MM-X7K2P9QR`)
3. The voucher is sent to the donor by SMS
4. The donor shows the voucher to the driver

**Complete the request:**
1. After donation, click **Mark Complete** → status becomes Completed

---

### Workflow 8 — Superadmin Panel

**Login:** `admin@medimatch.ug` / `Admin1234!`

**Dashboard (http://127.0.0.1:8000/dashboard/):**
- See live stats: total donors, active SOS, pending transport
- Blood type distribution bar chart
- Recent active SOS list
- All pending staff accounts requiring activation

**Admin panel (http://127.0.0.1:8000/admin/):**

| Section | What to do |
|---------|-----------|
| Accounts → Users | View all 26 users; activate pending staff by setting Active = True |
| Accounts → Facilities | View/edit 5 facilities; add new clinics or blood banks |
| Donors → Donor Profiles | Filter by blood type, status, district; bulk approve |
| Donors → Donation Records | Full donation history across all donors |
| Bulletins → Bulletins | Manage all 8 bulletins; bulk publish |
| Sos → SOS Requests | View all 6 requests with full details |
| Sos → SOS Status Updates | Full audit trail for every status change |
| Transport → Transport Requests | View all 5; see voucher codes |

**Activate a staff account (test this):**
1. In Admin → Accounts → Users
2. Find a staff user with **Active = No** (e.g. one you registered manually)
3. Click their name → tick **Active** checkbox → Save
4. Staff can now log in

---

### Workflow 9 — Donor Views Their Own Profile

**Login:** `amina.nalumansi@donors.medimatch.ug` / `Donor1234!`

1. Goes to **Dashboard** → sees donor-specific view
2. Clicks **My Profile** → sees:
   - Blood type badge (O+), Approved status, district
   - Age (auto-calculated from DOB)
   - Total donations: 3
   - Last donated: 1 Sep 2024
   - Next eligible donation date (90 days after last)
   - Donation history: 3 records at Mulago CHC
3. Profile photo placeholder (no photo uploaded — can upload one)
4. Eligibility checklist status: ✓ Clear

**Try with a flagged donor:**
Login as `rita.nabirye@donors.medimatch.ug` / `Donor1234!`
- Profile shows  Flagged status
- Warning message: "Flagged reason: Malaria Last 3months. A health officer will contact you."

---

### Workflow 10 — Public Browsing (No Login)

No account needed:

1. **Home page** — http://127.0.0.1:8000/
   - Hero banner, stats bar, how-it-works section
   - Latest 3 published bulletins shown
   - Call-to-action to register as donor

2. **Bulletins** — http://127.0.0.1:8000/bulletins/
   - 8 public bulletins visible
   - Filter by: All / Blood Drives / Urgent Appeals / Awareness
   - Filter by blood type dropdown
   - Urgent appeals have red left border and URGENT badge

3. **Register** — http://127.0.0.1:8000/accounts/register/
   - Role selector: Donor / Clinic Staff / Blood Bank
   - Staff roles show info banner: "Account pending administrator approval"

---

## Seeded Data Summary

### Facilities

| Name | Type | District |
|------|------|----------|
| Mulago Community Health Centre | Clinic | Kampala |
| Kisenyi Health Centre IV | Clinic | Kampala |
| Jinja Regional Referral Hospital | Clinic | Jinja |
| Uganda Blood Transfusion Service – Nakasero | Blood Bank | Kampala |
| UBTS Regional Centre – Mbarara | Blood Bank | Mbarara |

### SOS Requests (pre-seeded states)

| Blood Type | Urgency | Status | Facility |
|-----------|---------|--------|----------|
| O- (3 units) |  Critical | Open | Mulago → Nakasero |
| A+ (2 units) |  Urgent | Acknowledged | Kisenyi → Nakasero |
| B+ (4 units) |  Urgent | In Transit | Jinja → Mbarara |
| AB+ (1 unit) |  Standard | Resolved | Mulago → Nakasero |
| O+ (5 units) |  Critical | Resolved | Kisenyi → Broadcast |
| O- (2 units) |  Urgent | Cancelled | Jinja → Nakasero |

### Bulletins (pre-seeded)

| Title | Category | Facility |
|-------|----------|----------|
| Monthly Blood Drive — Mulago CHC | Blood Drive | Mulago |
| URGENT: O- Blood Needed — Kisenyi | Urgent Appeal | Kisenyi |
| World Blood Donor Day — Jinja | Awareness | Jinja |
| Emergency AB- Appeal — Mulago | Urgent Appeal | Mulago |
| Quarterly Drive — Kisenyi HC | Blood Drive | Kisenyi |
| Safe Blood Saves Lives Campaign | Awareness | Mulago |
| Staff Blood Drive — Jinja RRH | Blood Drive | Jinja |
| New Donor Registration Open | General | Mulago |

---

## All Application URLs

| Page | URL |
|------|-----|
| Home / Landing | http://127.0.0.1:8000/ |
| About | http://127.0.0.1:8000/about/ |
| Blood Drive Bulletins | http://127.0.0.1:8000/bulletins/ |
| Login | http://127.0.0.1:8000/accounts/login/ |
| Register | http://127.0.0.1:8000/accounts/register/ |
| Dashboard | http://127.0.0.1:8000/dashboard/ |
| Donor Registry | http://127.0.0.1:8000/donors/ |
| My Donor Profile | http://127.0.0.1:8000/donors/my-profile/ |
| Donor Registration Wizard | http://127.0.0.1:8000/donors/register/ |
| SOS Board | http://127.0.0.1:8000/sos/ |
| New SOS Request | http://127.0.0.1:8000/sos/create/ |
| Transport Requests | http://127.0.0.1:8000/transport/ |
| Django Admin Panel | http://127.0.0.1:8000/admin/ |

---



## Troubleshooting

| Problem | Solution |
|---------|----------|
| `Port 8000 is already in use` | `python manage.py runserver 8080` |
| `(venv)` not showing in terminal | Run `source venv/bin/activate` (Mac/Linux) or `venv\Scripts\activate` (Windows) |
| `ModuleNotFoundError: No module named 'django'` | Activate the venv first, then `pip install -r requirements.txt` |
| `No such table: accounts_customuser` | Run `python manage.py migrate` |
| `TemplateDoesNotExist` | Confirm you are inside the `medimatch/` folder (where `manage.py` is) |
| Login says "invalid credentials" | Run `python manage.py seed_data` first |
| Need to reset a password | `python manage.py changepassword email@example.com` |
| Want to clear all data and reseed | Delete `db.sqlite3`, run `migrate`, then `seed_data` |

---

## Technology Stack

| Technology | Role |
|-----------|------|
| **Django 5** | Web framework, ORM, admin panel |
| **SQLite** (dev) | Zero-config local database |
| **HTMX** | SOS board live refresh + donor search filtering |
| **django-allauth** | Email-based auth with password reset |
| **django-formtools** | Multi-step donor registration wizard |
| **Africa's Talking** | Uganda SMS gateway for donor notifications |
| **DM Serif Display + DM Sans** | Typography (Google Fonts) |

---


