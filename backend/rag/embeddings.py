from langchain_huggingface import HuggingFaceEmbeddings

_EMBEDDINGS_INSTANCE = None


def get_embedding_model():
    global _EMBEDDINGS_INSTANCE
    if _EMBEDDINGS_INSTANCE is None:
        _EMBEDDINGS_INSTANCE = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

    return _EMBEDDINGS_INSTANCE