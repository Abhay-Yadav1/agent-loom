"""AgentLoom - Build observable agent workflows with decorator-based Python API and full tracing."""

__version__ = "0.1.0"

from agentloom.core import (
    ExecutionTrace,
    StepResult,
    Workflow,
    step,
    tool,
)
from agentloom.tracer import Tracer

__all__ = [
    "__version__",
    "step",
    "tool",
    "Workflow",
    "ExecutionTrace",
    "StepResult",
    "Tracer",
    "as_step",
]
from agentloom.integrations.langchain import as_step
