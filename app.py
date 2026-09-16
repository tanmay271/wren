import streamlit as st
import os
import tempfile
from dotenv import load_dotenv

load_dotenv()

ACCENT   = "#D2603A"   # terracotta
INK      = "#2B2420"   # warm near-black
PAPER    = "#FBF5EC"   # cream page background
CARD     = "#FFFFFF"
NEST     = "#241E1A"   # dark warm brown, sidebar
CREAM    = "#F5EAD9"
DIM      = "#8A7A6B"

# A simple two-curve bird-in-flight mark — Wren's logomark.
BIRD_SVG = f"""
<svg width="26" height="16" viewBox="0 0 32 20" fill="none" style="vertical-align:-3px;">
  <path d="M2 15C6 6 11 4 16 10C21 4 26 6 30 15C25 10.5 21 11 16 16C11 11 7 10.5 2 15Z" fill="{ACCENT}"/>
</svg>
"""

BRAND_LOGO_HTML = (
    f"{BIRD_SVG}"
    f"<span style='font-family:\"Baloo 2\",cursive; font-weight:700; font-size:21px; color:{CREAM}; margin-left:9px;'>Wren</span>"
)

st.set_page_config(
    page_title="Wren — Ask Your Handbook Anything",
    page_icon="🐦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Wren Brand CSS ─────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Baloo+2:wght@500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; }}

/* Layout */
.stApp, [data-testid="stAppViewContainer"] {{ background-color: {PAPER} !important; }}
[data-testid="stHeader"] {{ background: transparent !important; }}
.block-container {{ padding-top: 1.25rem !important; max-width: 1100px; }}
h1, h2, h3 {{ font-family: 'Baloo 2', cursive !important; color: {INK} !important; }}
p, li, span, label, div {{ color: {INK}; }}
hr {{ border-color: rgba(43,36,32,0.12) !important; }}

/* ── Header ── */
.brand-header {{
    display: flex;
    align-items: center;
    gap: 1.1rem;
    padding: 1.1rem 1.4rem;
    background: {CARD};
    border: 1px solid rgba(43,36,32,0.08);
    border-radius: 16px;
    margin-bottom: 1.75rem;
    box-shadow: 0 2px 14px rgba(43,36,32,0.05);
}}
.brand-header-icon {{
    font-size: 34px;
    background: #FBEADF;
    border-radius: 12px;
    width: 58px; height: 58px;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
}}
.brand-header-title h1 {{
    margin: 0;
    font-size: 1.6rem;
    font-weight: 700;
    letter-spacing: -0.01em;
    line-height: 1.25;
}}
.brand-header-title p {{ margin: 0.25rem 0 0; font-size: 0.86rem; color: {DIM}; }}

/* ── Sidebar (the nest) ── */
[data-testid="stSidebar"] {{ background-color: {NEST} !important; }}
[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] .stMarkdown li,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stCaption span {{ color: {CREAM} !important; opacity: 0.85; }}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {{ color: {CREAM} !important; }}
[data-testid="stSidebar"] hr {{ border-color: rgba(245,234,217,0.14) !important; }}
[data-testid="stSidebar"] .stButton > button {{
    background: rgba(245,234,217,0.08) !important;
    color: {CREAM} !important;
    border: 1px solid rgba(245,234,217,0.20) !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
}}
[data-testid="stSidebar"] .stButton > button:hover {{
    background: rgba(210,96,58,0.25) !important;
    border-color: {ACCENT} !important;
    color: #F4B9A0 !important;
}}

/* ── Main content buttons (terracotta CTA) ── */
.stButton > button {{
    background-color: {ACCENT} !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    transition: transform 0.12s ease, background-color 0.15s ease !important;
}}
.stButton > button *  {{ color: #FFFFFF !important; }}
.stButton > button:hover {{ background-color: #B84F2E !important; transform: translateY(-1px); }}
.stButton > button:focus {{ box-shadow: 0 0 0 3px rgba(210,96,58,0.25) !important; outline: none !important; }}
[data-testid="stSidebar"] .stButton > button * {{ color: {CREAM} !important; }}

/* ── Chat messages ── */
[data-testid="stChatMessage"] {{
    background: {CARD};
    border: 1px solid rgba(43,36,32,0.07);
    border-radius: 16px;
    padding: 0.4rem 0.6rem;
    margin-bottom: 0.6rem;
    box-shadow: 0 1px 8px rgba(43,36,32,0.04);
}}
[data-testid="stChatInput"] textarea {{
    background: {CARD} !important;
    border-radius: 14px !important;
}}

/* ── Expander (source passages + suggested questions) ── */
[data-testid="stExpander"] {{ background: {CARD}; border-radius: 12px; border-color: rgba(43,36,32,0.08) !important; }}
[data-testid="stExpander"] summary {{
    color: {ACCENT} !important;
    font-weight: 700 !important;
    font-size: 0.88rem !important;
}}
[data-testid="stExpander"] summary:hover {{ color: #B84F2E !important; }}

/* ── FAQ panel ── */
.faq-panel-header {{ display: flex; align-items: center; gap: 0.6rem; margin-bottom: 0.5rem; }}
.faq-orange-bar {{ width: 5px; height: 1.3rem; background: {ACCENT}; border-radius: 3px; flex-shrink: 0; }}
.faq-panel-title {{ font-family: 'Baloo 2', cursive; font-size: 1.0rem; font-weight: 700; color: {INK}; margin: 0; }}
.faq-panel-sub {{ font-size: 0.82rem; color: {DIM}; margin: 0 0 0.9rem 1.1rem; }}
div[data-testid="column"] .stButton > button {{
    background: {CARD} !important;
    color: {INK} !important;
    border: 1px solid rgba(43,36,32,0.12) !important;
    font-weight: 500 !important;
    text-align: left !important;
    border-radius: 12px !important;
}}
div[data-testid="column"] .stButton > button *  {{ color: {INK} !important; }}
div[data-testid="column"] .stButton > button:hover {{
    background: #FBEADF !important;
    border-color: {ACCENT} !important;
    color: {INK} !important;
    transform: none;
}}

/* ── Status badges ── */
.badge-on  {{ background: #4C9A6A; color: #fff; padding: 0.18rem 0.75rem;
             border-radius: 20px; font-size: 0.69rem; font-weight: 700; letter-spacing: 0.05em; }}
.badge-off {{ background: #8A7A6B; color: #fff; padding: 0.18rem 0.75rem;
             border-radius: 20px; font-size: 0.69rem; font-weight: 700; letter-spacing: 0.05em; }}

/* ── Source cards ── */
.src-meta {{ font-weight: 700; color: {ACCENT}; font-size: 0.77rem; margin-bottom: 0.3rem; }}
.src-body {{ background: #FBF5EC; border: 1px solid rgba(210,96,58,0.25); border-radius: 12px;
            padding: 0.85rem 1.1rem; font-size: 0.82rem; line-height: 1.65;
            margin-bottom: 0.55rem; color: {INK}; }}

/* ── Divider ── */
.brand-divider {{ height: 1px; border: none;
              background: linear-gradient(to right, {ACCENT}, rgba(210,96,58,0.05));
              margin: 1.25rem 0; }}

::-webkit-scrollbar {{ width: 10px; height: 10px; }}
::-webkit-scrollbar-track {{ background: {PAPER}; }}
::-webkit-scrollbar-thumb {{ background: rgba(43,36,32,0.15); border-radius: 6px; }}
</style>
""", unsafe_allow_html=True)


# ── Helpers ────────────────────────────────────────────────────────────────────
def get_api_key() -> str:
    try:
        return st.secrets["ANTHROPIC_API_KEY"]
    except Exception:
        return os.getenv("ANTHROPIC_API_KEY", "")


def get_workspace_id() -> str:
    """Optional. Only needed if your API key is org-scoped rather than workspace-scoped."""
    try:
        return st.secrets["ANTHROPIC_WORKSPACE_ID"]
    except Exception:
        return os.getenv("ANTHROPIC_WORKSPACE_ID", "")


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


DEFAULT_PDF_PATH = os.path.join(os.path.dirname(__file__), "data", "sample_handbook.pdf")
DEFAULT_PDF_LABEL = "Sample Employee Handbook (preloaded demo)"


@st.cache_resource(show_spinner=False)
def _load_default_index():
    from ingest import build_index
    return build_index(DEFAULT_PDF_PATH)


def reset_session() -> None:
    for key in ("index", "doc_name", "messages", "faqs", "faq_visible", "faq_pending"):
        st.session_state.pop(key, None)
    st.session_state["skip_auto_load"] = True


def _process_prompt(prompt: str, api_key: str) -> None:
    """Render user bubble, query Claude, render assistant bubble, persist to history."""
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant", avatar="🐦"):
        with st.spinner("Wren is looking that up…"):
            from retrieval import get_answer
            answer, sources = get_answer(st.session_state.index, prompt, api_key, get_workspace_id())
        st.markdown(answer)
        show_sources(sources)
    st.session_state.messages.append(
        {"role": "assistant", "content": answer, "sources": sources}
    )


# ── Session state ──────────────────────────────────────────────────────────────
for k, v in [
    ("index",          None),
    ("doc_name",       None),
    ("messages",       []),
    ("faqs",           []),
    ("faq_visible",    True),
    ("faq_pending",    None),
    ("skip_auto_load", False),
]:
    st.session_state.setdefault(k, v)

api_key = get_api_key()

# Preload a bundled sample handbook so any visitor gets a working demo
# immediately — no upload required. Skipped once the user resets to bring
# their own document.
if (
    st.session_state.index is None
    and not st.session_state.skip_auto_load
    and os.path.exists(DEFAULT_PDF_PATH)
):
    with st.spinner("Loading the sample employee handbook — first load takes 30–60s…"):
        try:
            st.session_state.index = _load_default_index()
            st.session_state.doc_name = DEFAULT_PDF_LABEL
            if api_key:
                try:
                    from retrieval import generate_faqs
                    st.session_state.faqs = generate_faqs(st.session_state.index, api_key, get_workspace_id())
                except Exception:
                    st.session_state.faqs = []
        except Exception:
            pass  # fall through to the manual upload screen if the sample fails to load


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        f'<div style="padding:4px 0 10px;">{BRAND_LOGO_HTML}</div>',
        unsafe_allow_html=True,
    )
    st.markdown("### Your handbook, on call")
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
    f'  <div class="brand-header-icon">🐦</div>'
    f'  <div class="brand-header-title">'
    f'    <h1>Wren</h1>'
    f'    <p>Ask your handbook anything — grounded answers, cited sources, no waiting on HR.</p>'
    f'  </div>'
    f'</div>',
    unsafe_allow_html=True,
)


# ── Upload flow ────────────────────────────────────────────────────────────────
if st.session_state.index is None:
    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown("### Drop in a handbook")
        st.markdown(
            "Upload your HR policy handbook as a PDF. Wren will read it, index it, "
            "and be ready to answer any policy question in plain English."
        )
        uploaded = st.file_uploader("Choose PDF", type=["pdf"], label_visibility="collapsed")

        if uploaded:
            with st.spinner(
                f"Reading **{uploaded.name}** — first run downloads the embedding model "
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
                            st.session_state.faqs = generate_faqs(idx, api_key, get_workspace_id())
                        except Exception:
                            st.session_state.faqs = []

                except Exception as exc:
                    st.error(f"Indexing failed: {exc}")
                finally:
                    os.unlink(tmp_path)

            if st.session_state.index:
                st.success("Handbook loaded! Ask a question or click one below.")
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
        avatar = "🐦" if msg["role"] == "assistant" else None
        with st.chat_message(msg["role"], avatar=avatar):
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
                '  <p class="faq-panel-title">A few things people ask</p>'
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
            with st.expander("💬 Show suggested questions", expanded=False):
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
