# AgentLoom Roadmap

## Vision
Make multi-step agent workflows as easy to build, test, and debug as regular Python functions.

## ✅ Shipped
- Decorator-based workflow step definitions
- Automatic timing, input/output capture per step
- Async support
- Conditional branching and configurable retries
- 21+ tests

## 🔨 In Progress
- [ ] OpenTelemetry trace export (Jaeger, Zipkin, Datadog)
- [ ] Visual workflow diagram generation (Mermaid)
- [ ] LangChain / LangGraph compatibility layer

## 📋 Planned — Q2 2025
- [ ] Web UI for trace visualisation
- [ ] Workflow versioning and replay
- [ ] Parallel step execution
- [ ] Human-in-the-loop pause/resume

## 📋 Planned — Q3 2025
- [ ] CrewAI agent wrapping support
- [ ] Workflow library / registry (share reusable workflows)
- [ ] Cost tracking per workflow run (integrates with TokenMeter)

## 💡 Under Consideration
- VSCode extension for workflow visualisation
- AutoGen compatibility
- Streaming step output

## Contributing
See [CONTRIBUTING.md](CONTRIBUTING.md).
