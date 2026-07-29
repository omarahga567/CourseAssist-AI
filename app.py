import streamlit as st
import requests

st.set_page_config(
    page_title="CourseAssist AI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# Professional Custom CSS
# ============================================================
st.markdown("""
<style>
    /* Hide default Streamlit chrome but keep deploy bar from covering content */
    #MainMenu, footer {visibility: hidden;}
    header {visibility: visible;}

    /* Push content below the black deploy / stop bar */
    .stApp {
        background: linear-gradient(180deg, #0b1220 0%, #111827 55%, #0f172a 100%);
        color: #e2e8f0;
    }

    .block-container {
        padding-top: 3.2rem !important;   /* extra space under deploy bar */
        padding-bottom: 2.5rem;
        max-width: 1080px;
    }

    /* ---- Brand header (no crop) ---- */
    .brand-bar {
        display: flex;
        align-items: center;
        gap: 16px;
        padding: 16px 22px;
        margin-bottom: 1.4rem;
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 16px;
        box-shadow: 0 8px 28px rgba(0,0,0,0.35);
        overflow: visible;
    }
    .logo-box {
        width: 52px;
        height: 52px;
        min-width: 52px;
        border-radius: 14px;
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 26px;
        box-shadow: 0 6px 18px rgba(59,130,246,0.4);
    }
    .brand-title {
        margin: 0;
        font-size: 1.55rem;
        font-weight: 800;
        background: linear-gradient(90deg, #60a5fa, #c4b5fd);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.3px;
        line-height: 1.2;
    }
    .brand-sub {
        margin: 3px 0 0 0;
        font-size: 0.86rem;
        color: #94a3b8;
        line-height: 1.35;
    }

    /* ---- Hero video loader ---- */
    .hero-load {
        background: linear-gradient(145deg, #1e3a5f 0%, #1e293b 65%, #0f172a 100%);
        border: 2px solid #3b82f6;
        border-radius: 18px;
        padding: 1.6rem 1.8rem 1.3rem;
        margin-bottom: 1.3rem;
        box-shadow: 0 0 36px rgba(59,130,246,0.15);
        text-align: center;
    }
    .hero-load h2 {
        margin: 0 0 0.35rem 0;
        font-size: 1.35rem;
        font-weight: 700;
        color: #f1f5f9;
    }
    .hero-load p {
        margin: 0;
        color: #94a3b8;
        font-size: 0.88rem;
    }

    /* ---- Course title card (obvious) ---- */
    .course-title-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #3b82f6;
        border-radius: 14px;
        padding: 14px 20px;
        margin: 0.4rem 0 1.2rem 0;
        box-shadow: 0 4px 18px rgba(59,130,246,0.18);
    }
    .course-title-label {
        font-size: 0.78rem;
        color: #94a3b8;
        font-weight: 600;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        margin-bottom: 4px;
    }
    .course-title-text {
        font-size: 1.25rem;
        font-weight: 800;
        color: #f1f5f9;
        line-height: 1.3;
        word-break: break-word;
    }

    /* ---- Sidebar ---- */
    section[data-testid="stSidebar"] {
        background: #0b1220 !important;
        border-right: 1px solid #1e293b;
    }

    /* ---- Buttons ---- */
    .stButton > button {
        border-radius: 11px !important;
        font-weight: 600 !important;
        border: none !important;
        transition: all 0.18s ease !important;
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #3b82f6, #6366f1) !important;
        color: white !important;
        box-shadow: 0 4px 14px rgba(59,130,246,0.4);
    }
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 22px rgba(59,130,246,0.55) !important;
    }

    /* ---- Chat messages ---- */
    div[data-testid="stChatMessage"] {
        border-radius: 14px !important;
        padding: 0.7rem 1rem !important;
        margin-bottom: 0.5rem !important;
        border: 1px solid #334155 !important;
        background: #1e293b !important;
    }

    /* ---- Modern chat input area ---- */
    .chat-input-card {
        background: #1e293b;
        border: 1px solid #3b82f6;
        border-radius: 16px;
        padding: 1rem 1.2rem 0.9rem;
        margin-top: 0.8rem;
        box-shadow: 0 4px 20px rgba(59,130,246,0.12);
    }
    div[data-testid="stChatInput"] {
        border-radius: 14px !important;
    }
    div[data-testid="stChatInput"] textarea {
        border-radius: 12px !important;
        background: #0f172a !important;
        color: #f1f5f9 !important;
        border: 1px solid #475569 !important;
        font-size: 0.95rem !important;
    }
    div[data-testid="stChatInput"] textarea:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 3px rgba(59,130,246,0.25) !important;
    }

    /* ---- Inputs ---- */
    .stTextInput > div > div > input {
        border-radius: 11px !important;
        border: 1px solid #475569 !important;
        background: #0f172a !important;
        color: #f1f5f9 !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 3px rgba(59,130,246,0.2) !important;
    }

    /* ---- Status pills ---- */
    .pill-ready {
        background: linear-gradient(90deg, #065f46, #047857);
        color: #a7f3d0;
        padding: 7px 16px;
        border-radius: 999px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
    }
    .pill-wait {
        background: linear-gradient(90deg, #1e3a5f, #1e40af);
        color: #93c5fd;
        padding: 7px 16px;
        border-radius: 999px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
    }

    /* ---- Tabs ---- */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: #0f172a;
        padding: 7px;
        border-radius: 14px;
        border: 1px solid #334155;
        margin-bottom: 0.6rem;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px !important;
        color: #94a3b8 !important;
        font-weight: 600;
        padding: 10px 18px !important;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #3b82f6, #6366f1) !important;
        color: white !important;
    }

    /* ---- Expanders ---- */
    .stExpander {
        border-radius: 12px !important;
        border: 1px solid #334155 !important;
        background: #0f172a !important;
    }

    /* ---- Download ---- */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #059669, #10b981) !important;
        color: white !important;
        border-radius: 11px !important;
    }

    hr { border-color: #334155 !important; }
    h1, h2, h3 { color: #f1f5f9 !important; font-weight: 700 !important; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# Session state
# ============================================================
defaults = {
    "messages": [],
    "video_loaded": False,
    "chapter_summaries": None,
    "flashcards": None,
    "interview_questions": None,
    "pending_question": None,
    "video_title": None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


def call_api(api_url, api_key, endpoint, payload=None, timeout=600):
    try:
        r = requests.post(
            f"{api_url}{endpoint}",
            headers={"Authorization": f"Bearer {api_key}"},
            json=payload or {},
            timeout=timeout,
        )
        if r.status_code == 200:
            return r.json(), None
        return None, f"Server error ({r.status_code}): {r.text}"
    except requests.exceptions.Timeout:
        return None, "Request timed out — this can happen on long videos, try again."
    except Exception as e:
        return None, f"Connection error: {e}"


def confidence_badge(confidence):
    return {"High": "🟢", "Medium": "🟡", "Low": "🔴"}.get(confidence, "⚪")


def render_answer_meta(data):
    if not isinstance(data, dict):
        return
    badge = confidence_badge(data.get("confidence"))
    cols = st.columns(3)
    cols[0].markdown(f"{badge} **{data.get('confidence', 'Unknown')}** confidence")
    if data.get("found_in_course", True):
        cols[1].markdown(f"📍 `{data.get('source', 'N/A')}`")
    else:
        cols[1].markdown("⚠️ Outside course content")
    if data.get("topics"):
        cols[2].markdown("🏷️ " + ", ".join(f"`{t}`" for t in data["topics"]))
    if data.get("advisory"):
        st.caption(f"⚠️ {data['advisory']}")


def ensure_summaries(api_url, api_key):
    if not st.session_state.chapter_summaries:
        with st.spinner("📚 Summarizing the course first (required)..."):
            data, err = call_api(api_url, api_key, "/summarize", timeout=1800)
        if err:
            st.error(err)
            return False
        st.session_state.chapter_summaries = data["chapters"]
    return True


# ============================================================
# SIDEBAR — Server connection only
# ============================================================
with st.sidebar:
    st.markdown("""
    <div style="display:flex; align-items:center; gap:12px; margin-bottom:1.3rem;">
        <div class="logo-box" style="width:44px;height:44px;font-size:22px;">🎓</div>
        <div>
            <div style="font-weight:800;font-size:1.1rem;background:linear-gradient(90deg,#60a5fa,#c4b5fd);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">CourseAssist</div>
            <div style="font-size:0.75rem;color:#94a3b8;">AI Course Assistant</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("#### 🔌 Server Connection")
    st.caption("Connect to your backend (ngrok / API)")
    api_url = st.text_input(
        "API / Ngrok URL",
        placeholder="https://xxxx.ngrok-free.app",
        help="Paste your ngrok or backend base URL"
    ).rstrip("/")
    api_key = st.text_input("API Key", type="password", value="")

    st.divider()

    if st.session_state.video_loaded:
        st.markdown('<div class="pill-ready">✅ Video Ready</div>', unsafe_allow_html=True)
        if st.session_state.video_title:
            st.caption(f"📺 {st.session_state.video_title}")
        st.caption(f"💬 {len(st.session_state.messages)} messages")
    else:
        st.markdown('<div class="pill-wait">⏳ No video loaded</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.caption("CourseAssist AI · v2")

# ============================================================
# MAIN — Brand header
# ============================================================
st.markdown("""
<div class="brand-bar">
    <div class="logo-box">🎓</div>
    <div>
        <div class="brand-title">CourseAssist AI</div>
        <div class="brand-sub">Your intelligent YouTube course assistant — chat, flashcards, interview prep & summaries</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# HERO — Load YouTube URL
# ============================================================
st.markdown("""
<div class="hero-load">
    <h2>🎬 Load Your Course Video</h2>
    <p>Essential first step — paste a YouTube course URL to index it and unlock all features</p>
</div>
""", unsafe_allow_html=True)

url_col, btn_col = st.columns([4.2, 1])
with url_col:
    video_url = st.text_input(
        "YouTube Course URL",
        placeholder="https://www.youtube.com/watch?v=............",
        label_visibility="collapsed",
        help="Full YouTube link of the course video"
    )
with btn_col:
    st.write("")
    load_clicked = st.button("🚀 Load Video", type="primary", use_container_width=True)

if load_clicked:
    if not api_url:
        st.error("Please set the API / Ngrok URL in the sidebar first.")
    elif not video_url:
        st.error("Please paste a YouTube URL.")
    else:
        with st.spinner("📥 Downloading, transcribing & indexing the video..."):
            data, err = call_api(api_url, api_key, "/load_video", {"url": video_url}, timeout=300)
        if err:
            st.error(err)
        else:
            st.session_state.video_loaded = True
            st.session_state.messages = []
            st.session_state.chapter_summaries = None
            st.session_state.flashcards = None
            st.session_state.interview_questions = None
            # Prefer API title; otherwise show the URL so something is always visible
            st.session_state.video_title = (data or {}).get("title") or video_url
            st.success(f"✅ Indexed **{(data or {}).get('chunks_indexed', '?')}** chunks")
            st.rerun()

if not st.session_state.video_loaded:
    st.info("👆 Load a course video above to unlock Chat, Flashcards, Interview Questions and Summary.")
    st.stop()

# ============================================================
# COURSE TITLE — obvious, below load area (not cropped)
# ============================================================
course_title = st.session_state.video_title or "Loaded Course"
st.markdown(f"""
<div class="course-title-card">
    <div class="course-title-label">Current Course</div>
    <div class="course-title-text">📺 {course_title}</div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# FEATURE TABS
# ============================================================
tab_chat, tab_flash, tab_interview, tab_summary = st.tabs([
    "💬 Chat",
    "🗂️ Flashcards",
    "💼 Interview Questions",
    "📖 Course Summary"
])

# -------------------- TAB 1: Chat --------------------
with tab_chat:
    st.markdown("##### 📜 Conversation History")
    st.caption("Full chat history with the AI for the current course.")

    if not st.session_state.messages:
        st.markdown("""
        <div style="background:#1e293b; border:1px solid #334155; border-radius:14px;
                    padding:2.2rem; text-align:center; color:#94a3b8; margin-bottom:1rem;">
            <div style="font-size:2rem; margin-bottom:0.4rem;">💬</div>
            No messages yet. Ask your first question below.
        </div>
        """, unsafe_allow_html=True)
    else:
        history_box = st.container(height=360)
        with history_box:
            for i, msg in enumerate(st.session_state.messages):
                avatar = "🧑‍🎓" if msg["role"] == "user" else "🤖"
                with st.chat_message(msg["role"], avatar=avatar):
                    if msg["role"] == "assistant" and isinstance(msg.get("meta"), dict) and msg["meta"].get("friendly_intro"):
                        st.markdown(f"💬 *{msg['meta']['friendly_intro']}*")
                    st.markdown(msg["content"])
                    if msg["role"] == "assistant" and msg.get("meta"):
                        render_answer_meta(msg["meta"])
                        suggestions = (msg["meta"] or {}).get("suggested_questions") or []
                        if suggestions:
                            st.caption("💡 Suggested follow-ups:")
                            cols = st.columns(min(len(suggestions), 3))
                            for j, q in enumerate(suggestions[:3]):
                                if cols[j].button(q, key=f"sugg_{i}_{j}", use_container_width=True):
                                    st.session_state.pending_question = q
                                    st.rerun()

        if st.button("🗑️ Clear History", type="secondary"):
            st.session_state.messages = []
            st.rerun()

    st.markdown("""
    <div class="chat-input-card">
        <div style="font-weight:600; font-size:0.95rem; color:#e2e8f0; margin-bottom:0.35rem;">
            ✍️ Ask a question about the course
        </div>
        <div style="font-size:0.82rem; color:#94a3b8; margin-bottom:0.2rem;">
            Answers are grounded in the video content
        </div>
    </div>
    """, unsafe_allow_html=True)

    question = st.chat_input("Type your question here and press Enter...")
    if st.session_state.pending_question:
        question = st.session_state.pending_question
        st.session_state.pending_question = None

    if question:
        st.session_state.messages.append({"role": "user", "content": question})
        with st.spinner("🧠 Thinking..."):
            data, err = call_api(api_url, api_key, "/ask", {"question": question}, timeout=180)
        if err:
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"⚠️ {err}",
                "meta": None
            })
        else:
            st.session_state.messages.append({
                "role": "assistant",
                "content": (data or {}).get("answer", ""),
                "meta": data
            })
        st.rerun()

# -------------------- TAB 2: Flashcards --------------------
with tab_flash:
    st.markdown("##### 🗂️ Study Flashcards")
    st.caption("Generate flashcards automatically from the course chapters.")

    col_main, col_ctrl = st.columns([3, 1])
    with col_ctrl:
        num_cards = st.slider("Cards per chapter", 3, 10, 5, key="fc_slider")
        if st.button("✨ Generate Flashcards", use_container_width=True, type="primary"):
            if ensure_summaries(api_url, api_key):
                with st.spinner("Creating flashcards..."):
                    data, err = call_api(
                        api_url, api_key, "/flashcards",
                        {"num_cards_per_chapter": num_cards},
                        timeout=1800
                    )
                if err:
                    st.error(err)
                else:
                    st.session_state.flashcards = data["flashcards"]
                    st.rerun()

    with col_main:
        if st.session_state.flashcards:
            st.success(f"**{len(st.session_state.flashcards)}** flashcards ready")
            for i, card in enumerate(st.session_state.flashcards, 1):
                with st.expander(f"**{i}.** 🟦 {card['term']}"):
                    st.write(card["definition"])
        else:
            st.info("Click **Generate Flashcards** to create study cards from the course.")

# -------------------- TAB 3: Interview Questions --------------------
with tab_interview:
    st.markdown("##### 💼 Interview Practice")
    st.caption("Practice interview-style questions derived from the course material.")

    col_main, col_ctrl = st.columns([3, 1])
    with col_ctrl:
        num_q = st.slider("Questions per chapter", 3, 10, 5, key="iq_slider")
        if st.button("✨ Generate Questions", use_container_width=True, type="primary"):
            if ensure_summaries(api_url, api_key):
                with st.spinner("Generating interview questions..."):
                    data, err = call_api(
                        api_url, api_key, "/interview_questions",
                        {"num_questions_per_chapter": num_q},
                        timeout=1800
                    )
                if err:
                    st.error(err)
                else:
                    st.session_state.interview_questions = data["interview_questions"]
                    st.rerun()

    with col_main:
        if st.session_state.interview_questions:
            st.success(f"**{len(st.session_state.interview_questions)}** questions ready")
            for i, q in enumerate(st.session_state.interview_questions, 1):
                with st.expander(f"**{i}.** ❓ {q['question']}"):
                    st.markdown(f"**Sample answer:**  \n{q['sample_answer']}")
        else:
            st.info("Click **Generate Questions** to create practice interview questions.")

# -------------------- TAB 4: Course Summary --------------------
with tab_summary:
    st.markdown("##### 📖 Full Course Summary")
    st.caption("Chapter-by-chapter summary of the entire course — generated on demand.")

    if st.button("📝 Summarize Entire Course", type="primary"):
        with st.spinner("Summarizing the whole course... this can take a while for long videos."):
            data, err = call_api(api_url, api_key, "/summarize", timeout=1800)
        if err:
            st.error(err)
        else:
            st.session_state.chapter_summaries = data["chapters"]
            st.rerun()

    if st.session_state.chapter_summaries:
        st.success(f"**{len(st.session_state.chapter_summaries)}** chapters summarized")
        for ch in st.session_state.chapter_summaries:
            st.markdown(ch["markdown"])
            st.markdown("---")

        full_md = "\n\n".join(c["markdown"] for c in st.session_state.chapter_summaries)
        st.download_button(
            "⬇️ Download Summary (Markdown)",
            data=full_md,
            file_name="course_summary.md"
        )
    else:
        st.info("Click the button above to generate a detailed chaptered summary.")