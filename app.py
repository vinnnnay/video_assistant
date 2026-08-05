import streamlit as st
from dotenv import load_dotenv
import time

load_dotenv()

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Video Assistant",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&display=swap');

/* ── Global ── */
html, body, [class*="css"] {
    font-family: 'Syne', sans-serif;
}
.stApp {
    background: #0a0a0f;
    color: #e8e4dc;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #0f0f18 !important;
    border-right: 1px solid #1e1e2e;
}
[data-testid="stSidebar"] * {
    font-family: 'Syne', sans-serif !important;
}

/* ── Headings ── */
h1 { font-size: 2.6rem !important; font-weight: 800 !important; letter-spacing: -0.03em; }
h2 { font-size: 1.4rem !important; font-weight: 700 !important; letter-spacing: -0.01em; }
h3 { font-size: 1.1rem !important; font-weight: 600 !important; }

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #6c63ff 0%, #3ecfcf 100%) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    padding: 0.65rem 1.8rem !important;
    transition: opacity 0.2s, transform 0.15s !important;
    letter-spacing: 0.02em;
}
.stButton > button:hover { opacity: 0.88 !important; transform: translateY(-1px) !important; }
.stButton > button:active { transform: translateY(0px) !important; }

/* ── Inputs ── */
.stTextInput > div > div > input,
.stSelectbox > div > div,
.stTextArea > div > div > textarea {
    background: #13131f !important;
    border: 1px solid #2a2a40 !important;
    color: #e8e4dc !important;
    border-radius: 10px !important;
    font-family: 'DM Mono', monospace !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #6c63ff !important;
    box-shadow: 0 0 0 2px rgba(108,99,255,0.25) !important;
}

/* ── Cards ── */
.card {
    background: #13131f;
    border: 1px solid #1e1e30;
    border-radius: 14px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1rem;
    position: relative;
    overflow: hidden;
}
.card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #6c63ff, #3ecfcf);
}
.card-label {
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #6c63ff;
    margin-bottom: 0.55rem;
    font-family: 'DM Mono', monospace;
}
.card-content {
    font-size: 0.97rem;
    line-height: 1.7;
    color: #c8c4bc;
    white-space: pre-wrap;
    font-family: 'DM Mono', monospace;
}

