import asyncio
import logging
from layer_a import deterministic_pull

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("trading-swarm")

async def main():
    logger.info("Trading Swarm v4.0 — starting session")
    logger.info("Mode: Forward-testing simulation only. No live trades.")
    snapshot = await deterministic_pull(asset_pair="SOL/USDC")
    if snapshot is None:
        logger.error("Session aborted — Layer A returned no data")
        return
    logger.info(f"Layer A complete: {snapshot}")

if __name__ == "__main__":
    asyncio.run(main())
