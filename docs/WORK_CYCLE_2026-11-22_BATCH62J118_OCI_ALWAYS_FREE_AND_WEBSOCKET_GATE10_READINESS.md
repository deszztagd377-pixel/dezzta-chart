# DEZZTA CHART — Work Cycle 62J-118
## OCI Always Free due diligence and WebSocket / Gate 10 readiness

**Date:** 22 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Parent HEAD:** `7eabe53a4a623857a18761122d2d1df6b5d7fec1`  
**Scope:** official OCI Always Free terms, zero-cost hostname/TLS feasibility, WebSocket production acceptance blockers, Stage 1 / Gate 10 disposition  
**Cost policy:** ZERO COST. This is a documentation and evidence-reconciliation batch only. No account, cloud resource, deployment, public endpoint, production credential, paid service, device operation, or `main` change was created.

## 1. Exact-head repository CI — VERIFIED

The parent commit `7eabe53a4a623857a18761122d2d1df6b5d7fec1` was confirmed as the exact branch HEAD before this documentation batch. Its three workflows completed successfully against that exact SHA:

- Automated Tests #1953 — run `44982436097`: SUCCESS.
- CodeQL — run `44982436088`: SUCCESS.
- Full Git History Secret Audit — run `44982436076`: SUCCESS.

This confirms repository CI for the parent commit only. It does not establish that a public WSS endpoint, OCI host, production Redis, Firebase project, or real browser/Android production session exists.

The existing WebSocket repository test inventory remains:
- 17 WebSocket transport tests.
- 7 HTTPS ticket-exchange tests.
- 21 stream-supervisor/reconnect tests.
- Existing backend integration and security coverage for ticket scope, renewal, replay, snapshot, Redis guards and lifecycle failure handling.

Do not count a successful CI run as host or client acceptance.

## 2. OCI Always Free — what is genuinely free, and under which conditions

Oracle's current official documentation distinguishes the 30-day Free Trial from Always Free resources:

- The promotional Free Trial offers up to US$300 in credits for up to 30 days. It is not a long-term hosting plan and is not part of this project's zero-cost deployment budget.
- Oracle states that eligible Always Free resources are available for an unlimited period and remain available after the trial ends, provided the account remains active and the resources remain within Always Free eligibility and tenancy limits.
- The Console's **Always Free-eligible** label and actual tenancy usage limits are authoritative for each provisioned resource. A resource merely appearing in the Free Tier catalogue is not permission to exceed its Always Free quota.
- The Always Free offer is subject to regional capacity. Ampere A1 instances must be created in the tenancy's home region; an out-of-host-capacity error can prevent provisioning.
- Oracle does not provide an SLA or standard Oracle Support entitlement to an Always Free-only account.

### Relevant published quotas

The current Oracle Always Free resource documentation lists:

- Ampere A1: up to 1,500 OCPU-hours and 9,000 GB-hours per month, equivalent to a total of 2 OCPUs and 12 GB RAM across A1 instances.
- Block Volume: 200 GB total across boot and block volumes, with five volume backups. The boot volume consumes this same shared storage allowance.
- Flexible Load Balancer: one Always Free instance at 10 Mbps for eligible tenancies created on or after 15 December 2020.
- Outbound internet transfer: first 10 TB/month free; inbound transfer is free.
- Monitoring: 500 million ingestion data points and 1 billion retrieval data points.
- Notifications: 1 million HTTPS notifications and 1,000 email notifications per month.
- Vault: limited Always Free keys/secrets are available; this does not remove the need for independent recovery-key custody.

These are quotas, not a performance guarantee. The backend's actual storage growth, network throughput, Redis persistence, CPU/RAM use and backup size still require measurement.

### Conditions and operational risks

