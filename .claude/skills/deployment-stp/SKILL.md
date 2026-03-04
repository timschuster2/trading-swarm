---
name: deployment-stp
description: |
  Straight-through processing deployment procedures for all Timothy's live systems.
  Covers website (Vercel), bots/services (Railway), STP handoff pattern from Projects to Claude Code,
  commit standards, and the mandatory session close protocol.
  Keywords: deploy, deployment, stp, git, push, vercel, railway, commit, pipeline, handoff
version: "1.1"
owner: Timothy Schuster
agent: Elon (executes) | Nobody (gates)
status: active
created: 2026-03-01
allowed-tools: "Bash mcp__github mcp__railway mcp__vercel mcp__filesystem"
---

# Deployment STP Skill

Zero manual file moves. Ever. If a workflow requires Timothy to manually move files between tools, it is broken.

## When to Use
- Any `git push` or deployment to Railway/Vercel
- File handoffs from Claude Projects → Claude Code
- Session close (save_session.py)
- Any build that will go live

## Pipelines

**Website (timschuster.dev):**
```
Claude Code edits → git push → GitHub → Vercel auto-deploys → timschuster.dev
```

**Bots/Services:**
```
Claude Code edits → git push → GitHub → Railway auto-deploys
```

**NEVER:** Ask Timothy to copy files between tools. One download, one save to `working files for next session/`, Claude Code reads locally.

## STP Handoff Pattern (Projects → Claude Code)

1. Projects builds and Timothy approves visually
2. File → `/mnt/user-data/outputs/` with versioned filename (`name-vN-YYYYMMDD.ext`)
3. Tell Timothy: *"Save [filename] to working files for next session/"*
4. Give Claude Code instruction: *"Read [filename] from working files folder, deploy as [target], commit and push."*

Never say "paste this content into Claude Code." One download. One save. Code reads locally.

## Commit Standards

Format: `<type>(<scope>): <description>`

| Type | When |
|------|------|
| feat | New feature or capability |
| fix | Bug fix |
| docs | Documentation only |
| style | Formatting, no logic change |
| refactor | Code restructure, no behaviour change |
| chore | Config, deps, tooling |

Atomic commits — one feature/fix per commit. No batching unrelated changes.

## Repo Structure (every repo)

```
project-name/
├── CLAUDE.md                        ← always gitignored
├── .gitignore                       ← FIRST file before any commit
├── .swarm/STATE.md                  ← gitignored
├── working files for next session/  ← gitignored
└── src/
```

Minimum .gitignore: `CLAUDE.md`, `CLAUDE.local.md`, `.swarm/`, `working files for next session/`, `archive/`, `*.env`, `node_modules/`

## Session Close Protocol (MANDATORY)

Final step of every Claude Code session — run before sign-off:

```bash
cd C:\Users\Admin\ClaudeCryptoBotFeb26\swarm-telegram-bot

python save_session.py \
  --summary "[what was built/decided this session]" \
  --agents "Holly,Elon,Nobody" \
  --decisions "[decision 1|decision 2]" \
  --outcomes "[file1|service1]"
```

This feeds the COLD memory layer. Reflector reads it at 6:30am AEST and rebuilds MEMORY.md.
Skip this = memory is broken.

## FRAMEWORK_SYNC_GATE

After delivering any framework file → Holly states `HANDOFF_PENDING = v[X.X]`.
No new framework build until Timothy confirms deployment.

## Output Format

Every deployment produces a structured completion note before closing:

```
DEPLOYMENT COMPLETE — [service/repo] — [date]
Commit: [hash] — [commit message]
Deploy target: [Vercel / Railway / both]
Status: LIVE / PENDING / FAILED
Verified: [URL checked / Railway logs checked / health monitor pinged]
Rollback: [commit hash to revert to if needed]
Nobody gate: PASSED / FAILED (if failed — reason)
Session log: [save_session.py run Y/N]
```

On failure — state clearly:
```
DEPLOYMENT FAILED — [service] — [date]
Failure point: [which step]
Evidence: [log excerpt or error]
REPAIR_LOOP initiated: Step [1–6]
Next action: [exact next step]
```

## Railway Services Reference

| Service | Cron (UTC) | Cron (AEST) |
|---------|-----------|-------------|
| trading-swarm | `0 22 * * *` | 8:00am daily |
| ideation-scanner | `0 21 * * *` | 7:00am daily |
| reflector | `30 20 * * *` | 6:30am daily |
| health-monitor | `*/15 * * * *` | Every 15 min |
