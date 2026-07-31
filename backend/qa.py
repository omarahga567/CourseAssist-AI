"""
Grounded Q&A over the video transcript with structured metadata output.
"""

from __future__ import annotations

import itertools
import json
import random
import re
from typing import Any, Dict, List, Optional, Tuple

from langchain_classic.output_parsers import ResponseSchema, StructuredOutputParser
from langchain_core.prompts import PromptTemplate

from .generation import generate_text_quiet, generate_text_stream
from .state import state


# ---------------------------------------------------------------------------
# Structured output schema
# ---------------------------------------------------------------------------
response_schemas = [
    ResponseSchema(
        name="found_in_course",
        type="boolean",
        description=(
            "true if the transcript context contains this information, "
            "false if answering from general knowledge."
        ),
    ),
    ResponseSchema(
        name="confidence",
        type="string",
        description="One of exactly: High, Medium, Low.",
    ),
    ResponseSchema(
        name="topics",
        type="array",
        description="1-4 short topic tags.",
    ),
    ResponseSchema(
        name="source",
        type="string",
        description=(
            "Timestamp range HH:MM:SS-HH:MM:SS, or 'N/A' "
            "if found_in_course is false."
        ),
    ),
    ResponseSchema(
        name="advisory",
        type="string",
        description=(
            "One-line caution if found_in_course is false, else empty string."
        ),
    ),
    ResponseSchema(
        name="suggested_questions",
        type="array",
        description=(
            "2-3 short natural follow-up questions, "
            "only if answer in the transcript."
        ),
    ),
]
output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
format_instructions = output_parser.get_format_instructions()


# ---------------------------------------------------------------------------
# Prompt
# ---------------------------------------------------------------------------
qa_prompt = PromptTemplate(
    template="""You are an AI tutor for this course.

Rules:
- Answer using ONLY the retrieved transcript context below whenever possible.
- If found in transcript: found_in_course true, cite timestamp in source.
- If NOT found in transcript: start your answer with a short, natural sentence noting this wasn't covered in the course — vary the wording each time, don't reuse the same phrase — then give a brief general-knowledge answer after that. Set found_in_course false, source "N/A", and a one-line advisory telling the student to verify this independently.
- Suggest 2-3 natural follow-up questions only and only if the current question below are in the topic of transcript.

Transcript context:
{context}

Current question: {question}

Respond in EXACTLY this format — plain text answer first, then metadata:

ANSWER:
<Give a thorough, well-explained answer. Cover the concept in depth, with an example where it helps, you should always give an examples. If not covered in the course, open with your own natural note about that before answering briefly.>

METADATA:
{format_instructions}
""",
    input_variables=["context", "question"],
    partial_variables={"format_instructions": format_instructions},
)


# ---------------------------------------------------------------------------
# Friendly intro / outro pools
# ---------------------------------------------------------------------------
INTRO_STARTERS = [
    "Good question", "Nice one", "Great question", "Solid question",
    "Smart question", "Nice pick", "Good thinking",
    "That's a sharp question", "Nice curiosity", "Great pick",
]
INTRO_CONTINUATIONS = [
    "let's dig into this together.", "let's work through it.",
    "let's break it down.", "let's unpack it.", "here's the breakdown.",
    "let's get into it.", "let's walk through it together.",
    "here's what's going on.", "let's take a look.", "let's sort this out.",
]
FRIENDLY_INTROS = [
    f"{s} — {c}"
    for s, c in itertools.product(INTRO_STARTERS, INTRO_CONTINUATIONS)
]

OUT_STARTERS = [
    "Good question", "Curious question", "Fair question",
    "Interesting ask", "Nice question", "Solid question",
    "Great question", "That's a good one", "Nice curiosity",
    "Good instinct to ask",
]
OUT_CONNECTORS = [
    "though it's outside this course.",
    "though this video doesn't cover it.",
    "but this wasn't in the transcript.",
    "though it goes beyond this lesson.",
    "but it's not part of this course.",
    "though the video doesn't get into it.",
    "but this isn't covered here.",
    "though it's beyond what's in this course.",
    "but not something in this video.",
    "though outside today's material.",
]
FRIENDLY_OUT_OF_COURSE_INTROS = [
    f"{s} — {c}"
    for s, c in itertools.product(OUT_STARTERS, OUT_CONNECTORS)
]

OUTRO_STARTERS = [
    "Keep the questions coming", "You're building good habits",
    "That's the right instinct", "Good instinct to check",
    "Nice follow-up energy", "Keep that curiosity up",
    "That's how you learn well", "Good habit to keep up",
    "Stay curious", "That's solid studying",
]
OUTRO_CLOSERS = [
    ".", " — keep going.", ", honestly.", " for sure.",
    ", that's the way.", " — that's the mindset.",
    ", nicely done.", " — good stuff.", ", seriously.",
    " — keep at it.",
]
FRIENDLY_OUTRO = [
    f"{s}{c}" for s, c in itertools.product(OUTRO_STARTERS, OUTRO_CLOSERS)
]

