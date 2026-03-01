"""Unit tests for agentloom.core."""

from __future__ import annotations

import pytest

from agentloom.core import (
    ExecutionTrace,
    StepResult,
    StepStatus,
    Workflow,
    step,
    tool,
    get_tools,
)


# ---------------------------------------------------------------------------
# @step decorator
# ---------------------------------------------------------------------------

class TestStepDecorator:
    """Tests for the @step decorator."""

    def test_step_preserves_function_name(self) -> None:
        @step(name="my_step")
        def greet(name: str) -> str:
            return f"Hello, {name}"

        assert greet.__name__ == "greet"

    def test_step_attaches_metadata(self) -> None:
        @step(name="my_step")
        def greet(name: str) -> str:
            return f"Hello, {name}"

        assert greet._agentloom_step is True  # type: ignore[attr-defined]
        assert greet._agentloom_step_name == "my_step"  # type: ignore[attr-defined]

    def test_step_defaults_name_to_function_name(self) -> None:
        @step()
        def compute() -> int:
            return 42

        assert compute._agentloom_step_name == "compute"  # type: ignore[attr-defined]

    def test_step_returns_correct_value(self) -> None:
        @step(name="add")
        def add(a: int, b: int) -> int:
            return a + b

        result = add(3, 4)
        assert result == 7

    def test_step_records_result(self) -> None:
        """After calling a step, the module-level results list should contain the entry."""
        from agentloom import core

        saved = core._active_results
        core._active_results = []

        @step(name="recorder_test")
        def noop() -> str:
            return "done"

        noop()

        assert len(core._active_results) == 1
        assert core._active_results[0].step_name == "recorder_test"
        assert core._active_results[0].status == StepStatus.SUCCESS

        core._active_results = saved


# ---------------------------------------------------------------------------
# @tool decorator
# ---------------------------------------------------------------------------

class TestToolDecorator:
    """Tests for the @tool decorator."""

    def test_tool_registers_function(self) -> None:
        @tool(name="calculator")
        def calc(expr: str) -> float:
            return eval(expr)  # noqa: S307

        registry = get_tools()
        assert "calculator" in registry
        assert registry["calculator"]("2+3") == 5

    def test_tool_metadata(self) -> None:
        @tool(name="search")
        def search(query: str) -> list[str]:
            return [query]

        assert search._agentloom_tool is True  # type: ignore[attr-defined]
        assert search._agentloom_tool_name == "search"  # type: ignore[attr-defined]


# ---------------------------------------------------------------------------
# Workflow execution
# ---------------------------------------------------------------------------

class TestWorkflow:
    """Tests for the Workflow class."""

    def test_workflow_executes_steps_in_order(self) -> None:
        order: list[str] = []

        @step(name="first")
        def first() -> str:
            order.append("first")
            return "a"

        @step(name="second")
        def second(prev: str) -> str:
            order.append("second")
            return prev + "b"

        @step(name="third")
        def third(prev: str) -> str:
            order.append("third")
            return prev + "c"

        wf = Workflow(name="ordered")
        wf.add_step(first)
        wf.add_step(second)
        wf.add_step(third)
        trace = wf.run()

        assert order == ["first", "second", "third"]
        assert len(trace.results) == 3

    def test_workflow_passes_previous_result(self) -> None:
        @step(name="start")
        def start() -> int:
            return 10

        @step(name="double")
        def double(x: int) -> int:
            return x * 2

        wf = Workflow()
        wf.add_step(start)
        wf.add_step(double)
        trace = wf.run()

        # The double step should have received 10 and returned 20.
        assert trace.results[-1].output_data == 20

    def test_workflow_conditional_branching(self) -> None:
        calls: list[str] = []

        @step(name="check")
        def check() -> dict:
            calls.append("check")
            return {"__next__": "fallback", "value": "jumped"}

        @step(name="normal")
        def normal(prev: str) -> str:
            calls.append("normal")
            return "normal_result"

        @step(name="fallback")
        def fallback(prev: dict) -> str:
            calls.append("fallback")
            return "fallback_result"

        wf = Workflow()
        wf.add_step(check)
        wf.add_step(normal)
        wf.add_step(fallback)
        trace = wf.run()

        # "check" should jump to "fallback", skipping "normal".
        assert "check" in calls
        assert "fallback" in calls
        assert "normal" not in calls

    def test_workflow_error_handling_skip(self) -> None:
        @step(name="fail_step", on_error="skip")
        def fail_step() -> str:
            raise ValueError("boom")

        @step(name="after")
        def after(prev: str) -> str:
            return "recovered"

        wf = Workflow()
        wf.add_step(fail_step)
        wf.add_step(after)
        trace = wf.run()

        statuses = [r.status for r in trace.results]
        assert StepStatus.SKIPPED in statuses
        assert StepStatus.SUCCESS in statuses

    def test_workflow_error_handling_raise(self) -> None:
        @step(name="explode", on_error="raise")
        def explode() -> None:
            raise RuntimeError("kaboom")

        wf = Workflow()
        wf.add_step(explode)

        with pytest.raises(RuntimeError, match="kaboom"):
            wf.run()


# ---------------------------------------------------------------------------
# ExecutionTrace
# ---------------------------------------------------------------------------

class TestExecutionTrace:
    """Tests for the ExecutionTrace model."""

    def test_trace_captures_timing(self) -> None:
        trace = ExecutionTrace()
        trace.record(StepResult(step_name="a", duration_ms=12.5))
        trace.record(StepResult(step_name="b", duration_ms=7.3))

        assert trace.total_duration_ms == pytest.approx(19.8)
        assert len(trace.results) == 2

    def test_trace_to_dict_and_json(self) -> None:
        trace = ExecutionTrace()
        trace.record(StepResult(step_name="x", output_data=42, duration_ms=1.0))

        d = trace.to_dict()
        assert "steps" in d
        assert d["steps"][0]["step_name"] == "x"

        j = trace.to_json()
        assert '"step_name": "x"' in j

    def test_trace_summary(self) -> None:
        trace = ExecutionTrace()
        trace.record(StepResult(step_name="ok1", status=StepStatus.SUCCESS, duration_ms=5.0))
        trace.record(StepResult(step_name="err1", status=StepStatus.ERROR, duration_ms=2.0, error="e"))

        summary = trace.summary()
        assert "2 step(s)" in summary
        assert "1 succeeded" in summary
        assert "1 failed" in summary


# ---------------------------------------------------------------------------
# StepResult
# ---------------------------------------------------------------------------

class TestStepResult:
    """Tests for the StepResult pydantic model."""

    def test_default_values(self) -> None:
        sr = StepResult(step_name="test")
        assert sr.status == StepStatus.SUCCESS
        assert sr.error is None
        assert sr.duration_ms == 0.0

    def test_serialization_round_trip(self) -> None:
        sr = StepResult(
            step_name="demo",
            status=StepStatus.ERROR,
            input_data={"key": "val"},
            output_data=None,
            duration_ms=99.9,
            error="something broke",
        )
        d = sr.model_dump()
        sr2 = StepResult(**d)
        assert sr2.step_name == "demo"
        assert sr2.error == "something broke"