1. **Idle instance reclamation:** Oracle may reclaim an Always Free compute instance when, over a seven-day period, CPU utilization at the 95th percentile is below 20%, network utilization is below 20%, and (for A1) memory utilization is below 20%. A low-traffic backend can therefore be vulnerable to reclamation. Do not generate artificial load merely to evade this policy.
2. **Account inactivity:** Oracle's current Free Tier FAQ says accounts idle for 30 days or more may be considered abandoned and become eligible for suspension or termination. Keep the account owner responsible for reviewing account notices and terms.
3. **Capacity:** Free A1 capacity is not guaranteed in the chosen home region. No deployment date can be promised until capacity is actually confirmed.
4. **Signup verification:** Oracle requests accurate contact/billing information and a supported credit/debit card for identity verification. It may place a temporary authorization hold. This is not a reason to use another person's card or bypass checks. Because the project operator is a minor, any account eligibility, signup, identity/card verification and cloud ownership must be handled by a parent/guardian as the lawful account owner, with their consent.
5. **No SLA / limited support:** Always Free is suitable for development and a small proof of concept, not a contractual production-availability guarantee.
6. **Trial overages:** Never create paid resources during the trial and assume they will become free later. Do not upgrade to Pay As You Go. Do not treat promotional credits as the project budget.
7. **Resource changes:** Before any create/resize action, confirm the exact shape, image, boot volume, attached volumes, load balancer and every other resource are Always Free eligible in the actual home-region tenancy. Stop if the Console indicates a paid SKU, a billable overage, or an unclear charge.

**Conclusion:** OCI Always Free can remain free beyond the 30-day trial when the account and every resource remain eligible and within quota. It is not an unconditional promise that a server will run forever, remain unreclaimed, have guaranteed capacity, or carry a production SLA. The project's accurate claim is **“potentially long-lived zero-cost hosting within Oracle's current Always Free terms and limits,”** not “guaranteed free forever.”

## 3. Public HTTPS/WSS hostname and TLS — zero-cost feasibility

A stable public WSS endpoint requires more than a VM:

- An internet-reachable address and ingress route.
- A hostname that resolves to the current public address.
- A publicly trusted TLS certificate for that hostname.
- Automated certificate renewal and reverse-proxy WebSocket Upgrade support.

Current evidence:

- OCI documentation explains ephemeral and reserved public IPv4 addresses, but the sources reviewed for this batch do not conclusively establish that every desired public-IP configuration is free in every account/region/tenancy state. Do not infer zero cost solely from the ability to assign an IP. The adult account owner must verify the exact Console resource and pricing before use.
- Oracle's public DNS documentation allows public zones for publicly available domain names. A registered domain is still required; the existence of OCI DNS does not provide a free registered domain. Oracle's price list includes DNS query billing, so do not assume OCI public DNS is zero-cost without checking the applicable SKU and allowance.
- DuckDNS describes a free dynamic-DNS subdomain service and supports automated updates. Its terms reserve the right to change terms and suspend/remove domains. It is a candidate, not a guaranteed permanent hostname.
- Let's Encrypt states that its DV TLS certificates are free. It still requires successful proof of control of the public DNS name or IP address. Certificate issuance does not make the domain registration, DNS provider, public IP or hosting free.

**Candidate only, not accepted:** a DuckDNS subdomain updated to the OCI public IP, with Let's Encrypt HTTP-01 validation and automatic renewal, may provide a no-domain-purchase path. Before it can be used for Gate 35/36, the adult owner must verify current DuckDNS terms, OCI public IPv4 eligibility/cost, inbound port reachability, ACME issuance/renewal, certificate SAN/hostname validation, and browser/Android trust. If any step introduces a fee or unstable/unacceptable dependency, public WSS remains blocked under ZERO COST.

Do not put Redis on a public interface. Do not expose the FastAPI worker port directly. Redis stays loopback/private with TLS, hostname validation and a least-privilege ACL. The reverse proxy is the only public application ingress.

## 4. Recommended single-host OCI topology — conditional

This preserves the existing deployment design and avoids inventing new services:

