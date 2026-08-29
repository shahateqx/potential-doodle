# Embeddable Widget & Lead-Capture Platform

A backend platform that lets customers create embeddable widgets (signup forms, contact forms, CTA popovers) and install them on any website with a single `<script>` tag. When a visitor interacts with the widget, the submission is validated, spam-filtered, geo-enriched, stored, and shown to the widget owner in a dashboard.

**FlyRank Internship · Backend Track · Capstone**

---

## Architecture

```
Widget Owner (authenticated)
    → POST /api/auth/register, /api/auth/login (JWT)
    → CRUD /api/widgets/ (tenant-isolated)
    → GET /api/widgets/:id/snippet → embed code
    → GET /api/dashboard/* → submissions + stats

Customer Website (any origin)
    <script src="http://localhost:8000/widget.js?id=WIDGET_ID">
          → GET /api/widgets/:id/config   (public · cached · CORS)
                → renders widget form on page

Website Visitor
    → POST /api/submissions/   (public · CORS · rate-limited)
          │ validation           — bad payload? → 4xx, never 500
          │ rate limit + spam    — flood? → 429 · honeypot? → reject
          │ geo enrichment       — Provider A → Provider B → store anyway
          │ store submission
          │ email side effect    (failure does NOT block success)
```

### Layered Architecture

```
┌──────────────────────────────────────┐
│           HTTP Layer (Routers)       │  ← FastAPI routes, CORS, rate limiting
├──────────────────────────────────────┤
│         Business Logic (Services)    │  ← Validation, geo enrichment, spam check
├──────────────────────────────────────┤
│           Data Layer (Models)        │  ← SQLAlchemy models, Alembic migrations
├──────────────────────────────────────┤
│           PostgreSQL Database        │  ← Docker, tenant-isolated
└──────────────────────────────────────┘
```

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.12 |
| Framework | FastAPI |
| Database | PostgreSQL 16 (Docker) |
| ORM | SQLAlchemy 2.0 (async) |
| Migrations | Alembic |
| Auth | JWT (python-jose + passlib) |
| Validation | Pydantic v2 |
| Rate Limiting | slowapi |
| Geo Enrichment | ip-api.com + ipapi.co |
| Email | Console log (Mailpit optional) |
| Containerization | Docker + Docker Compose |

---

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.12+ (for running seed script locally)

### 1. Clone and configure
```bash
git clone https://github.com/shahateqx/potential-doodle.git
cd potential-doodle
cp .env.example .env
```

### 2. Start the platform
```bash
docker compose up --build
```

This starts:
- **PostgreSQL** on port 5432
- **FastAPI app** on port 8000
- Runs Alembic migrations automatically

### 3. Seed demo data
```bash
python seed.py
```

Creates 2 users, 3 widgets, and 5 sample submissions.

### 4. Test the customer site (second origin)
```bash
cd customer_site
python -m http.server 5500
```

Open `http://localhost:5500` — this is a different origin from the API (`localhost:8000`), proving CORS works.

---

## API Documentation

### Auth
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register a new user |
| POST | `/api/auth/login` | Login and get JWT token |

### Widgets (authenticated)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/widgets/` | Create a widget |
| GET | `/api/widgets/` | List your widgets |
| GET | `/api/widgets/{id}` | Get a widget |
| PUT | `/api/widgets/{id}` | Update a widget |
| DELETE | `/api/widgets/{id}` | Delete a widget |
| GET | `/api/widgets/{id}/snippet` | Get embed snippet |

### Public (no auth)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/widget.js` | Embeddable JS (versioned, cached 1yr) |
| GET | `/api/widgets/{id}/config` | Widget config (cached 5min, CORS) |
| POST | `/api/submissions/` | Submit form data (CORS, rate-limited) |

### Dashboard (authenticated)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/dashboard/submissions` | List submissions |
| GET | `/api/dashboard/stats` | Aggregated stats |
| GET | `/api/dashboard/widgets/{id}/stats` | Per-widget stats |
| GET | `/api/dashboard/geo` | Geo breakdown |

### Interactive docs
Visit `http://localhost:8000/docs` for Swagger UI.

---

## Design Decisions

### Data Model
- **Users** are tenants — each owns widgets and can only see their own data
- **Widgets** define form type, fields, display options — stored as JSON for flexibility
- **Submissions** link to widgets with geo-enrichment data and idempotency keys

### Security
- **Tenant isolation**: Every query filters by `owner_id` — one tenant can never see another's data
- **Input validation**: Pydantic schemas validate at the HTTP boundary — bad input → 4xx, never 500
- **Rate limiting**: Per-IP limits via slowapi → 429 under burst
- **Honeypot**: Hidden `website` field — bots fill it, humans don't
- **Secrets**: All in `.env`, never committed, `.env.example` with placeholders

### Resilience
- **Geo fallback chain**: ip-api.com → ipapi.co → store without geo data
- **Safe side effects**: Email failure doesn't block submission storage
- **Idempotency**: Duplicate submissions with same key are deduplicated

### Non-goal
This is a backend capstone. The widget UI is intentionally minimal — a functional form, not a polished frontend. The grade lives in the backend architecture, security, and resilience.

---

## Limitations

- The widget UI is minimal (functional form, not a design system)
- Email notifications log to console (no real SMTP configured by default)
- Geo enrichment depends on free API tiers with rate limits
- No real CDN — everything runs locally
- Rate limiting uses in-memory storage (resets on restart)

---

## Project Structure

```
├── app/
│   ├── main.py              # FastAPI app, CORS, middleware
│   ├── config.py            # Settings from environment
│   ├── database.py          # SQLAlchemy async engine
│   ├── models/              # Data layer (SQLAlchemy)
│   ├── schemas/             # Validation layer (Pydantic)
│   ├── routers/             # HTTP layer (FastAPI routes)
│   ├── services/            # Business logic layer
│   ├── middleware/           # Rate limiting
│   └── static/widget.js     # Embeddable widget script
├── migrations/              # Alembic migrations
├── tests/                   # Test suite
├── customer_site/           # Second-origin test page
├── seed.py                  # Demo data seeder
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── capstone.yaml            # Evaluator manifest
├── EVIDENCE.md              # Requirements proofs
└── BUILDLOG.md              # AI usage log
```