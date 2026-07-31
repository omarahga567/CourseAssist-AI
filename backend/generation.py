"""
Text-generation helpers (streaming and quiet).
"""

from __future__ import annotations

from threading import Thread
from typing import Optional

import torch
from transformers import TextIteratorStreamer

from . import config
from .state import state


# ---------------------------------------------------------------------------
# Quiet (non-streaming) generation
# ---------------------------------------------------------------------------
def generate_text_quiet(
    prompt: str,
    max_new_tokens: Optional[int] = None,
) -> str:
    """
    Run the model and return the generated string without printing anything.
    Used for intermediate steps (map-summaries, flashcards, interview Qs).
    """
    if max_new_tokens is None:
        max_new_tokens = config.DEFAULT_MAX_NEW_TOKENS

    messages = [{"role": "user", "content": prompt}]
    formatted = state.tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )
    inputs = state.tokenizer(formatted, return_tensors="pt").to(
        state.model.device
    )

    with torch.no_grad():
        outputs = state.model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=True,
            top_k=config.DEFAULT_TOP_K,
            top_p=config.DEFAULT_TOP_P,
            temperature=config.DEFAULT_TEMPERATURE,
            pad_token_id=state.tokenizer.eos_token_id,
        )

    generated = outputs[0][inputs["input_ids"].shape[-1] :]
    return state.tokenizer.decode(generated, skip_special_tokens=True).strip()


# ---------------------------------------------------------------------------
# Streaming generation – plain (for chapter summaries)
# ---------------------------------------------------------------------------
def generate_text_stream_plain(
    prompt: str,
    max_new_tokens: Optional[int] = None,
) -> str:
    """
    Stream tokens to stdout and also return the full string.
    No ANSWER:/METADATA: filtering – used for summaries.
    """
    if max_new_tokens is None:
        max_new_tokens = 1200

    messages = [{"role": "user", "content": prompt}]
    formatted = state.tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )
    inputs = state.tokenizer(formatted, return_tensors="pt").to(
        state.model.device
    )

    streamer = TextIteratorStreamer(
        state.tokenizer, skip_prompt=True, skip_special_tokens=True
    )
    generation_kwargs = dict(
        **inputs,
        streamer=streamer,
        max_new_tokens=max_new_tokens,
        do_sample=True,
        top_k=config.DEFAULT_TOP_K,
        top_p=config.DEFAULT_TOP_P,
        temperature=config.DEFAULT_TEMPERATURE,
        pad_token_id=state.tokenizer.eos_token_id,
    )
    thread = Thread(target=state.model.generate, kwargs=generation_kwargs)
    thread.start()

    full_output = ""
    for new_text in streamer:
        print(new_text, end="", flush=True)
        full_output += new_text

    thread.join()
    print()  # final newline
    return full_output.strip()


# ---------------------------------------------------------------------------
# Streaming generation – Q&A (filters ANSWER: / METADATA:)
# ---------------------------------------------------------------------------
def generate_text_stream(
    prompt: str,
    max_new_tokens: Optional[int] = None,
) -> str:
    """
    Stream only the ANSWER: section to the screen; return the full raw output
    (including METADATA:) so the caller can parse it.
    """
    if max_new_tokens is None:
        max_new_tokens = config.DEFAULT_MAX_NEW_TOKENS

    messages = [{"role": "user", "content": prompt}]
    formatted = state.tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )
    inputs = state.tokenizer(formatted, return_tensors="pt").to(
        state.model.device
    )

    streamer = TextIteratorStreamer(
        state.tokenizer, skip_prompt=True, skip_special_tokens=True
    )
    generation_kwargs = dict(
        **inputs,
        streamer=streamer,
        max_new_tokens=max_new_tokens,
        do_sample=True,
        top_k=config.DEFAULT_TOP_K,
        top_p=config.DEFAULT_TOP_P,
        temperature=config.DEFAULT_TEMPERATURE,
    )
    thread = Thread(target=state.model.generate, kwargs=generation_kwargs)
    thread.start()

    full_output = ""
    printed_len = 0
    answer_started = False
    answer_ended = False

    for new_text in streamer:
        full_output += new_text
        if answer_ended:
            continue  # ignore metadata tokens entirely

        if not answer_started:
            idx = full_output.find("ANSWER:")
            if idx == -1:
                continue
            answer_started = True
            printed_len = idx + len("ANSWER:")

        meta_idx = full_output.find("METADATA:")
        visible_end = meta_idx if meta_idx != -1 else len(full_output)
        if meta_idx != -1:
            answer_ended = True

        new_visible = full_output[printed_len:visible_end]
        if new_visible:
            print(new_visible, end="", flush=True)
            printed_len = visible_end

    thread.join()
    print()
    return full_output


# ---------------------------------------------------------------------------
# Legacy non-streaming helper (kept for completeness)
# ---------------------------------------------------------------------------
def generate_text(prompt: str, max_length: int = 1000) -> str:
    """Original notebook helper – streams everything, returns full output."""
    messages = [{"role": "user", "content": prompt}]
    formatted = state.tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )
    inputs = state.tokenizer(formatted, return_tensors="pt").to(
        state.model.device
    )

    streamer = TextIteratorStreamer(
        state.tokenizer, skip_prompt=True, skip_special_tokens=True
    )
    generation_kwargs = dict(
        **inputs,
        streamer=streamer,
        max_length=max_length,
        do_sample=True,
        top_k=config.DEFAULT_TOP_K,
        top_p=config.DEFAULT_TOP_P,
        temperature=config.DEFAULT_TEMPERATURE,
    )
    thread = Thread(target=state.model.generate, kwargs=generation_kwargs)
    thread.start()

    full_output = ""
    for new_text in streamer:
        print(new_text, end="", flush=True)
        full_output += new_text

    thread.join()
    print()
    return full_output
