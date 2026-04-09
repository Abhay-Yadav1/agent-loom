"""Tests for the LangChain / LangGraph compatibility layer."""

from __future__ import annotations

import pytest

from agentloom.core import Workflow
from agentloom.integrations.langchain import as_step

# ---------------------------------------------------------------------------
# Fake Runnable — no langchain install needed for tests
# ---------------------------------------------------------------------------

class FakeRunnable:
    """Minimal stand-in for any LangChain Runnable."""
    def __init__(self, fn):
        self.fn = fn

    def invoke(self, input):
        return self.fn(input)


class NotARunnable:
    """Has no .invoke() — should be rejected."""
    pass


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_as_step_returns_callable():
    runnable = FakeRunnable(lambda x: x)
    fn = as_step(runnable, name="my_step")
    assert callable(fn)


def test_as_step_invoke_called_with_input():
    runnable = FakeRunnable(lambda x: {"echoed": x})
    fn = as_step(runnable, name="echo")
    result = fn(prev_result={"data": "hi"})
    assert result == {"echoed": {"data": "hi"}}


def test_as_step_default_name_uses_class_name():
    runnable = FakeRunnable(lambda x: x)
    fn = as_step(runnable)
    assert fn.__name__ == "FakeRunnable"


def test_as_step_custom_name():
    runnable = FakeRunnable(lambda x: x)
    fn = as_step(runnable, name="custom_name")
    assert fn.__name__ == "custom_name"
    assert fn._agentloom_step_name == "custom_name"


def test_as_step_metadata_attached():
    runnable = FakeRunnable(lambda x: x)
    fn = as_step(runnable, name="meta_step", retries=2, on_error="skip")
    assert fn._agentloom_step is True
    assert fn._agentloom_retries == 2
    assert fn._agentloom_on_error == "skip"


def test_as_step_rejects_non_runnable():
    with pytest.raises(TypeError, match="invoke"):
        as_step(NotARunnable())


def test_as_step_works_in_workflow():
    """Full integration — runnable executes inside a real Workflow."""
    runnable = FakeRunnable(lambda x: {"processed": True})
    workflow = Workflow("test-wf")
    workflow.add_step(as_step(runnable, name="process"))
    trace = workflow.run({"input": "data"})
    results = trace.results
    assert len(results) == 1
    assert results[0].step_name == "process"
    assert results[0].output_data == {"processed": True}
