from backend.workflows.ecommerce_graph import graph

queries = [
    "Show executive dashboard",
    "Show delayed orders",
    "Show warehouse delays",
    "Show top delayed products",
    "Show open tickets"
]

for q in queries:
    print("\n" + "="*50)
    print(q)

    result = graph.invoke({
        "query": q
    })

    print(result["analysis"])