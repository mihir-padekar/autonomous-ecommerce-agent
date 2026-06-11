from langchain_chroma import Chroma

from backend.rag.embeddings import get_embedding_model


def get_vector_store():

    embeddings = get_embedding_model()

    vector_db = Chroma(
        persist_directory="./chroma_db",
        embedding_function=embeddings
    )

    return vector_db