- One eligible Ampere A1 instance.
- FastAPI backend, reverse proxy and local Redis on the same host.
- SQLite authoritative OHLCV database and durable outbox on a persistent boot/block volume.
- Redis bound only to loopback/private interfaces; TLS and dedicated least-privilege ACL.
- Reverse proxy terminates HTTPS/WSS and forwards to loopback FastAPI.
- Keep publisher/replica multi-host mode disabled for the first single-host acceptance. The default source-mode hub remains process-local.
- Use the existing backend container image only after ARM64 build and smoke validation.
- Preserve container UID/GID 10001 and prove volume ownership, restart persistence, WAL/SHM growth and disk-pressure behavior.
- No managed Redis, paid domain, paid DNS, paid load balancer, paid monitoring, paid backup, trial-credit resource or Pay As You Go upgrade.

A single VM is not high availability. A VM restart, host reclamation or regional capacity issue can interrupt service. Independent encrypted backup and a tested restore path remain mandatory.

## 5. WebSocket production acceptance — remaining evidence

Repository-side implementation and CI coverage are materially advanced, but production acceptance is still open.

| Acceptance item | Required external evidence | Current disposition |
|---|---|---|
| Real identity / Gate 20 | Actual Firebase project: valid, expired, revoked and wrong-project signed tokens; entitlement grant/revoke and renewal | OPEN |
| Redis / Gate 25 | Owner-host Redis TLS CA + hostname verification, least-privilege ACL, persistence, restart/failover, secret rotation and outage tests | OPEN |
| Global snapshot / Gate 25 & 36 | Exact snapshot bytes and SHA-256; authenticated install receipt on every required gateway; exact watermark alignment with publisher cursor | OPEN |
| Public transport / Gate 36 | Stable public hostname, trusted TLS, HTTPS ticket exchange, WSS Upgrade path, proxy timeouts and certificate renewal | OPEN |
| Real client lifecycle / Gate 36 | Browser and Android WebView foreground/background, network transition, expiry/revocation, reconnect, replay continuity and duplicate-stream checks | OPEN |
| Monitoring / Gate 38 | Owner-host durable metrics/log retention, alert route, operator acknowledgement, disk pressure and recovery drill | OPEN |

The production data path must not be enabled by guessing a runtime factory, snapshot watermark, Redis ACL or provider state. Source publisher and gateway replica roles remain separate unless a reviewed architecture explicitly changes that boundary. The source publisher checkpoint must match the exact global snapshot generation installed on every target gateway. Any retention gap must trigger explicit resnapshot recovery, never a silent cursor skip.

The client must continue to use HTTPS for short-lived, single-use WebSocket ticket issuance and WSS for the socket. Firebase ID tokens must not be placed in a WebSocket URL or raw auth frame. Redis remains private.

## 6. Stage 1 / Gate 10 — honest disposition

Gate 10 is still **0/10 formally closed**. The ten outstanding tracks are:

- Host/operator evidence: Gates 8, 30, 34, 35 and 39.
- Integration/acceptance evidence: Gates 20, 25, 31, 36 and 38.

OCI may provide a venue to collect some host evidence, but provisioning a VM alone closes none of these gates. In particular:
- Gate 8 requires real secret injection, file owner/mode, rotation and log-redaction evidence.
- Gate 30 requires a real backend database backup/restore drill. A separate Android-local database, if present, requires its own device-side acceptance and is not validated by OCI.
- Gate 34 requires persistent-volume identity, UID/GID 10001, restart and disk-pressure evidence.
- Gate 35 requires a verified public hostname and trusted HTTPS certificate.
- Gate 39 requires actual alert delivery, human acknowledgement and escalation.
- Gate 20 still requires a real Firebase project and signed-token/entitlement tests.
- Gate 25 still requires real Redis and snapshot/replica acceptance.
- Gate 31 still requires an independently controlled off-host encrypted backup and separately held recovery key.
- Gate 36 still requires public WSS and real browser/Android lifecycle acceptance.
- Gate 38 still requires the actual host's dashboards, retention, alerting and recovery evidence.

