"""Integration tests for AgentLoom - full workflow + trace export."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from agentloom import Workflow, step, Tracer
from agentloom.core import ExecutionTrace, StepStatus


class TestFullWorkflowExecution:
    """End-to-end test: build a multi-step workflow, run it, inspect the trace."""

    def test_multi_step_workflow(self) -> None:
        @step(name="ingest")
        def ingest() -> dict:
            return {
                "text": (
                    "The quick brown fox jumps over the lazy dog. "
                    "Pack my box with five dozen liquor jugs. "
                    "How vexingly quick daft zebras jump."
                )
            }

        @step(name="tokenize")
        def tokenize(data: dict) -> dict:
            words = data["text"].split()
            return {"words": words, "count": len(words)}

        @step(name="stats")
        def stats(data: dict) -> dict:
            words = data["words"]
            unique = set(words)
            return {
                "total_words": data["count"],
                "unique_words": len(unique),
                "avg_word_len": round(sum(len(w) for w in words) / len(words), 2),
            }

        wf = Workflow(name="text-pipeline")
        wf.add_step(ingest)
        wf.add_step(tokenize)
        wf.add_step(stats)

        trace = wf.run()

        # All three steps must have executed successfully.
        assert len(trace.results) == 3
        assert all(r.status == StepStatus.SUCCESS for r in trace.results)

        # Verify step names in order.
        names = [r.step_name for r in trace.results]
        assert names == ["ingest", "tokenize", "stats"]

        # Verify the final output contains expected keys.
        final_output = trace.results[-1].output_data
        assert "total_words" in final_output
        assert "unique_words" in final_output
        assert final_output["total_words"] > 0

        # Timing should be captured.
        assert trace.total_duration_ms > 0

    def test_workflow_with_error_recovery(self) -> None:
        call_count = {"n": 0}

        @step(name="flaky", retries=2, on_error="skip")
        def flaky_step() -> str:
            call_count["n"] += 1
            if call_count["n"] < 3:
                raise RuntimeError("Transient failure")
            return "success on third attempt"

        @step(name="finalize")
        def finalize(prev: str) -> str:
            return f"Finalized: {prev}"

        wf = Workflow(name="retry-pipeline")
        wf.add_step(flaky_step)
        wf.add_step(finalize)

        trace = wf.run()

        assert len(trace.results) == 2
        # The flaky step should have retried and succeeded.
        assert trace.results[0].status == StepStatus.RETRIED


class TestTraceExport:
    """Test that traces can be exported to JSON and read back."""

    def test_export_json(self) -> None:
        @step(name="alpha")
        def alpha() -> str:
            return "a"

        @step(name="beta")
        def beta(prev: str) -> str:
            return prev + "b"

        wf = Workflow(name="export-test")
        wf.add_step(alpha)
        wf.add_step(beta)
        trace = wf.run()

        tracer = Tracer.from_execution_trace(trace, name="export-test")

        with tempfile.TemporaryDirectory() as tmpdir:
            out_path = Path(tmpdir) / "trace.json"
            tracer.export_json(out_path)

            assert out_path.exists()

            with out_path.open("r", encoding="utf-8") as fh:
                data = json.load(fh)

            # Top-level span should be the workflow name.
            assert data["name"] == "export-test"
            # Children correspond to steps.
            assert len(data["children"]) == 2
            assert data["children"][0]["name"] == "alpha"
            assert data["children"][1]["name"] == "beta"
            # Duration should be present.
            assert data["children"][0]["duration_ms"] >= 0

    def test_trace_round_trip_dict(self) -> None:
        trace = ExecutionTrace()
        from agentloom.core import StepResult

        trace.record(StepResult(step_name="s1", output_data="hello", duration_ms=1.5))
        trace.record(StepResult(step_name="s2", output_data=42, duration_ms=3.2))

        d = trace.to_dict()
        j = trace.to_json()

        assert d["total_duration_ms"] == 4.7
        parsed = json.loads(j)
        assert parsed["steps"][0]["step_name"] == "s1"
        assert parsed["steps"][1]["output_data"] == 42
