# 🚀 [Tips Hindawi](https://www.tipshindawi.com/) Challenge (June–July) 2026
# 🎓 CourseAssist AI

### An AI-powered RAG assistant that turns any YouTube course into an interactive study tool — chat, summaries, flashcards & interview prep.

> 🏆 This repository is my official submission for the [ **Tips Hindawi** ](https://www.tipshindawi.com/) **Challenge (June–July) 2026**.

## 👤 Participant

| Field            | Value                                |
| ---------------- | ------------------------------------ |
| Full Name        | *[Omar Ahmed Gamal]*                   |
| Project Name     | CourseAssist AI                      |
| GitHub Username  | *[omarahga567]*             |
| Challenge Batch  | June–July 2026                       |
| Training Program | Large Language Models (LLMs) Program |
| Organization     | [**Edrak for Ai**](https://edrak4ai.com/en) |

---



# 📖 Project Overview

  Watching a multi-hour course video and trying to retain everything in it is inefficient — learners either take manual notes or repeatedly rewatch sections to find what they need. **CourseAssist AI** solves this by turning any YouTube course video into a searchable, interactive knowledge base.

Simply paste a video URL, and the system transcribes it, splits it into chapters, and builds a vector index of the content. From there, learners can:

- **Ask direct questions** and receive answers grounded in what was actually said in the video — complete with source timestamps and a confidence indicator, not hallucinated guesses
- **Get an automatic chapter-by-chapter summary** of the entire course
- **Generate flashcards** from the material for spaced-repetition review
- **Practice with interview-style questions** derived from the course content, complete with sample answers

Under the hood, CourseAssist AI is built as a **Retrieval-Augmented Generation (RAG)** pipeline: transcript extraction → semantic chunking → vector embeddings → FAISS similarity search → LLM-based generation — exposed through a secured FastAPI backend and consumed by a polished Streamlit frontend.

The project is split into two parts:
- A **backend** (Jupyter/Colab notebook) that handles transcript extraction, chunking, embeddings, the FAISS vector store, LLM inference, and exposes everything through a FastAPI service (tunneled with ngrok for easy demoing).
- A **frontend** (`app.py`) — a polished, dark-themed Streamlit dashboard that talks to that backend over a REST API.

---

# ✨ Features

### 💬 Grounded Q&A Chat
Ask natural-language questions about the video and get answers retrieved directly from the transcript — not generated from general knowledge. The LLM's response is constrained to a strict schema via **LangChain's `StructuredOutputParser`**, so every answer reliably includes:
- A **confidence badge** (High / Medium / Low) so you know how well-supported the answer is
- The **source timestamp range** in the video the answer was pulled from
- **Topic tags** and suggested follow-up questions to keep exploring
- An explicit flag when a question falls outside the course content, with an advisory to verify independently rather than presenting a guess as fact

If the model ever produces malformed output, a fallback response is returned instead of crashing the request — the app degrades gracefully rather than failing silently.

### 📖 Chapter-by-Chapter Summarization
Long courses are automatically split into hour-based chapters. Each chapter is summarized using a **map-reduce pipeline** — smaller sections are summarized individually first, then combined into a coherent chapter-level summary — so summary quality doesn't degrade on long videos. The full course summary is downloadable as Markdown.

### 🗂️ Auto-Generated Flashcards
Generates term/definition flashcards directly from the chapter summaries, with automatic deduplication so you don't get repeated concepts across chapters. Card count per chapter is adjustable.

### 💼 Interview Question Generator
Produces interview-style practice questions with model sample answers, grounded in the actual course content — useful for turning a course into interview prep, not just study material.

### 🔐 Secured, Stateless API
All backend endpoints are protected with **Bearer-token authentication**, so the FastAPI service isn't left open when tunneled publicly through ngrok.

### 🎨 Polished, Tabbed Interface
A custom dark-themed Streamlit dashboard with dedicated tabs for Chat, Flashcards, Interview Questions, and Summary — built for actual daily use, not just a demo script.
---

# 🛠️ Technologies Used

# 🛠️ Technologies Used

**Language**
- Python 3

**RAG Pipeline / NLP**

| Tool | Role |
|---|---|
| [LangChain](https://www.langchain.com/) (`langchain`, `langchain-community`, `langchain-core`, `langchain-huggingface`, `langchain-text-splitters`) | Orchestrates the retrieval + generation pipeline, prompt templates, and semantic text chunking |
| **LangChain `StructuredOutputParser`** | Enforces a strict JSON schema (`ResponseSchema`) on LLM output — confidence, source timestamp, topics, follow-ups — with a safe fallback if parsing fails |
| [FAISS](https://github.com/facebookresearch/faiss) (`faiss-cpu`) | Vector similarity search — indexes transcript chunks for fast retrieval |
| [Sentence-Transformers](https://www.sbert.net/) | Generates embeddings for transcript chunks and user queries |
| [Hugging Face Transformers](https://huggingface.co/docs/transformers) | Loads and runs the LLM used for answering, summarizing, flashcard and interview-question generation |
| [`youtube-transcript-api`](https://pypi.org/project/youtube-transcript-api/) | Extracts timestamped transcripts directly from YouTube |

**Backend / API**

| Tool | Role |
|---|---|
| [FastAPI](https://fastapi.tiangolo.com/) | REST API serving the RAG pipeline to the frontend |
| [Uvicorn](https://www.uvicorn.org/) | ASGI server running the FastAPI app |
| [Pydantic](https://docs.pydantic.dev/) | Request/response validation |
| [Pyngrok](https://pyngrok.readthedocs.io/) | Exposes the Colab-hosted backend via a public URL for the frontend to reach |

**Frontend**

| Tool | Role |
|---|---|
| [Streamlit](https://streamlit.io/) | Interactive web GUI — chat, tabs, flashcards, downloads |
| [Requests](https://requests.readthedocs.io/) | Frontend's HTTP client to call the FastAPI backend |

---

# 🧩 Project Structure

```
CourseAssist-AI/
├── notebook/
│   └── CourseAssist_AI_Backend.ipynb   # RAG pipeline + FastAPI backend (run in Colab/Jupyter)
├── app.py                              # Streamlit frontend (GUI)
├── requirements.txt                    # Frontend dependencies
├── .gitignore
└── README.md
```

> The backend currently lives in a single notebook (transcript extraction → chunking → embeddings → FAISS → LLM → FastAPI). A natural next step is splitting it into standalone modules (`transcript.py`, `embeddings.py`, `summarizer.py`, `flashcards.py`, `interview.py`, `api.py`) — see **Future Improvements** below.

---

# ⚙️ Installation

CourseAssist AI runs as two separate pieces: a **GPU-backed backend** (notebook) and a **local frontend** (Streamlit). You need both running to use the app.

### 1. Clone the repository
```bash
git clone https://github.com/omarahga567/CourseAssist-AI.git
cd CourseAssist-AI
```

### 2. Start the backend (Google Colab recommended)
The backend loads an LLM and embedding model, so a GPU environment is strongly recommended.

1. Open `notebook/CourseAssist_AI_Backend.ipynb` in [Google Colab](https://colab.research.google.com/) (or a local Jupyter environment with CUDA).
2. Set your credentials as environment variables or Colab secrets — **never hardcode tokens in the notebook**:
```python
   import os
   os.environ["HF_TOKEN"] = "<your-huggingface-token>"
   os.environ["NGROK_TOKEN"] = "<your-ngrok-authtoken>"
   os.environ["API_KEY"] = "<choose-a-secret-api-key>"
```
3. Run all cells in order. The final cell starts the FastAPI server and prints a public ngrok URL (e.g. `https://xxxx.ngrok-free.app`) — copy it, you'll need it in the next step.

### 3. Start the frontend (locally)
```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS/Linux

pip install -r requirements.txt
streamlit run app.py
```

### 4. Connect frontend to backend
In the Streamlit sidebar:
- **API / Ngrok URL** → paste the URL printed by the notebook in Step 2
- **API Key** → the same value you set as `API_KEY` in Step 2

You're now ready to load a course video and use the app.

---

# 🚀 Usage

1. Launch the Streamlit app and connect it to your running backend (see Installation).
2. Paste a YouTube course URL in the **Load Your Course Video** box and click **Load Video**.
3. Once indexed, use the tabs:
   - **💬 Chat** — ask questions grounded in the video content.
   - **🗂️ Flashcards** — generate study flashcards per chapter.
   - **💼 Interview Questions** — generate practice questions with sample answers.
   - **📖 Course Summary** — generate and download a full chaptered summary.

---

# 📸 Demo

*Add screenshots or a short GIF/video of the app here (e.g. the Chat tab, Flashcards tab, and a sample generated summary).*

---

# 📈 Results

*Summarize outcomes here — e.g. average response latency, length of course videos successfully processed, accuracy/quality observations from testing the Q&A and summarization features.*

---

# 🔮 Future Improvements

* Refactor the backend notebook into standalone Python modules (`transcript.py`, `vectorstore.py`, `summarizer.py`, `flashcards.py`, `interview.py`, `api.py`) for maintainability and testing.
* Persist the FAISS index and chapter summaries to disk so re-loading the same video doesn't require re-processing.
* Replace the ngrok-tunneled Colab backend with a proper hosted deployment (e.g. Docker + a cloud GPU instance).
* Add automated tests for the retrieval and generation pipeline.
* Support multi-language transcripts and courses without official captions (via Whisper transcription fallback).

---

# 📚 About the Challenge

This project was developed as part of the [**Tips Hindawi**](https://www.tipshindawi.com/) **Challenge (June–July) 2026**.

[Tips Hindawi](https://www.tipshindawi.com/) is the internships department of [**Edrak for Ai**](https://edrak4ai.com/en), and the challenge encourages participants to build real-world projects, apply practical skills, and showcase their work through GitHub.

For more information about the challenge, training programs, and upcoming batches, visit the official [Tips Hindawi](https://www.tipshindawi.com/) website.

---

# 📄 License

This project is shared for educational and portfolio purposes.
