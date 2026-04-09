"""LangChain / LangGraph compatibility layer for AgentLoom."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from agentloom.core import step as agentloom_step


def as_step(
    runnable: Any,
    name: str | None = None,
    retries: int = 0,
    on_error: str = "raise",
) -> Callable[..., Any]:
    """Wrap a LangChain Runnable as an AgentLoom step.

    Parameters
    ----------
    runnable:
        Any object with an ``.invoke(input)`` method —
        a LangChain Runnable, chain, or compiled LangGraph graph.
    name:
        Step name shown in traces. Defaults to the runnable's class name.
    retries:
        Number of automatic retries on failure (0 = no retry).
    on_error:
        ``"raise"`` or ``"skip"`` — matches AgentLoom's @step behaviour.
    """
    if not hasattr(runnable, "invoke"):
        raise TypeError(
            f"Expected a LangChain Runnable with an `.invoke()` method, "
            f"got {type(runnable).__name__!r} instead."
        )

    step_name = name or type(runnable).__name__

    # Apply the real @step decorator so tracing, retries, and
    # error handling work exactly like native AgentLoom steps.
    @agentloom_step(name=step_name, retries=retries, on_error=on_error)
    def wrapper(prev_result: Any = None) -> Any:
        return runnable.invoke(prev_result)

    wrapper.__name__ = step_name
    wrapper.__qualname__ = step_name

    return wrapper
