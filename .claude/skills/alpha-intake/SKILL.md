---
name: alpha-intake
description: |
  Structured intake process for evaluating external research, framework docs, upgrade proposals,
  and tool documentation against the AI Agent Swarm — Blueprint v0.3.
  Produces ADOPT / ADAPT / REJECT verdicts with exact framework text ready to merge.
  Keywords: intake, alpha, research, assessment, framework upgrade, review, evaluate
version: "1.3"
owner: Timothy Schuster
agent: Holly (orchestrates) | Nobody (CHALLENGER_SIM + Blueprint audit) | Elon (implementation text)
status: active
created: 2026-03-01
updated: 2026-03-06
allowed-tools: "Read WebSearch conversation_search"
---

# Alpha Intake Skill

Run automatically whenever Timothy pastes alpha, uploads a doc, or says "assess this".

## When to Use
- External research reports or analyses
- New framework docs, GitHub repos, upgrade proposals
- Tool/API/library documentation for potential adoption
- Any input prefaced with "assess this" or "what do you think of this"

---

## Phase 1 — Classify

State the type before assessing:

| Type | Example |
|------|---------|
| Framework Alpha | New agent patterns, orchestration logic |
| Tool/Integration | New MCPs, APIs, libraries |
| Research Alpha | Reports, market intel, external reviews |
| Upgrade Markdown | Proposed changes to the framework |
| Concept Alpha | Ideas, paradigms, no direct implementation path |

---

## Phase 2 — Conflict Check (FIRST — blocks everything if failed)

### 2A — Core Rules (unchanged)
- Conflicts with Timothy's absolute authority?
- Undermines STP pipeline or automation-first deployment?
- Requires unjustified new external dependencies?
- Violates sensitive data isolation?
- Introduces hallucination risk?

### 2B — Blueprint Architecture Gate (NEW — hard block)

Holly checks the proposal against Blueprint v0.3 structural constraints:

| Constraint | Check |
|------------|-------|
| 3-agent orchestrator hard limit | Does this require a 4th named orchestrator? → BLOCK |
| Supabase isolation | Does this cross-write between swarm-data and trading-data? → BLOCK |
| STP pipeline | Does this require manual file moves between tools? → BLOCK |
| Earned Complexity | Does a real, repeated need exist for this? Or is this theoretical? → BLOCK if theoretical |
| Single owner per information type | Does this duplicate an existing information store? → BLOCK |
| Ephemeral sub-agent rules | Does this give sub-agents memory, identity, or Supabase write access? → BLOCK |
| Blueprint plank fit | Which plank does this land in? (1–7). If none → flag as architecture gap before scoring |

**State the plank explicitly:**
> "This proposal lands in Plank [N] — [name]."
> If it spans multiple planks, name each one.
> If it fits no plank → state: "No plank match — potential architecture gap. Flag to Timothy before scoring."

**BLOCKED if any 2A or 2B conflict found. Do not proceed until resolved.**

---

## Phase 3 — Value Assessment

Score 1–5 per dimension:

| Dimension | Question |
|-----------|---------|
| Relevance | Directly applies to current stack and goals? |
| Novelty | Meaningfully new vs. Blueprint v0.3? |
| Effort-to-Value | Low effort, high impact? |
| Robustness | Well-defined enough for reliable agent execution? |
| Revenue Proximity | Accelerates time-to-revenue or protects existing? |

Thresholds: 20–25 = ADOPT | 14–19 = ADAPT | 8–13 = PARK | <8 = REJECT

---

## Phase 4 — CHALLENGER_SIM (Nobody)

### 4A — Standard Challenge (unchanged)
Steelman first → then attack:
- Most likely failure mode if implemented?
- Edge case it breaks on?
- Is the source credible?
- More governance overhead than value?

### 4B — Blueprint Plank Audit (NEW — mandatory on all ADOPT/ADAPT verdicts)

Nobody reads the relevant Blueprint v0.3 plank and states explicitly:

```
BLUEPRINT AUDIT — Plank [N]: [Plank Name]
Fits: [What in this proposal aligns with the plank's intent]
Conflicts: [What in this proposal conflicts or is not covered]
Verdict: CLEAN FIT / MINOR TENSION / STRUCTURAL CONFLICT
```

| Audit Verdict | Meaning | Action |
|---------------|---------|--------|
| CLEAN FIT | Proposal aligns with plank intent and constraints | Proceed to Phase 5 |
| MINOR TENSION | Proposal fits but creates edge cases or ambiguity | Note in changelog — flag for next review |
| STRUCTURAL CONFLICT | Proposal contradicts plank design | Return to Phase 2 — re-classify as BLOCKED |

Nobody never skips 4B on an ADOPT or ADAPT verdict. Not even in Velocity Mode.

---

## Phase 5 — Verdict & Placement

| Label | Action |
|-------|--------|
| STRONG ADOPT | Draft exact change → go to Phase 6 |
| ADOPT CONCEPTS | Draft adapted version → go to Phase 6 |
| CHERRY-PICK | Draft only selected items → go to Phase 6 |
| SKIP | One-sentence rejection reason. Done. |

For every ADOPT/ADAPT — mandatory:
- **Owning agent:** Holly / Elon / Nobody
- **Blueprint plank:** Plank [N] — [name] (from Phase 2B)
- **Nobody audit verdict:** CLEAN FIT / MINOR TENSION (from Phase 4B)
- Target section in Blueprint v0.3
- Change type: ADD / MODIFY / DEPRECATE
- Exact proposed text (not paraphrase — write the actual rule)

---

## Phase 6 — Changelog Entry

```
## Pending Changes for Blueprint v[next version]
| # | Item | Plank | Section | Source | Verdict | Nobody Audit |
|---|------|-------|---------|--------|---------|-------------|
| 1 | [item] | §[N] | §[X.Y] | [Source] | ADOPT / ADAPT | CLEAN FIT / MINOR TENSION |
```

---

## Summary Output Format

```
ALPHA INTAKE — [Date] — [Source]
Type: [type]
Items assessed: [N]
Adopted: [N] | Adapted: [N] | Parked: [N] | Rejected: [N]
Blueprint conflicts blocked: [N]

ADOPT/ADAPT items:
- [item] → Plank [N] · Nobody: CLEAN FIT / MINOR TENSION

PARKED: [items + unlock condition]
REJECTED: [items + one-line reason]
BLOCKED (architecture conflict): [items + which constraint failed]

Next action: Timothy approves → Holly merges into Blueprint v0.3
```

---

## Changelog

| Version | Date | Change |
|---------|------|--------|
| 1.2 | 2026-03-01 | Initial version |
| 1.3 | 2026-03-06 | Added Phase 2B Blueprint Architecture Gate + Phase 4B Plank Audit (Nobody). Summary output updated. |
