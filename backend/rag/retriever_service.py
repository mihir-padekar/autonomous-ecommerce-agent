from backend.rag.retriever import get_retriever


def retrieve_policy(query):

    retriever = get_retriever()

    docs = retriever.invoke(query)

    chunks = []

    for doc in docs:

        chunks.append(
            {
                "content": doc.page_content,
                "source": doc.metadata.get("source", ""),
                "page": doc.metadata.get("page", "")
            }
        )

    return chunks