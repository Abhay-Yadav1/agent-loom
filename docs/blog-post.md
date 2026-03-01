# I'm Mass-Deleting Agent Frameworks From My Projects. Here's the One I Replaced Them With.

*How a weekend of decorator-based thinking saved me from YAML-driven insanity.*

---

I have a confession. Over the past eighteen months, I have installed, configured, partially integrated, and then ripped out no fewer than five agent frameworks from production projects. LangChain. CrewAI. AutoGen. A brief fling with Semantic Kernel. Each time, the promise was the same: orchestrate your LLM agents with this beautiful abstraction layer. Each time, the reality was the same: I spent more time debugging the framework than debugging my actual logic.

Five frameworks in eighteen months. Every one promised to simplify my workflow. Every one *became* the workflow.

The final straw was a Tuesday afternoon. I had a three-step workflow -- fetch some data, run it through an LLM, format the output. Fifteen lines of actual logic. But by the time I had wired it up with the framework du jour, I was staring at four YAML files, two configuration objects, a custom callback handler, and a stack trace that pointed into framework internals I had never seen before.

So I built something different. And I want to show you what happened.

---

> **TL;DR -- What This Post Covers**
>
> - **Agent frameworks have an observability problem.** Most treat tracing as an afterthought. AgentLoom makes it automatic -- every step is traced with zero instrumentation code.
> - **Decorators beat YAML.** A `@step` decorator preserves your IDE experience (autocomplete, type-checking, jump-to-definition) while YAML configuration files destroy it.
> - **You can migrate in five minutes.** If you have an existing LangChain or CrewAI workflow, replacing it with AgentLoom is a matter of swapping class hierarchies for decorated functions.
> - **It ships at under 500 lines of core code.** Read it in an afternoon, contribute by evening, and never wonder what the framework is doing behind your back.

---

## By the Numbers

| | |
|---|---|
| **Under 500 lines** | of core code -- the entire engine fits in your head |
| **21 tests passing** | unit + integration, no mocks required |
| **Zero YAML files** | your workflow definition is just Python |
| **Automatic tracing** | on every step, every run, no opt-in needed |
| **Works with any LLM SDK** | OpenAI, Anthropic, Mistral, local models -- your choice |
| **Async-native** | swap `def` for `async def` and everything still works |

---

## The Observability Gap Nobody Talks About

Here is the dirty secret of agent frameworks in 2025: most of them treat observability as an afterthought. You get a `verbose=True` flag that dumps unstructured logs to stdout. You get a callback system that requires you to subclass three abstract classes. You get a dashboard that only works if you sign up for a hosted service.

**The best debugging tool is the one you never have to remember to turn on.**

But what you actually need when an agent workflow fails at 2 AM is simple. You need to know which step ran, what went in, what came out, how long it took, and whether it errored. You need that information in a structured format you can grep, export, and diff. You need it without adding a single line of instrumentation code to your business logic.

That is the core idea behind AgentLoom: observability is not a feature you opt into. It is a consequence of how you define your workflow. Every function you mark as a step is automatically traced -- inputs captured, outputs recorded, duration measured, errors logged -- with zero additional code from you.

## Building Your First Workflow, Step by Step

Let me walk through a real example. Say you are building a content analysis pipeline: fetch a web page, extract key information, and generate a summary. Here is what that looks like with AgentLoom.

First, install it:

```bash
pip install agentloom
```

Now define your steps. Each one is a plain Python function with a single decorator:

```python
import httpx
from agentloom import step, Workflow

@step(name="fetch_page")
def fetch_page(config: dict) -> str:
    """Fetch raw HTML from a URL."""
    url = config.get("url", "https://example.com")
    response = httpx.get(url, follow_redirects=True)
    response.raise_for_status()
    return response.text

@step(name="extract_info")
def extract_info(html: str) -> dict:
    """Pull out basic stats from the page content."""
    word_count = len(html.split())
    has_images = "<img" in html.lower()
    title_start = html.find("<title>")
    title_end = html.find("</title>")
    title = html[title_start + 7:title_end] if title_start > -1 else "Unknown"
    return {
        "title": title,
        "word_count": word_count,
        "has_images": has_images,
    }

@step(name="summarize")
def summarize(info: dict) -> str:
    """Produce a human-readable summary."""
    return (
        f"Page '{info['title']}' contains {info['word_count']} words. "
        f"Images: {'yes' if info['has_images'] else 'no'}."
    )
```

Notice something? These are just functions. No base classes. No method overrides. No special return types. The `@step` decorator wraps them transparently -- your function signature stays exactly the same, your type hints still work, your IDE still autocompletes, and you can unit test each step by calling it directly.

