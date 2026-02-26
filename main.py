"""
main.py — Trading Swarm v4.0 Entry Point
26 Feb 2026 | timschuster2/trading-swarm

Forward-testing simulation only.
No real trades. Educational simulation. No investment advice.
"""

import asyncio
import logging
from layer_a import deterministic_pull, db as supabase_db
from layer_b import run_swarm
from layer_c import execute_simulation

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("trading-swarm")


async def main():
    logger.info("=" * 50)
    logger.info("Trading Swarm v4.0 — session start")
    logger.info("Mode: Forward-testing simulation only. No live trades.")
    logger.info("=" * 50)

    # ── Layer A: Deterministic pull ───────────────────────────────────────────
    snapshot = await deterministic_pull(asset_pair="SOL/USDC")

    if snapshot is None:
        logger.error("Session aborted — Layer A returned no data")
        return

    logger.info(
        f"Layer A: {snapshot['asset_pair']} @ ${snapshot['price_close']} | "
        f"RTT: {snapshot['latency_p99_ms']}ms | "
        f"Slippage: {snapshot['projected_slippage_pct']}%"
    )

    # Get the snapshot_id from Supabase (most recent row for this asset)
    result = (
        supabase_db.table("market_snapshots")
        .select("snapshot_id")
        .eq("asset_pair", snapshot["asset_pair"])
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )

    if not result.data:
        logger.error("Could not retrieve snapshot_id — aborting Layer B")
        return

    snapshot_id = result.data[0]["snapshot_id"]

    # ── Layer B: LLM swarm ────────────────────────────────────────────────────
    result = await run_swarm(snapshot, snapshot_id)

    logger.info("=" * 50)
    logger.info(f"SWARM VERDICT: {result['verdict']}")
    logger.info(f"Tokens used: {result['total_tokens']}")
    logger.info(f"Reasoning ID: {result['reasoning_id']}")
    logger.info("=" * 50)

    # ── Layer C: Execution simulation ─────────────────────────────────────────
    trade = await execute_simulation(snapshot, result["reasoning_id"], result["verdict"])
    logger.info(f"Layer C: {trade['action_type']} | status: {trade['trade_status']} | hash: {trade['tx_hash'][:20]}...")


if __name__ == "__main__":
    asyncio.run(main())
