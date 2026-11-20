# DEZZTA CHART — Cross-device and remote-access architecture

**Decision date:** 20 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Status:** Architecture decision / implementation not authorized  
**Owner constraint:** ZERO COST — no payment method, paid tier, trial, paid domain, hosting, managed database, or usage-based bill.

## 1. Product requirement

The target is one DEZZTA CHART account and data experience across:
- Android phones and tablets (APK sideload is acceptable);
- iPhone/iPad where a compatible web/PWA client is provided;
- Windows/macOS/Linux PCs and laptops through a responsive web client;
- Wi-Fi and mobile-data connections, including when the client and backend are on different networks.

The same user should not need a separate project or separate data store on each device. Authentication, entitlement checks, chart preferences and durable market-data state must be served by a shared backend contract.

## 2. Important distinction: APK distribution vs backend hosting

Installing an APK outside Google Play does **not** remove the need for a server. APK distribution only determines how the Android client is installed and updated.

A single-device/offline build can run without a remote backend, but cross-device account synchronization, shared persistent data, authenticated WebSocket streams and remote access require a backend endpoint reachable by every client.

## 3. Candidate topologies and constraints

| Topology | Wi-Fi/LAN | Different networks / mobile data | Availability | Decision |
|---|---|---|---|---|
| Backend on Infinix, loopback only | Host phone only | No | Depends on Termux process | Useful for local development only |
| Backend on Infinix, LAN bind | Devices on same LAN | Not by itself | Phone must stay powered and process alive | First controlled network test |
| Phone backend + private mesh VPN | Enrolled devices only | Yes, if each device joins the private network | Phone and mesh connectivity required | Possible owner-only experiment; not public access |
| Phone backend + temporary public tunnel | Potentially | Potentially | Temporary URL/process; no uptime guarantee | Development smoke test only, not production |
| Owner-controlled always-on host + public HTTPS/WSS | Yes | Yes | Depends on host, ISP, power and operations | Required target for dependable public service |
| Paid cloud hosting | Yes | Yes | Provider-dependent | Prohibited by current ZERO COST decision |

## 4. Zero-cost reality and blockers

1. No server hardware or hosting account is currently available to the owner. The Infinix GT20 can host a local development backend, but it is not a dependable 24/7 production host.
2. Mobile operators may place the phone behind carrier-grade NAT. In that case, ordinary inbound port forwarding from the public internet is unavailable. This must be measured on the actual connection; do not assume a public IP.
3. Android may suspend or terminate background processes. A server on the phone is therefore best-effort and requires foreground operation, power, network continuity and device-specific acceptance.
4. A temporary tunnel can expose a local test service, but a changing URL and no uptime guarantee do not satisfy a stable production endpoint. Do not use a temporary tunnel as the permanent market-data API/WSS address.
5. A private mesh VPN can connect the owner's enrolled devices across networks, but it is not equivalent to a public application endpoint for arbitrary users. Any free plan must be checked for personal/non-commercial restrictions before use; no such service is selected or enabled here.
6. A genuinely public, reliable, always-on backend requires an always-on host and a routable/reverse-tunnel path. If no existing owner hardware/network can supply these at zero incremental cost, the public-production requirement remains blocked. Do not hide this constraint by switching to a paid free trial or silently changing security controls.

## 5. Recommended staged architecture

### Stage A — local development (no external services)
- Keep FastAPI backend and SQLite on the owner-controlled device.
- Bind to loopback for local-only development.
- Keep provider ingestion disabled and report `disconnected` / `unavailable` when no validated feed exists.
- Exercise HTTP and WebSocket protocol, persistence, restore and client lifecycle locally.
- Do not expose Redis, SQLite, operator endpoints or debug interfaces to a public network.

### Stage B — controlled LAN acceptance
- Only after owner approval and a reviewed Termux runbook, bind the backend to a LAN-reachable interface.
- Restrict access to the trusted local network; retain authentication and entitlement checks.
- Verify Android-to-Android and browser-to-backend requests, WebSocket upgrade, reconnect/snapshot behavior, and persistence after process restart.
- Record actual LAN address, firewall behavior and power/battery impact locally; never commit secrets or private addresses.
- LAN success does not count as public internet acceptance.

### Stage C — private remote-device experiment
- Evaluate a private mesh network only for the owner's own enrolled devices.
- Confirm the selected plan permits the intended use and has no billing/overage path.
- Require the client device to join the same private network. This is not public access for arbitrary users and is not the production launch topology.

### Stage D — public HTTPS/WSS acceptance
Before calling the product remotely accessible, require:
- stable hostname and certificate validation;
- public HTTPS REST and WSS reachability from at least two unrelated networks (Wi-Fi and mobile data);
- authenticated short-lived WebSocket ticket flow, exact-series entitlement checks, reconnect/resnapshot and replay acceptance;
- server-side Redis TLS/ACL or a separately reviewed zero-cost alternative that preserves atomic shared limits and fail-closed behavior;
- persistent SQLite volume, owner-host restore drill, encrypted backup/key custody and tested recovery;
- host restart, network interruption, Android client background/foreground and laptop browser tests;
- monitoring, bounded logs, operator access control and incident/recovery evidence.

No public exposure is authorized by this document. Each stage needs its own reviewed runbook and acceptance evidence.

## 6. Current implementation fit

- Backend: FastAPI, REST and WebSocket routes already exist in the repository.
- Durable local state: SQLite stores normalized OHLCV, instrument registry, coverage, entitlements, alerts and outbox-related records.
- Shared distributed guards and production ticket storage currently require Redis. Do not replace them with process-local in-memory controls in production.
- Provider ingestion is disabled unless separately configured; no real market feed is implied by an available endpoint.
- Frontend build is Vite/React. A responsive browser client can serve laptop/desktop; Android APK packaging is a separate client-distribution task and does not host the backend.
- Current repository does not establish a verified owner-controlled public host, public DNS, TLS certificate, mobile-carrier inbound path, or live production WSS.

## 7. Acceptance decision

**Current status: PUBLIC CROSS-NETWORK ACCESS = BLOCKED / NOT ACCEPTED.**

The next safe milestone is local backend verification followed by a controlled LAN test on the Infinix. Public access must remain marked blocked until a no-cost owner-controlled host and a stable secure network path are demonstrated. If zero incremental cost and reliable public uptime cannot both be met with existing owner resources, record the limitation honestly rather than provisioning a billable service.

No source code, production configuration, DNS, tunnel, VPN, hosting, or deployment was changed by this architecture decision.
