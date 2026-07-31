"""
Technical interview-question generation from chapter summaries.
"""

from __future__ import annotations

from typing import List

from langchain_core.prompts import PromptTemplate

from .flashcards import extract_json_array  # reuse the same tolerant parser
from .generation import generate_text_quiet


# ---------------------------------------------------------------------------
# Prompt
# ---------------------------------------------------------------------------
interview_prompt = PromptTemplate(
    template="""Based on the following course content, create {num_questions} technical interview questions a student might be asked about this material.
Each item has a "question" and a short "sample_answer" (1-2 sentences).

Course content:
{text}

Respond with ONLY a JSON array in this exact format, nothing else:
[
  {{"question": "...", "sample_answer": "..."}},
  {{"question": "...", "sample_answer": "..."}}
]""",
    input_variables=["text", "num_questions"],
)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def generate_interview_questions(
    chapter_summaries: list, num_questions_per_chapter: int = 9
) -> List[dict]:
    all_questions: List[dict] = []
    for chapter in chapter_summaries:
        prompt = interview_prompt.format(
            text=chapter["summary"],
            num_questions=num_questions_per_chapter,
        )
        raw = generate_text_quiet(prompt, max_new_tokens=5000)
        questions = extract_json_array(raw)
        if questions:
            for q in questions:
                q["chapter"] = chapter["chapter_number"]
            all_questions.extend(questions)
        else:
            print(
                f"⚠️ Interview question parse failed for Chapter "
                f"{chapter['chapter_number']}"
            )
    return all_questions


def display_interview_questions(questions: List[dict]) -> None:
    for i, q in enumerate(questions, 1):
        print(f"{i}. ❓ {q['question']}")
        print(f"   💡 {q['sample_answer']}\n")