Now wire them into a workflow:

```python
workflow = Workflow(name="content-analysis")
workflow.add_step(fetch_page)
workflow.add_step(extract_info)
workflow.add_step(summarize)

trace = workflow.run({"url": "https://example.com"})
print(trace.summary())
```

That is it. Five lines to compose the workflow. One line to run it. The `run()` method executes each step sequentially, passing the output of one step as the input to the next, and returns an `ExecutionTrace` -- an immutable record of everything that happened.

## The Trace Output: What You Get for Free

Here is where things get interesting. That `ExecutionTrace` object is not a dumb log. It is a structured, serializable record. You can print a human-friendly summary:

```
Trace: 3 step(s), 3 succeeded, 0 failed, total 142.7 ms
```

But the real power comes from the `Tracer` class, which renders a Rich terminal tree. Feed your trace into it:

```python
from agentloom import Tracer

tracer = Tracer.from_execution_trace(trace, name="content-analysis")
tracer.print_trace()
```

And you get output like this in your terminal:

```
+---------------------------------------------------------+
|              AgentLoom Execution Trace                   |
+---------------------------------------------------------+
|                                                         |
| OK  content-analysis  [142.7 ms]                        |
| |                                                       |
| +-- OK  fetch_page  [128.3 ms]                          |
| |   input: {'url': 'https://example.com'}               |
| |   output: '<!doctype html>\n<html>\n<head>...'        |
| |   duration_ms: 128.3                                  |
| |                                                       |
| +-- OK  extract_info  [0.8 ms]                          |
| |   input: '<!doctype html>\n<html>\n<head>\n ...'      |
| |   output: {'title': 'Example Domain', 'word_c...'}    |
| |   duration_ms: 0.8                                    |
| |                                                       |
| +-- OK  summarize  [0.1 ms]                             |
|     input: {'title': 'Example Domain', 'word_co...'}    |
|     output: "Page 'Example Domain' contains 267 w..."   |
|     duration_ms: 0.1                                    |
|                                                         |
+---------------------------------------------------------+
```

Every step. Inputs. Outputs. Timing. Status. All captured automatically because you wrote `@step` instead of `def`. And you can export the whole thing as JSON for programmatic analysis:

```python
tracer.export_json("traces/content-analysis-2025-01-15.json")
```

Or run it from the CLI:

```bash
agentloom run workflow.py --trace-out trace.json
agentloom trace trace.json  # pretty-print a saved trace
```

You did not write a single line of logging code. You did not configure a callback handler. You did not sign up for a tracing service. It just works.

## Why Decorators Beat Configuration Files

I want to make a claim that might be controversial in the workflow-engine world: **decorator-based workflow definitions are strictly superior to YAML/JSON configuration files for developer workflows.**

Here is why.

**Your IDE understands decorators.** When your workflow is defined in Python with `@step` decorators, you get autocomplete on function arguments, type checking from mypy or Pyright, jump-to-definition, and inline documentation. When your workflow is defined in a YAML file, you get none of that. You are writing strings that reference Python objects, and the feedback loop for catching errors goes from milliseconds (red squiggly in your editor) to minutes (run it and watch it crash).

**Decorators compose with existing code.** Want to add a step that calls a third-party library? Decorate the function. Want to reuse a step across three workflows? Import the function. Want to conditionally include a step? Use an `if` statement. With YAML definitions, each of these requires learning a framework-specific mechanism.

**Testing is trivial.** A `@step`-decorated function is still a regular function. Call it in a pytest test with normal arguments and assert on the output. No workflow context to mock. No execution engine to instantiate. No framework to bootstrap.

```python
def test_extract_info():
    html = "<html><title>Test</title><body><img src='x.png'></body></html>"
    result = extract_info(html)
    assert result["title"] == "Test"
    assert result["has_images"] is True
```

AgentLoom also supports conditional branching through a simple convention. Return a dict with a `"__next__"` key to jump to a specific step by name:

```python
@step(name="classify")
def classify(data: dict) -> dict:
    if data["word_count"] > 1000:
        return {"__next__": "deep_analysis", "value": data}
    return {"__next__": "quick_summary", "value": data}
```

No routing DSL. No graph definition language. Just a return value.

## Error Handling That Actually Helps You Sleep at Night

Real workflows fail. APIs time out. Data comes in malformed. Models hallucinate. The question is not whether your workflow will break -- it is whether you will understand *why* it broke without spending an hour on it.

Here is what debugging a failed step looks like in a typical framework:

