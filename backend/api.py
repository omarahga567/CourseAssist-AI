"""
FastAPI routes + ngrok launch.

This is the entry-point module.  Import `app` for ASGI servers, or call
`start_server()` to spin up uvicorn + ngrok in a background thread
(convenient for notebooks / interactive sessions).
"""

from __future__ import annotations

import random
import socket
import threading
import time
from typing import Optional

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pyngrok import conf, ngrok

from . import config
from .flashcards import dedupe_flashcards, generate_flashcards
from .interview import generate_interview_questions
from .model_loader import load_all
from .qa import FRIENDLY_INTROS, FRIENDLY_OUT_OF_COURSE_INTROS, ask_question
from .state import state
from .summarizer import generate_video_summary, render_summary_markdown
from .vectorstore import load_video

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------
app = FastAPI(title="CourseAssist AI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Auth dependency
# ---------------------------------------------------------------------------
def check_auth(req: Request) -> None:
    if req.headers.get("authorization") != f"Bearer {config.API_KEY}":
        raise HTTPException(status_code=401, detail="Unauthorized")


# ---------------------------------------------------------------------------
# Request bodies
# ---------------------------------------------------------------------------
class LoadVideoBody(BaseModel):
    url: str


class AskBody(BaseModel):
    question: str


class FlashcardsBody(BaseModel):
    num_cards_per_chapter: Optional[int] = None


class InterviewBody(BaseModel):
    num_questions_per_chapter: Optional[int] = None


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.post("/load_video")
async def api_load_video(body: LoadVideoBody, req: Request):
    check_auth(req)
    load_video(body.url)
    return {"status": "ok", "chunks_indexed": len(state.documents)}


@app.post("/ask")
async def api_ask(body: AskBody, req: Request):
    check_auth(req)
    try:
        parsed, docs = ask_question(body.question, debug=False, stream=False)
        if not isinstance(parsed, dict):
            raise HTTPException(
                status_code=500, detail="Model returned unparseable answer"
            )
        pool = (
            FRIENDLY_INTROS
            if parsed.get("found_in_course", True)
            else FRIENDLY_OUT_OF_COURSE_INTROS
        )
        parsed["friendly_intro"] = random.choice(pool)
        return parsed
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/summarize")
async def api_summarize(req: Request):
    check_auth(req)

    if not state.transcript:
        raise HTTPException(status_code=400, detail="Load a video first")

    try:
        state.chapter_summaries = generate_video_summary(
            state.transcript, stream=False
        )
        return {
            "chapters": state.chapter_summaries,
            "markdown": render_summary_markdown(state.chapter_summaries),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/flashcards")
async def api_flashcards(body: FlashcardsBody, req: Request):
    check_auth(req)
    if not state.chapter_summaries:
        raise HTTPException(status_code=400, detail="Run /summarize first")
    n = body.num_cards_per_chapter or config.DEFAULT_NUM_CARDS_PER_CHAPTER
    cards = generate_flashcards(
        state.chapter_summaries, num_cards_per_chapter=n
    )
    return {"flashcards": dedupe_flashcards(cards)}


@app.post("/interview_questions")
async def api_interview_questions(body: InterviewBody, req: Request):
    check_auth(req)
    if not state.chapter_summaries:
        raise HTTPException(status_code=400, detail="Run /summarize first")
    n = (
        body.num_questions_per_chapter
        or config.DEFAULT_NUM_QUESTIONS_PER_CHAPTER
    )
    questions = generate_interview_questions(
        state.chapter_summaries, num_questions_per_chapter=n
    )
    return {"interview_questions": questions}


@app.get("/health")
async def health():
    return {"status": "alive"}


# ---------------------------------------------------------------------------
# Server launcher (notebook-friendly)
# ---------------------------------------------------------------------------
def free_port() -> int:
    s = socket.socket()
    s.bind(("", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def start_server(load_models: bool = True) -> str:
    """
    Load models (optional), start uvicorn + ngrok, return the public URL.

    Call this from a notebook / interactive session:
        from backend.api import start_server
        url = start_server()
    """
    if load_models:
        load_all()

    if not config.NGROK_TOKEN:
        raise RuntimeError(
            "NGROK_TOKEN environment variable is not set. "
            "Export it before calling start_server()."
        )
    if not config.API_KEY:
        raise RuntimeError(
            "API_KEY environment variable is not set. "
            "Export it before calling start_server()."
        )

    port = free_port()
    conf.get_default().auth_token = config.NGROK_TOKEN
    public_url = ngrok.connect(port).public_url
    print("Your public URL:", public_url)

    def run():
        uvicorn.run(app, host="0.0.0.0", port=port)

    threading.Thread(target=run, daemon=True).start()
    time.sleep(1)
    return public_url


# Allow `python -m backend.api` to start the server
if __name__ == "__main__":
    start_server()
