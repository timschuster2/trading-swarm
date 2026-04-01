"""Batch processing for YouTube video extraction with checkpointing and cost tracking.

Supports three extraction modes:
  "transcript_only" — only Path A (free, Claude via transcript)
  "video_only"      — only Path B (paid, Gemini Flash via full video)
  "hybrid"          — try transcript first; if 0 patterns or unavailable, try video

Checkpoints are written per URL so batches are resumable after interruption.
"""

import asyncio
import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from .video_extractor import extract_from_transcript, extract_from_video
from .db import log_extraction, insert_pattern

logger = logging.getLogger(__name__)


@dataclass
class BatchConfig:
    video_urls: list[str]
    batch_name: str = "default"
    mode: str = "hybrid"  # "transcript_only" | "video_only" | "hybrid"
    cost_cap_usd: float = 150.0
    checkpoint_dir: str = "extraction/checkpoints"


@dataclass
class BatchResult:
    total_processed: int
    total_patterns: int
    total_cost_usd: float
    failed_urls: list[str]
    stopped_reason: Optional[str]  # None, "cost_cap", "complete"


# ---------------------------------------------------------------------------
# Checkpoint helpers
# ---------------------------------------------------------------------------

def _checkpoint_path(config: BatchConfig) -> Path:
    cp_dir = Path(config.checkpoint_dir)
    cp_dir.mkdir(parents=True, exist_ok=True)
    return cp_dir / f"{config.batch_name}.json"


def _load_checkpoint(path: Path) -> dict:
    if path.exists():
        try:
            with open(path) as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load checkpoint {path}: {e}")
    return {
        "batch_name": "",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "processed": {},
        "failed": [],
        "total_cost_usd": 0.0,
        "total_patterns": 0,
    }


def _save_checkpoint(path: Path, data: dict) -> None:
    try:
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        logger.error(f"Failed to save checkpoint {path}: {e}")


# ---------------------------------------------------------------------------
# Single-URL processing
# ---------------------------------------------------------------------------

def _process_url(url: str, mode: str) -> tuple[Optional[object], str]:
    """Process one URL according to mode. Returns (result, mode_used)."""
    if mode == "transcript_only":
        return extract_from_transcript(url), "transcript"

    if mode == "video_only":
        return extract_from_video(url), "video"

    # hybrid: transcript first, video if 0 patterns or unavailable
    transcript_result = extract_from_transcript(url)
    if transcript_result is not None and len(transcript_result.patterns) > 0:
        return transcript_result, "transcript"

    if transcript_result is not None:
        logger.info(f"Transcript yielded 0 patterns for {url} — escalating to video")
    else:
        logger.info(f"No transcript for {url} — escalating to video")

    video_result = extract_from_video(url)
    return video_result, "video"


# ---------------------------------------------------------------------------
# Main batch runner
# ---------------------------------------------------------------------------

async def run_batch(config: BatchConfig) -> BatchResult:
    """Process videos with checkpointing and cost tracking."""
    if config.mode not in ("transcript_only", "video_only", "hybrid"):
        raise ValueError(f"Unknown mode: {config.mode!r}. Use 'transcript_only', 'video_only', or 'hybrid'.")

    cp_path = _checkpoint_path(config)
    cp = _load_checkpoint(cp_path)
    cp["batch_name"] = config.batch_name

    already_processed: set[str] = set(cp.get("processed", {}).keys())
    already_failed: set[str] = set(cp.get("failed", []))
    total_cost: float = cp.get("total_cost_usd", 0.0)
    total_patterns: int = cp.get("total_patterns", 0)
    failed_urls: set[str] = set(already_failed)

    pending = [u for u in config.video_urls if u not in already_processed and u not in already_failed]
    logger.info(
        f"Batch '{config.batch_name}': {len(config.video_urls)} total, "
        f"{len(already_processed)} already done, {len(pending)} to process"
    )

    stopped_reason: Optional[str] = None

    for i, url in enumerate(pending):
        # Cost cap check before each URL
        if total_cost >= config.cost_cap_usd:
            logger.warning(
                f"Cost cap reached (${total_cost:.4f} >= ${config.cost_cap_usd}). Stopping."
            )
            stopped_reason = "cost_cap"
            break

        logger.info(f"[{i+1}/{len(pending)}] Processing: {url}")

        try:
            result, mode_used = await asyncio.to_thread(_process_url, url, config.mode)
        except Exception as e:
            logger.error(f"Unexpected error processing {url}: {e}")
            result = None
            mode_used = "error"

        if result is None:
            logger.warning(f"Extraction returned None for {url}")
            failed_urls.add(url)
            cp["failed"] = list(failed_urls)
            _save_checkpoint(cp_path, cp)
            continue

        # Log to DB (best effort — don't abort batch on DB failure)
        try:
            log_extraction(result)
            for pattern in result.patterns:
                insert_pattern(pattern)
        except Exception as e:
            logger.warning(f"DB write failed for {url}: {e}")

        url_cost = result.cost_usd or 0.0
        url_patterns = len(result.patterns)
        total_cost += url_cost
        total_patterns += url_patterns

        cp["processed"][url] = {
            "patterns": url_patterns,
            "cost": round(url_cost, 6),
            "mode": mode_used,
        }
        cp["total_cost_usd"] = round(total_cost, 6)
        cp["total_patterns"] = total_patterns
        _save_checkpoint(cp_path, cp)

        logger.info(
            f"  -> {url_patterns} patterns, ${url_cost:.4f} (cumulative: ${total_cost:.4f})"
        )

    else:
        # for-else: runs only when loop completes without hitting 'break' (i.e. no cost cap)
        stopped_reason = "complete"

    total_processed = len(cp.get("processed", {}))
    return BatchResult(
        total_processed=total_processed,
        total_patterns=total_patterns,
        total_cost_usd=round(total_cost, 4),
        failed_urls=list(failed_urls),
        stopped_reason=stopped_reason,
    )


def run_batch_sync(config: BatchConfig) -> BatchResult:
    """Synchronous wrapper for run_batch. Use from non-async call sites."""
    return asyncio.run(run_batch(config))
