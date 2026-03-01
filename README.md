# AgentLoom

**Build observable agent workflows with Python decorators. Full tracing, zero boilerplate.**

[![CI](https://github.com/YOUR_ORG/agentloom/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_ORG/agentloom/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/agentloom.svg)](https://pypi.org/project/agentloom/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Tests](https://img.shields.io/badge/tests-21%20passing-brightgreen)
![No LLM Required](https://img.shields.io/badge/LLM-not%20required-orange)

> Define workflows as decorated functions. Get execution traces for free.

---

## The Problem

Building agent workflows means wrestling with:
- Orchestration frameworks with steep learning curves (LangGraph, CrewAI configs)
- No visibility into what each step did, how long it took, or why it failed
- Tight coupling to specific LLM providers
- Can't test workflows without API keys

## The Fix

AgentLoom uses Python decorators to turn plain functions into traced, observable workflow steps:

```python
from agentloom import step, Workflow

@step(name="fetch")
def fetch():
    return {"text": "Hello, world!"}

@step(name="analyze", retries=2, on_error="skip")
def analyze(data):
    return {"words": len(data["text"].split())}

workflow = Workflow(name="my-pipeline")
workflow.add_step(fetch)
workflow.add_step(analyze)
trace = workflow.run()
```

**No LLM required.** Prototype, test, and debug workflows locally.

## Quickstart

```bash
pip install -e .

# Run the example workflow
agentloom run examples/summarize.py
```

Output:
```
+-----------------------------------------+
|      AgentLoom Execution Trace          |
+-----------------------------------------+
| OK  summarize-pipeline  [15.2 ms]      |
|   OK  fetch_text  [0.3 ms]             |
|   OK  analyze  [0.1 ms]                |
|   OK  summarize  [0.1 ms]              |
+-----------------------------------------+
Trace: 3 step(s), 3 succeeded, 0 failed
```

## Why AgentLoom?

| Framework | Learning Curve | LLM Required | Tracing | Testable Locally |
|-----------|:--------------:|:------------:|:-------:|:----------------:|
| LangGraph | Steep | Yes | Plugin | No |
| CrewAI | Medium | Yes | Limited | No |
| Prefect | Medium | No | Yes | Yes |
| **AgentLoom** | **Minimal** | **No** | **Built-in** | **Yes** |

## Decorator API

### `@step`

Mark a function as a workflow step. Inputs, outputs, timing, and errors are recorded automatically.

```python
@step(name="process", retries=2, on_error="skip")
def process(data):
    return {"result": data["value"] * 2}
```

| Parameter | Default | Description |
|-----------|---------|-------------|
| `name` | function name | Step name for tracing |
| `retries` | `0` | Automatic retry count on failure |
| `on_error` | `"raise"` | `"raise"` to re-raise, `"skip"` to continue |

### `@tool`

Register a function as a tool for agent discovery at runtime.

```python
from agentloom import tool

@tool(name="calculator")
def calculator(expression: str) -> float:
    return eval(expression)
```

### Conditional Branching

Return `{"__next__": "step_name"}` to jump to a named step:

```python
@step(name="router")
def router(data):
    if data.get("urgent"):
        return {"__next__": "fast_path", "value": data}
    return data  # continue sequentially
```

### Async Steps

```python
@step(name="fetch")
async def fetch(url):
    async with httpx.AsyncClient() as client:
        return (await client.get(url)).json()
```

## CLI Reference

```
agentloom run WORKFLOW_FILE       Execute a workflow
agentloom run FILE -t trace.json  Execute and save trace
agentloom trace TRACE_FILE        Pretty-print a saved trace
agentloom init                    Scaffold a new workflow file
```

## Trace Export

```python
from agentloom import Tracer

tracer = Tracer.from_execution_trace(trace)
tracer.export_json("trace.json")    # JSON export
tracer.print_trace()                 # Rich terminal tree
```

## Architecture

```
agentloom/
  core.py       Workflow engine, @step, @tool, ExecutionTrace
  tracer.py     Span-based tracing, JSON export, Rich rendering
  cli.py        Click CLI (run, trace, init)
```

- **Decorator-based** -- workflows are plain Python, no YAML required
- **Pydantic models** -- StepResult uses Pydantic for validation
- **Pluggable error handling** -- per-step retry and skip-on-error

## Use Cases

- **Agent prototyping** -- sketch multi-step pipelines without LLM API keys
- **Workflow testing** -- pytest against deterministic step logic
- **Observability** -- attach tracing to production workflows
- **CI/CD pipelines** -- run `agentloom run` in CI to validate correctness

## Development

```bash
pip install -e ".[dev]"
pytest
ruff check src/ tests/
mypy src/
```

## License

MIT. See [LICENSE](LICENSE).
