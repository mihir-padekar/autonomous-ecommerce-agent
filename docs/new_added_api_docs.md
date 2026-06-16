# API Documentation

Base URL (Local Development)

```http
http://127.0.0.1:8000
```

Swagger Documentation

```http
http://127.0.0.1:8000/docs
```

---

# Health Check

## GET /health

Checks whether the backend service is running.

### Request

```http
GET /health
```

### Response

```json
{
  "status": "healthy"
}
```

---

# Query Execution

## POST /query

Executes a LangGraph workflow based on a natural language query.

### Request

```http
POST /query
```

```json
{
  "query": "Show delayed orders"
}
```

### Example Queries

```text
Show executive dashboard
Show delayed orders
Show warehouse delays
Show top delayed products
Show open tickets
```

### Response

```json
{
  "workflow_type": "delayed_orders",
  "analysis": {
    "total_orders": 210,
    "average_delay_days": 9.35,
    "max_delay_days": 15
  },
  "report": "Generated report..."
}
```

---

# Dashboard APIs

## GET /dashboard

Returns the complete executive dashboard summary.

### Request

```http
GET /dashboard
```

### Response

```json
{
  "delayed_orders": 210,
  "top_warehouse": "Kolkata",
  "warehouse_delays": 42,
  "top_product": "Drone",
  "product_delays": 11,
  "top_complaint": "Defective Product",
  "complaint_count": 115,
  "busiest_team": "Returns Team"
}
```

---

## GET /dashboard/kpis

Returns KPI cards for dashboard overview.

### Request

```http
GET /dashboard/kpis
```

### Response

```json
{
  "total_orders": 1000,
  "delayed_orders": 210,
  "complaints": 500,
  "sla_violations": 210,
  "open_tickets": 64
}
```

---

## GET /dashboard/charts/warehouse-delays

Returns delayed order statistics grouped by warehouse.

### Request

```http
GET /dashboard/charts/warehouse-delays
```

### Response

```json
[
  {
    "warehouse": "Kolkata",
    "delayed_count": 42,
    "avg_delay_days": 5.26,
    "total_orders": 157
  }
]
```

---

## GET /dashboard/charts/complaints

Returns complaint counts grouped by category.

### Request

```http
GET /dashboard/charts/complaints
```

### Response

```json
[
  {
    "category": "Defective Product",
    "count": 115
  },
  {
    "category": "Late Delivery",
    "count": 87
  }
]
```

---

## GET /dashboard/charts/tickets

Returns ticket distribution by team.

### Request

```http
GET /dashboard/charts/tickets
```

### Response

```json
{
  "Returns Team": 32,
  "Logistics Team": 28,
  "Support Team": 18
}
```

---

# Agent Monitoring

## GET /agents/status

Returns current health status of all workflow agents.

### Request

```http
GET /agents/status
```

### Response

```json
[
  {
    "name": "Planner Agent",
    "status": "Healthy"
  },
  {
    "name": "Database Agent",
    "status": "Healthy"
  },
  {
    "name": "Analysis Agent",
    "status": "Healthy"
  },
  {
    "name": "Policy Agent",
    "status": "Healthy"
  },
  {
    "name": "Compliance Agent",
    "status": "Healthy"
  },
  {
    "name": "Executive Summary Agent",
    "status": "Healthy"
  },
  {
    "name": "Report Agent",
    "status": "Healthy"
  }
]
```

---

# Workflow Monitoring

## GET /workflows/history

Returns workflow execution history.

### Request

```http
GET /workflows/history
```

### Response

```json
[
  {
    "workflow_id": "d8a52c1f",
    "workflow_name": "dashboard_analysis",
    "user_query": "Show executive dashboard",
    "status": "COMPLETED",
    "started_at": "2025-07-09T12:30:00",
    "completed_at": "2025-07-09T12:30:02",
    "duration_seconds": 2.1
  }
]
```

---

## GET /workflows/{workflow_id}

Returns detailed execution logs for a workflow.

### Request

```http
GET /workflows/d8a52c1f
```

### Response

```json
[
  {
    "agent_name": "Planner Agent",
    "action": "Determine workflow",
    "status": "SUCCESS",
    "execution_time": 0.12,
    "timestamp": "2025-07-09T12:30:00"
  },
  {
    "agent_name": "Database Agent",
    "action": "Fetch database records",
    "status": "SUCCESS",
    "execution_time": 0.28,
    "timestamp": "2025-07-09T12:30:01"
  }
]
```

---

# Reports

## GET /reports/dashboard

Generates the executive operations dashboard report.

### Request

```http
GET /reports/dashboard
```

### Response

```json
{
  "workflow_type": "dashboard_analysis",
  "analysis": {
    "delayed_orders": 210,
    "top_warehouse": "Kolkata",
    "warehouse_delays": 42
  },
  "report": "EXECUTIVE OPERATIONS DASHBOARD..."
}
```

---

# AI Insights

## GET /insights

Returns operational insights generated from dashboard analytics.

### Request

```http
GET /insights
```

### Response

```json
{
  "insights": [
    "210 delayed orders require attention.",
    "Kolkata is currently the most affected warehouse.",
    "Drone has the highest delivery delays.",
    "Defective Product is the leading complaint category."
  ]
}
```

---

# Response Codes

| Code | Description                         |
| ---- | ----------------------------------- |
| 200  | Success                             |
| 400  | Invalid request / unsupported query |
| 404  | Resource not found                  |
| 500  | Internal server error               |

---

# Authentication

Currently authentication is not enabled.

All APIs are publicly accessible in the current development version.
