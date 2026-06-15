# POST /query

Executes an AI workflow based on a natural language query.

## Request

```json
{
  "query": "Show delayed orders"
}
```

## Common Response Structure

```json
{
  "workflow_type": "<workflow_name>",
  "analysis": {},
  "report": "..."
}
```

---

# Workflow: delayed_orders

## Request

```json
{
  "query": "Show delayed orders"
}
```

## Response

```json
{
  "workflow_type": "delayed_orders",
  "analysis": {
    "total_orders": 210,
    "average_delay_days": 9.35,
    "max_delay_days": 15,
    "sla_violations": 197,
    "high_risk_orders": 167,
    "risk_level": "HIGH",
    "most_affected_warehouse": "Kolkata",
    "most_delayed_product": "Drone"
  },
  "report": "DELAYED ORDER ANALYSIS REPORT..."
}
```

---

# Workflow: warehouse_analysis

## Request

```json
{
  "query": "Show warehouse delays"
}
```

## Response

```json
{
  "workflow_type": "warehouse_analysis",
  "analysis": {
    "warehouse": "Kolkata",
    "delayed_orders": 42,
    "avg_delay_days": 5.26,
    "total_orders": 157
  },
  "report": "WAREHOUSE DELAY REPORT..."
}
```

---

# Workflow: product_analysis

## Request

```json
{
  "query": "Show top delayed products"
}
```

## Response

```json
{
  "workflow_type": "product_analysis",
  "analysis": {
    "top_product": "Drone",
    "delayed_count": 11,
    "avg_delay_days": 10.4
  },
  "report": "PRODUCT DELAY REPORT..."
}
```

---

# Workflow: ticket_analysis

## Request

```json
{
  "query": "Show open tickets"
}
```

## Response

```json
{
  "workflow_type": "ticket_analysis",
  "analysis": {
    "open_tickets": 64,
    "critical_tickets": 6,
    "high_priority_tickets": 19,
    "busiest_team": "Logistics Team",
    "risk_level": "MEDIUM"
  },
  "report": "TICKET OPERATIONS REPORT..."
}
```

---

# Workflow: dashboard_analysis

## Request

```json
{
  "query": "Show executive dashboard"
}
```

## Response

```json
{
  "workflow_type": "dashboard_analysis",
  "analysis": {
    "delayed_orders": 210,
    "top_warehouse": "Kolkata",
    "warehouse_delays": 42,
    "top_product": "Drone",
    "product_delays": 11,
    "top_complaint": "Defective Product",
    "complaint_count": 115,
    "busiest_team": "Returns Team"
  },
  "report": "EXECUTIVE OPERATIONS DASHBOARD..."
}
```

---

# Error Responses

## Unsupported Query

Status: 400

```json
{
  "detail": "Unsupported query: <query>"
}
```

## Internal Error

Status: 500

```json
{
  "detail": "Workflow execution failed: <error>"
}
```
