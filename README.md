# Autonomous E-Commerce Operations Agent

An AI-powered multi-agent system for monitoring and analyzing e-commerce operations using LangGraph, FastAPI, PostgreSQL, and LLM-based workflow orchestration.

The system helps operations teams identify delivery delays, warehouse bottlenecks, customer complaints, SLA violations, and support ticket risks through automated analysis and reporting.

---

# Project Overview

This project simulates an enterprise-grade E-Commerce Operations Intelligence Platform.

The platform combines:

* PostgreSQL for operational data storage
* FastAPI for backend APIs
* LangGraph for workflow orchestration
* Groq LLM for executive summaries and insights
* Retrieval-Augmented Generation (RAG) for policy lookup
* Streamlit/Frontend Dashboard for visualization

The system supports operational workflows such as:

* Executive Dashboard Analysis
* Delayed Order Analysis
* Warehouse Delay Analysis
* Product Delay Analysis
* Support Ticket Analysis
* Compliance Evaluation
* Executive Summary Generation

---

# Architecture

```text
User / Frontend
        |
        v
     FastAPI
        |
        v
   LangGraph Workflow
        |
        +-------------------+
        |                   |
        v                   v
Database Agent       Policy Agent (RAG)
(PostgreSQL)               |
        |                  |
        +--------+---------+
                 |
                 v
          Analysis Agent
                 |
                 v
        Compliance Agent
                 |
                 v
      Executive Summary Agent
                 |
                 v
           Report Agent
                 |
                 v
              Response
```

---

# Folder Structure

```text
autonomous-ecommerce-agent/

├── backend/
│   ├── agents/
│   │   ├── planner_agent.py
│   │   ├── database_agent.py
│   │   ├── analysis_agent.py
│   │   ├── policy_agent.py
│   │   ├── compliance_agent.py
│   │   ├── executive_summary_agent.py
│   │   └── report_agent.py
│   │
│   ├── api/
│   │   ├── main.py
│   │   ├── schemas.py
│   │   └── routes/
│   │       ├── agent_routes.py
│   │       ├── dashboard_routes.py
│   │       └── health_routes.py
│   │
│   ├── config/
│   │   ├── settings.py
│   │   └── query_metadata.py
│   │
│   ├── database/
│   │   ├── db.py
│   │   ├── models.py
│   │   └── queries.py
│   │
│   ├── llm/
│   │   └── llm.py
│   │
│   └── workflows/
│       └── ecommerce_graph.py
│
├── docs/
│   └── API.md
│
├── frontend/
│
├── .env
├── requirements.txt
└── README.md
```

---

# API Documentation

The backend exposes REST APIs for operational analytics and workflow execution.

### Health Check

```http
GET /health
```

### Executive Dashboard

```http
GET /dashboard
```

### Warehouse Summary

```http
GET /warehouse-summary
```

### Top Delayed Products

```http
GET /top-products
```

### Delayed Orders

```http
GET /delayed-orders
```

### AI Workflow Query

```http
POST /query
```

Example Request:

```json
{
  "query": "Show delayed orders"
}
```

Supported Queries:

* Show executive dashboard
* Show delayed orders
* Show warehouse delays
* Show top delayed products
* Show open tickets
* Show critical tickets

For complete API details, refer to:

```text
docs/API.md
```

---

# Setup Instructions

## Clone Repository

```bash
git clone <repository-url>
cd autonomous-ecommerce-agent
```

## Create Virtual Environment

```bash
python -m venv venv
```

Activate Environment:

Windows

```bash
venv\Scripts\activate
```

Linux / Mac

```bash
source venv/bin/activate
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Environment Variables

Create a `.env` file in the project root.

Example:

```env
DATABASE_URL=postgresql://username:password@host/database?sslmode=require

GROQ_API_KEY=your_groq_api_key
```

---

# Running Locally

## Start FastAPI Backend

```bash
uvicorn backend.api.main:app --reload
```

Backend URL:

```text
http://localhost:8000
```

Swagger Documentation:

```text
http://localhost:8000/docs
```

---

## Run Workflow Test

```bash
python test_workflow.py
```

---

# Deployment

## Backend

Recommended deployment platform:

* Render
* Railway
* Fly.io

Environment Variables Required:

```env
DATABASE_URL
GROQ_API_KEY
```

Start Command:

```bash
uvicorn backend.api.main:app --host 0.0.0.0 --port 8000
```

---

## Database

Production database is hosted on Neon PostgreSQL.

Features:

* Managed PostgreSQL
* Automatic Backups
* SSL Connections
* Serverless Scaling

---

# Tech Stack

### Backend

* FastAPI
* LangGraph
* LangChain
* SQLAlchemy
* PostgreSQL
* Neon Database

### AI / LLM

* Groq API
* Llama 3.3 70B
* RAG-based Policy Retrieval

### Frontend

* Streamlit (Current)
* React (Future Ready)

---

# Future Enhancements

* Natural Language Query Expansion
* Multi-warehouse Root Cause Analysis
* Predictive Delay Forecasting
* Real-Time Alerts
* Agent Memory
* Authentication & Role-Based Access Control
* KPI Trend Forecasting
* Advanced Dashboard Visualizations

---


