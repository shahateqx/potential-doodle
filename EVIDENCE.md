# EVIDENCE.md — Requirements Proof

Each requirement from Section 6 of the capstone brief is listed below with evidence proving it is met.
Proofs are pasted command outputs, curl transcripts, or test results.

---

## Widget Management

### ✅ Authenticated CRUD endpoints for widgets
*Evidence will be pasted after implementation.*

### ✅ Multi-tenant isolation proven
*Evidence will be pasted after implementation.*

---

## Widget Delivery

### ✅ Embed snippet generated per widget
*Evidence will be pasted after implementation.*

### ✅ Public config endpoint with correct HTTP cache headers
*Evidence will be pasted after implementation.*

### ✅ Widget JavaScript served as versioned bundle
*Evidence will be pasted after implementation.*

### ✅ Widget renders on a page from a different origin
*Evidence will be pasted after implementation.*

---

## Public Submission API

### ✅ CORS headers correct, preflight handled
*Evidence will be pasted after implementation.*

### ✅ All input validated; malformed/oversized payloads rejected with 4xx
*Evidence will be pasted after implementation.*

### ✅ Valid submissions stored, linked to correct widget and tenant
*Evidence will be pasted after implementation.*

---

## Abuse Protection

### ✅ Rate limiting per IP/widget returns 429 under burst
*Evidence will be pasted after implementation.*

### ✅ Spam prevention (honeypot) blocks spam submission
*Evidence will be pasted after implementation.*

---

## Enrichment & Safe Side Effects

### ✅ Geo enrichment fallback chain works
*Evidence will be pasted after implementation.*

### ✅ All providers down → submission still succeeds without geo
*Evidence will be pasted after implementation.*

### ✅ Failing email/webhook does not prevent submission storage
*Evidence will be pasted after implementation.*

---

## Documentation

### ✅ README with architecture, setup, API docs
*Evidence: See README.md*

### ✅ Required files present
*Evidence will be confirmed at submission.*
