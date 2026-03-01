"""Core workflow engine for AgentLoom.

Provides the @step and @tool decorators, the Workflow orchestrator,
and the ExecutionTrace / StepResult data models.
"""

from __future__ import annotations

import asyncio
import functools
import inspect
import json
import time
from enum import Enum
from typing import Any, Callable, TypeVar

import structlog
from pydantic import BaseModel, Field

logger = structlog.get_logger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

class StepStatus(str, Enum):
    """Possible statuses for a step execution."""
    SUCCESS = "success"
    ERROR = "error"
    SKIPPED = "skipped"
    RETRIED = "retried"


class StepResult(BaseModel):
    """Immutable record of a single step execution."""
    step_name: str
    status: StepStatus = StepStatus.SUCCESS
    input_data: dict[str, Any] = Field(default_factory=dict)
    output_data: Any = None
    duration_ms: float = 0.0
    error: str | None = None


# ---------------------------------------------------------------------------
# ExecutionTrace
# ---------------------------------------------------------------------------

class ExecutionTrace:
    """Accumulates StepResult records and provides serialisation helpers."""

    def __init__(self) -> None:
        self._results: list[StepResult] = []

    # -- mutators ----------------------------------------------------------

    def record(self, result: StepResult) -> None:
        """Append a step result to the trace."""
        self._results.append(result)

    # -- accessors ---------------------------------------------------------

    @property
    def results(self) -> list[StepResult]:
        return list(self._results)

    @property
    def total_duration_ms(self) -> float:
        return sum(r.duration_ms for r in self._results)

    # -- serialisation -----------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        return {
            "steps": [r.model_dump(mode="json") for r in self._results],
            "total_duration_ms": self.total_duration_ms,
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    def summary(self) -> str:
        """One-line human-readable summary."""
        total = len(self._results)
        ok = sum(1 for r in self._results if r.status == StepStatus.SUCCESS)
        err = sum(1 for r in self._results if r.status == StepStatus.ERROR)
        return (
            f"Trace: {total} step(s), {ok} succeeded, {err} failed, "
            f"total {self.total_duration_ms:.1f} ms"
        )


# ---------------------------------------------------------------------------
# @step decorator
# ---------------------------------------------------------------------------

def step(
    name: str | None = None,
    retries: int = 0,
    on_error: str = "raise",  # "raise" | "skip"
) -> Callable[[F], F]:
    """Mark a function as a workflow step.

    Parameters
    ----------
    name:
        Human-readable name for tracing. Defaults to the function name.
    retries:
        Number of automatic retries on failure (0 = no retry).
    on_error:
        What to do when all retries are exhausted.
        ``"raise"`` re-raises the exception; ``"skip"`` records the error
        and returns ``None``.
    """

    def decorator(fn: F) -> F:
        step_name = name or fn.__name__

        @functools.wraps(fn)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            return await _execute_step(fn, step_name, retries, on_error, args, kwargs, is_async=True)

        @functools.wraps(fn)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            return _execute_step_sync(fn, step_name, retries, on_error, args, kwargs)

        wrapper: Any
        if inspect.iscoroutinefunction(fn):
            wrapper = async_wrapper
        else:
            wrapper = sync_wrapper

        # Attach metadata so the Workflow can introspect.
        wrapper._agentloom_step = True  # type: ignore[attr-defined]
        wrapper._agentloom_step_name = step_name  # type: ignore[attr-defined]
        wrapper._agentloom_retries = retries  # type: ignore[attr-defined]
        wrapper._agentloom_on_error = on_error  # type: ignore[attr-defined]

        return wrapper  # type: ignore[return-value]

    return decorator


