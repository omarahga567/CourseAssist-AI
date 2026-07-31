"""
CourseAssist AI Backend
=======================

Package layout (module map):

  config.py        – env-based settings (no hardcoded secrets)
  state.py         – shared runtime state (replaces notebook globals)
  model_loader.py  – loads the LLM + tokenizer once
  generation.py    – streaming / quiet text-generation helpers
  transcript.py    – YouTube transcript extraction + timestamp helpers
  vectorstore.py   – embeddings, FAISS index, load_video()
  qa.py            – grounded Q&A + structured output parser
  summarizer.py    – map-reduce chapter summarization
  flashcards.py    – flashcard generation + dedup
  interview.py     – interview-question generation
  api.py           – FastAPI routes + ngrok launch (entry point)

Typical usage (from a Kaggle / Colab notebook or a plain Python process):

    from backend.api import app, start_server
    start_server()          # starts uvicorn + ngrok in a background thread
"""

__all__ = [
    "config",
    "state",
    "model_loader",
    "generation",
    "transcript",
    "vectorstore",
    "qa",
    "summarizer",
    "flashcards",
    "interview",
    "api",
]
