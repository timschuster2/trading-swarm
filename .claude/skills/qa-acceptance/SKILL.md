---
name: qa-acceptance
description: |
  Quality assurance and acceptance criteria validation — callable at any build step,
  after any deployment, or on demand. Nobody runs component checks, integration traces,
  AC validation, degraded mode tests, and go-live sign-off. Not a final-only gate.
  Can be called mid-build after any meaningful output exists.
  Keywords: qa, testing, acceptance criteria, quality gate, integration test, sign-off, go live, verify
version: "1.0"
owner: Timothy Schuster
agent: Nobody (leads) | Elon (technical detail + fixes)
status: active
created: 2026-03-08
allowed-tools: "Read Bash mcp__supabase-swarm mcp__railway mcp__vercel"
---

# QA Acceptance Skill

Call this at any point where output needs to be verified — not just at the end.
An output is not complete until it is verified in the real environment.
"It should work" is not the same as "it works."

## When to Use
- After any build step with a Nobody gate in the build sequence
- "Is this done?" or "is this ready?"
- After Elon says "it's deployed"
- After a hotfix or repair — regression check
- Full end-to-end integration test before go-live
- Iterating back to a prior build step — verify the regression didn't break anything

---

## Gate Type

Nobody states at invocation:

| Type | When |
|------|------|
| **Step Gate** | After a specific build step — scope = that step's components only |
| **Integration Gate** | Multiple components connected — full data flow trace |
| **Regression Gate** | After a fix — verify fix + check adjacent components |
| **Go-Live Gate** | Final check — all ACs, degraded mode, security, cron enabled |

---

## Component Check (Step Gates)

### Code Review
- [ ] No hardcoded credentials or tokens
- [ ] No `SELECT *` queries
- [ ] LIMIT on all DB queries
- [ ] All error paths handled — no silent failures
- [ ] Async operations have timeout and fallback
- [ ] Env vars referenced, not embedded
- [ ] `brief_date` uses `pytz Australia/Sydney` — never `datetime.utcnow().date()` [RC-2]
- [ ] `telegram_delivered` set only on HTTP 200 + valid `result.message_id` — never on call [RC-3]

### Behaviour Check
```
BEHAVIOUR: [from component spec]
TEST: [how verified]
RESULT: PASS / FAIL / UNTESTED
EVIDENCE: [log, query, or observed behaviour]
```

### Failure Mode Check
For every integration point — what happens on error, timeout, and unavailability?
Test failure modes explicitly. Happy path only = not production-ready.

---

## Integration Check

### Data Flow Trace
```
TRACE: [trigger] → [component A] → [store] → [component B] → [output]
Step [N]: expected: [state] | actual: [observed] | PASS / FAIL
```

### Cross-System Isolation
- [ ] No MDD component writes to trading-data
- [ ] SUPABASE_SWARM_KEY absent from all client-side JS (DevTools network tab)

### Security Scan
- [ ] All env vars in Railway/Vercel — not in code, not in git
- [ ] `.gitignore` excludes `.env`, `CLAUDE.md`, `.swarm/`
- [ ] No accidental credential logging (check Railway logs)
- [ ] Vercel: all Supabase calls server-side only

---

## AC Validation

Binary only. No partial credit.

```
AC: [exact text]
Test method: [how]
Pass condition: [measurable, specific]
Result: PASS / FAIL
Evidence: [log / query / message / screenshot]
Failure path tested: YES / NO
```

MDD core ACs (from MASTER-CONTEXT §13):

| # | AC | Test |
|---|----|----|
| 1 | Gmail OAuth persists 2+ days | swarm_events sources_succeeded Day 1 + Day 2 |
| 2 | schedule_tomorrow[] populated | raw_payload after test run |
| 3 | Candida tasks source='todoist' | candida_tasks[] in raw_payload |
| 4 | /done updates within 5s | timer + DB query |
| 5 | approve/reject within 5s | timer + DB query |
| 6 | Valid JSON schema 2.0 on 95%+ runs | 20 test runs |
| 7 | Brief by 06:35 AEST, 7 consecutive days | swarm_events delivery_status |
| 8 | /daily <3s, mobile responsive | DevTools + mobile |
| 9 | SUPABASE_SWARM_KEY absent from client JS | DevTools network tab |
| 10 | Brief sends with 2 sources failed | simulate failure, verify delivery |
| 11 | /brief before 06:00 returns gate message | manual test |
| 12 | /brief after 06:30 does not change positions | raw_payload before/after |
| 13 | schema_version = "2.0" in every brief | parse 10 raw_payloads |

---

## Degraded Mode Validation

Test explicitly — not assumed from happy path passing.

For each integration:
1. Simulate source failure
2. Verify brief still sends
3. Verify degraded footer with correct source name
4. Verify `sources_failed` logged in swarm_events
5. Restore source — verify recovery

---

## Go-Live Gate

```
NOBODY GO-LIVE GATE — [System] — [Date]

[ ] All step gates passed
[ ] Integration gate passed
[ ] All 13 MDD ACs: PASS
[ ] Degraded mode tested for all 5 sources
[ ] Idempotency tested (duplicate run = no duplicate row)
[ ] 90-day retention verified (runs in finally block)
[ ] Rollback path documented

Security:
[ ] No credentials in git (git log --all)
[ ] Env vars confirmed in Railway + Vercel dashboards
[ ] SUPABASE_SWARM_KEY server-side only

VERDICT: GO-LIVE / BLOCK (items listed)
BIGGEST RISK IF SHIPPED: [single item]
```

Nobody never self-resolves a BLOCK. Timothy sees verdict and decides to override or fix.
Override logged to swarm_events with reason.

---

## Repair Loop (on FAIL)

1. Diagnose — read logs, query swarm_events, reproduce
2. Elon fixes — scoped to failing component only
3. Nobody retests — failing check + regression on adjacent components
4. If 3 loops without resolution → escalate to Timothy with diagnosis
5. Partial fixes that pass the target but skip regression do not ship

---

## Output

```
QA GATE — [Type] — [System] — [Date]
Components tested: [list] | ACs tested: [N of M]
[component/AC]: PASS / FAIL — [evidence]
Degraded mode: PASS / FAIL / NOT TESTED THIS GATE
VERDICT: PASS / FAIL
Blocking items: [list] | Next: [fix+retest / go-live / escalate]
```
