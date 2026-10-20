import re
from typing import Optional, Pattern
from pydantic import BaseModel, Field


class InputModerationResult(BaseModel):
    """
    Standard evaluation payload produced by the input moderation guardrail.
    """
    allowed: bool = Field(description="Whether the query is safe to pass to the agent")
    risk_detected: bool = Field(description="Whether a security threat was flagged")
    category: str = Field(description="Threat classification (CLEAN, PROMPT_INJECTION, MALICIOUS_SQL, OVERSIZED_INPUT)")
    reason: Optional[str] = Field(default=None, description="Explanation for the moderation verdict")
    sanitized_input: str = Field(description="Sanitized input string ready for processing")


# ==============================================================================
# COMPILED SECURITY PATTERNS
# ==============================================================================

PROMPT_INJECTION_PATTERNS = [
    re.compile(r"(ignore|disregard|forget|override)\s+(all\s+)?(previous|prior|above)\s+(instructions|directives|prompts|rules)", re.IGNORECASE),
    re.compile(r"(system\s+prompt|system\s+message|system\s+instructions)", re.IGNORECASE),
    re.compile(r"(you\s+are\s+now|act\s+as)\s+(an\s+unrestricted|DAN|jailbreak|developer\s+mode|evil|god\s+mode)", re.IGNORECASE),
    re.compile(r"(reveal|display|output|show|print)\s+(your|the)\s+(system|initial)\s+(instructions|prompt|secret|api\s*key)", re.IGNORECASE),
    re.compile(r"<\s*script\s*>", re.IGNORECASE),
]

SQL_INJECTION_PATTERNS = [
    re.compile(r"\bunion\s+(all\s+)?select\b", re.IGNORECASE),
    re.compile(r"\bdrop\s+table\b", re.IGNORECASE),
    re.compile(r"\bexec(\s|\+)+(s|x)p\b", re.IGNORECASE),
    re.compile(r"'\s+or\s+'1'='1", re.IGNORECASE),
    re.compile(r";\s*--", re.IGNORECASE),
]

MAX_INPUT_LENGTH = 4000


def moderate_input(user_query: str) -> InputModerationResult:
    """
    Evaluates incoming user prompts against prompt injection, jailbreak attempts,
    SQL payloads, and buffer stuffing attacks.
    """
    if not user_query or not user_query.strip():
        return InputModerationResult(
            allowed=False,
            risk_detected=True,
            category="EMPTY_INPUT",
            reason="Input prompt cannot be empty.",
            sanitized_input=""
        )

    # 1. Payload size check
    if len(user_query) > MAX_INPUT_LENGTH:
        return InputModerationResult(
            allowed=False,
            risk_detected=True,
            category="OVERSIZED_INPUT",
            reason=f"Input exceeds maximum allowed character length of {MAX_INPUT_LENGTH}.",
            sanitized_input=user_query[:MAX_INPUT_LENGTH]
        )

    # 2. Prompt injection & jailbreak check
    for pattern in PROMPT_INJECTION_PATTERNS:
        if pattern.search(user_query):
            return InputModerationResult(
                allowed=False,
                risk_detected=True,
                category="PROMPT_INJECTION",
                reason="Input contains potential prompt injection or system instruction override attempt.",
                sanitized_input=""
            )

    # 3. SQL injection pattern check
    for pattern in SQL_INJECTION_PATTERNS:
        if pattern.search(user_query):
            return InputModerationResult(
                allowed=False,
                risk_detected=True,
                category="MALICIOUS_SQL",
                reason="Input contains potentially malicious SQL tokens.",
                sanitized_input=""
            )

    # 4. Input sanitization (strip non-printable characters)
    sanitized = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", user_query).strip()

    return InputModerationResult(
        allowed=True,
        risk_detected=False,
        category="CLEAN",
        reason=None,
        sanitized_input=sanitized
    )