/* ── Title badge ── */
.title-badge {
    display: inline-block;
    background: linear-gradient(135deg, #6c63ff22, #3ecfcf22);
    border: 1px solid #6c63ff55;
    border-radius: 999px;
    padding: 0.35rem 1.1rem;
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #9d97ff;
    margin-bottom: 0.8rem;
}

/* ── Chat bubbles ── */
.chat-user {
    background: linear-gradient(135deg, #6c63ff18, #3ecfcf18);
    border: 1px solid #6c63ff33;
    border-radius: 14px 14px 4px 14px;
    padding: 0.85rem 1.2rem;
    margin-bottom: 0.7rem;
    color: #d4d0f5;
    font-size: 0.95rem;
    font-family: 'DM Mono', monospace;
}
.chat-ai {
    background: #13131f;
    border: 1px solid #1e1e30;
    border-radius: 14px 14px 14px 4px;
    padding: 0.85rem 1.2rem;
    margin-bottom: 0.7rem;
    color: #c8c4bc;
    font-size: 0.95rem;
    line-height: 1.7;
    font-family: 'DM Mono', monospace;
    position: relative;
}
.chat-ai::before {
    content: '';
    position: absolute;
    left: 0; top: 0; bottom: 0;
    width: 2px;
    background: linear-gradient(180deg, #6c63ff, #3ecfcf);
    border-radius: 2px;
}

/* ── Status chips ── */
.status-chip {
    display: inline-flex;
    align-items: center;
    gap: 0.45rem;
    padding: 0.3rem 0.9rem;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    font-family: 'DM Mono', monospace;
}
.chip-done  { background: #0d2a1f; border: 1px solid #1a5c3a; color: #4ade80; }
.chip-error { background: #2a0d0d; border: 1px solid #5c1a1a; color: #f87171; }
.chip-info  { background: #0d1a2a; border: 1px solid #1a3a5c; color: #60a5fa; }

/* ── Divider ── */
.fancy-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, #2a2a40, transparent);
    margin: 1.5rem 0;
}

/* ── Section header ── */
.section-header {
    display: flex;
    align-items: center;
    gap: 0.65rem;
    margin-bottom: 1rem;
}
.section-icon {
    font-size: 1.3rem;
    line-height: 1;
}
.section-title {
    font-size: 1.1rem;
    font-weight: 700;
    color: #e8e4dc;
    letter-spacing: -0.01em;
}

/* ── Expander tweaks ── */
.streamlit-expanderHeader {
    background: #13131f !important;
    border: 1px solid #1e1e30 !important;
    border-radius: 10px !important;
    font-family: 'Syne', sans-serif !important;
    color: #e8e4dc !important;
}
details[open] .streamlit-expanderHeader {
    border-radius: 10px 10px 0 0 !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #0a0a0f; }
::-webkit-scrollbar-thumb { background: #2a2a40; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #6c63ff; }
</style>
""", unsafe_allow_html=True)


# ── Session state init ─────────────────────────────────────────────────────────
for key in ["pipeline_result", "chat_history", "processing", "pipeline_error"]:
    if key not in st.session_state:
        st.session_state[key] = None if key != "chat_history" else []


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="title-badge">⚡ AI Video Assistant</div>', unsafe_allow_html=True)
    st.markdown("## Configure")
    st.markdown('<div class="fancy-divider"></div>', unsafe_allow_html=True)

    source = st.text_input(
        "YouTube URL or File Path",
        placeholder="https://youtube.com/watch?v=... or /path/to/file.mp4",
        help="Paste a YouTube link or enter the absolute path to a local audio/video file.",
    )

    language = st.selectbox(
        "Transcription Language",
        options=["english", "hinglish"],
        index=0,
        help="Choose the spoken language in the recording.",
    )

    st.markdown('<div class="fancy-divider"></div>', unsafe_allow_html=True)

    run_btn = st.button("🚀 Run Pipeline", use_container_width=True)

    if st.session_state.pipeline_result:
        st.markdown('<div class="fancy-divider"></div>', unsafe_allow_html=True)
        st.markdown("### 📊 Session Info")
        res = st.session_state.pipeline_result
        st.markdown(f'<span class="status-chip chip-done">✓ Pipeline complete</span>', unsafe_allow_html=True)
        st.caption(f"Language: **{language}**")
        transcript_len = len(res.get("transcript", ""))
        st.caption(f"Transcript: **{transcript_len:,} chars**")
        chat_count = len(st.session_state.chat_history)
        st.caption(f"Chat turns: **{chat_count}**")

        if st.button("🔄 Reset", use_container_width=True):
            st.session_state.pipeline_result = None
            st.session_state.chat_history = []
            st.session_state.pipeline_error = None
            st.rerun()


# ── Main area ─────────────────────────────────────────────────────────────────
st.markdown("# 🎬 AI Video Assistant")
st.markdown("Transcribe, summarise, and chat with any meeting, lecture, or video — instantly.")
st.markdown('<div class="fancy-divider"></div>', unsafe_allow_html=True)

# ── Run pipeline ──────────────────────────────────────────────────────────────
if run_btn:
    if not source.strip():
        st.warning("⚠️  Please enter a YouTube URL or file path in the sidebar first.")
    else:
        st.session_state.pipeline_result = None
        st.session_state.chat_history = []
        st.session_state.processing = {"status": "Queued"}

        # Check cache first and otherwise run pipeline in background thread
        from utils.cache import get_cached_result
        from utils.audio_processor import get_video_id
        from utils.worker import process_video_async

        video_key = get_video_id(source) or source
        cached = get_cached_result(video_key)
        if cached:
            st.success("Loaded previous result from cache — showing immediately.")
            cached["rag_chain"] = None
            st.session_state.pipeline_result = cached
        else:
            status_box = st.empty()

            def progress_cb(message: str):
                st.session_state.processing = {"status": message}

            def done_cb(result: dict):
                if result.get("error"):
                    st.session_state.processing = {"status": "Error"}
                    st.session_state.pipeline_result = None
                    st.session_state.pipeline_error = result.get("error")
                else:
                    st.session_state.pipeline_result = result
                    st.session_state.processing = {"status": "Complete"}

            process_video_async(source, language, progress_cb, done_cb)

            # Poll progress until complete
            while True:
                proc = st.session_state.get("processing", {})
                status_box.markdown(f"**Status:** {proc.get('status','Queued')}")
                if proc.get("status") in ("Complete", "Loaded from cache", "Error"):
                    break
                time.sleep(0.5)


# ── Error Display ─────────────────────────────────────────────────────────────
if st.session_state.get("pipeline_error"):
    st.error(f"❌ **Pipeline Error**: {st.session_state.pipeline_error}")
    st.markdown('<div class="fancy-divider"></div>', unsafe_allow_html=True)

# ── Results ───────────────────────────────────────────────────────────────────
if st.session_state.pipeline_result:
    res = st.session_state.pipeline_result

    # Title
    st.markdown(f"## 📌 {res['title']}")
    st.markdown('<div class="fancy-divider"></div>', unsafe_allow_html=True)

    # Top 3 cards in columns
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class="card">
            <div class="card-label">✅ Action Items</div>
            <div class="card-content">{res['action_items']}</div>
        </div>""", unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="card">
            <div class="card-label">🔑 Key Decisions</div>
            <div class="card-content">{res['key_decisions']}</div>
        </div>""", unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="card">
            <div class="card-label">❓ Open Questions</div>
            <div class="card-content">{res['open_questions']}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown('<div class="fancy-divider"></div>', unsafe_allow_html=True)

    # Summary
    st.markdown(f"""
    <div class="card">
        <div class="card-label">📋 Summary</div>
        <div class="card-content">{res['summary']}</div>
    </div>""", unsafe_allow_html=True)

    # Transcript (collapsible)
    with st.expander("📄 Full Transcript", expanded=False):
        st.markdown(f"""
        <div style="font-family:'DM Mono',monospace; font-size:0.9rem; line-height:1.8;
                    color:#c8c4bc; white-space:pre-wrap; max-height:420px; overflow-y:auto;">
        {res['transcript']}
        </div>""", unsafe_allow_html=True)

    st.markdown('<div class="fancy-divider"></div>', unsafe_allow_html=True)

    # ── Chat ─────────────────────────────────────────────────────────────────
    st.markdown('<div class="section-header"><span class="section-icon">💬</span><span class="section-title">Chat with your content</span></div>', unsafe_allow_html=True)

    # Render history
    if st.session_state.chat_history:
        for turn in st.session_state.chat_history:
            st.markdown(f'<div class="chat-user">🧑 {turn["question"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="chat-ai">🤖 {turn["answer"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<p style="color:#555568; font-size:0.9rem; font-family:\'DM Mono\',monospace;">Ask anything about the transcript above…</p>', unsafe_allow_html=True)

    # Input row
    q_col, btn_col = st.columns([5, 1])
    with q_col:
        user_q = st.text_input(
            "Your question",
            placeholder="e.g. What were the main takeaways?",
            label_visibility="collapsed",
            key="chat_input",
        )
    with btn_col:
        ask_btn = st.button("Ask →", use_container_width=True)

    if ask_btn and user_q.strip():
        from core.rag_engine import ask_question
        with st.spinner("Thinking…"):
            answer = ask_question(res["rag_chain"], user_q.strip())
        st.session_state.chat_history.append({"question": user_q.strip(), "answer": answer})
        st.rerun()

# ── Empty state ───────────────────────────────────────────────────────────────
else:
    st.markdown("""
    <div style="text-align:center; padding:5rem 2rem;">
        <div style="font-size:4rem; margin-bottom:1rem;">🎬</div>
        <h2 style="color:#555568; font-weight:700; font-size:1.3rem;">No content yet</h2>
        <p style="color:#3a3a50; font-size:0.95rem; font-family:'DM Mono',monospace; max-width:420px; margin:0 auto;">
            Enter a YouTube URL or local file path in the sidebar and hit <strong style="color:#6c63ff">Run Pipeline</strong> to get started.
        </p>
    </div>
    """, unsafe_allow_html=True)