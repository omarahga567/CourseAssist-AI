"""
Shared runtime state.

Replaces the notebook-level globals (transcript, documents, vectordb,
retriever, chapter_summaries, …).  Every module that needs mutable
shared data imports and mutates attributes on the single `state`
instance defined here.
"""

from __future__ import annotations

from typing import Any, List, Optional

from langchain_core.documents import Document


class AppState:
    """Mutable container for everything that used to be a notebook global."""

    def __init__(self) -> None:
        # YouTube / transcript
        self.video_url: Optional[str] = None
        self.transcript: Optional[Any] = None  # list of FetchedTranscriptSnippet

        # RAG index
        self.documents: List[Document] = []
        self.vectordb: Any = None  # FAISS instance
        self.retriever: Any = None

        # Summaries / study aids (populated after /summarize)
        self.chapter_summaries: List[dict] = []

        # Heavy objects loaded once at startup
        self.tokenizer: Any = None
        self.model: Any = None
        self.embedding_model: Any = None


# Singleton used by the whole package
state = AppState()
