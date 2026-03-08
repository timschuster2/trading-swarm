---
name: trading-analysis
description: |
  Analysis framework for the Solana multi-layer AI trading swarm (v4.0).
  Covers Layer A/B/C architecture, sub-agent verdicts, threshold calibration,
  market regime classification, and performance review of trade_executions.
  Keywords: trading, solana, analysis, trade, market, regime, signal, layer, swarm, crypto
version: "1.0"
owner: Timothy Schuster
agent: Elon (builds) | Nobody (validates thresholds)
status: active
created: 2026-03-01
allowed-tools: "Read Bash mcp__supabase-trading WebSearch"
---

# Trading Analysis Skill

All thresholds marked 🔴 SPECULATIVE until validated by 100+ forward tests.
CCXT library always for exchange connections. Never direct exchange APIs.

## When to Use
- Reviewing trading swarm performance
- Calibrating thresholds (slippage, RTT, volatility)
- Interpreting Layer B sub-agent verdicts
- Planning Layer A/B/C upgrades
- Any "how is the trading bot doing" question

## System Architecture

```
Layer A (layer_a.py) — Deterministic Sentinel
  ├── RTT measurement: Helius / QuickNode / Ankr
  ├── SOL/USDC price via Jupiter quote endpoint
  ├── Slippage calculation
  └── Writes → market_snapshots (Supabase trading-data)

Layer B (layer_b.py) — LLM Reasoning
  ├── REGIME_SYNTH — classifies market environment
  ├── NARRATIVE_ARB — sentiment vs price anomaly detection
  ├── DATA_SKEPTIC — timestamp desync audit
  └── GOD_TRADE — kill switch / trade QA
      └── Writes → swarm_reasoning (Supabase trading-data)

Layer C (layer_c.py) — Execution Simulation
  └── Writes → trade_executions (Supabase trading-data)
```

**RPC Failover:** Skip any provider >100ms P99. All exceed threshold → HALT.

## Current Thresholds (all SPECULATIVE 🔴)

| Gate | Threshold | Status |
|------|-----------|--------|
| Slippage kill | >2% | 🔴 SPECULATIVE |
| RTT skip | >100ms P99 | 🔴 SPECULATIVE |
| DATA_SKEPTIC WARN | >200ms timestamp desync | 🔴 SPECULATIVE |
| DATA_SKEPTIC HALT | >500ms timestamp desync | 🔴 SPECULATIVE |
| System halt | >20% component failure rate | 🟢 Hard rule |

## GOD_TRADE Verdict Logic

GOD_TRADE currently defaults to REJECT because Layer A doesn't supply:
- `volatility_z_score` (not yet implemented)
- `liquidity_depth_1pct` (not yet implemented)

Until these fields are populated, all trades = REJECT. This is correct behaviour.

**Next milestone:** Add volatility Z-score + liquidity depth to layer_a.py → enables APPROVE verdicts.

## Querying Trade Performance

Using supabase-trading MCP:

```sql
-- Recent trade decisions
SELECT created_at, god_trade_verdict, regime_synth_verdict, narrative_arb_verdict
FROM swarm_reasoning
ORDER BY created_at DESC
LIMIT 20;

-- Market snapshots
SELECT created_at, sol_price_usdc, slippage_pct, rtt_ms, rpc_provider
FROM market_snapshots
ORDER BY created_at DESC
LIMIT 20;

-- Execution audit trail
SELECT created_at, verdict, simulation_pnl_pct
FROM trade_executions
ORDER BY created_at DESC
LIMIT 20;
```

## Regime Classification Reference

| Regime | Characteristics | GOD_TRADE Bias |
|--------|----------------|----------------|
| BULL_TREND | Higher highs, momentum positive | APPROVE-leaning |
| BEAR_TREND | Lower lows, momentum negative | REJECT-leaning |
| RANGING | Price oscillating in band | Context-dependent |
| HIGH_VOL | Z-score >2, elevated volatility | REJECT-leaning |
| LOW_LIQ | Depth <threshold | REJECT always |

## Upgrade Backlog (priority order)

1. Add `volatility_z_score` to layer_a.py
2. Add `liquidity_depth_1pct` to layer_a.py
3. Move cron to hourly after Layer A indicators confirmed
4. Add Telegram APPROVE alert in layer_c.py
5. Link dashboard.html to trading-swarm data (replace deprecated bot display)

## SPECULATIVE Threshold Calibration Process

Before promoting any threshold from SPECULATIVE to VERIFIED:
1. Run 100+ forward tests (paper trading)
2. Nobody validates distribution of outcomes
3. Log calibration decision in DECISIONS.md
4. Update threshold label in this file and TRADING-SYSTEM.md
