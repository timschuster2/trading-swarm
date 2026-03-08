---
name: architecture
description: |
  Produces or updates technical architecture at any point in delivery.
  Covers service topology, data schema, API contracts, environment variables,
  component design, and dependency map. New systems, mid-build changes, or
  post-build documentation. Elon leads. Holly checks business alignment.
  Keywords: architecture, schema, service topology, api, component, database, env vars, technical spec
version: "1.0"
owner: Timothy Schuster
agent: Elon (leads) | Holly (business alignment) | Nobody (pre-build gate)
status: active
created: 2026-03-08
allowed-tools: "Read Bash mcp__supabase-swarm mcp__github WebSearch"
---

# Architecture Skill

Call this when the technical shape of a system needs to be defined, changed, or documented.
Elon owns technical decisions. If Elon's architecture cannot deliver Holly's design intent —
escalate to Timothy. Never silently descope to make something easier to build.

## When to Use
- "How should this be built technically?"
- Before a significant build step
- New table, service, or integration needs specifying
- Mid-build: a technical decision needs locking before proceeding
- Post-build: documenting what was actually built
- Architecture change needed due to a design delta

---

## Mode

Elon states at invocation: **New / Delta / Documentation**

---

## Step 1 — Service Topology

```
SERVICE: [name]
Platform: [Railway cron / Railway service / Vercel serverless / Vercel static]
Trigger: [cron UTC / HTTP / event]
Writes to: [tables or APIs]
Reads from: [tables, APIs, env vars]
On failure: [degraded behaviour]
CLAUDE.md required: [YES / NO]
```

---

## Step 2 — Data Schema

```sql
-- TABLE: [name] | Written by: [service] | Read by: [service]
CREATE TABLE [name] (
  id         BIGSERIAL PRIMARY KEY,
  [field]    [type] [constraints],  -- purpose
  created_at TIMESTAMPTZ DEFAULT NOW()
);
-- Migration: [NNN_create_name.sql] — REQUIRED before any deploy touching this table
```

No SELECT *. LIMIT on all queries. UNIQUE constraints explicit.

---

## Step 3 — API Contracts

```
ENDPOINT: [METHOD] [path/URL]
Service: [owner] | Auth: [method]
Request:  { field: type — required/optional }
Response (200): { field: type }
Response (error): { status, body shape }
Timeout: [s] | Retry: [strategy]
Supabase key server-side only: [YES — mandatory for any Supabase call]
```

---

## Step 4 — Environment Variables

```
VAR: [NAME] | Service: [Railway/Vercel] | Purpose: [one line]
Type: [API key / OAuth token / URL / config]
Never in: git, client-side JS, logs
```

Shared vars (multiple services) = one entry per service.

---

## Step 5 — Component Design

For non-trivial components:
```
COMPONENT: [filename/module]
Responsibility: [one sentence]
Inputs: [what it receives]
Outputs: [what it returns or writes]
Dependencies: [imports, tables, APIs]
Error handling: [graceful failure path]
```

Complex logic (async, auth, retry) gets pseudocode before code is written.

---

## Step 6 — Dependency Map

```
BUILD ORDER:
1. [Migration] — no dependencies
2. [Component A] — depends on: step 1
3. [Auth flow] — depends on: manual action by [who]
...

HUMAN-REQUIRED STEPS (declare here, not mid-build):
[what] — [who] — [before which step]
```

---

## Nobody Architecture Gate

```
NOBODY ARCHITECTURE GATE — [System] — [Date]
1. SECURITY — credential in code, unprotected endpoint, or client-side Supabase key?
2. ISOLATION — any cross-write between swarm-data and trading-data?
3. MIGRATION — schema change without a migration file?
4. STP — any step requiring a manual file move?
5. ROLLBACK — rollback path defined for each deploy?
6. HOLLY ALIGNMENT — does this deliver Holly's stated design intent?

VERDICT: BUILD READY / BLOCK (items listed)
```

Elon writes no code until BUILD READY. If Timothy overrides a BLOCK — log the risk.

---

## Output

```
ARCHITECTURE — [System] — v[N] — [Date] — Mode: [New/Delta/Documentation]
Service topology | Schema | API contracts | Env vars | Components | Dependency map
Nobody gate: [BUILD READY / BLOCK / SKIPPED — reason]
```

Version: `ARCH-[system]-vN-YYYYMMDD`
