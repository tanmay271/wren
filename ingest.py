import chromadb
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, StorageContext, Settings
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

_EMBED_MODEL_NAME = "BAAI/bge-small-en-v1.5"
_embed_model_initialized = False


def _init_embed_model() -> None:
    global _embed_model_initialized
    if not _embed_model_initialized:
        Settings.embed_model = HuggingFaceEmbedding(model_name=_EMBED_MODEL_NAME)
        Settings.llm = None  # LLM is supplied per query in retrieval.py
        _embed_model_initialized = True


def build_index(pdf_path: str) -> VectorStoreIndex:
    """Load a PDF, chunk it, embed it, and store in an ephemeral ChromaDB index."""
    _init_embed_model()

    documents = SimpleDirectoryReader(input_files=[pdf_path]).load_data()

    chroma_client = chromadb.EphemeralClient()
    collection = chroma_client.get_or_create_collection("hr_policies")
    vector_store = ChromaVectorStore(chroma_collection=collection)
    storage_ctx = StorageContext.from_defaults(vector_store=vector_store)

    index = VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_ctx,
        show_progress=False,
    )
    return index
