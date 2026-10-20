import re
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.database.session import SessionLocal
from app.database.models import Order, Ticket, Complaint


class ComplianceResult(BaseModel):
    is_compliant: bool = Field(description="Whether the proposed action satisfies platform SLA and business policy")
    action_name: str
    reasons: List[str] = Field(default_factory=list, description="Violation or approval justifications")
    risk_level: str = Field(default="LOW", description="LOW | MEDIUM | HIGH | CRITICAL")


# System output redaction patterns
REDACTION_PATTERNS = [
    re.compile(r"gsk_[A-Za-z0-9]{20,}", re.IGNORECASE),
    re.compile(r"postgresql://[^:]+:[^@]+@[^\s/]+/[^\s?]+", re.IGNORECASE),
    re.compile(r"Bearer\s+[A-Za-z0-9\-_\.]+", re.IGNORECASE)
]


def verify_refund_policy(
    order_id: int,
    reason: str,
    refund_amount: Optional[float] = None
) -> ComplianceResult:
    """
    Evaluates whether an order refund proposal complies with platform SLA rules:
    1. Order must exist in the database.
    2. Fulfillment delay must exceed 5 days, OR complaint must cite damaged/defective items.
    3. Maximum automated refund threshold is $1,000.00.
    """
    violations: List[str] = []
    risk_level = "LOW"

    db = SessionLocal()
    try:
        order = db.query(Order).filter(Order.order_id == order_id).first()
        if not order:
            return ComplianceResult(
                is_compliant=False,
                action_name="issue_refund",
                reasons=[f"Order #{order_id} does not exist in the database."],
                risk_level="CRITICAL"
            )

        # Monetary limit threshold
        if refund_amount and refund_amount > 1000.0:
            violations.append(
                f"Requested refund amount (${refund_amount:.2f}) exceeds the operations tier cap of $1,000.00."
            )
            risk_level = "HIGH"

        # Check delay or defect grounds
        reason_lower = reason.lower()
        has_defect_claim = any(
            w in reason_lower for w in ["damaged", "defective", "broken", "wrong item", "missing item"]
        )
        is_severely_delayed = (order.delay_days or 0) >= 5 or order.status == "Delayed"

        if not is_severely_delayed and not has_defect_claim:
            violations.append(
                f"Order #{order_id} is marked as '{order.status}' with delay={order.delay_days or 0} days. "
                "SLA policy requires delay >= 5 days or damaged/defective claim for full refund."
            )
            risk_level = "MEDIUM"

        return ComplianceResult(
            is_compliant=(len(violations) == 0),
            action_name="issue_refund",
            reasons=violations if violations else [f"Refund proposal for Order #{order_id} meets SLA criteria."],
            risk_level=risk_level
        )
    finally:
        db.close()


def verify_escalation_policy(
    ticket_id: int,
    escalation_reason: str,
    target_team: str
) -> ComplianceResult:
    """
    Evaluates whether a support ticket escalation complies with operations protocols:
    1. Ticket must exist.
    2. Ticket must not already be resolved.
    3. Valid justification must be documented.
    """
    violations: List[str] = []
    risk_level = "LOW"

    db = SessionLocal()
    try:
        ticket = db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()
        if not ticket:
            return ComplianceResult(
                is_compliant=False,
                action_name="escalate_ticket",
                reasons=[f"Ticket #{ticket_id} does not exist."],
                risk_level="CRITICAL"
            )

        if ticket.status == "Resolved":
            violations.append(f"Ticket #{ticket_id} is already marked as 'Resolved' and cannot be escalated.")
            risk_level = "HIGH"

        if len(escalation_reason.strip()) < 10:
            violations.append("Escalation reason is too brief. Policy requires substantive rationale.")
            risk_level = "MEDIUM"

        return ComplianceResult(
            is_compliant=(len(violations) == 0),
            action_name="escalate_ticket",
            reasons=violations if violations else [f"Escalation for Ticket #{ticket_id} conforms to policy."],
            risk_level=risk_level
        )
    finally:
        db.close()


def sanitize_agent_output(output_text: str) -> str:
    """
    Scans agent response text and redacts sensitive credentials,
    API keys, or database connection strings before delivery to clients.
    """
    if not output_text:
        return output_text

    sanitized = output_text
    for pattern in REDACTION_PATTERNS:
        sanitized = pattern.sub("[REDACTED_CREDENTIAL]", sanitized)

    return sanitized

