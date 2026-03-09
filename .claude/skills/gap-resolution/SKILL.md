---
name: gap-resolution
description: |
  Resolves design, architecture, or integration gaps using a structured 3-agent swarm vote.
  Callable at any point in delivery. Holly classifies and proposes. Elon assesses
  technical feasibility. Nobody challenges. Produces a locked decision.
  TRIGGER: "What do we do about X?", "Resolve this", "Swarm vote", "We need to decide",
  "This is blocking — pick one", "Lock this decision"
  Do NOT use for: Requirements gathering (use requirements), solution design
  (use solution-design), or quality gates (use qa-acceptance).
  Keywords: gap, decision, resolution, vote, design gap, architecture gap, lock, pending, swarm vote
version: "1.0"
owner: Timothy Schuster
agent: Holly (leads + proposes) | Elon (technical feasibility) | Nobody (adversarial challenge)
status: active
created: 2026-03-08
allowed-tools: "Read conversation_search mcp__supabase-swarm"
---

# Gap Resolution Skill

Call this any time a decision is unresolved and blocking — or about to block — progress.
Works at any stage: early design, mid-build, post-deploy issue.
Every gap gets the same treatment: classify → options → swarm vote → lock.
Parked is a valid outcome. Silent deferral is not.

## When to Use
- A gap from the backlog (RS-N / RE-N) is being addressed
- "What do we do about X?"
- Nobody flags an unresolved decision during a gate
- Elon hits an ambiguous design choice mid-build
- Two valid approaches exist and the team needs to pick one

---

## Step 1 — Classify the Gap

One sentence. Then:

**Type:**
| Type | Definition |
|------|-----------|
| Design Gap | Missing decision about what the system does or how users interact |
| Architecture Gap | Missing decision about how the system is built |
| Integration Gap | Undefined behaviour for an external dependency |
| Edge Case Gap | System works generally but has undefined behaviour in a specific scenario |
| Scope Gap | Ambiguity about what is in or out |

**Severity:**
| Level | Meaning |
|-------|---------|
| 🔴 Critical | Blocks build now. Cannot proceed. |
| 🟠 Significant | Doesn't block current step but will block a later one. Resolve before that step. |
| 🟡 Edge Case | System works without this. Resolve before go-live. |

---

## Step 2 — Options

Holly generates 2–4 genuine options.
Options must be meaningfully different — variants of the same approach don't count.

```
OPTION [N]: [Short name]
What: [one sentence description]
Pros: [specifics]
Cons: [specifics]
Tradeoff: [what you gain vs lose]
```

No thumb on the scale at this stage. All options presented fairly.

---

## Step 3 — Swarm Vote

Fixed order. Each agent runs independently.

**Holly — Proposal:**
`HOLLY RECOMMENDS: Option [N] — [one sentence rationale]`

**Elon — Technical Feasibility:**
For the leading option(s):
```
OPTION [N] FEASIBILITY:
Implementation complexity: [low/medium/high]
New dependencies: [list or none]
Technical risk: [what could go wrong]
```
`ELON ASSESSMENT: Option [N] is [most viable] because [reason]`

**Nobody — Adversarial Challenge:**
Challenge the leading option:
```
NOBODY CHALLENGE — Option [N]:
Most likely failure mode: [specific]
Edge case it breaks on: [specific]
Assumption that must hold: [specific]
```
`NOBODY VERDICT: ACCEPT / ACCEPT WITH CONDITIONS [state condition] / CHALLENGE [state what's wrong]`

---

## Step 4 — Resolution

**Swarm aligns (2/3 or 3/3):**
```
SWARM CONSENSUS: Option [N]
Holly: [for] | Elon: [for] | Nobody: [accept]

DECISION LOCKED: [exact statement — one clear sentence]
Rationale: [2-3 sentences]
Rejected: [other options + one-line reason]
```

**Swarm split:**
```
SWARM SPLIT:
Holly: Option [N] | Elon: Option [M] | Nobody: [position]

ESCALATE TO TIMOTHY:
Question: [single clear question]
Options: [A] [B] (or [A] [B] [C])
Swarm leans: [best guess even in split]
```

**No viable option:**
`NO VIABLE OPTION — all options blocked because: [reason]`
`Park until: [specific unlock condition]`

Critical gaps cannot be parked without Timothy's explicit approval.

---

## Step 5 — Decision Log

```
DECISION LOG ENTRY
ID: [RS-N / RE-N / DEC-N]
Date: [YYYY-MM-DD]
Gap: [original statement]
Decision: [locked rule — exact implementation statement]
Rationale: [2-3 sentences]
Rejected: [list]
Source of truth to update: [MASTER-CONTEXT / ARCHITECTURE / SD — section]
```

Write to Supabase decisions table.
Update source-of-truth document before session closes.
Holly confirms: `DECISION LOCKED — [document + section] updated.`

---

## Running Multiple Gaps

1. Classify all gaps first (Step 1 for all)
2. Sort: 🔴 Critical → 🟠 Significant → 🟡 Edge Case
3. Full process per gap in order
4. At session end: all Critical + Significant gaps must be LOCKED or ESCALATED
5. Edge cases may be parked with explicit unlock conditions

---

## Output Per Gap

```
GAP RESOLUTION — [ID] — [Date]
Type: [type] | Severity: [level]
Options: [N assessed]
Holly: [recommendation] | Elon: [assessment] | Nobody: [verdict]
OUTCOME: LOCKED / ESCALATED / PARKED
[If locked]: Decision: [statement]
[If escalated]: Question for Timothy: [question]
[If parked]: Unlock condition: [statement]
Source of truth updated: YES / PENDING
Supabase write: YES / PENDING
```
