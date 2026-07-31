"""
Document chunking, embeddings, FAISS index, and load_video().
"""

from __future__ import annotations

from typing import List

from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS

from . import config
from .state import state
from .transcript import get_youtube_transcript, seconds_to_timestamp


def create_documents(transcript, tokenizer) -> List[Document]:
    """
    Turn a YouTube transcript into overlapping Document chunks,
    each carrying start/end timestamps in its metadata.
    """
    documents: List[Document] = []
    current_snippets: list = []
    current_tokens = 0
    chunk_id = 1
    video_url = state.video_url or ""

    for snippet in transcript:
        snippet_text = snippet.text.strip()
        snippet_tokens = len(
            tokenizer.encode(snippet_text, add_special_tokens=False)
        )

        # If adding this snippet would exceed the budget, flush the current chunk
        if current_snippets and current_tokens + snippet_tokens > config.MAX_TOKENS:
            text = " ".join(s.text for s in current_snippets)
            start_time = current_snippets[0].start
            end_time = (
                current_snippets[-1].start + current_snippets[-1].duration
            )

            documents.append(
                Document(
                    page_content=text,
                    metadata={
                        "chunk_id": chunk_id,
                        "start_time": start_time,
                        "end_time": end_time,
                        "start_timestamp": seconds_to_timestamp(start_time),
                        "end_timestamp": seconds_to_timestamp(end_time),
                        "video_url": video_url,
                    },
                )
            )
            chunk_id += 1

            # Build overlap from whole trailing snippets
            overlap: list = []
            overlap_tokens = 0
            for s in reversed(current_snippets):
                t = len(
                    tokenizer.encode(s.text, add_special_tokens=False)
                )
                if overlap_tokens + t > config.OVERLAP_TOKENS:
                    break
                overlap.insert(0, s)
                overlap_tokens += t

            current_snippets = overlap
            current_tokens = overlap_tokens

        current_snippets.append(snippet)
        current_tokens += snippet_tokens

    # Final chunk
    if current_snippets:
        text = " ".join(s.text for s in current_snippets)
        start_time = current_snippets[0].start
        end_time = (
            current_snippets[-1].start + current_snippets[-1].duration
        )
        documents.append(
            Document(
                page_content=text,
                metadata={
                    "chunk_id": chunk_id,
                    "start_time": start_time,
                    "end_time": end_time,
                    "start_timestamp": seconds_to_timestamp(start_time),
                    "end_timestamp": seconds_to_timestamp(end_time),
                    "video_url": video_url,
                },
            )
        )

    return documents


def load_video(video_url: str):
    """
    End-to-end: fetch transcript → chunk → embed → build FAISS retriever.
    Updates shared state in-place.
    """
    state.video_url = video_url
    state.transcript = get_youtube_transcript(video_url)
    state.documents = create_documents(state.transcript, state.tokenizer)
    state.vectordb = FAISS.from_documents(
        state.documents, state.embedding_model
    )
    state.retriever = state.vectordb.as_retriever(
        search_kwargs={"k": config.RETRIEVER_K}
    )
    # Invalidate previous summaries (they belonged to the old video)
    state.chapter_summaries = []

    print(f"✅ Loaded new video — {len(state.documents)} chunks indexed.")
    return state.retriever
