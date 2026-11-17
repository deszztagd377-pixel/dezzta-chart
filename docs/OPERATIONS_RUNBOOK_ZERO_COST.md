# DEZZTA CHART — Zero-cost operations runbook (Gates 38–39)

Status: **DOCUMENTED / NOT YET OPERATIONALLY ACCEPTED**  
Date: 2026-11-17  
Applies to: existing process-local metrics and local alert reporter only  
Owner constraint: one Android phone; no PC, laptop, second phone, or independently operated production host is currently available.

## 1. Safety and ownership

This runbook is for a **designated responsible adult system owner and an authorized maintainer**. The project owner is not the on-call operator and must not be asked to handle production credentials, billing settings, server administration, or incident response alone.

- No paid plan, external notification provider, trial, payment method, or billing activation is permitted.
- Do not share secrets, bearer tokens, Firebase credentials, user IDs, FCM tokens, event payloads, or private account data in chat, screenshots, issues, or logs.
- Do not enable the alert worker merely to test the reporter. It is disabled by default and production prerequisites remain unaccepted.
- If the host, access control, data retention, or no-billing status cannot be verified, stop and record the gate as constrained/open. Never weaken authentication or expose an operations endpoint publicly.

## 2. Gate 38 — process-local metrics

### Existing implementation

- Metrics route: `GET /internal/metrics`.
- Alert worker status route: `GET /internal/alert-delivery`.
- Both routes are registered only when `OBSERVABILITY_METRICS_TOKEN` is configured.
- Authentication is an `Authorization: Bearer` header; the configured token must be 32–256 non-whitespace characters.
- Responses set private/no-store headers.
- Metrics contain bounded method/route/status counters and latency histograms. Route labels are sanitized and total route series are capped at 127 including overflow.
- The metrics scope is `process_local_since_start`: counters reset when the process restarts and are not aggregated across instances.
- HTTP request logs deliberately omit raw URLs, query strings, path parameters, headers, and client addresses.

### Authorized operator review

1. Confirm the host and deployment identity through its trusted administration console.
2. Confirm the metrics token is injected through the host's protected secret mechanism; never put it in a URL, source file, frontend bundle, shell history, screenshot, or chat.
3. Request the two operations routes only from an authorized, protected operator context.
4. Verify expected schema, process-local scope, 127-series ceiling, and no sensitive identifiers.
5. Record whether logs/metrics are collected, retention is bounded, access is restricted, and disk-pressure behavior is tested.
6. If the process restarts or traffic is spread across instances, do not interpret the snapshot as durable or fleet-wide monitoring.

### Gate 38 acceptance evidence still required

- Actual owner-controlled host and protected token injection.
- Self-hosted collector or explicitly accepted minimal local collection.
- Bounded retention/rotation and disk-pressure test.
- Dashboard access-control test and a sanitized sample incident trace.
- Evidence that monitoring remains within the zero-incremental-cost constraint.

A passing unit test or process-local endpoint does not satisfy these external requirements.

## 3. Gate 39 — local alert signals

The existing opt-in delivery worker sends sanitized records to the application logger. Current event names are:

| Event | Meaning | Required operator interpretation |
|---|---|---|
| `alert_delivery_attention` | Retry scheduled, terminal failure, or lease lost | Delivery is degraded; inspect sanitized counters |
| `alert_delivery_worker_error` | Worker exception | Worker encountered an error; only exception class is logged |
| `alert_delivery_recovered` | Worker returned to a healthy batch after degradation | Recovery signal; independently verify service health |

The reporter deduplicates repeated states and does not log owner IDs, installation IDs, FCM tokens, provider/event payloads, credentials, or raw exception messages. These records are local application logs, not push notifications or guaranteed out-of-band alerts.

### Incident procedure for the authorized adult operator

1. **Acknowledge:** record UTC time, deployment/revision, event name, and sanitized counters. Do not copy credentials or user-level payloads.
2. **Classify:** distinguish retry-only degradation, terminal failure/lease loss, and worker exception. A repeated state is not a new incident merely because a polling cycle occurred.
3. **Contain:** do not manually edit the database, replay real user notifications, weaken authentication, or enable a disabled worker. Use only an already-reviewed host control and documented change procedure.
4. **Escalate:** notify the designated adult system owner through an already-approved channel only after confirming the channel is available without incremental charges and is appropriate for the information. No channel is assumed to be free or configured by this document.
5. **Recover:** the authorized maintainer investigates the host/service and data integrity, applies an approved correction, and verifies a healthy recovery event plus independent health checks.
6. **Close:** record acknowledgement, actions, recovery evidence, and remaining risk. If no responsible operator observes the alert, Gate 39 has not passed.

### Safe test boundary

- Current reporter unit tests verify warning/error/recovery transitions, deduplication, redaction, and counter validation.
- Those tests are not a live worker drill, not proof of log collection, and not proof that a responsible operator received an alert.
- Do not induce failures against real users or enable FCM for acceptance testing. Any future operational drill must use an isolated synthetic environment and adult authorization.

### Gate 39 acceptance evidence still required

- Actual host log collection and bounded retention.
- A named responsible adult operator and documented escalation path.
- A no-cost, privacy-reviewed channel that is verified to be available; otherwise explicitly defer out-of-band delivery.
- An isolated failure/acknowledgement/recovery exercise with sanitized evidence.

## 4. Current phone-only and ZERO COST disposition

The present owner environment has one Android phone and no separate host or second device. This repository can be inspected and tested remotely, but cannot manufacture independent host monitoring, durable cross-instance metrics, or an operator escalation channel from documentation alone.

No Termux command or package is required for this runbook. Do not install packages, alter Termux repositories/keyrings, create cloud resources, add payment details, or enable a paid plan to satisfy these gates.

**Disposition:** Gate 38 and Gate 39 remain OPEN / externally unaccepted. The runbook documents the safe procedure and evidence boundary; it does not claim an operational system or on-call service exists.
