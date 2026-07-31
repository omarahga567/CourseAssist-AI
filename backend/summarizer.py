"""
Map-reduce chapter summarisation of a video transcript.
"""

from __future__ import annotations

from typing import Any, Dict, List

from langchain_core.prompts import PromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter

from . import config
from .generation import generate_text_quiet, generate_text_stream_plain
from .transcript import seconds_to_timestamp


# ---------------------------------------------------------------------------
# Chapter bucketing
# ---------------------------------------------------------------------------
def group_transcript_by_hour(
    transcript, hour_seconds: int = None
) -> Dict[int, list]:
    """
    Groups transcript snippets into 1-hour buckets based on start time.
    bucket 0 → Chapter 1 (00:00:00 – 01:00:00), etc.
    """
    if hour_seconds is None:
        hour_seconds = config.HOUR_SECONDS
    buckets: Dict[int, list] = {}
    for snippet in transcript:
        hour_index = int(snippet.start // hour_seconds)
        buckets.setdefault(hour_index, []).append(snippet)
    return buckets


def build_chapters(
    transcript,
    hour_seconds: int = None,
    min_chapter_seconds: int = None,
) -> List[dict]:
    """
    Turns hourly buckets into a list of chapter dicts.
    A short trailing chapter (< min_chapter_seconds) is merged into the
    previous one instead of getting its own paragraph.
    """
    if hour_seconds is None:
        hour_seconds = config.HOUR_SECONDS
    if min_chapter_seconds is None:
        min_chapter_seconds = config.MIN_CHAPTER_SECONDS

    buckets = group_transcript_by_hour(transcript, hour_seconds)
    bucket_indices = sorted(buckets.keys())

    # Merge a short trailing chapter into the one before it
    if len(bucket_indices) > 1:
        last_idx = bucket_indices[-1]
        last_snippets = buckets[last_idx]
        last_duration = (
            (last_snippets[-1].start + last_snippets[-1].duration)
            - last_snippets[0].start
        )
        if last_duration < min_chapter_seconds:
            prev_idx = bucket_indices[-2]
            buckets[prev_idx].extend(last_snippets)
            del buckets[last_idx]
            bucket_indices = sorted(buckets.keys())

    chapters = []
    for order, idx in enumerate(bucket_indices, start=1):
        snippets = buckets[idx]
        chapter_text = " ".join(s.text.strip() for s in snippets)
        start_ts = seconds_to_timestamp(snippets[0].start)
        end_ts = seconds_to_timestamp(
            snippets[-1].start + snippets[-1].duration
        )
        chapters.append(
            {
                "chapter_number": order,
                "start_timestamp": start_ts,
                "end_timestamp": end_ts,
                "text": chapter_text,
                "is_only_chapter": len(bucket_indices) == 1,
            }
        )
    return chapters


# ---------------------------------------------------------------------------
# Text splitting for very long chapters
# ---------------------------------------------------------------------------
chapter_splitter = RecursiveCharacterTextSplitter(
    chunk_size=config.CHAPTER_SPLIT_CHUNK_SIZE,
    chunk_overlap=config.CHAPTER_SPLIT_OVERLAP,
)


def chunk_chapter_text(
    chapter_text: str, max_chars: int = None
) -> List[str]:
    """
    Only split if the chapter is extremely long.
    18 k characters ≈ 4-5 k tokens – still safe for Mistral-7B.
    """
    if max_chars is None:
        max_chars = config.CHAPTER_MAX_CHARS
    if len(chapter_text) <= max_chars:
        return [chapter_text]
    return chapter_splitter.split_text(chapter_text)


# ---------------------------------------------------------------------------
# Prompts
# ---------------------------------------------------------------------------
mini_summary_prompt = PromptTemplate(
    template="""You are summarizing part of a course transcript.

Write a short, plain summary (3-6 lines) of the main points covered in the text below.
Do not add opinions, do not repeat these instructions, only output the summary text.

Transcript part:
{text}

Summary:""",
    input_variables=["text"],
)

chapter_summary_prompt = PromptTemplate(
    template="""You are creating a chapter summary for a course video.

Using the notes below, write ONE paragraph that summarizes everything covered in this
part of the course. This is {chapter_label}, covering {start_ts} to {end_ts}.

{length_instruction}

Rules:
- Only output the paragraph. No title, no bullet points, no preamble, no "Summary:" label.
- Write it as flowing prose a student could read to catch up on this part of the course.
- Do not invent information that isn't in the notes below.

Notes:
{text}

Paragraph:""",
    input_variables=[
        "text", "chapter_label", "start_ts", "end_ts", "length_instruction"
    ],
)


# ---------------------------------------------------------------------------
# Map / reduce
# ---------------------------------------------------------------------------
def map_summarize_pieces(pieces: List[str], debug: bool = False) -> List[str]:
    """
    Turns each transcript piece into a short bullet-point summary.
    Runs quietly (no streaming) since these are intermediate notes.
    """
    mini_summaries = []
    for i, piece in enumerate(pieces, 1):
        prompt = mini_summary_prompt.format(text=piece)
        summary = generate_text_quiet(prompt, max_new_tokens=120)
        mini_summaries.append(summary)
        if debug:
            print(f"   map {i}/{len(pieces)} done")
    return mini_summaries


def reduce_chapter_summary(
    mini_summaries: List[str], chapter: dict, stream: bool = True
) -> str:
    """
    Combines the map-step notes into one flowing paragraph.
    This is what the student actually reads, so it streams live when stream=True.
    """
    combined_notes = "\n".join(mini_summaries)

    length_instruction = (
        "Keep it concise (5-12 lines)."
        if chapter.get("is_only_chapter") or len(chapter["text"]) < 10000
        else "Write a detailed paragraph of roughly 10-25 lines."
    )

    prompt = chapter_summary_prompt.format(
        text=combined_notes,
        chapter_label=f"Chapter {chapter['chapter_number']}",
        start_ts=chapter["start_timestamp"],
        end_ts=chapter["end_timestamp"],
        length_instruction=length_instruction,
    )

    if stream:
        return generate_text_stream_plain(prompt, max_new_tokens=400)
    return generate_text_quiet(prompt, max_new_tokens=400)


def summarize_chapter(
    chapter: dict, stream: bool = True, debug: bool = False
) -> dict:
    pieces = chunk_chapter_text(chapter["text"])
    mini_summaries = map_summarize_pieces(pieces, debug=debug)
    summary_text = reduce_chapter_summary(mini_summaries, chapter, stream=stream)

    header = (
        f"### Chapter {chapter['chapter_number']}  "
        f"({chapter['start_timestamp']} – {chapter['end_timestamp']})\n\n"
    )
    return {
        "chapter_number": chapter["chapter_number"],
        "start_timestamp": chapter["start_timestamp"],
        "end_timestamp": chapter["end_timestamp"],
        "summary": summary_text,
        "markdown": header + summary_text,
    }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def generate_video_summary(
    transcript,
    hour_seconds: int = None,
    stream: bool = True,
) -> List[dict]:
    chapters = build_chapters(transcript, hour_seconds)
    summaries = []
    for i, chapter in enumerate(chapters, 1):
        print(
            f"\n⏳ Chapter {i}/{len(chapters)} "
            f"({chapter['start_timestamp']}–{chapter['end_timestamp']})\n"
        )
        summaries.append(summarize_chapter(chapter, stream=stream))
    return summaries


def render_summary_markdown(chapter_summaries: List[dict]) -> str:
    return "\n\n".join(c["markdown"] for c in chapter_summaries)
