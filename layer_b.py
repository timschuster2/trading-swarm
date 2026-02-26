"""
layer_b.py — Probabilistic LLM Swarm (Layer B)
trading-swarm v4.0 | 26 Feb 2026

Agents (run in order):
  1. REGIME_SYNTH   — market environment classification
  2. NARRATIVE_ARB  — sentiment vs price anomaly detection
  3. DATA_SKEPTIC   — ledger audit and desync detection
  4. GOD_TRADE      — kill switch; defaults to REJECT

Rules:
  - Token cap: <4k per agent prompt (§8.1)
  - No LLM self-verification — NARRATIVE_ARB cross-checks against Layer A data (§8.1)
  - GOD_TRADE defaults to REJECT unless all conditions pass
  - All output written to swarm_reasoning table (trading-data Supabase)
  - Uses Anthropic SDK; model: claude-haiku-4-5-20251001 (fast, cheap for swarm calls)
"""

import asyncio
import os
import logging
from typing import Optional
import anthropic
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

db = create_client(SUPABASE_URL, SUPABASE_KEY)
claude = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# Fast, cheap model for swarm agents — upgrade to Sonnet for production
SWARM_MODEL = "claude-haiku-4-5-20251001"
MAX_TOKENS = 512  # Keep responses tight — token discipline (§5)

# ── Shared prompt helper ───────────────────────────────────────────────────────

