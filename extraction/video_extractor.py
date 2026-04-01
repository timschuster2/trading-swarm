"""Extract trading patterns from YouTube videos.

Two extraction paths:
  Path A (transcript): Free — fetch transcript via youtube-transcript-api, send to Claude Sonnet.
  Path B (video):      Paid — send full video URL to Gemini 2.5 Flash for visual extraction.

Smart entry point `extract_video()` tries transcript first, falls back to video when needed.
"""

import logging
import os
from typing import Optional
from urllib.parse import urlparse

from dotenv import load_dotenv

from .schema import ExtractionResult
from .pattern_extractor import (
    EXTRACTION_PROMPT,
    EXTRACTION_MODEL,
    _parse_patterns,
    extract_patterns_from_text,
)
from .transcript_fetcher import fetch_transcript

load_dotenv()
logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-2.5-flash"

# Gemini 2.5 Flash pricing (approx USD per 1M tokens)
_GEMINI_INPUT_COST_PER_M = 0.15
_GEMINI_OUTPUT_COST_PER_M = 0.60
_GEMINI_THINKING_COST_PER_M = 3.50  # Gemini 2.5 Flash thinking output rate

VIDEO_EXTRACTION_PROMPT = (
    EXTRACTION_PROMPT
    + "\n\nAdditional instructions for video analysis:\n"
    "- Read exact indicator values visible on TradingView charts\n"
    "- Note timestamps when setups are demonstrated\n"
    "- Correlate verbal explanation with visual chart state"
)


def extract_from_transcript(video_url: str) -> Optional[ExtractionResult]:
    """Path A: Free transcript -> Claude extraction.

    Returns None if no transcript is available for the video.
    """
    transcript = fetch_transcript(video_url)
    if transcript is None:
        logger.info(f"No transcript available for: {video_url}")
        return None

    if not transcript.text.strip():
        logger.warning(f"Transcript fetched but empty for: {video_url}")
        return None

    logger.info(
        f"Transcript fetched for {transcript.video_id} "
        f"({len(transcript.segments)} segments, generated={transcript.is_generated})"
    )
    result = extract_patterns_from_text(
        transcript.text,
        source_url=video_url,
        source_type="youtube_transcript",
    )
    return result


def extract_from_video(video_url: str) -> Optional[ExtractionResult]:
    """Path B: Full video -> Gemini Flash extraction.

    Returns None on failure or missing API key.
    """
    if not GEMINI_API_KEY:
        logger.warning("GEMINI_API_KEY not set — skipping video extraction")
        return None

    try:
        from google import genai
        from google.genai import types
    except ImportError:
        logger.warning("google-genai not installed — skipping video extraction")
        return None

    _ALLOWED_HOSTS = {"www.youtube.com", "youtube.com", "youtu.be"}
    parsed = urlparse(video_url)
    if parsed.scheme not in ("https", "http") or parsed.netloc not in _ALLOWED_HOSTS:
        logger.warning(f"Rejected non-YouTube URL for video extraction: {video_url}")
        return None

    try:
        client = genai.Client(api_key=GEMINI_API_KEY)

        video_part = types.Part(
            file_data=types.FileData(file_uri=video_url)
        )

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=[VIDEO_EXTRACTION_PROMPT, video_part],
        )

        raw_text = response.text or ""

        # Estimate cost from usage metadata when available
        cost = 0.0
        usage = getattr(response, "usage_metadata", None)
        if usage:
            input_tokens = getattr(usage, "prompt_token_count", 0) or 0
            output_tokens = getattr(usage, "candidates_token_count", 0) or 0
            thinking_tokens = getattr(usage, "thoughts_token_count", 0) or 0
            cost = (
                input_tokens * _GEMINI_INPUT_COST_PER_M
                + output_tokens * _GEMINI_OUTPUT_COST_PER_M
                + thinking_tokens * _GEMINI_THINKING_COST_PER_M
            ) / 1_000_000

        patterns = _parse_patterns(raw_text, source_url=video_url, source_type="youtube_video")

        return ExtractionResult(
            source_type="youtube_video",
            source_url=video_url,
            patterns=patterns,
            raw_response=raw_text[:5000],
            model_used=GEMINI_MODEL,
            cost_usd=round(cost, 4) if cost else None,
        )

    except Exception as e:
        logger.error(f"Gemini video extraction failed for {video_url}: {e}")
        return None


def extract_video(video_url: str, force_video: bool = False) -> Optional[ExtractionResult]:
    """Smart extraction: try transcript first, fall back to video if needed.

    Args:
        video_url:    YouTube video URL.
        force_video:  Skip transcript path and go straight to Gemini video extraction.

    Returns:
        ExtractionResult or None if both paths fail.
    """
    if not force_video:
        result = extract_from_transcript(video_url)
        if result is not None:
            return result
        logger.info(f"Transcript path failed for {video_url}, falling back to video extraction")

    return extract_from_video(video_url)
