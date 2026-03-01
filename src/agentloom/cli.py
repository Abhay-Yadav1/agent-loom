"""AgentLoom CLI - command-line interface for running and inspecting workflows."""

from __future__ import annotations

import importlib.util
import json
import sys
import textwrap
from pathlib import Path
from typing import Any

import click
from rich.console import Console

import agentloom
from agentloom.tracer import Tracer

console = Console()


@click.group()
@click.version_option(version=agentloom.__version__, prog_name="agentloom")
def main() -> None:
    """AgentLoom - Build observable agent workflows with full tracing."""


# -----------------------------------------------------------------------
# agentloom run
# -----------------------------------------------------------------------

@main.command()
@click.argument("workflow_file", type=click.Path(exists=True))
@click.option("--trace-out", "-t", default=None, help="Path to write trace JSON.")
def run(workflow_file: str, trace_out: str | None) -> None:
    """Execute a workflow Python file.

    The file must expose either a ``workflow`` variable (a Workflow instance)
    or a ``main()`` function that returns a Workflow or ExecutionTrace.
    """
    path = Path(workflow_file).resolve()
    console.print(f"[bold blue]AgentLoom[/bold blue] running [cyan]{path.name}[/cyan]")

    module = _load_module(path)

    trace = None

    # Strategy 1: the module has a ``workflow`` Workflow object.
    wf = getattr(module, "workflow", None)
    if wf is not None and hasattr(wf, "run"):
        trace = wf.run()

    # Strategy 2: the module has a callable ``main``.
    if trace is None:
        main_fn = getattr(module, "main", None)
        if main_fn is not None and callable(main_fn):
            result = main_fn()
            if isinstance(result, agentloom.ExecutionTrace):
                trace = result
            elif hasattr(result, "get_trace"):
                trace = result.get_trace()

    if trace is None:
        console.print(
            "[red]Could not find a 'workflow' variable or 'main()' function "
            "in the workflow file.[/red]"
        )
        sys.exit(1)

    # Print trace.
    tracer = Tracer.from_execution_trace(trace)
    tracer.print_trace(console)
    console.print(trace.summary())

    # Optionally persist.
    if trace_out:
        tracer.export_json(trace_out)
        console.print(f"[green]Trace written to {trace_out}[/green]")


# -----------------------------------------------------------------------
# agentloom trace
# -----------------------------------------------------------------------

@main.command()
@click.argument("trace_file", type=click.Path(exists=True))
def trace(trace_file: str) -> None:
    """Pretty-print a saved trace JSON file."""
    path = Path(trace_file).resolve()
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)

    tracer = Tracer(name=data.get("name", "trace"))
    _rebuild_spans(tracer.root, data)
    tracer.print_trace(console)


# -----------------------------------------------------------------------
# agentloom init
# -----------------------------------------------------------------------

TEMPLATE = textwrap.dedent('''\
    """Auto-generated AgentLoom workflow scaffold."""

    from agentloom import Workflow, step


    @step(name="load_data")
    def load_data():
        """Load or fetch input data."""
        return {"text": "Hello, world!"}


    @step(name="process")
    def process(data):
        """Transform or analyse the data."""
        text = data.get("text", "")
        return {"word_count": len(text.split()), "text": text}


    @step(name="report")
    def report(data):
        """Produce the final output."""
        print(f"Word count: {data['word_count']}")
        return data


    # -- Workflow assembly ------------------------------------------------

    workflow = Workflow(name="my-workflow")
    workflow.add_step(load_data)
    workflow.add_step(process)
    workflow.add_step(report)

    if __name__ == "__main__":
        trace = workflow.run()
        print(trace.summary())
''')


@main.command()
@click.option(
    "--output", "-o",
    default="workflow.py",
    help="Output file name.",
    show_default=True,
)
def init(output: str) -> None:
    """Scaffold a new workflow file from a starter template."""
    dest = Path(output)
    if dest.exists():
        console.print(f"[yellow]File {dest} already exists. Overwrite? (y/N)[/yellow]", end=" ")
        answer = input()
        if answer.lower() != "y":
            console.print("[dim]Aborted.[/dim]")
            return

    dest.write_text(TEMPLATE, encoding="utf-8")
    console.print(f"[green]Created {dest}[/green]")


# -----------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------

def _load_module(path: Path) -> Any:
    """Dynamically import a Python file as a module."""
    spec = importlib.util.spec_from_file_location("_agentloom_workflow", str(path))
    if spec is None or spec.loader is None:
        console.print(f"[red]Cannot load {path}[/red]")
        sys.exit(1)
    module = importlib.util.module_from_spec(spec)
    sys.modules["_agentloom_workflow"] = module
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


def _rebuild_spans(parent_span: Any, data: dict[str, Any]) -> None:
    """Recursively populate a Span tree from a dict (loaded from JSON)."""
    parent_span.start_time = data.get("start_time", 0)
    parent_span.end_time = data.get("end_time", 0)
    parent_span.status = data.get("status", "ok")
    parent_span.attributes = data.get("attributes", {})

    for child_data in data.get("children", []):
        child = parent_span.add_child(child_data.get("name", "unnamed"))
        _rebuild_spans(child, child_data)
