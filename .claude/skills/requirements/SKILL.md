---
name: requirements
description: |
  Structured business analysis for eliciting, documenting, and validating requirements
  at any fidelity level. Covers scope definition, user stories, functional + non-functional
  requirements, assumption surfacing, and sign-off gates. Holly leads.
  TRIGGER: "What does this need to do?", "Write me requirements", "User stories",
  "Scope this", "What are the requirements?", "Functional requirements"
  Do NOT use for: Solution design (use solution-design), technical architecture
  (use architecture), or quality testing (use qa-acceptance).
  Keywords: requirements, ba, business analysis, scope, user stories, functional, acceptance, sign-off
version: "1.0"
owner: Timothy Schuster
agent: Holly (leads) | Nobody (gap challenges)
status: active
created: 2026-03-08
updated: 2026-03-09
allowed-tools: "Read conversation_search mcp__supabase-swarm"
---

# Requirements Skill

Holly owns requirements. Nobody challenges completeness. Elon never starts building
until a requirements artefact exists and Nobody has gated it. No exceptions.

## When to Use
- New system or service being designed from scratch
- Significant new feature added to an existing system
- Ambiguity about what to build or for whom
- Timothy says "I want to build X" or "add X to the system"
- Any session where build work is the next step

---

## Phase 1 — Context Load

Before eliciting requirements, establish:

1. **What already exists** — query swarm_backlog and swarm_sessions for prior context on this topic
2. **Who the users are** — names, roles, access levels, technical comfort
3. **What problem this solves** — one sentence, Timothy confirms before proceeding
4. **Hard constraints** — infra, cost, timeline, IP boundaries, integrations off-limits

State explicitly: "Requirements elicitation starting for: [system/feature name]."
Do not skip to Phase 2 until context is confirmed by Timothy.

---

## Phase 2 — Requirements Elicitation

Elicit in this order. Never skip a category.

### 2A — Functional Requirements
What the system must DO. One requirement per statement. Active voice.

Format:
```
FR-[N]: The system shall [action] when [trigger/condition].
```

Examples:
- FR-1: The system shall deliver a Telegram brief by 06:30 AEST daily.
- FR-2: The system shall mark a task as done when Timothy replies "done [n]" to the brief.

Minimum questions to ask:
- What does success look like on Day 1?
- What does the user do, step by step?
- What does the system do in response, step by step?
- What happens when something goes wrong?

### 2B — Non-Functional Requirements
How the system must PERFORM. Quantified where possible.

| Category | Example |
|----------|---------|
| Performance | Response within X seconds |
| Reliability | Degraded mode — brief sends even if source fails |
| Security | No credentials in client-side code |
| Maintainability | Config tunable without redeploy |
| Scalability | N users, N requests per day |

### 2C — Assumptions
Things believed to be true but not confirmed. List every one.
Format: `ASSUMPTION-[N]: [statement] — to be confirmed by [owner] before build.`

### 2D — Out of Scope
Explicit list of what this system does NOT do.
Every removed or deferred requirement must appear here with reason.

### 2E — Dependencies
External systems, APIs, credentials, or decisions that must exist before build begins.
Format: `DEP-[N]: [what] — owned by [who] — status: [confirmed/pending]`

---

## Phase 3 — Requirements Review

Holly presents the full requirements set.
Nobody runs completeness challenge before Timothy signs off:

```
NOBODY REQUIREMENTS CHALLENGE
1. MISSING FRs — any user action or system response not covered?
2. AMBIGUOUS — any requirement that two engineers could interpret differently?
3. UNTESTABLE — any requirement with no clear pass/fail condition?
4. ASSUMPTION RISK — any assumption that, if wrong, breaks multiple FRs?
5. SCOPE CREEP — any requirement that wasn't in the original problem statement?

VERDICT: SIGN-OFF READY / REVISE (items listed)
```

No build proceeds until Nobody verdict = SIGN-OFF READY and Timothy confirms.

---

## Phase 4 — Sign-Off Artefact

Output format — confirmed requirements ready for Elon:

```
REQUIREMENTS SIGN-OFF — [System/Feature] — [Date]
Problem: [one sentence]
Users: [list]
Out of scope: [list]

FUNCTIONAL REQUIREMENTS
FR-1: ...
FR-2: ...

NON-FUNCTIONAL REQUIREMENTS
NFR-1: ...
NFR-2: ...

ASSUMPTIONS (unconfirmed)
ASSUMPTION-1: ...

DEPENDENCIES
DEP-1: ...

Nobody gate: PASS
Timothy sign-off: [CONFIRMED / PENDING]
```

---

## Output Rules
- Never present requirements to Elon without Nobody gate PASS
- Assumptions must be surfaced, never buried in FRs
- Out of scope list is mandatory — not optional
- Version requirements artefacts: `REQ-[system]-vN-YYYYMMDD`
- If Timothy sign-off is not confirmed → flag HANDOFF_PENDING before Code session
