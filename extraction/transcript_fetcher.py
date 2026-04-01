"""Fetch YouTube transcripts for free using youtube-transcript-api."""

import logging
import re
from dataclasses import dataclass
from typing import Optional

from youtube_transcript_api import YouTubeTranscriptApi

logger = logging.getLogger(__name__)


@dataclass
class TranscriptResult:
    """Result from fetching a YouTube transcript."""
    video_id: str
    text: str
    language: str
    is_generated: bool  # auto-generated vs manual captions
    segments: list[dict]  # raw segments with start/duration/text


def extract_video_id(url: str) -> Optional[str]:
    """Extract video ID from various YouTube URL formats."""
    patterns = [
        r'(?:v=|/v/|youtu\.be/)([a-zA-Z0-9_-]{11})',
        r'(?:embed/)([a-zA-Z0-9_-]{11})',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def fetch_transcript(video_url: str) -> Optional[TranscriptResult]:
    """Fetch transcript for a YouTube video. Returns None if unavailable.

    Uses youtube-transcript-api v1.x instance-based API.
    FetchedTranscript carries is_generated, language, language_code directly
    so no separate list() call is needed to detect caption type.
    """
    video_id = extract_video_id(video_url)
    if not video_id:
        logger.error(f"Could not extract video ID from: {video_url}")
        return None

    try:
        ytt_api = YouTubeTranscriptApi()
        # fetch() returns a FetchedTranscript dataclass with .snippets, .is_generated, .language
        transcript = ytt_api.fetch(video_id)

        segments = []
        for snippet in transcript:
            segments.append({
                "start": snippet.start,
                "duration": snippet.duration,
                "text": snippet.text,
            })

        full_text = " ".join(s["text"] for s in segments)

        return TranscriptResult(
            video_id=video_id,
            text=full_text,
            language=transcript.language_code,
            is_generated=transcript.is_generated,
            segments=segments,
        )
    except Exception as e:
        logger.warning(f"Transcript fetch failed for {video_url}: {e}")
        return None
