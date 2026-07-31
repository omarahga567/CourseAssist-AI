"""
Flashcard generation from chapter summaries.
"""

from __future__ import annotations

import json
import re
from typing import List, Optional

from langchain_core.prompts import PromptTemplate

from .generation import generate_text_quiet


# ---------------------------------------------------------------------------
# JSON extraction (tolerant of truncated model output)
# ---------------------------------------------------------------------------
def extract_json_array(text: str) -> Optional[list]:
    match = re.search(r"\[.*\]", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass  # fall through to recovery below

    # Recovery: pull out only the complete {..} objects
    objects = re.findall(r"\{[^{}]*\}", text, re.DOTALL)
    cards = []
    for obj_str in objects:
        try:
            cards.append(json.loads(obj_str))
        except json.JSONDecodeError:
            continue
    return cards if cards else None


# ---------------------------------------------------------------------------
# Prompt
# ---------------------------------------------------------------------------
flashcard_prompt = PromptTemplate(
    template="""Based on the following course content, create {num_cards} flashcards for a student to study from.
Each flashcard has a "term" (a key concept, short) and a "definition" (clear, 1-2 sentences).

Course content:
{text}

Respond with ONLY a JSON array in this exact format, nothing else:
[
  {{"term": "...", "definition": "..."}},
  {{"term": "...", "definition": "..."}}
]""",
    input_variables=["text", "num_cards"],
)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def generate_flashcards(
    chapter_summaries: list, num_cards_per_chapter: int = 9
) -> List[dict]:
    all_cards: List[dict] = []
    for chapter in chapter_summaries:
        prompt = flashcard_prompt.format(
            text=chapter["summary"], num_cards=num_cards_per_chapter
        )
        raw = generate_text_quiet(prompt, max_new_tokens=5000)
        cards = extract_json_array(raw)
        if cards:
            for c in cards:
                c["chapter"] = chapter["chapter_number"]
            all_cards.extend(cards)
        else:
            print(
                f"⚠️ Flashcard parse failed for Chapter "
                f"{chapter['chapter_number']}"
            )
            print("Raw output was:\n", raw)
    return all_cards


def dedupe_flashcards(cards: List[dict]) -> List[dict]:
    seen = set()
    unique = []
    for c in cards:
        key = c["term"].strip().lower()
        if key not in seen:
            seen.add(key)
            unique.append(c)
    return unique


def display_flashcards(cards: List[dict]) -> None:
    for i, c in enumerate(cards, 1):
        print(f"{i}. 🟦 {c['term']}")
        print(f"   {c['definition']}\n")
