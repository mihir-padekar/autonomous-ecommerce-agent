import json
import logging
from observability.logging import JSONFormatter, setup_logger
from observability.langfuse_tracer import get_langfuse_client, trace_action


def test_json_formatter_structure():
    """Verify JSONFormatter outputs valid parseable JSON with context attributes."""
    formatter = JSONFormatter()
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="test.py",
        lineno=10,
        msg="Test execution message",
        args=(),
        exc_info=None
    )
    record.thread_id = "th-test-456"
    record.event = "TEST_EVENT"

    output = formatter.format(record)
    parsed = json.loads(output)

    assert parsed["level"] == "INFO"
    assert parsed["message"] == "Test execution message"
    assert parsed["thread_id"] == "th-test-456"
    assert parsed["event"] == "TEST_EVENT"
    assert "timestamp" in parsed


def test_trace_action_decorator_resilience():
    """Verify trace_action decorates functions and executes without exceptions."""
    @trace_action(name="test_unit_trace")
    def sample_op(x: int, y: int) -> int:
        return x * y

    result = sample_op(4, 5)
    assert result == 20


def test_langfuse_client_initialization_safety():
    """Verify get_langfuse_client does not crash in offline dev environments."""
    client = get_langfuse_client()
    # In dev without keys, should gracefully be None or inactive without throwing
    assert client is None or hasattr(client, "trace")

