# DEZZTA CHART — Zero-cost owner policy

Decision owner: project owner
Decision date: 2026-11-10
Status: **MANDATORY — ZERO INCREMENTAL SPEND**

## Non-negotiable rule

DEZZTA CHART must not create a payment obligation for the owner. The project must operate without paid subscriptions, metered API usage, paid hosting, paid managed databases, paid market-data feeds, paid monitoring, paid backup storage, paid email/SMS delivery, or paid add-ons.

This is a hard architecture and release constraint, not a preference or a temporary budget target. No developer, automation, CI workflow, deployment guide, or runtime fallback may enable a billable resource without a separate explicit owner decision. Silence, a green CI run, or an available free trial is not authorization.

"Free tier" is not automatically acceptable. A service is disallowed if it requires a payment method that can be charged, automatically upgrades, permits usage overages, converts a trial into a paid plan, or has unclear billing controls. Do not attach a payment card or enable billing to unlock a quota.

## Explicit prohibitions

- No Databento paid API, dataset, historical request, live subscription, or entitlement. Keep provider ingestion disabled unless a genuinely no-cost and legally permitted source is independently verified.
- No Fly.io deployment, Machine, Volume, managed Redis, or other paid resource under the current decision. Existing Fly deployment notes are historical design work only and are superseded by this policy.
- No paid Redis/hosting/database service. Do not silently replace Redis with an insecure in-memory guard; any zero-cost single-host alternative must preserve atomic shared limits, leases, fail-closed behavior, and receive tests and review before use.
- No Firebase Blaze upgrade, phone/SMS authentication, paid identity add-on, or billing activation. Firebase may only be considered on a no-billing configuration such as Spark, subject to current quota/terms verification; if it requires billing to continue, disable that integration rather than upgrade.
- No paid backup bucket, paid object storage, paid encryption/KMS service, paid external monitoring, paid log retention, paid alert routing, email/SMS delivery, domain, CDN, or observability add-on.
- No free trial, promotional credit, auto-renewing subscription, usage-based plan with possible overage, or service whose billing status cannot be verified.
- No automated command or CI action may provision resources, enable billing, add a payment method, upgrade a plan, or create a paid subscription.

## Allowed approach

- Prefer local development and self-hosting on hardware and network resources the owner already has, with no new paid infrastructure commitment. Explain any incremental electricity, data, or hardware implications rather than pretending they are zero.
- Prefer open-source software that can be run locally without a license fee. Software being open source does not make the host, storage, bandwidth, or operations free.
- Use no-billing free plans only after verifying current terms, quotas, expiry/pausing behavior, and that no payment method or automatic upgrade can create a charge. Record the verification date and exact feature limits.
- Keep market-data source selection provider-neutral. Use only data that is genuinely free to access, lawful for the intended display/redistribution, and sufficient for the claimed latency, instruments, and history. If no source meets the requirements, show an explicit unavailable/delayed/degraded state; never fabricate data or silently switch to a paid feed.
- Keep optional integrations disabled by default. No credential or API key may be requested or used for a paid service.

## Consequences for current Stage 1 design

1. The existing Fly.io deployment plan is on hold and must not be executed under this policy.
2. The current production configuration requires TLS Redis. This is not permission to purchase managed Redis. A no-cost hosting topology must be designed and tested before changing that security requirement.
3. Firebase Authentication is not permission to enable billing. Use only a verified no-billing setup and non-billable authentication methods; otherwise defer production authentication integration.
4. Databento remains disabled. Its existing SDK integration is not an authorized live-data source under this policy.
5. External backup, monitoring, and alerting must use a genuinely no-cost self-hosted or no-billing option, or remain explicitly unverified. Do not send operational data to a paid service.
6. CI may use the repository's existing GitHub Actions allowance only within the account's actual included quota. Do not enable paid runners, purchase minutes, or upgrade a plan. If included quota is exhausted, pause CI rather than incur charges.
7. A no-cost design may have lower availability, slower updates, reduced coverage, manual operation, or local-only access. State these trade-offs clearly.

## Required zero-cost preflight for every dependency/service

Before adding or enabling any external service, document:
- exact service, plan, features, and intended use;
- whether payment details are required;
- whether billing can be enabled or a trial can auto-convert;
- hard quota limits and behavior at quota exhaustion;
- whether overages or automatic upgrades are possible;
- data licensing/redistribution restrictions;
- how to disable/remove the service before any charge can occur.

If any answer is unknown, do not enable the service. If there is no reliable way to guarantee zero charges, reject it.

## Acceptance rule

Stage 1 cannot be accepted as compliant until the selected runtime, authentication, market-data source, persistence/backup, and operations path have a documented zero-cost design and reproducible tests. A free-tier label alone is insufficient. Any requirement that cannot be met at zero incremental cost must be marked constrained or deferred, not solved by introducing a bill.

This policy does not guarantee that unrelated services in the owner's personal accounts are free. Project documentation and repository changes cannot inspect or control the owner's Gmail, Google Cloud, Firebase, GitHub, hosting, or payment-account billing settings. The owner must verify those account-level settings directly; no secrets or payment details should be shared in chat.

## Owner approval

The project owner explicitly confirmed on 2026-11-10 that **all DEZZTA CHART data and infrastructure must remain ZERO MONEY**, with no unexpected future charge. This decision supersedes any earlier hosting/provider preference that conflicts with this policy.
