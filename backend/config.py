"""
Environment-based configuration.

All secrets and tunable knobs live here.  Nothing is hard-coded;
values are read from environment variables (with sensible defaults
for non-secret settings).
"""

from __future__ import annotations

import os


# ---------------------------------------------------------------------------
# Secrets (must be supplied via environment)
# ---------------------------------------------------------------------------
NGROK_TOKEN: str = os.environ.get("NGROK_TOKEN", "")
API_KEY: str = os.environ.get("API_KEY", "")

# ---------------------------------------------------------------------------
# Model
# ---------------------------------------------------------------------------
MODEL_NAME: str = os.environ.get(
    "MODEL_NAME", "mistralai/Mistral-7B-Instruct-v0.3"
)
EMBEDDING_MODEL_NAME: str = os.environ.get(
    "EMBEDDING_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2"
)

# ---------------------------------------------------------------------------
# Chunking / retrieval
# ---------------------------------------------------------------------------
MAX_TOKENS: int = int(os.environ.get("MAX_TOKENS", "2000"))
OVERLAP_TOKENS: int = int(os.environ.get("OVERLAP_TOKENS", "100"))
RETRIEVER_K: int = int(os.environ.get("RETRIEVER_K", "2"))

# ---------------------------------------------------------------------------
# Summarisation
# ---------------------------------------------------------------------------
HOUR_SECONDS: int = int(os.environ.get("HOUR_SECONDS", "3600"))
MIN_CHAPTER_SECONDS: int = int(os.environ.get("MIN_CHAPTER_SECONDS", "600"))
CHAPTER_MAX_CHARS: int = int(os.environ.get("CHAPTER_MAX_CHARS", "18000"))
CHAPTER_SPLIT_CHUNK_SIZE: int = int(
    os.environ.get("CHAPTER_SPLIT_CHUNK_SIZE", "4000")
)
CHAPTER_SPLIT_OVERLAP: int = int(
    os.environ.get("CHAPTER_SPLIT_OVERLAP", "200")
)

# ---------------------------------------------------------------------------
# Generation defaults
# ---------------------------------------------------------------------------
DEFAULT_MAX_NEW_TOKENS: int = int(
    os.environ.get("DEFAULT_MAX_NEW_TOKENS", "1000")
)
DEFAULT_TEMPERATURE: float = float(
    os.environ.get("DEFAULT_TEMPERATURE", "0.3")
)
DEFAULT_TOP_K: int = int(os.environ.get("DEFAULT_TOP_K", "50"))
DEFAULT_TOP_P: float = float(os.environ.get("DEFAULT_TOP_P", "0.95"))

# ---------------------------------------------------------------------------
# Flashcards / interview
# ---------------------------------------------------------------------------
DEFAULT_NUM_CARDS_PER_CHAPTER: int = int(
    os.environ.get("DEFAULT_NUM_CARDS_PER_CHAPTER", "5")
)
DEFAULT_NUM_QUESTIONS_PER_CHAPTER: int = int(
    os.environ.get("DEFAULT_NUM_QUESTIONS_PER_CHAPTER", "5")
)
