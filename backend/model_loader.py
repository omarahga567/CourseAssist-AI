"""
Load the causal-LM and the embedding model once at process start.
"""

from __future__ import annotations

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from langchain_huggingface import HuggingFaceEmbeddings

from . import config
from .state import state


def load_llm() -> None:
    """Download / load Mistral-7B-Instruct (or whatever MODEL_NAME is set to)."""
    print(f"Loading LLM: {config.MODEL_NAME} …")
    state.tokenizer = AutoTokenizer.from_pretrained(config.MODEL_NAME)
    state.model = AutoModelForCausalLM.from_pretrained(
        config.MODEL_NAME,
        torch_dtype=torch.float16,
        device_map="auto",
    )
    print("LLM ready.")


def load_embeddings() -> None:
    """Load the sentence-transformers embedding model."""
    print(f"Loading embeddings: {config.EMBEDDING_MODEL_NAME} …")
    state.embedding_model = HuggingFaceEmbeddings(
        model_name=config.EMBEDDING_MODEL_NAME
    )
    print("Embeddings ready.")


def load_all() -> None:
    """Convenience: load both LLM and embeddings."""
    load_llm()
    load_embeddings()