def _execute_step_sync(
    fn: Callable[..., Any],
    step_name: str,
    retries: int,
    on_error: str,
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
) -> Any:
    """Run a **sync** step with retry / error-handling semantics."""
    input_data = _capture_input(fn, args, kwargs)
    attempts = retries + 1
    last_exc: Exception | None = None

    for attempt in range(1, attempts + 1):
        start = time.perf_counter()
        try:
            result = fn(*args, **kwargs)
            duration = (time.perf_counter() - start) * 1000
            sr = StepResult(
                step_name=step_name,
                status=StepStatus.RETRIED if attempt > 1 else StepStatus.SUCCESS,
                input_data=input_data,
                output_data=result,
                duration_ms=round(duration, 3),
            )
            _push_result(sr)
            logger.info("step.ok", step=step_name, duration_ms=sr.duration_ms)
            return result
        except Exception as exc:
            duration = (time.perf_counter() - start) * 1000
            last_exc = exc
            logger.warning(
                "step.error",
                step=step_name,
                attempt=attempt,
                error=str(exc),
            )

    # All retries exhausted
    duration = (time.perf_counter() - start) * 1000  # type: ignore[possibly-undefined]
    sr = StepResult(
        step_name=step_name,
        status=StepStatus.ERROR if on_error == "raise" else StepStatus.SKIPPED,
        input_data=input_data,
        output_data=None,
        duration_ms=round(duration, 3),
        error=str(last_exc),
    )
    _push_result(sr)

    if on_error == "raise":
        raise last_exc  # type: ignore[misc]
    return None


async def _execute_step(
    fn: Callable[..., Any],
    step_name: str,
    retries: int,
    on_error: str,
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
    *,
    is_async: bool = True,
) -> Any:
    """Run an **async** step with retry / error-handling semantics."""
    input_data = _capture_input(fn, args, kwargs)
    attempts = retries + 1
    last_exc: Exception | None = None

    for attempt in range(1, attempts + 1):
        start = time.perf_counter()
        try:
            result = await fn(*args, **kwargs)
            duration = (time.perf_counter() - start) * 1000
            sr = StepResult(
                step_name=step_name,
                status=StepStatus.RETRIED if attempt > 1 else StepStatus.SUCCESS,
                input_data=input_data,
                output_data=result,
                duration_ms=round(duration, 3),
            )
            _push_result(sr)
            logger.info("step.ok", step=step_name, duration_ms=sr.duration_ms)
            return result
        except Exception as exc:
            duration = (time.perf_counter() - start) * 1000
            last_exc = exc
            logger.warning(
                "step.error",
                step=step_name,
                attempt=attempt,
                error=str(exc),
            )

    # All retries exhausted
    duration = (time.perf_counter() - start) * 1000  # type: ignore[possibly-undefined]
    sr = StepResult(
        step_name=step_name,
        status=StepStatus.ERROR if on_error == "raise" else StepStatus.SKIPPED,
        input_data=input_data,
        output_data=None,
        duration_ms=round(duration, 3),
        error=str(last_exc),
    )
    _push_result(sr)

    if on_error == "raise":
        raise last_exc  # type: ignore[misc]
    return None


# ---------------------------------------------------------------------------
# @tool decorator
# ---------------------------------------------------------------------------

_TOOL_REGISTRY: dict[str, Callable[..., Any]] = {}


def tool(name: str | None = None) -> Callable[[F], F]:
    """Mark a function as a tool that agents can invoke.

    Tools are registered globally so that agent logic can look them up by
    name at runtime.
    """

    def decorator(fn: F) -> F:
        tool_name = name or fn.__name__

        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return fn(*args, **kwargs)

        wrapper._agentloom_tool = True  # type: ignore[attr-defined]
        wrapper._agentloom_tool_name = tool_name  # type: ignore[attr-defined]
        _TOOL_REGISTRY[tool_name] = wrapper
        return wrapper  # type: ignore[return-value]

    return decorator


def get_tools() -> dict[str, Callable[..., Any]]:
    """Return a copy of the global tool registry."""
    return dict(_TOOL_REGISTRY)


# ---------------------------------------------------------------------------
# Workflow
# ---------------------------------------------------------------------------

# Module-level list used by step wrappers to push results into the
# currently-active workflow.  The Workflow.run() method swaps this in/out.
_active_results: list[StepResult] = []


def _push_result(sr: StepResult) -> None:
    _active_results.append(sr)


