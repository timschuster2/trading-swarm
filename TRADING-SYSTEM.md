# Trading System Reference

**Version:** 1.0 | **Date:** 1 Mar 2026 | **Owner:** Timothy Schuster (Sydney, AU)
**Purpose:** All trading-specific specs, thresholds, schemas, and sub-agent roles.
**Load when:** Working on trading-swarm repo, Layer A/B/C changes, Supabase trading-data, RPC config.
**Do not load for:** Swarm governance → FRAMEWORK.md | Infrastructure topology → ARCHITECTURE.md
**Update rule:** Elon updates on any trading-swarm change. Nobody gates. Version bump required.
**Reality standard:** ✅ Verified | 🟡 Built, unverified | 🔴 Designed, not built | 🟠 SPECULATIVE (needs validation)

---

## 1. System Overview

**Repo:** `timschuster2/trading-swarm` (private)
**Platform:** Railway cron — `0 22 * * *` (8:00am AEST daily)
**Language:** Python
**Database:** Supabase trading-data (isolated — never cross-writes with swarm-data)
**Status:** ✅ Live — running daily. GOD_TRADE currently always returns REJECT (Layer A missing volatility/liquidity signals).

**Architecture:** Three sequential layers — deterministic data ingestion → LLM reasoning → execution simulation.

```
Layer A (layer_a.py) — Deterministic sentinel
    → Supabase write: market_snapshots
Layer B (layer_b.py) — LLM reasoning (4 sub-agents)
    → reads market_snapshots
    → Supabase write: swarm_reasoning
Layer C (layer_c.py) — Execution simulation + audit
    → reads swarm_reasoning
    → Supabase write: trade_executions
    → Telegram alert on APPROVE (NOT YET BUILT 🔴)
```

---

## 2. Layer A — Deterministic Sentinel

**File:** `layer_a.py`
**Role:** Data ingestion, health checks, slippage gate. No LLM calls. Pure deterministic logic.

**Checks performed each run:**
1. Measure RTT to all three RPC providers — select fastest below threshold
2. Fetch SOL/USDC price via Jupiter quote endpoint
3. Calculate projected slippage
4. Apply slippage gate — REJECT if >2% (🟠 SPECULATIVE threshold)
5. Write `market_snapshot` to Supabase trading-data

**Next milestone:** Add volatility Z-score + liquidity depth → unlocks GOD_TRADE APPROVE verdicts

---

## 3. Layer B — LLM Reasoning (4 Sub-Agents)

**File:** `layer_b.py`
**Role:** Parallel LLM analysis via 4 trading sub-agents. Reads market_snapshot. Writes swarm_reasoning.

These are trading-specific sub-agents — not swarm core agents. They do not appear in Framework §3.0.

| Sub-Agent | Function | Key Rule |
|-----------|----------|----------|
| **REGIME_SYNTH** | Market environment classification | Injects dynamic anti-patterns from DB (e.g., volatility spikes) |
| **NARRATIVE_ARB** | Sentiment vs. price anomaly detection | Cross-verify against deterministic Layer A data. No LLM self-verification. |
| **DATA_SKEPTIC** | Ledger audit and timestamp desync detection | >200ms desync → WARN + log. >500ms → HALT. |
| **GOD_TRADE** | Kill switch / trade QA | Defaults to REJECT. Checks: latency desync, correlation >0.7, slippage gate, front-running risk. |

**GOD_TRADE unlock condition:** Requires volatility Z-score AND liquidity depth from Layer A before it can issue APPROVE. Currently returns REJECT on every run by design.

---

## 4. Layer C — Execution Simulation

**File:** `layer_c.py`
**Role:** Reads swarm_reasoning. Simulates trade execution. Writes full audit trail to trade_executions.

**On APPROVE verdict:**
- Simulate execution at current Jupiter price
- Record tx_hash, slippage_bps, api_provider_used
- Send Telegram alert — 🔴 NOT YET BUILT

**On REJECT verdict:** Log the rejection with full reasoning context. No execution.

---

## 5. RPC Providers & Failover

| Provider | Role | RTT Threshold |
|----------|------|---------------|
| Helius | Primary | <100ms P99 |
| QuickNode | Failover 1 | <100ms P99 |
| Ankr | Failover 2 | <100ms P99 |

**Rotation rule:** Measure RTT before each pull. Skip any provider exceeding threshold. If all exceed threshold → HALT session and log. Do not proceed with stale or high-latency data.

**Hard halt rule:** >20% component failure rate → halt, log, flag. Never continue trade execution past this threshold.

---

## 6. Retry & Error Handling (tenacity)

| Context | Backoff | Max Attempts |
|---------|---------|-------------|
| Solana RPC calls | exponential 50ms–200ms | 3 |
| External REST APIs (Helius, Birdeye) | exponential 1s–5s | 3 |
| On 429 rate limit | Honour Retry-After header; else exponential | 3 |

After 3 failed attempts on any provider → failover to next. All providers exhausted → HALT and log to Supabase.

🟠 **All retry thresholds are SPECULATIVE** — validate against 100+ forward-test sessions. Elon promotes to OBSERVED once validation data exists.

