# Autonomous E-Commerce Agent API Documentation

## Base URL

```text
http://localhost:8000
```

---

# Health Check

## GET /health

### Request

No request body required.

### Response

```json
{
  "status": "healthy",
  "service": "autonomous-ecommerce-agent"
}
```

---

# Executive Dashboard

## GET /dashboard

Returns complete dashboard metrics for charts, KPI cards, complaints, warehouse delays, product delays, and ticket distribution.

### Request

No request body required.

### Response Schema

```json
{
  "order_status": [
    {
      "status": "string",
      "count": 0
    }
  ],
  "complaint_categories": [
    {
      "category": "string",
      "count": 0
    }
  ],
  "complaint_priorities": [
    {
      "priority": "string",
      "count": 0
    }
  ],
  "warehouse_delays": [
    {
      "warehouse": "string",
      "total_orders": 0,
      "delayed_count": 0,
      "avg_delay_days": 0.0
    }
  ],
  "top_delayed_products": [
    {
      "product": "string",
      "delayed_count": 0,
      "avg_delay_days": 0.0
    }
  ],
  "ticket_teams": {
    "team_name": 0
  }
}
```

### Status Codes

| Code | Meaning               |
| ---- | --------------------- |
| 200  | Success               |
| 500  | Internal Server Error |

---

# Warehouse Summary

## GET /warehouse-summary

Returns warehouse-wise delay statistics.

### Request

No request body required.

### Response Schema

```json
[
  {
    "warehouse": "string",
    "total_orders": 0,
    "delayed_count": 0,
    "avg_delay_days": 0.0
  }
]
```

### Status Codes

| Code | Meaning               |
| ---- | --------------------- |
| 200  | Success               |
| 500  | Internal Server Error |

---

# Top Delayed Products

## GET /top-products

Returns products ranked by delay count.

### Request

No request body required.

### Response Schema

```json
[
  {
    "product": "string",
    "delayed_count": 0,
    "avg_delay_days": 0.0
  }
]
```

### Status Codes

| Code | Meaning               |
| ---- | --------------------- |
| 200  | Success               |
| 500  | Internal Server Error |

---

# Delayed Orders

## GET /delayed-orders

Returns all delayed orders.

### Request

No request body required.

### Response Schema

```json
[
  {
    "order_id": 0,
    "customer_id": 0,
    "customer_name": "string",
    "product_name": "string",
    "warehouse": "string",
    "status": "Delayed",
    "delay_days": 0,
    "order_date": "YYYY-MM-DD",
    "expected_delivery_date": "YYYY-MM-DD",
    "actual_delivery_date": null
  }
]
```

### Status Codes

| Code | Meaning               |
| ---- | --------------------- |
| 200  | Success               |
| 500  | Internal Server Error |

---

