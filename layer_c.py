import asyncio
import os
import hashlib
import logging
import time
from typing import Optional
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
db = create_client(SUPABASE_URL, SUPABASE_KEY)
SIM_TRADE_SIZE_USD = 150.0

def generate_sim_hash(reasoning_id: str, timestamp: float) -> str:
    raw = f"SIM:{reasoning_id}:{timestamp}"
    return "SIM_" + hashlib.sha256(raw.encode()).hexdigest()[:32]

def calc_slippage_bps(projected_pct: float) -> float:
    return round(projected_pct * 100, 2)

async def execute_simulation(snapshot: dict, reasoning_id: str, verdict: str) -> dict:
    timestamp = time.time()
    price = snapshot.get("price_close", 0)
    slippage_pct = snapshot.get("projected_slippage_pct", 0)
    provider = snapshot.get("data_sources", {}).get("provider", "unknown")

    if verdict == "APPROVE":
        action_type = "limit_buy"
        trade_status = "simulated"
        slippage_bps = calc_slippage_bps(slippage_pct)
        logger.info(f"EXECUTE (sim): {action_type} {SIM_TRADE_SIZE_USD} USD @ ${price} | slippage: {slippage_bps}bps")
    else:
        action_type = "skip"
        trade_status = "rejected"
        slippage_bps = 0.0
        logger.info(f"EXECUTE: skipped — verdict was {verdict}")

    sim_hash = generate_sim_hash(reasoning_id, timestamp)

    record = {
        "reasoning_id": reasoning_id,
        "action_type": action_type,
        "execution_price": price if verdict == "APPROVE" else None,
        "size_usd": SIM_TRADE_SIZE_USD if verdict == "APPROVE" else None,
        "slippage_bps": slippage_bps,
        "tx_hash": sim_hash,
        "trade_status": trade_status,
        "api_provider_used": provider,
    }

    await asyncio.to_thread(
        lambda: db.table("trade_executions").insert(record).execute()
    )

    logger.info(f"Trade execution logged | status: {trade_status} | hash: {sim_hash[:20]}...")
    return record
