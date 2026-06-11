from backend.rag.retriever_service import retrieve_policy

results = retrieve_policy(
    "delivery SLA escalation rules for delayed orders"
)

for r in results:

    print("\nSOURCE:", r["source"])
    print("PAGE:", r["page"])

    print("\nCONTENT:")
    print(r["content"][:300])