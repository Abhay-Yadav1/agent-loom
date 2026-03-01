# AgentLoom Architecture

## Overview

AgentLoom provides a decorator-based Python API for building observable agent workflows. Each step is traced with timing, inputs, outputs, and status. Workflows can be sequential, conditional, or error-recovering.

## C4 Diagrams

### Level 1: System Context

```mermaid
graph TB
    User["Developer"]
    AgentLoom["AgentLoom<br/>Workflow Builder"]
    LLM["LLM API<br/>(optional)"]
    Trace["Execution Traces<br/>(JSON)"]

    User -->|"Python decorators"| AgentLoom
    AgentLoom -->|"step calls"| LLM
    AgentLoom -->|"export"| Trace

    style AgentLoom fill:#8b5cf6,stroke:#7c3aed,color:#fff
```

### Level 2: Container Diagram

```mermaid
graph TB
    subgraph AgentLoom["AgentLoom"]
        Decorators["@step / @tool<br/>Decorators"]
        Engine["Workflow Engine"]
        Tracer["Tracer<br/>(span collection)"]
        Export["Export<br/>(JSON / console)"]
    end

    UserCode["User's Python Code"] --> Decorators
    Decorators --> Engine
    Engine --> Tracer
    Tracer --> Export

    style AgentLoom fill:#f5f3ff,stroke:#8b5cf6
    style Engine fill:#8b5cf6,color:#fff
    style Tracer fill:#10b981,color:#fff
```

### Sequence Diagram: Workflow Execution

```mermaid
sequenceDiagram
    participant User
    participant Engine as Workflow Engine
    participant Step1 as @step: fetch
    participant Step2 as @step: analyze
    participant Step3 as @step: summarize
    participant Tracer

    User->>Engine: workflow.run()
    Engine->>Tracer: start_trace()

    Engine->>Step1: execute(input)
    Step1-->>Engine: result
    Engine->>Tracer: record_span(fetch, 12ms)

    Engine->>Step2: execute(result)
    Step2-->>Engine: analysis
    Engine->>Tracer: record_span(analyze, 5ms)

    Engine->>Step3: execute(analysis)
    Step3-->>Engine: summary
    Engine->>Tracer: record_span(summarize, 3ms)

    Engine->>Tracer: end_trace()
    Engine-->>User: ExecutionTrace(3 steps, 20ms total)
```

## Design Decisions

### Decorators vs. YAML/JSON Workflow Definition

**Chose:** Python decorators (`@step`, `@tool`).

**Why:** Native Python — no DSL to learn, full IDE support (autocomplete, type checking), easy to test individual steps. YAML definition is on the roadmap for non-developer users.

### Built-in Tracer vs. OpenTelemetry

**Chose:** Custom lightweight tracer for v0.1.

**Why:** Zero-dependency tracing that works out of the box. OpenTelemetry export is planned — the internal span model is designed to map directly to OTEL spans.

## Extension Points

1. Custom step types (async, parallel)
2. OpenTelemetry span export
3. Web UI trace viewer
4. YAML workflow definition
5. LLM-specific step types (chat, embed, classify)
