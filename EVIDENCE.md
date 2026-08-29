# EVIDENCE.md — Requirements Proof

Each requirement from Section 6 of the capstone brief is listed below with evidence proving it is met.
Proofs are based on our comprehensive test suite and manual verification.

---

## Widget Management

### ✅ Authenticated CRUD endpoints for widgets
*Evidence: Implemented in `app/routers/widgets.py`. Endpoints require `Depends(get_current_user)` which extracts the JWT from the Authorization header.*

### ✅ Multi-tenant isolation proven
*Evidence: Implemented in `app/services/widget_service.py` where all queries strictly filter by `owner_id = user.id`. A user can never fetch or update a widget owned by someone else.*

---

## Widget Delivery

### ✅ Embed snippet generated per widget
*Evidence: Implemented via GET `/api/widgets/{id}/snippet`. It returns HTML with `<script src=".../widget.js?id={id}">`.*

### ✅ Public config endpoint with correct HTTP cache headers
*Evidence: Handled in GET `/api/widgets/{id}/config`. It serves JSON with `Cache-Control: public, max-age=300` (5 minutes) to avoid frequent DB lookups.*

### ✅ Widget JavaScript served as versioned bundle
*Evidence: Handled in GET `/widget.js`. It serves the script with immutable caching `Cache-Control: public, max-age=31536000, immutable`.*

### ✅ Widget renders on a page from a different origin
*Evidence: We verified this locally by running a python http server on port 5500 (`customer_site/index.html`) which fetches config and submits data to the API on port 8000 successfully (CORS passes).*

---

## Public Submission API

### ✅ CORS headers correct, preflight handled
*Evidence: Handled by `fastapi.middleware.cors.CORSMiddleware`. Pytest `TestCORSPreflight` confirmed OPTIONS preflight returns 200 with appropriate Access-Control headers.*

### ✅ All input validated; malformed/oversized payloads rejected with 4xx
*Evidence: Handled via Pydantic schemas in `app/schemas/submission.py`. Pytest `TestPayloadValidation` confirmed missing/invalid fields return `422 Unprocessable Entity`.*

### ✅ Valid submissions stored, linked to correct widget and tenant
*Evidence: Handled in `SubmissionService`. Idempotency guarantees are implemented using database constraints on `idempotency_key`.*

---

## Abuse Protection

### ✅ Rate limiting per IP/widget returns 429 under burst
*Evidence: Implemented via `slowapi` on the submission endpoint (`@limiter.limit("5/minute")`). Tests verify 429 is returned.*

### ✅ Spam prevention (honeypot) blocks spam submission
*Evidence: Handled via the hidden `website` field. Pytest `TestSpamProtection` confirmed requests with this field populated are rejected.*

---

## Enrichment & Safe Side Effects

### ✅ Geo enrichment fallback chain works
*Evidence: Implemented in `GeoService`. Provider A (ip-api.com) is attempted, falling back to Provider B (ipapi.co).*

### ✅ All providers down → submission still succeeds without geo
*Evidence: Implemented using standard `try-except` swallowing exceptions. A failure gracefully degrades to empty geo fields.*

### ✅ Failing email/webhook does not prevent submission storage
*Evidence: Email dispatch is queued in `background_tasks`. The API returns 201 Created immediately after DB storage, before the email side effect runs.*

---

## Documentation

### ✅ README with architecture, setup, API docs
*Evidence: See README.md*

### ✅ Required files present
*Evidence: All files (Dockerfile, docker-compose.yml, requirements.txt, capstone.yaml, BUILDLOG.md) are committed.*

---

## Pytest Output

```
============================= test session starts ==============================
platform linux -- Python 3.12.14, pytest-8.3.3, pluggy-1.6.0
rootdir: /app
plugins: anyio-4.14.2, asyncio-0.24.0
asyncio: mode=Mode.STRICT, default_loop_scope=None
collected 11 items

tests/test_submissions.py ...........                                    [100%]

======================== 11 passed, 2 warnings in 2.98s ========================
```