class Workflow:
    """Collect steps and execute them, capturing a full ExecutionTrace.

    Steps are executed in the order they are added. A step may return a
    ``dict`` with a special ``"__next__"`` key whose value is the *name* of
    the next step to jump to (conditional branching). If a step returns any
    other value it is passed to the next step as ``prev_result``.
    """

    def __init__(self, name: str = "workflow") -> None:
        self.name = name
        self._steps: list[tuple[str, Callable[..., Any]]] = []
        self._trace = ExecutionTrace()

    # -- building ----------------------------------------------------------

    def add_step(self, fn: Callable[..., Any], name: str | None = None) -> "Workflow":
        """Register a callable as a step.

        If *fn* was decorated with ``@step`` its metadata is reused;
        otherwise *name* (or ``fn.__name__``) is used.
        """
        step_name = name or getattr(fn, "_agentloom_step_name", fn.__name__)
        self._steps.append((step_name, fn))
        return self  # allow chaining

    # -- execution ---------------------------------------------------------

    def run(self, initial_input: dict[str, Any] | None = None) -> ExecutionTrace:
        """Execute all registered steps sequentially and return the trace."""
        global _active_results  # noqa: PLW0603
        saved = _active_results
        _active_results = []

        try:
            self._run_steps(initial_input or {})
        finally:
            for sr in _active_results:
                self._trace.record(sr)
            _active_results = saved

        return self._trace

    async def arun(self, initial_input: dict[str, Any] | None = None) -> ExecutionTrace:
        """Async variant of :meth:`run`."""
        global _active_results  # noqa: PLW0603
        saved = _active_results
        _active_results = []

        try:
            await self._arun_steps(initial_input or {})
        finally:
            for sr in _active_results:
                self._trace.record(sr)
            _active_results = saved

        return self._trace

    def get_trace(self) -> ExecutionTrace:
        """Return the current execution trace."""
        return self._trace

    # -- internal ----------------------------------------------------------

    def _run_steps(self, initial_input: dict[str, Any]) -> None:
        prev_result: Any = initial_input
        step_index = 0
        step_map: dict[str, int] = {name: i for i, (name, _) in enumerate(self._steps)}

        while step_index < len(self._steps):
            _name, fn = self._steps[step_index]
            sig = inspect.signature(fn)
            kwargs: dict[str, Any] = {}

            # Provide prev_result if the function accepts it.
            params = list(sig.parameters.keys())
            if params:
                first = params[0]
                kwargs[first] = prev_result

            result = fn(**kwargs)

            # Conditional branching: if the result contains "__next__",
            # jump to that step.
            if isinstance(result, dict) and "__next__" in result:
                target = result["__next__"]
                if target in step_map:
                    step_index = step_map[target]
                    prev_result = result.get("value", result)
                    continue

            prev_result = result
            step_index += 1

    async def _arun_steps(self, initial_input: dict[str, Any]) -> None:
        prev_result: Any = initial_input
        step_index = 0
        step_map: dict[str, int] = {name: i for i, (name, _) in enumerate(self._steps)}

        while step_index < len(self._steps):
            _name, fn = self._steps[step_index]
            sig = inspect.signature(fn)
            kwargs: dict[str, Any] = {}

            params = list(sig.parameters.keys())
            if params:
                first = params[0]
                kwargs[first] = prev_result

            if inspect.iscoroutinefunction(fn):
                result = await fn(**kwargs)
            else:
                result = fn(**kwargs)

            if isinstance(result, dict) and "__next__" in result:
                target = result["__next__"]
                if target in step_map:
                    step_index = step_map[target]
                    prev_result = result.get("value", result)
                    continue

            prev_result = result
            step_index += 1


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _capture_input(fn: Callable[..., Any], args: tuple[Any, ...], kwargs: dict[str, Any]) -> dict[str, Any]:
    """Build a JSON-friendly dict of the function's bound arguments."""
    sig = inspect.signature(fn)
    try:
        bound = sig.bind(*args, **kwargs)
        bound.apply_defaults()
        return {k: _safe_repr(v) for k, v in bound.arguments.items()}
    except TypeError:
        return {"args": [_safe_repr(a) for a in args], "kwargs": {k: _safe_repr(v) for k, v in kwargs.items()}}


def _safe_repr(value: Any) -> Any:
    """Return a JSON-safe representation of *value*."""
    if isinstance(value, (str, int, float, bool, type(None))):
        return value
    if isinstance(value, (list, tuple)):
        return [_safe_repr(v) for v in value]
    if isinstance(value, dict):
        return {str(k): _safe_repr(v) for k, v in value.items()}
    return repr(value)