---

## 7. Slippage Gate

**Endpoint:** Jupiter quote endpoint (direct API call — CCXT has no equivalent for this)
**Current kill threshold:** >2% projected slippage = REJECT
**Formula:** `vol_z_score * 0.5%`

🟠 **Both threshold and formula are SPECULATIVE** — not backtested. Elon must validate against 100+ live SOL/USDC fills before treating as hard rules.

---

## 8. Supabase Schema (trading-data project)

**Project ref:** `bugibfudbgoeajmsqcsu`
**URL:** `https://bugibfudbgoeajmsqcsu.supabase.co`
**Isolation:** Zero cross-writes with swarm-data. Ever.

```sql
-- Table 1: Market Snapshots (Layer A — deterministic)
CREATE TABLE market_snapshots (
    snapshot_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    asset_pair VARCHAR(20) NOT NULL,
    price_close NUMERIC NOT NULL,
    volatility_z_score NUMERIC,           -- not yet populated 🔴
    liquidity_depth_1pct NUMERIC,          -- not yet populated 🔴
    trend_structure VARCHAR(50),
    data_sources JSONB,
    latency_p99_ms NUMERIC,
    projected_slippage_pct NUMERIC
);

-- Table 2: Swarm Reasoning (Layer B — probabilistic)
CREATE TABLE swarm_reasoning (
    reasoning_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    snapshot_id UUID REFERENCES market_snapshots(snapshot_id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    regime_synth_output TEXT,
    narrative_arb_bias VARCHAR(50),
    data_skeptic_flag BOOLEAN DEFAULT false,
    god_verdict VARCHAR(20) NOT NULL,      -- currently always 'REJECT'
    full_prompt_context JSONB,
    token_cost NUMERIC,
    failure_injected BOOLEAN DEFAULT false
);

-- Table 3: Trade Executions (Layer C — audit trail)
CREATE TABLE trade_executions (
    trade_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    reasoning_id UUID REFERENCES swarm_reasoning(reasoning_id),
    executed_at TIMESTAMPTZ DEFAULT NOW(),
    action_type VARCHAR(20),
    execution_price NUMERIC,
    size_usd NUMERIC,
    slippage_bps NUMERIC,
    tx_hash VARCHAR(100),
    trade_status VARCHAR(20),
    api_provider_used VARCHAR(50)
);
```

---

## 9. Failure Injection (Test Environments Only)

```python
def inject_failure(prob: float = 0.2, seed: int = 42) -> None:
    """Reproducible failure injection. Test environments only."""
    import random
    rng = random.Random(seed)
    if rng.random() < prob:
        raise Exception(f"Simulated RPC drop [seed={seed}, prob={prob}]")
```

**Hard gate:** `inject_failure()` callable ONLY when `ENVIRONMENT=test` env var is set. Never in live or paper trading sessions.

---

## 10. Telegram Urgency Tags (trading-swarm alerts)

All Telegram messages from trading-swarm must carry urgency prefix:

| Urgency | Tag | Trigger |
|---------|-----|---------|
| `CRITICAL` | 🔴 | Trading halt, >20% failure rate, GOD_TRADE emergency |
| `HIGH` | 🟠 | APPROVE verdict, all RPC providers down |
| `NORMAL` | 🟡 | Daily run summary, Layer B reasoning digest |
| `LOW` | ⚪ | Data quality warnings, SPECULATIVE threshold breaches |

Messages without urgency tags are a process failure.

---

## 11. Kronos-mini (Parked)

**Purpose:** ML-based probabilistic OHLCV forecasting — 400 candles in, 120-candle prediction out.
**Model:** NeoQuasar/Kronos-mini (4.1M params, CPU inference, 2048 context)
**Repo:** github.com/shiyu-coder/Kronos | HuggingFace: NeoQuasar/Kronos-mini
**Position in stack:** Between Layer A data ingestion and Layer B reasoning (CHART agent)
**Unlock condition:** Validate on Solana data first. Fine-tuning (Qlib) parked until GPU available.
**Owner:** Elon builds, Elon validates signal quality.

---

## 12. CCXT Rule

**All crypto exchange connections use CCXT library. Never direct exchange APIs.**

Exception: Jupiter quote endpoint for slippage calculation — no CCXT equivalent exists. This is the only approved direct API call in the trading system.

---

## 13. Known Gaps

| Gap | Impact | Priority |
|-----|--------|----------|
| volatility_z_score not populated in Layer A | GOD_TRADE cannot issue APPROVE — always REJECTs | 🔴 High |
| liquidity_depth_1pct not populated in Layer A | Same — APPROVE blocked | 🔴 High |
| Telegram APPROVE alert not built | No live notification when trade signal fires | 🟠 Medium |
| All thresholds SPECULATIVE | Can't trust signals until 100+ forward tests | 🟠 Medium |
| Cron still daily — needs hourly after Layer A upgraded | Low signal frequency | 🟡 Low |

---

*End of TRADING-SYSTEM-v1.0*
*Update trigger: any Layer A/B/C change, schema migration, threshold validation, or new sub-agent.*
