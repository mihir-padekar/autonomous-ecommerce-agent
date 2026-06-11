# test_rag.py

from backend.rag.retriever_service import retrieve_policy

docs = retrieve_policy(
    "delivery SLA escalation rules for delayed orders"
)

print("\nTOTAL DOCS:", len(docs))

for i, doc in enumerate(docs, start=1):

    print(f"\nRESULT {i}")
    print("=" * 50)

    print("\nMETADATA:")
    print(doc.metadata)

    print("\nCONTENT:")
    print(doc.page_content[:500])