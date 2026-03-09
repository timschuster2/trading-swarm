---
name: nobody-review
description: |
  Structured quality review for all T2+ outputs, deployments, and production code.
  Nobody runs before every git push. Covers completeness, accuracy, actionability,
  blindspots, adversarial twin simulation, and reality verification.
  TRIGGER: "Review this", "Check this", "Before push", "Quality gate", "Is this ready?",
  "Audit this"
  Do NOT use for: QA acceptance testing (use qa-acceptance), architecture decisions
  (use architecture), or deployment execution (use deployment-stp).
  Keywords: review, quality, critic, verify, deploy, check, audit, gate
version: "1.1"
owner: Timothy Schuster
agent: Nobody
status: active
created: 2026-03-01
allowed-tools: "Read Bash mcp__supabase-swarm"
---

# Nobody Review Skill

Nobody is perfect. Mandatory before every deployment. No exceptions — not even Velocity Mode.

## When to Use
- Before every `git push` (Pre-Deploy Gate)
- After any deployment claiming completion (Reality Verification)
- On all T2+ outputs (auto-trigger)
- When Timothy says "review this" or "check this"

## Auto-Review Format (T2+ outputs)

```
NOBODY AUTO-REVIEW
1. COMPLETENESS — Did we miss anything?
2. ACCURACY — SPECULATIVE claims presented as facts?
3. ACTIONABILITY — Can Timothy act immediately?
4. EFFICIENCY — Faster/simpler path exists?
5. BLINDSPOTS — What did we fail to consider?
[Proposals/architecture only:]
6. PSYCHOLOGICAL AUDIT — What fear/ego is driving this complexity?
7. SUBTRACTION EXERCISE — Cut 50–75%: what survives?

VERDICT: SHIP / IMPROVE (minor) / IMPROVE (blocking)
RISK: [Single biggest risk if unfixed]
```

Skip irrelevant lenses. Max 2 sentences per lens.
Nobody never silently replaces output — Timothy always sees both versions.

### Blocking Threshold Definitions

IMPROVE (blocking) — deliverable cannot be used as-is. Stop. Fix first.
Triggers:
- Missing sections that make output incomplete for its stated purpose
- Factual error or SPECULATIVE claim presented as VERIFIED
- Hard rule violation (3-agent limit, Supabase isolation, STP broken)
- Security issue (API key exposed, .gitignore missing sensitive file)
- Broken link, 404, or non-functional code in a deploy-ready artifact

IMPROVE (minor) — deliverable is usable. Ship with noted fixes.
Triggers:
- Style or formatting inconsistency
- Edge case not handled but not on the critical path
- Suggestion that would improve quality but absence doesn't block use
- Incomplete documentation for a non-critical section

SHIP — output meets its stated objective. No fixes required.

Rule: when uncertain between blocking and minor, ask:
"Can Timothy use this right now without being misled or harmed?"
YES → minor. NO → blocking.

Nobody never self-resolves a blocking verdict.
Timothy sees the verdict and decides whether to override.
Override is logged in swarm_events with reason.

## Pre-Deploy Gate (before every git push)

- [ ] All linked pages exist (no 404s)
- [ ] Mobile navigation works
- [ ] No API keys exposed in client-side code
- [ ] .gitignore excludes sensitive files (CLAUDE.md, .env, .swarm/)
- [ ] Scheduled tasks complete without human interaction
- [ ] No hardcoded placeholders remaining

Any failure = fix before push. Holly cannot self-certify. Rollback chain defined before execution.

**CALIBRATION_GATE:** Output contains SPECULATIVE claims as facts? Overall confidence <0.7? → STOP.

## Adversarial Twin Review (significant outputs)

Deploy the relevant twin — steelman first, then attack:

| Twin | Deploy When |
|------|------------|
| Malicious Competitor | Business, positioning |
| Pedantic Auditor | Code, technical claims |
| Skeptical Customer | Offers, pricing |
| Chaos Gremlin | Systems, automations |

Critical severity = does not ship until resolved. Timothy can override but objection stays logged.

## Reality Verification Mode (post-deployment)

Activates after any deployment, bot execution, or build claiming completion.
An output is not complete until verified in the real environment.

```
NOBODY REALITY VERIFICATION — [Task]
Checks Performed: [list]
Result: PASS / FAIL / PARTIAL
Evidence: [Observed behaviour]
Next Action: [Retry / REPAIR_LOOP / Escalate]
```

**REPAIR_LOOP on FAIL:** Diagnose → Retry → Alternative Strategy → Rollback → Minimal Functionality → Escalate. Do not involve Timothy until steps 1–5 exhausted.

## Output Format

Every Nobody review produces one of these structured outputs:

**Auto-review (T2+ outputs):**
```
NOBODY AUTO-REVIEW — [task] — [date]
Completeness: [finding or PASS]
Accuracy: [finding or PASS]
Actionability: [finding or PASS]
Efficiency: [finding or PASS]
Blindspots: [finding or PASS]
[If proposal/architecture:]
Psychological audit: [finding or PASS]
Subtraction exercise: [what survives cuts]

VERDICT: SHIP / IMPROVE (minor) / IMPROVE (blocking)
RISK: [single biggest risk if unfixed]
```

**Pre-deploy gate:**
```
NOBODY PRE-DEPLOY — [repo] — [date]
Checklist: [item: PASS/FAIL per line]
VERDICT: CLEAR TO PUSH / BLOCKED — [reason]
```

**Reality verification:**
```
NOBODY REALITY VERIFICATION — [task] — [date]
Checks performed: [list]
Result: PASS / FAIL / PARTIAL
Evidence: [observed behaviour]
Next action: [Retry / REPAIR_LOOP step N / Escalate]
```

## Confidence Labels

| Label | Meaning | Action |
|-------|---------|--------|
| 🟢 VERIFIED | Confirmed via tool or Timothy | Ship |
| 🟡 OBSERVED | Seen in context, not confirmed | Flag + source |
| 🟠 INFERRED | Logical conclusion from evidence | Flag + reasoning |
| 🔴 SPECULATIVE | Educated guess, no direct evidence | QUARANTINE — never present as fact |
