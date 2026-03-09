---
name: backlog-review
description: |
  Structured review of Timothy's swarm backlog — surfaces what to work on next,
  reorders by impact, and clears stale or completed items. Queries swarm_tasks
  as canonical source.
  TRIGGER: "What next?", "Review my backlog", "What should I work on?", "Prioritise",
  "What's left?", "Weekly planning"
  Do NOT use for: Assessing external research (use alpha-intake), requirements
  gathering (use requirements), or deployment (use deployment-stp).
  Keywords: backlog, review, prioritise, next, todo, tasks, queue, what next
version: "1.0"
owner: Timothy Schuster
agent: Holly (leads) | Nobody (challenges priority calls)
status: active
created: 2026-03-01
allowed-tools: "Read mcp__supabase-swarm conversation_search"
---

# Backlog Review Skill

Run when Timothy asks "what should I work on next", "review my backlog", or at the start
of any planning session.

## When to Use
- Session start when direction isn't clear
- Weekly planning
- After a big build sprint to reorder priorities
- "What's left?" or "what next?" questions

## Phase 1 — Pull Current State

Query swarm_tasks from Supabase:
```sql
SELECT id, task, priority, status, owner, blocker, next_action, notes, last_touched
FROM swarm_tasks
WHERE status NOT IN ('done')
ORDER BY priority ASC;
```

Check userMemory for any backlog items stored there.

Flag immediately if sources conflict — backlog fragmentation is a known gap.

## Phase 2 — Triage Each Item

For every open item, apply:

| Check | Question |
|-------|---------|
| Still relevant? | Does this still serve an active objective? |
| Blocked? | What's actually stopping this? |
| Duplicate? | Already in swarm_tasks with different ID? |
| Stale? | Not touched in 14+ days with no blocker = deprioritise |
| Quick win? | Can this ship in <2hrs? Flag for immediate action. |

## Phase 3 — Priority Stack

Rank surviving items against Timothy's 4 objectives:

1. Job security (AI mastery — real shipped systems)
2. Income (productise swarm, timschuster.dev shop front)
3. Trading edge (live Solana signals, not simulation)
4. Westpac (skills transfer only — no IP crossover)

Scoring weights:

| Factor | Weight |
|--------|--------|
| Unblocks another item | 30% |
| Revenue proximity | 25% |
| Learning value | 20% |
| Effort-to-value | 15% |
| Fun / momentum | 10% |

## Phase 4 — Output Format

```
BACKLOG REVIEW — [Date]
Source: swarm_tasks ([N] items)
Conflicts found: [Y/N — if Y, list them]

PRIORITY STACK (top 5):
1. [Item] — [why now] — [estimated effort] — [blocker if any]
2. [Item] — [why now] — [estimated effort] — [blocker if any]
3. [Item] — [why now] — [estimated effort] — [blocker if any]
4. [Item] — [why now] — [estimated effort] — [blocker if any]
5. [Item] — [why now] — [estimated effort] — [blocker if any]

QUICK WINS (ship today):
- [Item] — [why fast]

DEPRIORITISED:
- [Item] — [reason]

RECOMMEND DELETING:
- [Item] — [why no longer relevant]

Recommended action: [What Timothy should do right now]
```

## Phase 5 — Cleanup Proposal

After review, propose any items to:
- **Close** — completed but not marked done
- **Delete** — no longer relevant
- **Merge** — duplicate entries across sources

Requires Timothy approval before any deletes. Never silently remove items.
