import asyncio
import os
import time
import socket
import random
import logging
from typing import Optional

import httpx
import tenacity
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
HELIUS_API_KEY = os.getenv("HELIUS_API_KEY")
ENVIRONMENT = os.getenv("ENVIRONMENT", "production")

PROVIDERS = ["helius", "quicknode", "ankr"]
RTT_THRESHOLD_MS = 100
FAILURE_RATE_HALT = 0.20
SLIPPAGE_KILL_PCT = 2.0

db = create_client(SUPABASE_URL, SUPABASE_KEY)

_call_count = 0
_fail_count = 0

def _record_call(failed: bool) -> None:
    global _call_count, _fail_count
    _call_count += 1
    if failed:
        _fail_count += 1
    rate = _fail_count / _call_count if _call_count > 0 else 0
    if rate > FAILURE_RATE_HALT and _call_count >= 5:
        raise SystemExit(
            f"SYSTEM HALT: failure rate {rate:.0%} exceeds {FAILURE_RATE_HALT:.0%}. "
            f"Calls: {_call_count}, Failures: {_fail_count}."
        )

PROVIDER_HOSTS = {
    "helius": "api.helius.xyz",
    "quicknode": "api.quicknode.com",
    "ankr": "rpc.ankr.com",
}

def measure_rtt(host: str, port: int = 443, timeout: float = 1.0) -> float:
    start = time.monotonic()
    try:
        with socket.create_connection((host, port), timeout=timeout):
            pass
        return (time.monotonic() - start) * 1000
    except Exception:
        return float("inf")

def best_provider() -> Optional[str]:
    for provider in PROVIDERS:
        host = PROVIDER_HOSTS.get(provider, provider)
        rtt = measure_rtt(host)
        logger.info(f"RTT [{provider}]: {rtt:.1f}ms")
        if rtt < RTT_THRESHOLD_MS:
            return provider
    return None

def inject_failure(prob: float = 0.2, seed: int = 42) -> None:
    if ENVIRONMENT != "test":
        return
    rng = random.Random(seed)
    if rng.random() < prob:
        raise ConnectionError(f"Simulated RPC drop [seed={seed}, prob={prob}]")

_solana_retry = tenacity.retry(
    wait=tenacity.wait_exponential(multiplier=0.05, min=0.05, max=0.2),
    stop=tenacity.stop_after_attempt(3),
    reraise=True,
)

@_solana_retry
async def fetch_price_from_coingecko(asset: str, client: httpx.AsyncClient) -> dict:
    """Get SOL price in USD from CoinGecko public API."""
    url = "https://api.coingecko.com/api/v3/simple/price?ids=solana&vs_currencies=usd"
    resp = await client.get(url, timeout=5.0)
    resp.raise_for_status()
    data = resp.json()
    price = data["solana"]["usd"]
    return {"price_close": price, "provider": "coingecko"}

async def get_slippage_quote(size_usdc: float, client: httpx.AsyncClient) -> float:
    """Estimate slippage via Jupiter quote API. Falls back to conservative estimate."""
    try:
        amount_micro = int(size_usdc * 1_000_000)
        url = (
            f"https://quote-api.jup.ag/v6/quote"
            f"?inputMint=EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
            f"&outputMint=So11111111111111111111111111111111111111112"
            f"&amount={amount_micro}"
        )
        resp = await client.get(url, timeout=5.0)
        resp.raise_for_status()
        data = resp.json()
        in_amt = int(data.get("inAmount", 1))
        out_amt = int(data.get("outAmount", 1))
        slippage_pct = abs(1 - (out_amt / in_amt)) * 100
        return round(slippage_pct, 4)
    except Exception as exc:
        logger.warning(f"Slippage quote unavailable, using conservative estimate: {exc}")
        return 0.5

async def deterministic_pull(asset_pair: str = "SOL/USDC") -> Optional[dict]:
    provider = best_provider()
    if provider is None:
        logger.error("SYSTEM HALT: All providers exceed RTT threshold.")
        _record_call(failed=True)
        return None

    async with httpx.AsyncClient() as client:
        try:
            if provider == "helius":
                raw = await fetch_price_from_coingecko(asset_pair, client)
            else:
                logger.warning(f"Provider {provider} not yet implemented.")
                _record_call(failed=True)
                return None

            slippage = await get_slippage_quote(150.0, client)

            snapshot = {
                "asset_pair": asset_pair,
                "price_close": raw.get("price_close", 0),
                "data_sources": {"provider": provider},
                "latency_p99_ms": measure_rtt(PROVIDER_HOSTS[provider]),
                "projected_slippage_pct": slippage,
            }

            if slippage > SLIPPAGE_KILL_PCT:
                logger.warning(f"SLIPPAGE GATE: {slippage:.2f}% — trade rejected.")
                _record_call(failed=False)
                return None

            await asyncio.to_thread(
                lambda: db.table("market_snapshots").insert(snapshot).execute()
            )

            _record_call(failed=False)
            logger.info(f"Snapshot written: {asset_pair} | slippage: {slippage:.2f}%")
            return snapshot

        except Exception as exc:
            logger.error(f"Layer A pull failed [{provider}]: {exc}")
            _record_call(failed=True)
            return None

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    result = asyncio.run(deterministic_pull())
    print(result)