OUT_OF_COURSE_OPENERS = [
    "This isn't something the course covers, but here's a quick answer:",
    "That's outside what this course teaches — for what it's worth:",
    "Not part of this course's material, but briefly:",
    "The course doesn't get into this, though here's a short answer:",
    "This falls outside the course content, but here's a general answer:",
    "Not covered in the transcript, but for general knowledge:",
    "This topic isn't part of the course, but quickly:",
    "Outside the scope of this course, though here's a brief overview:",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def pick_friendly_line(
    found_in_course: bool, show_probability: Optional[float] = None
) -> Optional[str]:
    if show_probability is None:
        show_probability = 0.6 if found_in_course else 0.9
    if random.random() > show_probability:
        return None
    pool = FRIENDLY_INTROS if found_in_course else FRIENDLY_OUT_OF_COURSE_INTROS
    return random.choice(pool)


def source_from_docs(docs) -> str:
    if not docs:
        return "N/A"
    d = docs[0]
    return f"{d.metadata['start_timestamp']}-{d.metadata['end_timestamp']}"


def extract_json_block(text: str) -> Optional[dict]:
    matches = re.findall(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
    if not matches:
        matches = re.findall(r"(\{.*?\})", text, re.DOTALL)
    if not matches:
        return None
    try:
        return json.loads(matches[-1])  # last block = actual answer
    except json.JSONDecodeError:
        return None


def retrieve_context(query: str) -> Tuple[list, str]:
    docs = state.retriever.invoke(query)
    context = "\n\n".join(
        f"[{d.metadata['start_timestamp']}–{d.metadata['end_timestamp']}] "
        f"{d.page_content}"
        for d in docs
    )
    return docs, context


def display_answer(parsed: dict, skip_answer: bool = False) -> None:
    badge = {
        "High": "🟢", "Medium": "🟡", "Low": "🔴"
    }.get(parsed.get("confidence"), "⚪")

    if not skip_answer:
        intro = pick_friendly_line(parsed.get("found_in_course", True))
        if intro:
            print(f"💬 {intro}")

    print(f"{badge} Confidence: {parsed.get('confidence', 'Unknown')}")

    if parsed.get("opener"):
        print(f"\n{parsed['opener']}")

    if not skip_answer:
        print(f"\n{parsed.get('answer', '')}\n")

    if parsed.get("topics"):
        print("Topics:", ", ".join(parsed["topics"]))
    if parsed.get("found_in_course", True):
        print(f"📍 Covered around: {parsed.get('source', 'N/A')}")
    else:
        print("⚠️ Not covered in this course.")
        if parsed.get("advisory"):
            print(f"   {parsed['advisory']}")
    if parsed.get("found_in_course", True) and random.random() < 0.4:
        print(f"\n✨ {random.choice(FRIENDLY_OUTRO)}")
    if parsed.get("suggested_questions"):
        print("\n🤔 You might also ask:")
        for i, q in enumerate(parsed["suggested_questions"], 1):
            print(f"   {i}. {q}")


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------
def ask_question(
    query: str, debug: bool = True, stream: bool = True
) -> Tuple[Dict[str, Any], list]:
    docs, context = retrieve_context(query)
    prompt = qa_prompt.format(context=context, question=query)

    if stream:
        print(f"💬 {random.choice(FRIENDLY_INTROS)}\n")
        full_output = generate_text_stream(prompt, max_new_tokens=1000)
        print()
    else:
        full_output = generate_text_quiet(prompt, max_new_tokens=1000)

    after_answer = (
        full_output.split("ANSWER:", 1)[-1]
        if "ANSWER:" in full_output
        else full_output
    )
    answer_text, _, metadata_part = after_answer.partition("METADATA:")
    answer_text = answer_text.strip()

    parsed = extract_json_block(metadata_part) if metadata_part else None

    if not isinstance(parsed, dict):
        if debug:
            print("⚠️ PARSE FAILED — raw model output was:\n", full_output)
        parsed = {
            "found_in_course": False,
            "confidence": "Low",
            "topics": [],
            "source": "N/A",
            "advisory": "",
            "suggested_questions": [],
        }
        if not answer_text:
            answer_text = (
                "Sorry, I couldn't generate a valid response — "
                "please try rephrasing."
            )

    parsed["answer"] = answer_text
    parsed["opener"] = None
    if not parsed.get("found_in_course", True):
        parsed["confidence"] = "Low"
        parsed["suggested_questions"] = []
        parsed["opener"] = random.choice(OUT_OF_COURSE_OPENERS)

    display_answer(parsed, skip_answer=stream)
    return parsed, docs
