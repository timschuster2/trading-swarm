---
title: "Skills Hub — MOC"
description: "Entry point for all swarm skills. Callable on demand at any stage of delivery."
status: active
created: 2026-03-01
updated: 2026-03-09
framework_version: "v3.5"
---

# Swarm Skills Hub

Scan this first (~150 tokens). Load full SKILL.md only when invoked.
Skills are a toolkit — any skill can be called at any stage of delivery.
Holly routes to the right skill based on what Timothy asks for.

---

## All Skills

| Skill | File | Call When | Agent |
|-------|------|-----------|-------|
| **lean-canvas** | `.claude/skills/lean-canvas/SKILL.md` | Frame or stress-test a product/service idea | Holly |
| **service-design** | `.claude/skills/service-design/SKILL.md` | Map user experience and system boundary | Holly |
| **requirements** | `.claude/skills/requirements/SKILL.md` | High-level or detailed requirements at any fidelity | Holly |
| **solution-design** | `.claude/skills/solution-design/SKILL.md` | Design or document system — new, delta, or post-build | Holly |
| **architecture** | `.claude/skills/architecture/SKILL.md` | Define or update technical design — schema, services, APIs | Elon |
| **gap-resolution** | `.claude/skills/gap-resolution/SKILL.md` | Resolve any unresolved decision via swarm vote | Holly |
| **alpha-intake** | `.claude/skills/alpha-intake/SKILL.md` | Assess new tools, patterns, research before adopting | Holly |
| **backlog-review** | `.claude/skills/backlog-review/SKILL.md` | Review and prioritise open work | Holly |
| **deployment-stp** | `.claude/skills/deployment-stp/SKILL.md` | Deploy to Railway or Vercel via STP pipeline | Elon |
| **nobody-review** | `.claude/skills/nobody-review/SKILL.md` | Quality gate — before any git push or T2+ output | Nobody |
| **qa-acceptance** | `.claude/skills/qa-acceptance/SKILL.md` | Verify output at any build step, integration, or go-live | Nobody |
| **trading-analysis** | `.claude/skills/trading-analysis/SKILL.md` | Trading swarm performance review or upgrade planning | Elon |

---

## Agent Ownership

| Agent | Leads | Never leads |
|-------|-------|-------------|
| **Holly** | lean-canvas, service-design, requirements, solution-design, gap-resolution, alpha-intake, backlog-review | architecture, deployment-stp, trading-analysis |
| **Elon** | architecture, deployment-stp, trading-analysis | lean-canvas, service-design, requirements, solution-design |
| **Nobody** | nobody-review, qa-acceptance | All production + design skills — gates only, never produces |

---

## Routing Guide

| Timothy says... | Skill |
|----------------|-------|
| "Is this worth building / what should this be?" | lean-canvas |
| "Map the user flow / how does a user experience this?" | service-design |
| "What does this need to do / write me requirements / user stories" | requirements |
| "Design this / how should it work / update the design" | solution-design |
| "How should this be built / define the architecture / schema" | architecture |
| "What do we do about X / resolve this / swarm vote" | gap-resolution |
| "Assess this / should we use X / intake this" | alpha-intake |
| "What next / review my backlog / what should I work on" | backlog-review |
| "Deploy / push / ship this" | deployment-stp |
| "Review this / check this / before push" | nobody-review |
| "Is this done / test this / go-live check" | qa-acceptance |
| "How is the trading bot / trading review" | trading-analysis |

---

## Skill Health

| Skill | Version | Updated | Status |
|-------|---------|---------|--------|
| lean-canvas | 1.0 | 9 Mar 2026 | ⚠️ Stub |
| service-design | 1.0 | 9 Mar 2026 | ⚠️ Stub |
| requirements | 1.0 | 9 Mar 2026 | ✅ Active |
| solution-design | 1.0 | 9 Mar 2026 | ✅ Active |
| architecture | 1.1 | 9 Mar 2026 | ✅ Active |
| gap-resolution | 1.0 | 9 Mar 2026 | ✅ Active |
| alpha-intake | 1.3 | 9 Mar 2026 | ✅ Active |
| backlog-review | 1.0 | 9 Mar 2026 | ✅ Active |
| deployment-stp | 1.1 | 9 Mar 2026 | ✅ Active |
| nobody-review | 1.1 | 9 Mar 2026 | ✅ Active |
| qa-acceptance | 1.0 | 9 Mar 2026 | ✅ Active |
| trading-analysis | 1.0 | 9 Mar 2026 | ✅ Active |

Quarterly review: skills not triggered in 90 days → DEPRECATED (Holly flags, Timothy approves).
