import json
import os

def build_evaluation_datasets():
    """
    Constructs:
    1. 15 core, authoritative RAG queries verified against:
       - refund_policy.pdf
       - delivery_sla_policy.pdf
       - escalation_rules.pdf
       - product_catalog.pdf
    2. 35 high-signal routing test queries covering all 10 operational tools,
       numerical thresholds (> / <), severity synonyms, and conversational intents.
    """

    # ========================================================
    # 1. 15 AUTHORITATIVE RAG SAMPLES (Fast & Rate-Limit Safe)
    # ========================================================
    rag_samples = [
        {
            "question_id": "RAG_001",
            "user_input": "What is the return window for electronics items?",
            "reference": "Electronic items have a return window of 14 days starting from the confirmed delivery date.",
            "reference_facts": ["category = Electronics", "return_window = 14 Days"],
            "expected_source_document": "refund_policy.pdf",
            "expected_source_page": 4,
            "expected_chunk_keywords": ["RETURN WINDOWS BY PRODUCT CATEGORY", "Electronics 14 Days"],
            "category": "return_window"
        },
        {
            "question_id": "RAG_002",
            "user_input": "What is the return window for mobile devices?",
            "reference": "Mobile devices have an eligible return window of 7 days from the confirmed delivery date.",
            "reference_facts": ["category = Mobile Devices", "return_window = 7 Days"],
            "expected_source_document": "refund_policy.pdf",
            "expected_source_page": 4,
            "expected_chunk_keywords": ["Mobile Devices 7 Days"],
            "category": "return_window"
        },
        {
            "question_id": "RAG_003",
            "user_input": "How many days does a customer have to return fashion and apparel?",
            "reference": "Fashion & Apparel products have a return window of 30 days from delivery.",
            "reference_facts": ["category = Fashion & Apparel", "return_window = 30 Days"],
            "expected_source_document": "refund_policy.pdf",
            "expected_source_page": 4,
            "expected_chunk_keywords": ["Fashion & Apparel 30 Days"],
            "category": "return_window"
        },
        {
            "question_id": "RAG_004",
            "user_input": "What is the return window for home and furniture items?",
            "reference": "Home & Furniture items can be returned within 15 days of the confirmed delivery date.",
            "reference_facts": ["category = Home & Furniture", "return_window = 15 Days"],
            "expected_source_document": "refund_policy.pdf",
            "expected_source_page": 4,
            "expected_chunk_keywords": ["Home & Furniture 15 Days"],
            "category": "return_window"
        },
        {
            "question_id": "RAG_005",
            "user_input": "What is the return policy for home appliances?",
            "reference": "Appliances have a return window of 10 days starting from the delivery date.",
            "reference_facts": ["category = Appliances", "return_window = 10 Days"],
            "expected_source_document": "refund_policy.pdf",
            "expected_source_page": 4,
            "expected_chunk_keywords": ["Appliances 10 Days"],
            "category": "return_window"
        },
        {
            "question_id": "RAG_006",
            "user_input": "Can beauty products be returned after opening?",
            "reference": "Beauty products are strictly non-returnable after opening.",
            "reference_facts": ["category = Beauty Products", "condition = Non-Returnable After Opening"],
            "expected_source_document": "refund_policy.pdf",
            "expected_source_page": 4,
            "expected_chunk_keywords": ["Beauty Products Non-Returnable After Opening"],
            "category": "return_window"
        },
        {
            "question_id": "RAG_007",
            "user_input": "What is the return policy on grocery products?",
            "reference": "Grocery products are non-returnable under the company refund policy.",
            "reference_facts": ["category = Grocery Products", "condition = Non-Returnable"],
            "expected_source_document": "refund_policy.pdf",
            "expected_source_page": 4,
            "expected_chunk_keywords": ["Grocery Products Non-Returnable"],
            "category": "return_window"
        },
        {
            "question_id": "RAG_008",
            "user_input": "What is the reporting window and proof required for damaged goods?",
            "reference": "Customers must report damaged goods within 48 hours of delivery and submit photographic evidence. Support must initiate resolution within 24 hours of verification.",
            "reference_facts": ["report_timeline = within 48 hours", "evidence = photographic evidence"],
            "expected_source_document": "refund_policy.pdf",
            "expected_source_page": 5,
            "expected_chunk_keywords": ["DAMAGED GOODS HANDLING", "Report damage within 48 hours"],
            "category": "claims_handling"
        },
        {
            "question_id": "RAG_009",
            "user_input": "When is an undelivered shipment officially classified as lost?",
            "reference": "A shipment is considered lost when tracking shows no movement for 7 consecutive days, carrier confirms loss, or delivery cannot be verified.",
            "reference_facts": ["lost_condition = no movement for 7 consecutive days"],
            "expected_source_document": "refund_policy.pdf",
            "expected_source_page": 5,
            "expected_chunk_keywords": ["LOST SHIPMENT POLICY", "no movement for 7 consecutive days"],
            "category": "claims_handling"
        },
        {
            "question_id": "RAG_010",
            "user_input": "What refund applies for orders delayed by 1 to 3 days?",
            "reference": "For delivery delays of 1 to 3 days, customer notification is sent and there is no automatic refund.",
            "reference_facts": ["delay_duration = 1-3 Days", "refund_eligibility = No automatic refund"],
            "expected_source_document": "refund_policy.pdf",
            "expected_source_page": 6,
            "expected_chunk_keywords": ["DELIVERY DELAY REFUND RULES", "Delay: 1–3 Days", "No automatic refund"],
            "category": "delay_refund"
        },
        {
            "question_id": "RAG_011",
            "user_input": "What action is taken if a delivery delay exceeds 14 days?",
            "reference": "For delays greater than 14 days, a critical escalation is triggered and a full refund is recommended.",
            "reference_facts": ["delay_duration = More Than 14 Days", "action = Critical escalation", "recommendation = Full refund recommended"],
            "expected_source_document": "refund_policy.pdf",
            "expected_source_page": 7,
            "expected_chunk_keywords": ["Delay: More Than 14 Days", "Full refund recommended"],
            "category": "delay_refund"
        },
        {
            "question_id": "RAG_012",
            "user_input": "What is the refund approval limit for a frontline Customer Support Agent?",
            "reference": "A Customer Support Agent can approve refunds up to $50.",
            "reference_facts": ["role = Customer Support Agent", "max_amount = $50"],
            "expected_source_document": "refund_policy.pdf",
            "expected_source_page": 8,
            "expected_chunk_keywords": ["APPROVAL AUTHORITY MATRIX", "Up to $50 Customer Support Agent"],
            "category": "approval_authority"
        },
        {
            "question_id": "RAG_013",
            "user_input": "What approval level is needed for refunds between $251 and $1000?",
            "reference": "Refunds between $251 and $1,000 require approval from the Operations Manager.",
            "reference_facts": ["amount_range = $251 - $1,000", "approver = Operations Manager"],
            "expected_source_document": "refund_policy.pdf",
            "expected_source_page": 8,
            "expected_chunk_keywords": ["$251 - $1,000 Operations Manager"],
            "category": "approval_authority"
        },
        {
            "question_id": "RAG_014",
            "user_input": "What is the SLA commitment for Standard Delivery?",
            "reference": "Standard Delivery commitment requires order processing within 24 hours and delivery in 3 to 7 business days.",
            "reference_facts": ["tier = Standard Delivery", "processing = Within 24 hours", "delivery = 3–7 business days"],
            "expected_source_document": "delivery_sla_policy.pdf",
            "expected_source_page": 2,
            "expected_chunk_keywords": ["4.1 Standard Delivery", "Processing: Within 24 hours", "Delivery: 3–7 business days"],
            "category": "delivery_sla"
        },
        {
            "question_id": "RAG_015",
            "user_input": "What are the specs and price of the iPhone 16 in the catalog?",
            "reference": "Product ID 101 iPhone 16 is in the Mobile category by Apple, priced at 90000 with 50 units in stock, featuring the A18 chip and advanced camera system.",
            "reference_facts": ["product_id = 101", "brand = Apple", "price = 90000", "chip = A18"],
            "expected_source_document": "product_catalog.pdf",
            "expected_source_page": 0,
            "expected_chunk_keywords": ["101 iPhone 16 Mobile Apple 90000 50 Flagship smartphone with A18 chip"],
            "category": "product_catalog"
        }
    ]

    # ========================================================
    # 2. 35 HIGH-SIGNAL ROUTING SAMPLES (Balanced & Edge-Case Rich)
    # ========================================================
    routing_samples = [
        # Policy RAG (5 samples)
        {"query_id": "ROUTE_001", "query": "What is the return policy for electronics items?", "expected_route": "policy_lookup", "category": "policy"},
        {"query_id": "ROUTE_002", "query": "Explain the delivery SLA compensation policy", "expected_route": "policy_lookup", "category": "policy"},
        {"query_id": "ROUTE_003", "query": "What is the refund timeline for damaged goods?", "expected_route": "policy_lookup", "category": "policy"},
        {"query_id": "ROUTE_004", "query": "How does the customer complaint escalation policy work?", "expected_route": "policy_lookup", "category": "policy"},
        {"query_id": "ROUTE_005", "query": "What are the return rules for beauty products?", "expected_route": "policy_lookup", "category": "policy"},

        # Delayed Orders (4 samples)
        {"query_id": "ROUTE_006", "query": "Show me all delayed orders", "expected_route": "get_delayed_orders", "category": "orders"},
        {"query_id": "ROUTE_007", "query": "Which shipments are currently running behind schedule?", "expected_route": "get_delayed_orders", "category": "orders"},
        {"query_id": "ROUTE_008", "query": "List pending deliveries that missed their delivery date", "expected_route": "get_delayed_orders", "category": "orders"},
        {"query_id": "ROUTE_009", "query": "Fetch delayed orders list", "expected_route": "get_delayed_orders", "category": "orders"},

        # High Delay Orders with > / over thresholds (4 samples)
        {"query_id": "ROUTE_010", "query": "Show orders delayed by more than 5 days", "expected_route": "get_high_delay_orders", "category": "orders"},
        {"query_id": "ROUTE_011", "query": "Show shipments delayed > 5 days", "expected_route": "get_high_delay_orders", "category": "orders"},
        {"query_id": "ROUTE_012", "query": "List orders with high delays over 5 days", "expected_route": "get_high_delay_orders", "category": "orders"},
        {"query_id": "ROUTE_013", "query": "Fetch high delay orders", "expected_route": "get_high_delay_orders", "category": "orders"},

        # Open Complaints (3 samples)
        {"query_id": "ROUTE_014", "query": "Show all open complaints", "expected_route": "get_open_complaints", "category": "complaints"},
        {"query_id": "ROUTE_015", "query": "List unresolved customer complaints", "expected_route": "get_open_complaints", "category": "complaints"},
        {"query_id": "ROUTE_016", "query": "Fetch pending customer disputes", "expected_route": "get_open_complaints", "category": "complaints"},

        # Critical Complaints with synonyms (3 samples)
        {"query_id": "ROUTE_017", "query": "Show critical complaints", "expected_route": "get_critical_complaints", "category": "complaints"},
        {"query_id": "ROUTE_018", "query": "List all urgent customer complaints", "expected_route": "get_critical_complaints", "category": "complaints"},
        {"query_id": "ROUTE_019", "query": "Emergency high priority complaints", "expected_route": "get_critical_complaints", "category": "complaints"},

        # High & Critical Complaints (2 samples)
        {"query_id": "ROUTE_020", "query": "Show high and critical complaints", "expected_route": "get_high_and_critical_complaints", "category": "complaints"},
        {"query_id": "ROUTE_021", "query": "List severe and high severity complaints", "expected_route": "get_high_and_critical_complaints", "category": "complaints"},

        # Open Tickets (3 samples)
        {"query_id": "ROUTE_022", "query": "Show all open tickets", "expected_route": "get_open_tickets", "category": "tickets"},
        {"query_id": "ROUTE_023", "query": "List active support tickets", "expected_route": "get_open_tickets", "category": "tickets"},
        {"query_id": "ROUTE_024", "query": "Current open ticket backlog", "expected_route": "get_open_tickets", "category": "tickets"},

        # Critical Tickets (3 samples)
        {"query_id": "ROUTE_025", "query": "Show critical open tickets", "expected_route": "get_critical_open_tickets", "category": "tickets"},
        {"query_id": "ROUTE_026", "query": "List urgent unresolved support tickets", "expected_route": "get_critical_open_tickets", "category": "tickets"},
        {"query_id": "ROUTE_027", "query": "Emergency P1 tickets pending", "expected_route": "get_critical_open_tickets", "category": "tickets"},

        # Analytics: Warehouse Delays (2 samples)
        {"query_id": "ROUTE_028", "query": "Show warehouse delay summary", "expected_route": "get_warehouse_delay_summary", "category": "analytics"},
        {"query_id": "ROUTE_029", "query": "Which warehouse has highest shipping delays?", "expected_route": "get_warehouse_delay_summary", "category": "analytics"},

        # Analytics: Delayed Products vs Orders (2 samples)
        {"query_id": "ROUTE_030", "query": "What are the top delayed products?", "expected_route": "get_top_delayed_products", "category": "analytics"},
        {"query_id": "ROUTE_031", "query": "Which items face the most shipping delays?", "expected_route": "get_top_delayed_products", "category": "analytics"},

        # Chit-Chat & Help (4 samples)
        {"query_id": "ROUTE_032", "query": "hello", "expected_route": "greeting", "category": "chat"},
        {"query_id": "ROUTE_033", "query": "help", "expected_route": "help", "category": "chat"},
        {"query_id": "ROUTE_034", "query": "thank you", "expected_route": "thanks", "category": "chat"},
        {"query_id": "ROUTE_035", "query": "bye", "expected_route": "goodbye", "category": "chat"}
    ]

    return rag_samples, routing_samples


if __name__ == "__main__":
    rag_data, routing_data = build_evaluation_datasets()

    with open("eval_rag_authoritative.json", "w", encoding="utf-8") as f:
        json.dump(rag_data, f, indent=2)
    print(f"Saved {len(rag_data)} authoritative RAG evaluation queries to eval_rag_authoritative.json")

    with open("eval_routing_dataset.json", "w", encoding="utf-8") as f:
        json.dump(routing_data, f, indent=2)
    print(f"Saved {len(routing_data)} routing queries to eval_routing_dataset.json")