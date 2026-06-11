from fastapi import FastAPI
from backend.workflows.ecommerce_graph import graph

app = FastAPI()

@app.get("/")
def home():
    return {"status": "running"}



@app.post("/query")

def query(data: dict):

    result = graph.invoke(
        {
            "query": data["query"]
        }
    )

    return {
        "report": result["report"]
    }