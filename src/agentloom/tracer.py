"""Tracing and observability for AgentLoom workflows.

The Tracer builds a tree of Span objects that mirror the step execution,
can be exported to JSON, and rendered to the terminal via Rich.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.tree import Tree

from agentloom.core import ExecutionTrace, StepStatus


# ---------------------------------------------------------------------------
# Span
# ---------------------------------------------------------------------------

@dataclass
class Span:
    """A single unit of traced work (analogous to an OpenTelemetry span)."""

    name: str
    start_time: float = 0.0
    end_time: float = 0.0
    attributes: dict[str, Any] = field(default_factory=dict)
    status: str = "ok"
    children: list["Span"] = field(default_factory=list)

    # -- context manager ---------------------------------------------------

    def __enter__(self) -> "Span":
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.end_time = time.time()
        if exc_type is not None:
            self.status = "error"
            self.attributes["error"] = str(exc_val)

    # -- helpers -----------------------------------------------------------

    @property
    def duration_ms(self) -> float:
        return round((self.end_time - self.start_time) * 1000, 3)

    def add_child(self, name: str) -> "Span":
        child = Span(name=name)
        self.children.append(child)
        return child

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_ms": self.duration_ms,
            "status": self.status,
            "attributes": self.attributes,
            "children": [c.to_dict() for c in self.children],
        }


# ---------------------------------------------------------------------------
# Tracer
# ---------------------------------------------------------------------------

class Tracer:
    """Collects spans during workflow execution and provides export helpers.

    Usage::

        tracer = Tracer("my-workflow")
        with tracer.span("step-1") as s:
            s.attributes["input"] = "hello"
            ...
        tracer.print_trace()
        tracer.export_json("trace.json")

    You can also feed an :class:`ExecutionTrace` from a
    :class:`~agentloom.core.Workflow` run into the tracer via
    :meth:`from_execution_trace`.
    """

    def __init__(self, name: str = "root") -> None:
        self.root = Span(name=name)
        self._current: Span = self.root

    # -- span management ---------------------------------------------------

    def span(self, name: str, **attributes: Any) -> Span:
        """Create a child span under the current context.

        The returned ``Span`` is a context manager::

            with tracer.span("do-work") as s:
                ...
        """
        child = self._current.add_child(name)
        child.attributes.update(attributes)
        return child

    # -- bulk import -------------------------------------------------------

    @classmethod
    def from_execution_trace(cls, trace: ExecutionTrace, name: str = "workflow") -> "Tracer":
        """Build a Tracer tree from a finished :class:`ExecutionTrace`."""
        tracer = cls(name=name)
        tracer.root.start_time = time.time()

        for result in trace.results:
            child = tracer.root.add_child(result.step_name)
            child.status = result.status.value
            child.attributes["input"] = result.input_data
            child.attributes["output"] = (
                result.output_data
                if isinstance(result.output_data, (str, int, float, bool, type(None), list, dict))
                else repr(result.output_data)
            )
            child.attributes["duration_ms"] = result.duration_ms
            if result.error:
                child.attributes["error"] = result.error
            # Synthesise timing (relative offsets from root).
            child.end_time = tracer.root.start_time + result.duration_ms / 1000
            child.start_time = child.end_time - result.duration_ms / 1000

        tracer.root.end_time = time.time()
        return tracer

    # -- export ------------------------------------------------------------

    def export_json(self, path: str | Path) -> None:
        """Write the trace tree as a JSON file."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as fh:
            json.dump(self.root.to_dict(), fh, indent=2, default=str)

    def to_dict(self) -> dict[str, Any]:
        return self.root.to_dict()

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, default=str)

    # -- rich output -------------------------------------------------------

    def print_trace(self, console: Console | None = None) -> None:
        """Render the execution tree to the terminal using Rich."""
        console = console or Console()
        tree = self._build_tree(self.root)
        console.print()
        console.print(Panel(tree, title="AgentLoom Execution Trace", border_style="blue"))
        console.print()

    def _build_tree(self, span: Span, depth: int = 0) -> Tree:
        """Recursively build a Rich Tree from Span objects."""
        status_icon = self._status_icon(span.status)
        label = Text()
        label.append(f"{status_icon} ", style="bold")
        label.append(span.name, style="bold cyan")
        if span.duration_ms > 0:
            label.append(f"  [{span.duration_ms:.1f} ms]", style="dim")
        if span.status == "error":
            label.append("  ERROR", style="bold red")

        tree = Tree(label)

        # Show key attributes (skip very large ones).
        for key, value in span.attributes.items():
            val_str = self._truncate(repr(value), 120)
            attr_text = Text()
            attr_text.append(f"{key}: ", style="green")
            attr_text.append(val_str, style="white")
            tree.add(attr_text)

        for child in span.children:
            tree.add(self._build_tree(child, depth + 1))

        return tree

    @staticmethod
    def _status_icon(status: str) -> str:
        return {
            "ok": "[green]OK[/green]",
            "success": "[green]OK[/green]",
            "error": "[red]ERR[/red]",
            "skipped": "[yellow]SKIP[/yellow]",
            "retried": "[yellow]RETRY[/yellow]",
        }.get(status, "[white]--[/white]")

    @staticmethod
    def _truncate(text: str, max_len: int = 120) -> str:
        if len(text) > max_len:
            return text[: max_len - 3] + "..."
        return text