def call_agent(system: str, user: str) -> tuple[str, int]:
    """
    Call Claude with tight token cap. Returns (response_text, total_tokens).
    Model failover: if primary fails, log and re-raise — caller handles.
    """
    response = claude.messages.create(
        model=SWARM_MODEL,
        max_tokens=MAX_TOKENS,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    text = response.content[0].text
    tokens = response.usage.input_tokens + response.usage.output_tokens
    return text, tokens


# ── Agent 1: REGIME_SYNTH ─────────────────────────────────────────────────────

def regime_synth(snapshot: dict) -> dict:
    """
    Classifies market environment from Layer A data.
    Output: regime label + brief rationale.
    """
    system = (
        "You are REGIME_SYNTH, a market environment classifier. "
        "Given a trading snapshot, classify the current regime in 2-3 sentences. "
        "End with a JSON line: {\"regime\": \"<label>\", \"confidence\": \"<low|medium|high>\"}\n"
        "Regime labels: trending_bullish | trending_bearish | mean_reverting | high_volatility | low_liquidity | unclear\n"
        "Be concise. No padding. No investment advice."
    )
    user = (
        f"Asset: {snapshot.get('asset_pair')}\n"
        f"Price: {snapshot.get('price_close')}\n"
        f"Volatility Z-score: {snapshot.get('volatility_z_score', 'unavailable')}\n"
        f"Liquidity depth 1%: {snapshot.get('liquidity_depth_1pct', 'unavailable')}\n"
        f"Trend structure: {snapshot.get('trend_structure', 'unavailable')}\n"
        f"Slippage: {snapshot.get('projected_slippage_pct')}%\n"
        f"Latency P99: {snapshot.get('latency_p99_ms')}ms"
    )
    text, tokens = call_agent(system, user)
    logger.info(f"REGIME_SYNTH: {text[:100]}...")
    return {"output": text, "tokens": tokens}


# ── Agent 2: NARRATIVE_ARB ────────────────────────────────────────────────────

def narrative_arb(snapshot: dict, regime_output: str) -> dict:
    """
    Detects sentiment vs price anomalies.
    Cross-checks against deterministic Layer A data — NOT LLM self-verification (§8.1).
    Flags if narrative contradicts price/volume data by >5%.
    """
    system = (
        "You are NARRATIVE_ARB, a sentiment-vs-price anomaly detector. "
        "Compare the regime assessment against the hard price/slippage data provided. "
        "Identify any contradiction between narrative and data. "
        "End with a JSON line: {\"bias\": \"<bullish|bearish|neutral|contradictory>\", \"anomaly\": <true|false>, \"divergence_pct\": <number or null>}\n"
        "Rule: If regime narrative contradicts Layer A price data by more than 5%, set anomaly=true. "
        "Be concise. No investment advice."
    )
    user = (
        f"--- Layer A (deterministic ground truth) ---\n"
        f"Asset: {snapshot.get('asset_pair')}\n"
        f"Price close: {snapshot.get('price_close')}\n"
        f"Projected slippage: {snapshot.get('projected_slippage_pct')}%\n"
        f"Latency: {snapshot.get('latency_p99_ms')}ms\n\n"
        f"--- Layer B (REGIME_SYNTH assessment) ---\n"
        f"{regime_output}\n\n"
        "Does the regime narrative contradict the Layer A data? Flag any anomaly."
    )
    text, tokens = call_agent(system, user)
    logger.info(f"NARRATIVE_ARB: {text[:100]}...")
    return {"output": text, "tokens": tokens}


# ── Agent 3: DATA_SKEPTIC ─────────────────────────────────────────────────────

def data_skeptic(snapshot: dict) -> dict:
    """
    Audits the ledger for data quality issues.
    Flags timestamp desync >200ms → WARN; >500ms → HALT signal.
    """
    system = (
        "You are DATA_SKEPTIC, a data quality auditor. "
        "Review the snapshot for data integrity issues. "
        "Check for: missing fields, suspicious values, latency issues. "
        "End with JSON: {\"flag\": <true|false>, \"severity\": \"<none|warn|halt>\", \"reason\": \"<one sentence or null>\"}\n"
        "Rules:\n"
        "- latency_p99_ms > 200 → severity=warn\n"
        "- latency_p99_ms > 500 → severity=halt\n"
        "- price_close = 0 or null → severity=halt\n"
        "- projected_slippage_pct > 2.0 → severity=warn\n"
        "- Any missing critical field → severity=warn\n"
        "Be concise. Flag honestly."
    )
    user = (
        f"Snapshot to audit:\n"
        f"asset_pair: {snapshot.get('asset_pair')}\n"
        f"price_close: {snapshot.get('price_close')}\n"
        f"volatility_z_score: {snapshot.get('volatility_z_score')}\n"
        f"liquidity_depth_1pct: {snapshot.get('liquidity_depth_1pct')}\n"
        f"latency_p99_ms: {snapshot.get('latency_p99_ms')}\n"
        f"projected_slippage_pct: {snapshot.get('projected_slippage_pct')}\n"
        f"data_sources: {snapshot.get('data_sources')}"
    )
    text, tokens = call_agent(system, user)
    logger.info(f"DATA_SKEPTIC: {text[:100]}...")

    # Check for halt signal in output
    halt_triggered = "halt" in text.lower()
    return {"output": text, "tokens": tokens, "halt": halt_triggered}


# ── Agent 4: GOD_TRADE ────────────────────────────────────────────────────────

def god_trade(snapshot: dict, regime: str, narrative: str, skeptic: str, skeptic_halt: bool) -> dict:
    """
    Final kill switch. Reviews all agent outputs. Defaults to REJECT.
    Approves only if all conditions pass cleanly.
    """
    # Auto-reject on DATA_SKEPTIC halt signal — no LLM call needed
    if skeptic_halt:
        logger.warning("GOD_TRADE: Auto-REJECT — DATA_SKEPTIC issued halt signal")
        return {
            "verdict": "REJECT",
            "reason": "DATA_SKEPTIC halt signal",
            "tokens": 0,
        }

    system = (
        "You are GOD_TRADE, the final risk gatekeeper for a trading simulation. "
        "Your default is REJECT. You approve only when evidence is clearly positive. "
        "Review all agent outputs and the snapshot. "
        "End with JSON: {\"verdict\": \"<APPROVE|REJECT>\", \"reason\": \"<one sentence>\"}\n"
        "Reject if ANY of the following:\n"
        "- DATA_SKEPTIC flagged any issue\n"
        "- NARRATIVE_ARB detected anomaly\n"
        "- Regime is high_volatility, low_liquidity, or unclear\n"
        "- Slippage > 2%\n"
        "- Price is 0 or suspicious\n"
        "- Latency > 100ms\n"
        "This is a simulation. No real trades. Be conservative. When in doubt: REJECT."
    )
    user = (
        f"--- Snapshot ---\n"
        f"Asset: {snapshot.get('asset_pair')} | Price: {snapshot.get('price_close')}\n"
        f"Slippage: {snapshot.get('projected_slippage_pct')}% | Latency: {snapshot.get('latency_p99_ms')}ms\n\n"
        f"--- REGIME_SYNTH ---\n{regime}\n\n"
        f"--- NARRATIVE_ARB ---\n{narrative}\n\n"
        f"--- DATA_SKEPTIC ---\n{skeptic}\n\n"
        "Issue your verdict."
    )
    text, tokens = call_agent(system, user)
    logger.info(f"GOD_TRADE: {text[:100]}...")

    verdict = "REJECT"  # default
    if '"verdict": "APPROVE"' in text or "'verdict': 'APPROVE'" in text:
        verdict = "APPROVE"

    return {"verdict": verdict, "output": text, "tokens": tokens}


# ── Ledger Writer ─────────────────────────────────────────────────────────────

def write_reasoning(snapshot_id: str, regime: dict, narrative: dict, skeptic: dict, god: dict) -> str:
    """Write full swarm reasoning to swarm_reasoning table. Returns reasoning_id."""
    total_tokens = (
        regime.get("tokens", 0)
        + narrative.get("tokens", 0)
        + skeptic.get("tokens", 0)
        + god.get("tokens", 0)
    )

    # Parse narrative bias from output
    bias = "unknown"
    narrative_output = narrative.get("output", "")
    for label in ["bullish", "bearish", "neutral", "contradictory"]:
        if label in narrative_output.lower():
            bias = label
            break

    record = {
        "snapshot_id": snapshot_id,
        "regime_synth_output": regime.get("output"),
        "narrative_arb_bias": bias,
        "data_skeptic_flag": skeptic.get("halt", False),
        "god_verdict": god.get("verdict", "REJECT"),
        "full_prompt_context": {
            "regime": regime.get("output"),
            "narrative": narrative.get("output"),
            "skeptic": skeptic.get("output"),
            "god": god.get("output"),
        },
        "token_cost": total_tokens,
        "failure_injected": False,
    }

    result = db.table("swarm_reasoning").insert(record).execute()
    reasoning_id = result.data[0]["reasoning_id"]
    logger.info(f"Swarm reasoning written | verdict: {god.get('verdict')} | tokens: {total_tokens}")
    return reasoning_id


# ── Main Orchestrator ─────────────────────────────────────────────────────────

async def run_swarm(snapshot: dict, snapshot_id: str) -> dict:
    """
    Run all 4 Layer B agents in sequence.
    Returns final verdict dict.
    """
    logger.info("Layer B swarm starting...")

    # Agent 1
    regime = regime_synth(snapshot)

    # Agent 2
    narrative = narrative_arb(snapshot, regime["output"])

    # Agent 3
    skeptic = data_skeptic(snapshot)

    # Agent 4
    god = god_trade(
        snapshot,
        regime["output"],
        narrative["output"],
        skeptic["output"],
        skeptic["halt"],
    )

    # Write to Supabase
    reasoning_id = write_reasoning(snapshot_id, regime, narrative, skeptic, god)

    return {
        "reasoning_id": reasoning_id,
        "verdict": god["verdict"],
        "regime": regime["output"],
        "narrative_bias": narrative.get("output", ""),
        "skeptic_flag": skeptic["halt"],
        "total_tokens": (
            regime.get("tokens", 0)
            + narrative.get("tokens", 0)
            + skeptic.get("tokens", 0)
            + god.get("tokens", 0)
        ),
    }