```
Traceback (most recent call last):
  File "/env/lib/python3.11/site-packages/bigframework/engine/runner.py", line 847, in _execute
    result = await self._invoke_chain(chain_config, **kwargs)
  File "/env/lib/python3.11/site-packages/bigframework/chains/base.py", line 234, in _invoke
    return self._call(inputs, run_manager=run_manager)
  File "/env/lib/python3.11/site-packages/bigframework/chains/sequential.py", line 92, in _call
    _input = self.chains[i](_input, callbacks=callbacks)
  File "/env/lib/python3.11/site-packages/bigframework/chains/base.py", line 312, in __call__
    raise e
  File "/env/lib/python3.11/site-packages/bigframework/chains/base.py", line 306, in __call__
    self._validate_outputs(outputs)
httpx.ReadTimeout: timed out
```

Twelve lines of stack trace. Eight of them are framework internals. You know *something* timed out, but which step? What was the input? Was it retried? How long did it wait? You are about to open six files you did not write to find out.

Now here is the same failure in AgentLoom. You get two knobs per step: `retries` and `on_error`.

```python
@step(name="call_api", retries=3, on_error="skip")
def call_api(query: str) -> dict:
    response = httpx.get(f"https://api.example.com/search?q={query}", timeout=5.0)
    response.raise_for_status()
    return response.json()
```

If `call_api` throws an exception, AgentLoom retries it up to 3 times. If all retries are exhausted, `on_error="skip"` means the step is recorded with a `SKIPPED` status and the workflow continues with `None` as the output. The alternative is `on_error="raise"`, which aborts the workflow and surfaces the exception.

Every retry attempt is logged. The final `StepResult` records the error message, the duration, and whether the step was retried, skipped, or failed. When you look at the trace, you see exactly what happened:

```
+-- ERR  call_api  [15234.2 ms]
    input: {'query': 'test'}
    output: None
    duration_ms: 15234.2
    error: 'ReadTimeout: timed out'
```

Five lines. The step name. The input that caused the failure. The total time spent (including retries). The exact error. No framework internals. No guessing.

**When your 2 AM pager goes off, the difference between a 12-line framework stack trace and a 5-line structured error record is the difference between fixing the bug and going back to sleep, or opening your laptop and losing an hour.**

No silent failures. No swallowed exceptions. No mystery about why your workflow produced garbage output.

Async steps work seamlessly too -- just define your function with `async def` and AgentLoom handles it:

```python
@step(name="fetch_async", retries=2, on_error="raise")
async def fetch_async(url: str) -> str:
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        return resp.text
```

Run async workflows with `await workflow.arun(initial_input)`. Same trace. Same error handling. Same decorators.

## The 5-Minute Migration: From LangChain to AgentLoom

If you are reading this and thinking "sounds nice, but I already have a LangChain workflow in production" -- here is how to migrate a typical chain without rewriting your logic.

**Before (LangChain):**

```python
from langchain.chains import SequentialChain, LLMChain
from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI

llm = OpenAI(temperature=0.7)

prompt1 = PromptTemplate(input_variables=["topic"], template="Research {topic} and list 5 key facts.")
chain1 = LLMChain(llm=llm, prompt=prompt1, output_key="facts")

prompt2 = PromptTemplate(input_variables=["facts"], template="Summarize these facts: {facts}")
chain2 = LLMChain(llm=llm, prompt=prompt2, output_key="summary")

pipeline = SequentialChain(
    chains=[chain1, chain2],
    input_variables=["topic"],
    output_variables=["summary"],
    verbose=True,
)

result = pipeline({"topic": "quantum computing"})
```

That is four imports from LangChain, two prompt templates, two chain objects, a pipeline object, and framework-specific concepts like `output_key` and `input_variables` that exist nowhere else in the Python ecosystem.

**After (AgentLoom):**

```python
import openai
from agentloom import step, Workflow, Tracer

client = openai.OpenAI()

@step(name="research")
def research(config: dict) -> str:
    """Ask the LLM to list key facts about a topic."""
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": f"Research {config['topic']} and list 5 key facts."}],
    )
    return resp.choices[0].message.content

@step(name="summarize")
def summarize(facts: str) -> str:
    """Ask the LLM to summarize the facts."""
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": f"Summarize these facts: {facts}"}],
    )
    return resp.choices[0].message.content

wf = Workflow(name="research-pipeline")
wf.add_step(research)
wf.add_step(summarize)
trace = wf.run({"topic": "quantum computing"})

tracer = Tracer.from_execution_trace(trace, name="research-pipeline")
tracer.print_trace()
```

Same outcome. But now you own the LLM call. You can swap OpenAI for Anthropic, or a local model, or a mock -- without changing AgentLoom code. Your prompt is a Python f-string, not a `PromptTemplate` object. And you get a full execution trace for free, without `verbose=True` dumping unstructured text to your console.

