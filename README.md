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

* 💬 **Contextual Q&A Chat** — Ask natural-language questions about the video; answers are retrieved from the transcript (RAG), with a confidence badge, source timestamp/topic tags, and suggested follow-up questions.
* 📖 **Chapter-by-Chapter Summarization** — Splits long transcripts into hour-based chapters and produces a structured, map-reduce summary of the entire course.
* 🗂️ **Auto-Generated Flashcards** — Term/definition flashcards generated per chapter, with automatic deduplication.
* 💼 **Interview Question Generator** — Produces interview-style practice questions with sample answers, derived from the course material.
* 🔐 **Secured API** — FastAPI backend endpoints protected with Bearer-token authentication.
* 🎨 **Polished Streamlit GUI** — Tabbed dashboard (Chat / Flashcards / Interview Questions / Summary) with a custom dark theme.

---

# 🛠️ Technologies Used

**Language & Core:** Python

**RAG / NLP:**
- [LangChain](https://www.langchain.com/) (`langchain`, `langchain-community`, `langchain-core`, `langchain-huggingface`, `langchain-text-splitters`)
- [FAISS](https://github.com/facebookresearch/faiss) (`faiss-cpu`) — vector similarity search
- [Hugging Face Transformers](https://huggingface.co/docs/transformers) & [Sentence-Transformers](https://www.sbert.net/) — embeddings + LLM inference
- [`youtube-transcript-api`](https://pypi.org/project/youtube-transcript-api/) — transcript extraction

**Backend:**
- [FastAPI](https://fastapi.tiangolo.com/) + [Uvicorn](https://www.uvicorn.org/) — REST API
- [Pyngrok](https://pyngrok.readthedocs.io/) — public tunnel for a Colab-hosted backend
- [Pydantic](https://docs.pydantic.dev/) — request validation

**Frontend:**
- [Streamlit](https://streamlit.io/) — interactive web GUI
- [Requests](https://requests.readthedocs.io/) — API client

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

### 1. Clone the repository
```bash
git clone https://github.com/<your-github-username>/CourseAssist-AI.git
cd CourseAssist-AI
```

### 2. Backend (notebook)
The backend needs a GPU-backed environment (Google Colab recommended, or a local machine with CUDA):
1. Open `notebook/CourseAssist_AI_Backend.ipynb` in Colab or Jupyter.
2. Set your Hugging Face and ngrok tokens as environment variables / Colab secrets — **never hardcode them in the notebook**:
   ```python
   import os
   os.environ["HF_TOKEN"] = "<your-huggingface-token>"
   os.environ["NGROK_TOKEN"] = "<your-ngrok-authtoken>"
   os.environ["API_KEY"] = "<choose-a-secret-api-key>"
   ```
3. Run all cells. The last cell starts the FastAPI server and prints a public ngrok URL — copy it.

### 3. Frontend (Streamlit app)
```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

In the sidebar, paste the ngrok URL from the backend and the API key you set, then load a course video.

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
