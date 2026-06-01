from fastapi import FastAPI
from backend.agents.planner_agent import planner_agent

app = FastAPI()

@app.get("/")
def home():
    return {"status": "running"}

@app.post("/plan")
def create_plan(query: str):

    plan = planner_agent(query)

    return {"plan": plan}