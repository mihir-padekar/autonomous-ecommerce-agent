from backend.rag.document_loader import load_documents
from backend.rag.chunking import split_documents
from backend.rag.vector_store import get_vector_store


def ingest_documents():

    print("Loading documents...")

    docs = load_documents()

    print(f"Loaded {len(docs)} documents")

    if len(docs) == 0:
        print("No documents loaded.")
        return

    chunks = split_documents(docs)

    print(f"Generated {len(chunks)} chunks")

    if len(chunks) == 0:
        print("No chunks generated.")
        return

    vector_db = get_vector_store()

    print("Adding chunks to ChromaDB...")

    vector_db.add_documents(chunks)

    print("Documents indexed successfully!")


if __name__ == "__main__":
    ingest_documents()