from backend.rag.vector_store import get_vector_store

def get_retriever():

    vector_db = get_vector_store()

    return vector_db.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 3}
    )