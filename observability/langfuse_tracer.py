import os
from typing import Any, Callable, Dict, Optional
from langfuse import Langfuse, observe
from app.core.config import settings
from observability.logging import app_logger


_langfuse_client: Optional[Langfuse] = None


def get_langfuse_client() -> Optional[Langfuse]:
    """
    Returns the Langfuse client if public/secret keys are configured,
    or None if running in local offline development mode.
    """
    global _langfuse_client
    if _langfuse_client is not None:
        return _langfuse_client

    if settings.LANGFUSE_PUBLIC_KEY and settings.LANGFUSE_SECRET_KEY:
        try:
            _langfuse_client = Langfuse(
                public_key=settings.LANGFUSE_PUBLIC_KEY,
                secret_key=settings.LANGFUSE_SECRET_KEY,
                host=settings.LANGFUSE_HOST
            )
            app_logger.info("Langfuse distributed tracing initialized successfully.")
        except Exception as e:
            app_logger.warning(f"Failed to initialize Langfuse client: {e}")
            _langfuse_client = None
    else:
        # Development mode without external trace backend
        _langfuse_client = None

    return _langfuse_client


def trace_action(name: Optional[str] = None) -> Callable:
    """
    Decorator for tracing workflow execution, tool calls, and LLM steps
    using Langfuse OpenTelemetry spans. Gracefully degrades if Langfuse is inactive.
    """
    def decorator(fn: Callable) -> Callable:
        # Langfuse's native observe decorator handles disabled state gracefully
        observed_fn = observe(name=name or fn.__name__)(fn)
        return observed_fn
    return decorator

