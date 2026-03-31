# CLAUDE.md -- AgentLoom

AgentLoom is a Python decorator framework for building observable agent
workflows. It wraps plain functions with a @step decorator to provide
automatic execution traces, timing, dependency tracking, and error handling
with no LLM required, no YAML, and no framework-specific concepts to learn.

## Project Owner

Nirbhay Singh -- Cloud and AI Architect based in Warsaw. AgentLoom is part of
his AI engineering portfolio, which also includes:
- airlock -- LLM security proxy (PII redaction, prompt injection defense)
- data-mint -- synthetic test data generator for LLM evaluation
- tune-forge -- fine-tuning pipeline toolkit

## Repo Layout

```
src/agentloom/
  __init__.py   exports: step, tool, Workflow, ExecutionTrace, Tracer
  core.py       @step, @tool decorators; Workflow; ExecutionTrace; StepResult
  tracer.py     Span-based tracing, JSON export, Rich terminal rendering
  cli.py        Click CLI: run / trace / init subcommands
tests/
  test_core.py        unit tests for decorators, Workflow, StepResult
  test_integration.py end-to-end workflow execution tests
examples/
  summarize.py        three-step summarise workflow example
docs/
  architecture.md     design decisions and component overview
```

## Core Concepts

### StepResult (Pydantic model)

The atomic unit of tracing. Produced by every step execution:

| Field       | Type        | Description                                      |
|-------------|-------------|--------------------------------------------------|
| step_name   | str         | human-readable name from @step(name=...)         |
| status      | StepStatus  | SUCCESS / ERROR / SKIPPED / RETRIED              |
| input_data  | dict        | JSON-safe snapshot of function arguments         |
| output_data | Any         | return value of the function                     |
| duration_ms | float       | wall-clock execution time in milliseconds        |
| error       | str or None | exception message if status is ERROR or SKIPPED  |

### ExecutionTrace

Accumulates StepResult objects as a workflow runs. Key methods:
- record(result) -- append a result (called internally by step wrappers)
- results property -- ordered list of all StepResults
- total_duration_ms -- sum of all step durations
- to_dict() / to_json() -- serialise to a JSON-safe dict or JSON string
- summary() -- one-line text: "3 step(s), 3 succeeded, 0 failed, total 15.3 ms"

### @step Decorator -- How It Works Internally

step(name, retries, on_error) is a decorator factory in core.py. It:

1. Detects whether the decorated function is async (inspect.iscoroutinefunction)
   and wraps it with either async_wrapper or sync_wrapper.
2. The wrapper calls _execute_step_sync or _execute_step (async), which
   captures the function arguments into a JSON-safe dict via _capture_input
   (uses inspect.signature.bind).
3. The function is called (with retries if configured). time.perf_counter
   is used for microsecond-precision timing.
4. On success, a StepResult(status=SUCCESS) is constructed and pushed to the
   module-level _active_results list via _push_result.
5. On failure after all retries: if on_error="skip", a StepResult(status=SKIPPED)
   is pushed and None is returned; if on_error="raise", the exception is re-raised.
6. The wrapper has _agentloom_step=True and _agentloom_step_name attributes
   attached so that Workflow.add_step() can introspect metadata without the
   user passing the same arguments twice.

### @tool Decorator

Registers a function in the module-level _TOOL_REGISTRY dict for agent
discovery at runtime. get_tools() returns a copy of the registry.
Unlike @step, @tool does not add tracing -- it is a simple registration
mechanism for LLM agent frameworks to enumerate available tools.

### Workflow Class

Workflow(name) orchestrates sequential step execution:

- add_step(fn, name=None) -- registers a callable; supports method chaining
- run(initial_input={}) -- executes steps synchronously, returns ExecutionTrace
- arun(initial_input={}) -- async variant for workflows with async steps
- get_trace() -- returns the accumulated ExecutionTrace

#### Execution Internals

_run_steps / _arun_steps iterate the registered steps in order:

1. Before execution, the global _active_results list is swapped out
   (the Workflow saves the outer list and installs a fresh one), preventing
   result contamination between nested workflows.
2. Each step receives prev_result (the prior step return value, or
   initial_input for the first step) as its first argument.
3. Conditional branching: if a step returns a dict containing "__next__",
   the Workflow jumps to the named step instead of advancing sequentially.
   The branching payload is passed as result.get("value", result).
4. After all steps, recorded results are copied into the Workflow ExecutionTrace
   and _active_results is restored to the outer list.

## Tracer -- Span-Based Observability

Location: src/agentloom/tracer.py

The Tracer class builds a tree of Span objects (analogous to OpenTelemetry
spans). Each Span has: name, start_time, end_time, status, attributes dict,
and a list of child spans.

Tracer.from_execution_trace(trace, name) is the main integration point:
it converts an ExecutionTrace (from Workflow.run()) into a Span tree for
visualisation and export.

### Exporting Traces

```python
from agentloom import Workflow, Tracer

trace = workflow.run()
tracer = Tracer.from_execution_trace(trace, name="my-workflow")

tracer.print_trace()              # Rich terminal tree (coloured, timed)
tracer.export_json("trace.json")  # Write JSON to file
tracer.to_dict()                  # Return as dict (for custom handling)
tracer.to_json()                  # Return as JSON string
```

