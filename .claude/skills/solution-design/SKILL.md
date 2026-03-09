---
name: solution-design
description: |
  Produces or updates a solution design at any point in delivery — early concept,
  mid-build pivot, or post-build documentation. Covers system overview, user journeys,
  data flows, integration contracts, locked decisions, and build sequence.
  Holly owns the business layer. Elon owns the technical layer.
  TRIGGER: "Design this", "How should it work?", "Update the design", "System design",
  "What did we actually build?", "Design document"
  Do NOT use for: Technical architecture details (use architecture), requirements
  elicitation (use requirements), or quality testing (use qa-acceptance).
  Keywords: solution design, system overview, user journey, data flow, integration, decision, design document
version: "1.0"
owner: Timothy Schuster
agent: Holly (leads — business layer) | Elon (technical feasibility input) | Nobody (design integrity gate)
status: active
created: 2026-03-08
allowed-tools: "Read conversation_search mcp__supabase-swarm"
---

# Solution Design Skill

Call this when the team needs to articulate or update how the system works — at any
fidelity, any stage. Early = high-level concept design. Mid-build = design delta for
new feature. Post-build = design documentation to match what was actually built.
The design is always the current truth about the system, not a historical artefact.

## When to Use
- "Design this for me" — new system or feature
- "Update the design — we changed X" — design delta after a build decision
- Before handing off to Elon for a significant build step
- Before a stakeholder review — need a coherent system picture
- "What did we actually build?" — post-build documentation mode

---

## Mode Selection

Holly states the mode:

| Mode | Use when |
|------|----------|
| **New Design** | System or feature doesn't exist yet |
| **Design Delta** | Existing design exists — documenting a change |
| **Documentation** | System is built — capturing design to match reality |

---

## Step 1 — System Overview

One paragraph. What does it do, who uses it, what triggers it, what are its outputs?

Delivery surfaces:
```
SURFACE-[N]: [name] — [type: Telegram/web/API/cron/webhook] — [user] — [trigger]
```

---

## Step 2 — User Journeys

```
JOURNEY: [User] — [Goal]
Step 1: [trigger or user action] → [system response] → [user sees/receives]
Step 2: ...
Happy path: [outcome]
Failure path: [degraded experience]
```

Any journey step with no defined failure path gets flagged.

---

## Step 3 — Data Flow

For each external source:
```
SOURCE: [name] | Provides: [fields] | Auth: [method + location] | On failure: [behaviour]
```

For each internal store:
```
STORE: [table] | Written by: [component] | Read by: [component] | Retention: [rule]
```

---

## Step 4 — Integration Contracts

```
CONTRACT: [name]
Protocol: [REST/MCP/webhook] | Auth: [method]
Key request fields: [what we send]
Key response fields: [what we consume]
On error: [behaviour]
```

---

## Step 5 — Locked Decisions

```
DEC-[N]: [Decision — one clear sentence]
Rationale: [why this / 1-2 sentences]
Rejected: [alternatives and why]
```

Changes logged as new decisions: `DEC-[N+1] supersedes DEC-[N] because [reason]`

---

## Step 6 — Build Sequence (when handing to Elon)

```
STEP [N]: [what gets built]
  Delivers: [what can be tested]
  Nobody gate: [YES — what Nobody checks / NO]
  Est. effort: [hours]
```

Nobody gates after: schema changes, external integrations, user-facing output, deployments.

---

## Nobody Design Gate

```
NOBODY DESIGN GATE — [System/Feature] — [Date]
1. JOURNEY COVERAGE — every user goal has a journey with a failure path?
2. DECISION GAPS — any implicit choice that should be explicit?
3. CONTRACT GAPS — any integration with undefined error handling?
4. DATA EXPOSURE — any sensitive data without a protection mechanism?
5. SCOPE INTEGRITY — does the design match the agreed problem?

VERDICT: HANDOFF READY / REVISE (items listed)
```

---

## Output Artefact

```
SOLUTION DESIGN — [System] — v[N] — [Date]
Mode: [New / Delta / Documentation]
System overview | Delivery surfaces | User journeys | Data flows
Integration contracts | Locked decisions | Build sequence (if applicable)
Nobody gate: [HANDOFF READY / REVISE / SKIPPED — reason]
```

Version: `SD-[system]-vN-YYYYMMDD`. Log decisions to Supabase.
