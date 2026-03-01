# AgentLoom Launch Kit

## HN Post Draft

**Title:** Show HN: AgentLoom – Build observable LLM agent workflows with Python decorators

**Body:**
AgentLoom lets you build agent workflows using Python decorators. Every step is automatically traced with timing, inputs, outputs, and errors.

```python
from agentloom import step, Workflow

@step(name="fetch")
def fetch_data(url: str) -> str:
    return requests.get(url).text

@step(name="analyze")
def analyze(text: str) -> dict:
    return {"word_count": len(text.split())}

wf = Workflow(steps=[fetch_data, analyze])
trace = wf.run({"url": "https://example.com"})
trace.print_trace()  # Rich terminal output with timing tree
```

No LLM required for the core — it's a workflow engine with observability built in. Use it with any LLM library, or without one.

GitHub: [link]

---

## Reddit Post Draft

**Title:** Python decorators for observable agent workflows — trace every step with timing and I/O

Built AgentLoom — a decorator-based workflow engine where every step is automatically traced. Use `@step` to mark functions, compose them into a Workflow, and get a full execution trace with timing tree. Export traces as JSON for debugging.

Works without any LLM — it's a workflow engine, not an LLM framework.

---

## LinkedIn Post Draft

Debugging LLM agents shouldn't require guesswork.

Open-sourced AgentLoom — a Python library for building observable agent workflows.

How it works:
→ Decorate functions with @step
→ Compose into a Workflow
→ Run and get a full execution trace
→ Export traces as JSON for analysis

The key: observability is built in, not bolted on.

#LLMAgents #Observability #OpenSource #Python

---

## 10 Build-in-Public Updates

1. "AgentLoom's @step decorator adds <0.1ms overhead per call — here's the benchmark"
2. "Why I built a workflow engine without depending on LangChain"
3. "AgentLoom traces: what a 12-step agent execution looks like in the terminal"
4. "Adding conditional branching: workflow steps can now route based on output"
5. "AgentLoom v0.2: async step support with concurrent execution"
6. "The decorator pattern for ML workflows: lessons from building AgentLoom"
7. "AgentLoom + OpenTelemetry: exporting traces to Jaeger in 5 lines"
8. "Error recovery in agent workflows: retry, skip, or fail-fast"
9. "AgentLoom reaches 50 stars — mostly from LangChain users who want something simpler"
10. "AgentLoom v0.3: YAML workflow definition for non-Python users"

---

## Benchmark Plan

**Chart:** "Workflow overhead: AgentLoom vs. bare function calls"

- Measure: 10-step workflow execution with trivial steps
- Compare: raw function calls vs. AgentLoom decorated steps
- Show: overhead per step in microseconds

---

## Before vs After

**Before:** Agent code with manual print statements for debugging, no timing, lost context on errors.
**After:** Same agent with @step decorators — full execution trace with timing tree, error context, exportable JSON.

---

## 30-Day Roadmap

| Week | Milestone |
|------|-----------|
| 1 | v0.1.0 release. Launch on Python subreddits. |
| 2 | Add async step support. Error recovery strategies. |
| 3 | v0.2.0: OpenTelemetry export. Parallel step execution. |
| 4 | v0.3.0: Web trace viewer. LLM-specific step types. |

---

## 20 Good First Issues

1. Add `@step` retry parameter (max_retries=3)
2. Add step timeout parameter
3. Add parallel step execution (fan-out/fan-in)
4. Add YAML workflow definition support
5. Add `agentloom validate` to check workflow file
6. Add OpenTelemetry span export
7. Add step caching (memoization)
8. Add workflow composition (sub-workflows)
9. Add step input/output type validation
10. Add Mermaid diagram generation from workflow
11. Add `agentloom replay` to re-run a workflow from trace
12. Add step hooks (before/after)
13. Add progress bar for long-running workflows
14. Add HTML trace viewer
15. Add workflow versioning
16. Add step dependency graph (DAG execution)
17. Write tutorial: "Building a RAG pipeline with AgentLoom"
18. Add LLM-specific step type (@llm_step)
19. Add trace comparison (diff two runs)
20. Add workflow metrics (success rate, average duration)