The print_trace() method uses Rich Tree and Panel for a coloured hierarchical
display. Status icons: OK (green), ERR (red), SKIP (yellow), RETRY (yellow).

## Defining a Multi-Step Workflow

```python
from agentloom import step, Workflow

@step(name="fetch", retries=2)
def fetch():
    return {"text": "Hello, world!"}

@step(name="analyze", on_error="skip")
def analyze(data):
    return {"words": len(data["text"].split()), "text": data["text"]}

@step(name="report")
def report(data):
    print(f"Word count: {data['words']}")
    return data

workflow = Workflow(name="my-pipeline")
workflow.add_step(fetch).add_step(analyze).add_step(report)
trace = workflow.run()
print(trace.summary())
```

## Conditional Branching

Return a dict with "__next__" set to a step name to jump to that step:

```python
@step(name="router")
def router(data):
    if data.get("urgent"):
        return {"__next__": "fast_path", "value": data}
    return data  # continue sequentially
```

## Async Steps

```python
import httpx

@step(name="fetch_url")
async def fetch_url(url):
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        return resp.json()

# Use workflow.arun() for workflows containing async steps
import asyncio
trace = asyncio.run(workflow.arun({"url": "https://example.com"}))
```

## CLI Reference

```bash
# Execute a workflow file (must expose a workflow variable or main() function)
agentloom run examples/summarize.py

# Execute and save trace to JSON
agentloom run examples/summarize.py --trace-out trace.json

# Pretty-print a saved trace file
agentloom trace trace.json

# Scaffold a new workflow file from a template
agentloom init                       # creates workflow.py
agentloom init --output my_flow.py   # custom output path
```

The run command uses importlib.util to dynamically load the workflow file
as a module, then looks for either a workflow variable (Workflow instance)
or a main() callable that returns a Workflow or ExecutionTrace.

## Installation and Running

```bash
# Install for development
pip install -e ".[dev]"

# Run the example workflow
agentloom run examples/summarize.py

# Run a workflow and save the trace
agentloom run examples/summarize.py -t trace.json
agentloom trace trace.json
```

PyPI package name: agentloom (pip install agentloom).

## Testing

```bash
pip install -e ".[dev]"
pytest                            # run all 21 tests
pytest tests/test_core.py         # decorator and Workflow unit tests
pytest tests/test_integration.py  # end-to-end workflow tests
pytest -v --tb=short              # verbose with short tracebacks
```

Test files:
- tests/test_core.py -- @step decorator behaviour (retries, on_error, async,
  timing, StepResult fields, Workflow branching, @tool registration)
- tests/test_integration.py -- multi-step workflow execution, trace export,
  error propagation, JSON round-trip

No external services or LLM API keys are required.

## Extending with Custom Step Types

AgentLoom does not have a formal plugin registry for step types, but you can
extend the system in three ways:

### 1. Custom decorator wrapping @step

Build domain-specific defaults on top of @step:

```python
from agentloom import step
import functools

def retrying_step(name, max_retries=3):
    def decorator(fn):
        @step(name=name, retries=max_retries, on_error="skip")
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            return fn(*args, **kwargs)
        return wrapper
    return decorator
```

### 2. Custom Tracer rendering

Subclass Tracer and override _build_tree or _status_icon to add custom
rendering, or override export_json to add new export formats alongside
the built-in JSON export.

### 3. Workflow subclass

Subclass Workflow and override _run_steps / _arun_steps for parallel
execution, priority ordering, or external event triggers.

## Code Style and Tooling

```bash
ruff check src/ tests/    # linting (line-length 100)
ruff format src/ tests/   # auto-formatting
mypy src/                 # strict type checking
```

Python 3.10+ required. All public APIs have docstrings. Pydantic v2 is used
for StepResult; v1 is not supported. The codebase avoids heavy framework
dependencies by design -- the core workflow engine has no LLM dependency.

## Key Dependencies

| Package     | Role                                                |
|-------------|-----------------------------------------------------|
| pydantic v2 | StepResult and data model validation                |
| click       | CLI framework                                       |
| rich        | Terminal trace rendering (Tree, Panel, Text)        |
| structlog   | Structured logging from step wrappers               |
| httpx       | Optional -- used in examples for HTTP-fetching steps|
| pyyaml      | Optional -- available for workflow config loading   |

## Architecture Notes

The tracing mechanism uses a module-level mutable list (_active_results) that
Workflow.run() swaps in and out around execution. This is intentionally
simple -- it avoids threading complexity and context variables for the common
single-threaded use case. For concurrent workflows, the Workflow subclass
approach is recommended.

The @step decorator attaches metadata attributes (_agentloom_step,
_agentloom_step_name, _agentloom_retries, _agentloom_on_error) to the
wrapper function so that Workflow.add_step() can read them without requiring
the user to pass the same arguments twice.

## Use Cases

- Agent prototyping: sketch multi-step pipelines without LLM API keys
- Workflow testing: pytest against deterministic step logic
- Production observability: attach tracing to existing Python functions
- CI/CD validation: agentloom run workflow.py in CI to verify correctness