The pattern is always the same: take the logic that was *inside* the framework abstraction, put it *inside a plain function*, and add `@step`. That is the migration.

## How AgentLoom Compares

Let me be direct about where AgentLoom sits relative to the incumbents.

**vs. LangGraph:** LangGraph is powerful. It gives you stateful, cyclic graphs with persistence and streaming. If you need a complex multi-agent system with checkpointing and human-in-the-loop, LangGraph is the more mature choice. But if you need a linear or lightly-branching workflow with good observability, LangGraph's graph-definition overhead is significant. You are writing `StateGraph`, defining edges, compiling the graph, and managing state schemas -- all before your first step runs. AgentLoom gets you from zero to traced workflow in under a minute.

**vs. CrewAI:** CrewAI is built around the metaphor of agents with roles. It is great for multi-persona setups where you want agents to delegate tasks to each other. But that abstraction forces you into its worldview: agents, tasks, crews, processes. If your workflow is "run these four functions in order and tell me what happened," CrewAI's agent-role abstraction adds friction without adding value. AgentLoom has no opinions about your domain model. It traces functions.

**vs. Prefect:** Prefect is a battle-tested workflow orchestration platform. It has scheduling, retries, caching, a web UI, and a cloud service. If you are running data pipelines in production with SLAs, Prefect is the right tool. AgentLoom is not trying to replace Prefect. It is for the use case Prefect is too heavy for: prototyping agent workflows locally, debugging LLM chains during development, and getting observability into experimental code that is not ready for a production orchestrator.

## What's Missing (And Why I Shipped Without It)

AgentLoom is at version 0.1.0. I believe in being upfront about what it does not do yet -- and why none of these gaps should stop you from using it today.

**No parallel execution.** Steps run sequentially. Fan-out/fan-in is on the roadmap but not shipped. If you need to run ten API calls concurrently, you will need to handle that inside a single step for now. I shipped without it because sequential covers 80% of real agent workflows, and getting the tracing right matters more than premature concurrency primitives.

**No persistence or scheduling.** There is no built-in database, no cron-like scheduler, no retry-from-checkpoint. AgentLoom runs when you call `workflow.run()` and gives you back a trace. If you need durable execution, you should pair it with something like Celery or a proper orchestrator. I shipped without it because persistence is a deployment concern, not a workflow-definition concern.

**No web UI.** The trace viewer is terminal-only (Rich tree rendering) and JSON export. A browser-based trace viewer is planned but does not exist yet. I shipped without it because a good CLI trace beats a mediocre dashboard every time.

**No built-in LLM integration.** This is actually intentional. AgentLoom does not wrap OpenAI or Anthropic SDKs. You call whatever LLM library you want inside your `@step` functions. This means no vendor lock-in, but it also means AgentLoom does not provide prompt management, token counting, or model fallbacks. Those are your responsibility. I kept it this way because the moment a workflow framework starts wrapping LLM clients, it starts aging. SDKs move fast. Wrappers rot.

**Limited community.** This is a new project. The ecosystem of plugins, integrations, and community-contributed steps is exactly zero right now. That is a feature request, not a blocker.

## Try It

If any of this resonated -- if you have felt the weight of over-engineered agent frameworks, if you have wanted observability without ceremony, if you believe that Python decorators are a better workflow definition language than YAML -- give AgentLoom a try.

```bash
pip install agentloom
agentloom init -o my_workflow.py   # scaffold a starter workflow
agentloom run my_workflow.py       # run it and see the trace
```

Or build from source:

```python
from agentloom import step, tool, Workflow, Tracer

@step(name="hello")
def hello():
    return "Hello from AgentLoom"

@tool(name="greet")
def greet(name: str) -> str:
    return f"Hello, {name}"

wf = Workflow(name="quickstart")
wf.add_step(hello)
trace = wf.run()

tracer = Tracer.from_execution_trace(trace)
tracer.print_trace()
```

Twenty-one tests passing. Built with Click, Pydantic, structlog, Rich, and httpx. No LLM API keys required to get started.

The `@tool` decorator registers functions in a global registry that agent logic can discover at runtime -- useful when you want an LLM to select which tools to call without hardcoding the mapping.

The whole thing is under 500 lines of core code. Read it in an afternoon. Contribute by evening.

**We do not have a framework problem in AI. We have an abstraction addiction. The cure is not a better framework -- it is less framework.**

Star the repo. Open an issue. Tell me what you would build with it. The best frameworks are not the ones with the most features -- they are the ones that disappear and let you focus on the thing you actually came to build.

---

*AgentLoom is open source and MIT licensed. Built by someone who got tired of debugging frameworks instead of debugging ideas.*
