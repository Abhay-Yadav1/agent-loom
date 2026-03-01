"""Example AgentLoom workflow: Text Summarization Pipeline.

A 3-step workflow that demonstrates:
  1. Fetching / loading text
  2. Analysing the text (word count, sentence count)
  3. Producing a summary (first N sentences)

Run directly::

    python examples/summarize.py

Or via the CLI::

    agentloom run examples/summarize.py
"""

from __future__ import annotations

from agentloom import Workflow, step, Tracer


# ---------------------------------------------------------------------------
# Steps
# ---------------------------------------------------------------------------

@step(name="fetch_text")
def fetch_text() -> dict:
    """Simulate fetching a document. Returns sample text."""
    text = (
        "AgentLoom is a Python library for building observable agent workflows. "
        "It provides a clean decorator-based API that makes workflow definition intuitive. "
        "Every step execution is automatically traced with timing and input/output capture. "
        "The built-in CLI lets you run workflows and inspect traces from the terminal. "
        "Conditional branching allows steps to dynamically choose the next step to execute. "
        "Error handling supports configurable retry policies and graceful skip-on-failure. "
        "Rich console output renders execution trees with colour-coded status indicators. "
        "Traces can be exported to JSON for further analysis or visualisation. "
        "The tool decorator registers functions that agents can discover and invoke at runtime. "
        "AgentLoom requires no LLM dependency, making it fast to prototype and test locally."
    )
    return {"text": text}


@step(name="analyze")
def analyze(data: dict) -> dict:
    """Count words and sentences in the text."""
    text: str = data["text"]
    words = text.split()
    sentences = [s.strip() for s in text.split(".") if s.strip()]
    return {
        "text": text,
        "word_count": len(words),
        "sentence_count": len(sentences),
        "sentences": sentences,
    }


@step(name="summarize")
def summarize(data: dict) -> dict:
    """Extract the first N sentences as a summary."""
    n = min(3, data["sentence_count"])
    summary_sentences = data["sentences"][:n]
    summary = ". ".join(summary_sentences) + "."
    return {
        "summary": summary,
        "original_word_count": data["word_count"],
        "summary_word_count": len(summary.split()),
        "compression_ratio": round(len(summary.split()) / data["word_count"], 2),
    }


# ---------------------------------------------------------------------------
# Workflow assembly
# ---------------------------------------------------------------------------

workflow = Workflow(name="summarize-pipeline")
workflow.add_step(fetch_text)
workflow.add_step(analyze)
workflow.add_step(summarize)


# ---------------------------------------------------------------------------
# Direct execution
# ---------------------------------------------------------------------------

def main() -> None:
    """Run the workflow and display results."""
    trace = workflow.run()

    # Build a tracer from the execution trace and print it.
    tracer = Tracer.from_execution_trace(trace, name="summarize-pipeline")
    tracer.print_trace()

    # Print the summary.
    print("\n--- Trace Summary ---")
    print(trace.summary())

    # Show the final result.
    final = trace.results[-1]
    print("\n--- Summarization Result ---")
    if isinstance(final.output_data, dict):
        print(f"Summary:            {final.output_data.get('summary', 'N/A')}")
        print(f"Original words:     {final.output_data.get('original_word_count', 'N/A')}")
        print(f"Summary words:      {final.output_data.get('summary_word_count', 'N/A')}")
        print(f"Compression ratio:  {final.output_data.get('compression_ratio', 'N/A')}")


if __name__ == "__main__":
    main()