Stage 1 remains **30/40 = 75% provisional**. No points are awarded by this documentation, by CI alone, or by creating a cloud account. Stage 2 must not begin until all Stage 1 gates are actually accepted and the Stage 1 completion criteria are met. No stage is marked complete in this batch.

## 7. Indicator progress — complete ledger retained, no new credit

This batch does not change indicator formulas, data contracts, hooks, chart UI, renderers or indicator tests. The current source-backed ledger remains:

- SMA20 — 🟨 foundation; 20-close mean, first valid index 19.
- EMA20 — 🟨 foundation; SMA-seeded EMA, alpha 2/21, first valid index 19.
- RSI14 Wilder — 🟨 foundation; 14 close changes, first valid index 14.
- MACD12/26/9 — 🟨 foundation; MACD first valid index 25, signal/histogram first valid index 33.
- Bollinger20,2 — 🟨 foundation; 20-close mean ±2 population standard deviations, first valid index 19.
- Shared Indicator Hook — 🟨 foundation; validated backend snapshot, chart integration and full lifecycle still incomplete.
- Footprint — 🟧 synthetic educational accumulator only; reference image and reviewed blueprint required before visual implementation. OFF must preserve normal candle spacing; explicit ON alone enables spaced clusters.
- Heatmap — 🟥 not implemented; zero-cost source feasibility, user reference, validated contract, reviewed blueprint and renderer still required.
- Liquidation Maps — 🟥 not implemented; zero-cost source feasibility, validated calculation/data contract, reference/blueprint and renderer still required.

Shared indicator invariants remain: warm-up values are null rather than zero; values stay aligned to source candle indices; no future-candle repaint; stale series clear when symbol, venue, dataset, chart or timeframe changes. Do not begin Footprint or Heatmap visual work before the relevant user reference image(s) and reviewed blueprint are available. Aggregate indicator percentage remains unscored without approved weights and denominator.

## 8. Next safe sequence

1. Keep the verified repository CI baseline green.
2. Complete an ARM64 image build/smoke audit and a host configuration pack without provisioning.
3. Have the adult account owner independently verify current OCI eligibility, region capacity, exact Always Free labels, public-IP pricing, hostname/DNS terms and billing controls.
4. Only after adult owner consent and explicit authorization, consider provisioning strictly Always Free resources. No credentials or payment details are to be sent through chat.
5. Collect redacted host evidence for Gates 8, 30, 34, 35 and 39; complete the real Firebase, Redis, snapshot, backup, WSS and monitoring acceptance tracks.
6. Run the actual browser and Android WebView acceptance matrix.
7. Close Gate 10 only when every required artifact and operator sign-off is present. Then perform the Stage 1 exit review before entering Stage 2.

## 9. Official references reviewed on 22 November 2026

- Oracle Always Free resources and quotas: https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier_topic-Always_Free_Resources.htm
- Oracle Free Tier terms, account eligibility, trial and Always Free continuation: https://www.oracle.com/apac/cloud/free/faq/
- Oracle Free Tier account and post-trial behavior: https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier.htm
- Oracle public IPv4 address behavior: https://docs.oracle.com/en-us/iaas/Content/Network/Tasks/managingpublicIPs.htm
- Oracle OCI price list: https://www.oracle.com/cloud/price-list/
- Oracle DNS public zone documentation: https://docs.oracle.com/en-us/iaas/Content/DNS/Concepts/gettingstarted.htm
- DuckDNS free dynamic DNS description: https://www.duckdns.org/about.jsp
- DuckDNS terms of use: https://www.duckdns.org/tac.jsp
- Let's Encrypt certificate cost and validation: https://letsencrypt.org/docs/faq/
- Let's Encrypt ACME challenge types: https://letsencrypt.org/docs/challenge-types/

**Final status:** repository CI is green at parent HEAD; WebSocket production acceptance is not complete; OCI Always Free is a conditional candidate, not a guaranteed forever-on server; Gate 10 remains 0/10; Stage 1 remains 75% provisional; indicator ledger remains unchanged. No provisioning, deployment, paid resource, credential handling, device operation or `main` change occurred.
