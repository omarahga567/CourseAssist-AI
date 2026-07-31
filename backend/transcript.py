"""
YouTube transcript extraction and timestamp helpers.
"""

from __future__ import annotations

import re
from typing import Any, List

from youtube_transcript_api import YouTubeTranscriptApi


def seconds_to_timestamp(seconds: float) -> str:
    """Convert a float number of seconds to HH:MM:SS."""
    seconds = int(seconds)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours:02}:{minutes:02}:{secs:02}"


def get_youtube_transcript(youtube_url: str) -> Any:
    """
    Fetch the transcript for a YouTube video.

    Returns a FetchedTranscript (iterable of snippets with .text, .start,
    .duration attributes) from youtube-transcript-api >= 1.0.
    """
    match = re.search(r"(?:v=|youtu\.be/)([\w-]{11})", youtube_url)
    if not match:
        raise ValueError("Invalid YouTube URL")

    video_id = match.group(1)
    api = YouTubeTranscriptApi()
    transcript = api.fetch(video_id)
    return transcript
