import streamlit as st
import os
import tempfile
from dotenv import load_dotenv

load_dotenv()

BRAND_LOGO_HTML = (
    "<span style='font-weight:900; font-size:20px; color:#06B6D4;'>&#9670;</span>"
    "<span style='font-weight:800; font-size:16px; color:#fff; margin-left:8px;'>Atlas Assist</span>"
)

st.set_page_config(
    page_title="Atlas Assist — AI HR Policy Assistant",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Atlas Assist Brand CSS ────────────────────────────────────────────────────
st.markdown("""
<style>
/* Layout */
.block-container { padding-top: 0.75rem !important; max-width: 1100px; }

/* ── Header ── */
.brand-header {
    display: flex;
    align-items: center;
    gap: 1.25rem;
    padding: 1rem 0.25rem 1rem;
    border-bottom: 3px solid #06B6D4;
    margin-bottom: 1.75rem;
}
.brand-header-title h1 {
    margin: 0;
    font-size: 1.5rem;
    font-weight: 700;
    color: #1A1A1A;
    letter-spacing: -0.02em;
    line-height: 1.25;
}
.brand-header-title p { margin: 0.2rem 0 0; font-size: 0.84rem; color: #777; }

/* ── Sidebar ── */
[data-testid="stSidebar"] { background-color: #0B1120 !important; }
[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] .stMarkdown li,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stCaption span { color: #C8D4DC !important; }
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color: #FFFFFF !important; }
[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.12) !important; }
[data-testid="stSidebar"] .stButton > button {
    background: rgba(255,255,255,0.07) !important;
    color: #FFFFFF !important;
    border: 1px solid rgba(255,255,255,0.18) !important;
    border-radius: 6px !important;
    font-weight: 500 !important;
    font-size: 0.85rem !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(6,182,212,0.2) !important;
    border-color: #06B6D4 !important;
    color: #67E8F9 !important;
}

/* ── Main content buttons (cyan CTA) ── */
.stButton > button {
    background-color: #06B6D4 !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 6px !important;
    font-weight: 600 !important;
    transition: background-color 0.15s ease !important;
}
.stButton > button:hover { background-color: #0891B2 !important; color: #FFFFFF !important; }
.stButton > button:focus { box-shadow: 0 0 0 2px rgba(6,182,212,0.35) !important; outline: none !important; }

/* ── Expander (source passages + suggested questions) ── */
[data-testid="stExpander"] summary {
    color: #06B6D4 !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
}
[data-testid="stExpander"] summary:hover { color: #0891B2 !important; }

/* ── FAQ panel ── */
.faq-panel-header {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    margin-bottom: 0.5rem;
}
.faq-orange-bar {
    width: 4px; height: 1.3rem;
    background: #06B6D4; border-radius: 2px; flex-shrink: 0;
}
.faq-panel-title {
    font-size: 0.85rem; font-weight: 700; color: #1A1A1A;
    text-transform: uppercase; letter-spacing: 0.07em; margin: 0;
}
.faq-panel-sub { font-size: 0.79rem; color: #888; margin: 0 0 0.9rem 1rem; }

/* ── Status badges ── */
.badge-on  { background: #00A651; color: #fff; padding: 0.14rem 0.65rem;
             border-radius: 12px; font-size: 0.69rem; font-weight: 700; letter-spacing: 0.05em; }
.badge-off { background: #4E606E; color: #fff; padding: 0.14rem 0.65rem;
             border-radius: 12px; font-size: 0.69rem; font-weight: 700; letter-spacing: 0.05em; }

/* ── Source cards ── */
.src-meta { font-weight: 600; color: #06B6D4; font-size: 0.77rem; margin-bottom: 0.3rem; }
.src-body { background: #ECFEFF; border: 1px solid #A5F3FC; border-radius: 8px;
            padding: 0.75rem 1rem; font-size: 0.82rem; line-height: 1.65;
            margin-bottom: 0.55rem; color: #333; }

/* ── Divider ── */
.brand-divider { height: 1px; border: none;
              background: linear-gradient(to right, #06B6D4, rgba(6,182,212,0.06));
              margin: 1.25rem 0; }
</style>
""", unsafe_allow_html=True)


# ── Helpers ────────────────────────────────────────────────────────────────────
def get_api_key() -> str:
    try:
        return st.secrets["ANTHROPIC_API_KEY"]
    except Exception:
        return os.getenv("ANTHROPIC_API_KEY", "")


def show_sources(sources: list[dict]) -> None:
    if not sources:
        return
    with st.expander(f"View source passages ({len(sources)})", expanded=False):
        for i, s in enumerate(sources, 1):
            page    = s.get("page", "—")
            score   = s.get("score", 0.0)
            text    = s.get("text", "")
            snippet = text[:650] + ("…" if len(text) > 650 else "")
            st.markdown(
                f'<p class="src-meta">Passage {i} &nbsp;·&nbsp; Page {page}'
                f' &nbsp;·&nbsp; Relevance {score:.2f}</p>'
                f'<div class="src-body">{snippet}</div>',
                unsafe_allow_html=True,
            )


def reset_session() -> None:
    for key in ("index", "doc_name", "messages", "faqs", "faq_visible", "faq_pending"):
        st.session_state.pop(key, None)


def _process_prompt(prompt: str, api_key: str) -> None:
    """Render user bubble, query Claude, render assistant bubble, persist to history."""
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("Searching policy documents…"):
            from retrieval import get_answer
            answer, sources = get_answer(st.session_state.index, prompt, api_key)
        st.markdown(answer)
        show_sources(sources)
    st.session_state.messages.append(
        {"role": "assistant", "content": answer, "sources": sources}
    )


# ── Session state ──────────────────────────────────────────────────────────────
for k, v in [
    ("index",       None),
    ("doc_name",    None),
    ("messages",    []),
    ("faqs",        []),
    ("faq_visible", True),
    ("faq_pending", None),
]:
    st.session_state.setdefault(k, v)

api_key = get_api_key()


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        f'<div style="padding:4px 0 10px;">{BRAND_LOGO_HTML}</div>',
        unsafe_allow_html=True,
    )
    st.markdown("### AI HR Policy Assistant")
    st.markdown("---")

    st.markdown("#### Document Status")
    if st.session_state.doc_name:
        st.markdown('<span class="badge-on">LOADED</span>', unsafe_allow_html=True)
        st.markdown(f"**{st.session_state.doc_name}**")
        st.caption("Indexed and ready for questions.")
    else:
        st.markdown('<span class="badge-off">NO DOCUMENT</span>', unsafe_allow_html=True)
        st.caption("Upload a PDF handbook to begin.")

    st.markdown("---")

    if st.session_state.index is not None:
        if st.button("↩  Reset / Load New Document", use_container_width=True):
            reset_session()
            st.rerun()

    st.markdown("---")
    st.markdown(
        "**How it works**\n\n"
        "1. Upload your HR handbook PDF\n"
        "2. Document is chunked & embedded\n"
        "3. Ask questions in plain English\n"
        "4. Answers grounded in policy text\n   with source citations\n\n"
        "_Stack: LlamaIndex · ChromaDB · Claude_"
    )

    if not api_key:
        st.markdown("---")
        st.error("API key missing.\nAdd `ANTHROPIC_API_KEY` to `.env`.")


# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown(
    f'<div class="brand-header">'
    f'  <div style="font-size:34px;">🧭</div>'
    f'  <div class="brand-header-title">'
    f'    <h1>Atlas Assist</h1>'
    f'    <p>Ask your handbook anything — instant, grounded answers with cited sources, powered by RAG + Claude</p>'
    f'  </div>'
    f'</div>',
    unsafe_allow_html=True,
)


# ── Upload flow ────────────────────────────────────────────────────────────────
if st.session_state.index is None:
    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown("### Load HR Handbook")
        st.markdown(
            "Upload your HR policy handbook as a PDF. "
            "It will be chunked, embedded, and indexed so you can "
            "ask any policy question in natural language."
        )
        uploaded = st.file_uploader("Choose PDF", type=["pdf"], label_visibility="collapsed")

        if uploaded:
            with st.spinner(
                f"Indexing **{uploaded.name}** — first run downloads the embedding model "
                "(~25 MB). Takes 30–60 s…"
            ):
                from ingest import build_index

                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(uploaded.read())
                    tmp_path = tmp.name

                try:
                    idx = build_index(tmp_path)
                    st.session_state.index    = idx
                    st.session_state.doc_name = uploaded.name
                    st.session_state.messages = []
                    st.session_state.faq_visible = True

                    if api_key:
                        try:
                            from retrieval import generate_faqs
                            st.session_state.faqs = generate_faqs(idx, api_key)
                        except Exception:
                            st.session_state.faqs = []

                except Exception as exc:
                    st.error(f"Indexing failed: {exc}")
                finally:
                    os.unlink(tmp_path)

            if st.session_state.index:
                st.success("Document indexed! Ask a question or click a suggested one below.")
                st.rerun()


# ── Chat flow ──────────────────────────────────────────────────────────────────
else:
    # Drain any pending FAQ click from the previous render pass
    active_prompt: str | None = None
    if st.session_state.faq_pending:
        active_prompt = st.session_state.faq_pending
        st.session_state.faq_pending = None
        st.session_state.faq_visible = False

    # Render existing message history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg["role"] == "assistant" and msg.get("sources"):
                show_sources(msg["sources"])

    # FAQ panel
    faqs = st.session_state.faqs
    has_messages = bool(st.session_state.messages)

    if faqs:
        if not has_messages and st.session_state.faq_visible:
            # Full FAQ panel before first message
            st.markdown(
                '<div class="faq-panel-header">'
                '  <div class="faq-orange-bar"></div>'
                '  <p class="faq-panel-title">Frequently Asked Questions</p>'
                '</div>'
                '<p class="faq-panel-sub">Click any question for an instant answer</p>',
                unsafe_allow_html=True,
            )
            cols = st.columns(2)
            for i, q in enumerate(faqs):
                if cols[i % 2].button(q, key=f"faq_{i}", use_container_width=True):
                    st.session_state.faq_pending = q
                    st.rerun()
            st.markdown('<hr class="brand-divider" />', unsafe_allow_html=True)

        elif has_messages:
            # Collapsible panel once conversation is underway
            with st.expander("💡 Show suggested questions", expanded=False):
                cols = st.columns(2)
                for i, q in enumerate(faqs):
                    if cols[i % 2].button(q, key=f"faq_exp_{i}", use_container_width=True):
                        st.session_state.faq_pending = q
                        st.rerun()

    # Chat input
    chat_input = st.chat_input("Ask about leave, benefits, conduct, procedures…")
    if chat_input and not active_prompt:
        active_prompt = chat_input
        st.session_state.faq_visible = False

    # Process the active prompt (FAQ click or typed message)
    if active_prompt:
        if not api_key:
            st.error("No API key — add `ANTHROPIC_API_KEY` to `.env`.")
        else:
            _process_prompt(active_prompt, api_key)
