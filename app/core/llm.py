from langchain_groq import ChatGroq
from app.core.config import settings


def get_llm():
    """
    Creates and returns the primary Groq LLM instance with an automatic fallback
    to a secondary model if rate limits or network errors occur.
    """
    primary_llm = ChatGroq(
        model=settings.PRIMARY_MODEL,
        api_key=settings.GROQ_API_KEY,
        temperature=settings.TEMPERATURE,
        max_retries=settings.MAX_RETRIES,
    )

    fallback_llm = ChatGroq(
        model=settings.FALLBACK_MODEL,
        api_key=settings.GROQ_API_KEY,
        temperature=settings.TEMPERATURE,
        max_retries=settings.MAX_RETRIES,
    )

    # Attach fallback chain
    resilient_llm = primary_llm.with_fallbacks([fallback_llm])
    return resilient_llm

