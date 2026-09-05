# SentinelJob AI — Domain, Email & Company Verification Architecture (Phase 5)

---

## 1. Executive Summary & Core Philosophy

The **Verification Engine** provides an out-of-band reputation and identity validation layer in SentinelJob AI. It operates as the third intelligence layer alongside the **NLP Machine Learning Classifier** and the **Deterministic Security Rule Engine**.

> [!IMPORTANT]
> **EVIDENTIARY PRINCIPLE — VERIFICATION IS EVIDENCE, NOT ABSOLUTE PROOF**:
> - **Domain Exists ≠ Company is Legitimate**: Malicious threat actors can register lookalike domains or compromise legitimate infrastructure.
> - **Recently Registered Domain ≠ Definitive Scam**: Early-stage startups, spin-offs, and legitimate new ventures register new domains frequently.
> - **Missing MX Records ≠ Fraud**: Pure redirect domains and microsites frequently do not configure inbound mail exchangers.
> - **Free Webmail (Gmail/Yahoo) ≠ Fraud**: Legitimate small business recruiters occasionally use personal email addresses.
> - **Low Risk Classification**: A low risk score means **"No significant suspicious indicators detected"** — the system **never claims** that a posting is proven legitimate.

The Verification Engine treats these attributes as **supporting signals** (capped at a maximum of 25 penalty points) that contribute to the multi-factor risk score.

---

## 2. RDAP Architecture vs. Deprecated WHOIS

Following ICANN's global policy transitions (2025 registration data guidelines), **Registration Data Access Protocol (RDAP)** is the definitive, structured mechanism for querying domain registration data:

- **Protocol**: Standardized JSON over HTTPS (`RFC 7480`, `RFC 7481`, `RFC 7482`).
- **Cryptographic Security**: Queries are encrypted end-to-end via TLS.
- **Structured Schemas**: Structured JSON responses parsing UTC `eventDate` timestamps (`registration_date`, `expiration_date`), `rdap_status`, `domain_age_days`, `entities` (`registrar_name`), and `nameservers`.
- **Privacy Handling**: Handles GDPR/ccTLD privacy-redacted fields gracefully without assuming missing data implies malicious concealment.

```
Client Request
      │
      ▼
URL Extractor & SSRF Firewall
      │
      ▼
Safe RDAP Client (HTTPS) ───► In-Memory TTL Cache (1 Hour)
      │
      ▼
ICANN / Registry Bootstrap Endpoint (rdap.org / iana.org)
      │
      ▼
UTC Event Timestamp (registration_date) & Domain Age (domain_age_days)
```

---

## 3. Safe DNS & MX Architecture

The DNS inspection module (`app/verification/dns_client.py`) performs fast, non-blocking queries:
- **A / AAAA Record Resolution**: Verifies whether the domain is routed to public IPv4 / IPv6 addresses.
- **Mail Exchanger (MX) Verification**: Verifies presence and preference ranking of corporate mail servers.
- **Nameserver (NS) Records**: Inspects authoritative nameservers.
- **DNS Rebinding Protection**: Resolved IPs are dynamically validated against the SSRF firewall before being accepted.

---

## 4. SSRF & Network Security Safeguards

To prevent Server-Side Request Forgery (SSRF) and intranet port reconnaissance, every user-supplied hostname and IP is validated through `app/verification/ssrf.py`:

| Forbidden Target | Subnet / Range | Security Action |
| :--- | :--- | :--- |
| **Localhost / Loopback** | `127.0.0.0/8`, `::1` | **Blocked Immediately** |
| **Private RFC 1918 IPv4**| `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16` | **Blocked Immediately** |
| **Link-Local IPv4** | `169.254.0.0/16` | **Blocked Immediately** |
| **Cloud Metadata Endpoints**| `169.254.169.254`, `metadata.google.internal` | **Blocked Immediately** |
| **Internal Domain Suffixes**| `.local`, `.localhost`, `.internal`, `.corp`, `.lan` | **Blocked Immediately** |

---

## 5. Recruiter Email & Company Consistency Analysis

Recruiter email addresses extracted from posting text are cross-referenced against extracted company websites:

| Case Scenario | Email Domain | Website Domain | Generated Signal | Risk Penalty |
| :--- | :--- | :--- | :--- | :--- |
| **Enterprise Match** | `recruiter@stripe.com` | `stripe.com` | *None (Consistent)* | `0 pts` |
| **Free Webmail Signal**| `recruitment@gmail.com` | `google.com` | `EMAIL_FREE_WEBMAIL` | `+4 pts` (Weak) |
| **Unrelated Domain** | `hr@apex-jobs.top` | `microsoft.com` | `EMAIL_DOMAIN_MISMATCH` | `+8 pts` (Medium) |
| **Unresolving Domain** | `careers@scam-fake.xyz`| `scam-fake.xyz` | `DOMAIN_NOT_RESOLVING` | `+10 pts` (High) |
| **Recent Registration**| `hr@brandnewportal.com`| `brandnewportal.com` | `DOMAIN_RECENT_REGISTRATION` | `+10 pts` (Medium) |

---

## 6. Multi-Layered Risk Synthesis Formula

$$\text{Final Risk Score} = \min(100, \text{ML Score (Max 35)} + \text{Rule Penalty (Max 65)} + \text{Domain Penalty (Max 25)})$$

### Calibrated Risk Tiers:
- **`0 – 29` = LOW RISK**: **No significant suspicious indicators detected.**
- **`30 – 59` = MEDIUM RISK**: **Elevated Caution / Unverified Attributes.**
- **`60 – 79` = HIGH RISK**: **Suspicious / High-Probability Scam.**
- **`80 – 100` = CRITICAL RISK**: **Severe Multi-Vector Threat / High Financial Danger.**

The combined domain penalty is capped at **25 points**, ensuring that external domain attributes can never dominate the overall risk score in isolation.
