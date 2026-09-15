# Atlas Assist

**Ask your HR handbook anything — get grounded, cited answers instantly.**

Atlas Assist is a Retrieval-Augmented Generation (RAG) chatbot: upload any HR policy handbook as a PDF, and employees can ask plain-English questions about leave, benefits, conduct, or procedures and get answers pulled from — and cited to — the actual document, not a language model's general knowledge.

**[Live demo →](#deployment)** &nbsp;·&nbsp; Built with LlamaIndex, ChromaDB, and Claude.

![Atlas Assist — chat with cited sources](assets/screenshot-chat-answer.png)

## The problem

Company handbooks are long, dense, and rarely read end-to-end. When an employee has a benefits or leave question, they either dig through a 60-page PDF, ping HR and wait, or guess. A keyword search over the PDF doesn't help much either — real questions ("how much notice do I need to give for parental leave?") rarely match the document's exact wording. Atlas Assist fixes this with semantic search plus an LLM that answers *only* from what's actually in the document, and shows its work.

## Use case

An employee uploads their company's HR handbook once. Atlas Assist chunks and embeds it, generates a set of realistic FAQ starter questions grounded in that specific document, and then answers any follow-up question conversationally — always citing the exact passages and page numbers it used, so the answer is auditable, not just plausible-sounding.

## How it works

```
PDF Upload
    │
    ▼
LlamaIndex SimpleDirectoryReader   — parses PDF into text nodes
    │
    ▼
FastEmbed (BAAI/bge-small-en-v1.5) — dense vector embeddings per chunk
    │
    ▼
ChromaDB (in-memory)               — vector store for the session
    │
    ▼
User asks a question
    │
    ▼
Top-3 relevant chunks retrieved by cosine similarity
    │
    ▼
Chunks + question → Claude          — generates a grounded answer
    │
    ▼
Answer + source passages shown in the UI
```

| Layer | Technology |
|---|---|
| LLM | Anthropic Claude, via the Anthropic API |
| RAG orchestration | LlamaIndex |
| Vector store | ChromaDB (ephemeral, per-session) |
| Embeddings | HuggingFace `BAAI/bge-small-en-v1.5` |
| Frontend | Streamlit |
| PDF parsing | `pypdf` via `llama-index-readers-file` |

## Running locally

```bash
python -m venv .venv
# macOS/Linux: source .venv/bin/activate
# Windows:     .venv\Scripts\activate

pip install -r requirements.txt
cp .env.example .env   # then add your ANTHROPIC_API_KEY

streamlit run app.py
```

Open `http://localhost:8502`, upload any PDF handbook (a sample is in `data/test_hr.pdf`), and start asking questions. Get an API key at [console.anthropic.com](https://console.anthropic.com/).

## Deployment

This is a Python/Streamlit app, so it can't be hosted on GitHub Pages (static files only). It deploys for free on **[Streamlit Community Cloud](https://share.streamlit.io)**:

1. Push this repo to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New app** → select this repo, branch `main`, file `app.py`.
3. Under **Settings → Secrets**, add `ANTHROPIC_API_KEY = "sk-ant-..."`.
4. Deploy — you'll get a public `*.streamlit.app` URL.

## Project structure

```
gf-hr-bot/
├── app.py                      # Streamlit UI — upload, chat, source display
├── ingest.py                   # PDF loading, chunking, embedding, ChromaDB indexing
├── retrieval.py                # RAG query engine + Claude answer generation
├── assets/                     # Screenshots used in this README
├── data/                       # Sample HR PDF for testing (uploads aren't committed)
├── requirements.txt
├── .env.example
└── .streamlit/config.toml      # Theme + server config
```

## Disclaimer

This is a portfolio project. It is document-agnostic — it works with any HR policy PDF you upload. No real employer's confidential information, branding, or trademarks are used; the sample document and any company names referenced in demo answers are fictional.

## License

MIT — see [LICENSE](LICENSE).
