# Changelog

All notable changes to AgentLoom will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-01-15

### Added

- `@step` decorator with retry and error-handling semantics
- `@tool` decorator with global registry for agent tool discovery
- Workflow engine with sequential execution and conditional branching
- ExecutionTrace with timing, input/output capture, and serialization
- Span-based tracing with Rich terminal tree rendering
- JSON trace export for programmatic analysis
- Async workflow support
- CLI commands: `run`, `trace`, `init`
