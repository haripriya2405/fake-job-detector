# SentinelJob AI — Security Policy & Controls

## 1. Security Architecture Overview
SentinelJob AI implements defense-in-depth security across network, container, application, and ML layers.

---

## 2. Key Controls & Safeguards

### A. Network & SSRF Firewall
- Strict DNS resolution and pre-request IP inspection.
- Blocks `localhost`, `127.0.0.1`, `::1`, RFC1918 subnets (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`), cloud metadata (`169.254.169.254`), and internal TLDs (`.local`, `.corp`, `.internal`, `.lan`).
- Validates every hop in redirect chains.
- Limits maximum payload downloads to 5 MB with 8-second timeouts.

### B. Ingestion & File Upload Safety
- Maximum payload limit of 10 MB.
- Whitelisted MIME types (`application/pdf`, `image/png`, `image/jpeg`, `image/webp`).
- PDF documents are processed strictly as static text streams with zero macro or script execution.
- Images are protected against decompression bomb attacks using `PIL.Image.MAX_IMAGE_PIXELS` limits.
- Hard 10-second timeout on Tesseract OCR operations.

### C. Authentication & Access Control
- Passwords hashed using bcrypt.
- Stateless JWT authentication with HS256 signatures and 24-hour expiration.
- User isolation: All analyses and history records are restricted to the authenticated user ID.
- Tokens, passwords, and sensitive documents are excluded from log outputs.

### D. Rate Limiting & DoS Mitigation
- In-memory sliding-window rate limiting per client IP:
  - Auth endpoints: 15 requests/min
  - Ingestion/Analysis endpoints: 20 requests/min
  - General API: 60 requests/min
- Nginx reverse proxy enforces connection timeouts (15s connect, 60s read/send) and payload limits (15 MB).

### E. HTTP Security Headers
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Permissions-Policy: geolocation=(), camera=(), microphone=()`
- `Strict-Transport-Security: max-age=31536000; includeSubDomains` (production / HTTPS)
- `Content-Security-Policy: default-src 'self'; frame-ancestors 'none';`

---

## 3. Reporting Security Vulnerabilities
If you discover a potential security vulnerability within SentinelJob AI, please submit a responsible disclosure report to `security@sentineljob.ai`. Do not disclose vulnerabilities publicly until patched.
