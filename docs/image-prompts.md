# AgentLoom Blog Post — Gemini Image Generation Prompts

> Style guidelines applied to ALL images below:
> - Modern, clean, minimalist tech aesthetic
> - Dark theme: deep teal `#0d2137` as the primary background, cyan/turquoise `#00bcd4` as the accent color, white `#ffffff` for text and foreground elements
> - Professional enough for Medium but eye-catching enough to stop scrolling
> - Flat design / isometric illustration style — absolutely no stock-photo feel
> - Weaving, thread, and loom visual metaphors woven throughout the set
> - Consistent visual language, color palette, and icon style across every image so they feel like a cohesive series

---

### Image 1: Hero / Cover Image
**Filename:** `agentloom-blog-hero.png`
**Dimensions:** 1200x630
**Prompt:**
Create a wide 1200x630 hero banner illustration in a flat, minimalist, dark-themed tech style. The background is a deep teal (#0d2137) gradient that subtly lightens toward the center. In the center of the image, a stylized weaving loom made of thin, glowing cyan (#00bcd4) threads stretches horizontally. Each thread represents a workflow step; three threads pass through the loom from left to right, each labeled with a small glowing "@step" tag where it enters the loom. On the left side of the loom, show a tangle of messy, dull gray YAML brackets, curly braces, and configuration keywords dissolving into loose fibers. On the right side, the threads emerge as a clean, orderly woven fabric with a subtle hexagonal pattern, symbolizing structured, observable output. Below the loom, a single line of stylized Python code reads `@step(name="magic")` in a monospaced font rendered in white with the decorator symbol highlighted in cyan. At the top, in large, clean sans-serif white text, display the title "AgentLoom" with a subtle glow. Small floating particles of cyan light drift around the loom. No photorealism, no people, no stock imagery. Pure flat vector illustration aesthetic with soft glows and clean lines.

**Alt Text:** A wide banner illustration showing a stylized digital loom weaving glowing cyan threads labeled with @step decorators. On the left, tangled YAML configuration dissolves into loose fibers; on the right, the threads emerge as clean, structured fabric, representing AgentLoom transforming messy framework complexity into simple, observable workflows.

**Placement:** Top of the blog post, directly below the title "I'm Mass-Deleting Agent Frameworks From My Projects."

---

### Image 2: Framework Fatigue
**Filename:** `agentloom-blog-framework-fatigue.png`
**Dimensions:** 800x500
**Prompt:**
Create an 800x500 illustration in a flat, minimalist, dark-themed tech style on a deep teal (#0d2137) background. Show five rectangular cards or boxes arranged in a slight arc or scattered grid. Each box is a dull, desaturated gray with rounded corners, and each contains a generic framework logo placeholder — abstract shapes like interlocking gears, chain links, a brain icon, a flow-chart symbol, and a puzzle piece — all rendered in muted gray tones. Over each of the five boxes, draw a bold, hand-drawn-style "X" in a soft red (#e74c3c) with a slight chalk-like texture. Below and slightly in front of the five crossed-out boxes, place a single, clean, glowing card that is smaller and more refined, rendered in white with a cyan (#00bcd4) border glow. On this card, display a clean "@step" decorator symbol in monospaced white font. Thin glowing cyan threads radiate outward from this single card, suggesting it replaces all five. Add the text "5 frameworks in. 1 decorator out." in small white sans-serif text at the bottom. No photorealism. Flat vector style with soft shadows and clean iconography.

**Alt Text:** Five gray framework boxes, each crossed out with a red X, arranged behind a single glowing card displaying the @step decorator symbol in cyan, illustrating the replacement of five complex frameworks with one simple decorator-based approach.

**Placement:** After the opening paragraphs, near the line "Five frameworks in eighteen months. Every one promised to simplify my workflow."

---

### Image 3: Observability Gap
**Filename:** `agentloom-blog-observability-gap.png`
**Dimensions:** 800x500
**Prompt:**
Create an 800x500 split-screen illustration in a flat, minimalist, dark-themed tech style. The background is deep teal (#0d2137). Divide the image vertically down the center with a thin dashed white line. On the LEFT side, labeled "verbose=True" in small gray monospaced text at the top, show a chaotic terminal window with a dark background. Inside it, render several lines of unstructured, overlapping log text in dim green and yellow monospaced font — lines like "DEBUG: chain invoked...", "INFO: calling LLM...", "WARNING: retrying...", randomly scattered and overlapping, some partially cut off, creating a visual sense of messy, overwhelming stdout noise. A small frowning face icon or a confused question mark floats near the terminal. On the RIGHT side, labeled "AgentLoom Trace" in small cyan monospaced text at the top, show a clean, structured Rich-style tree output rendered in a dark terminal window. The tree has a root node "content-analysis" with three child nodes, each prefixed with "OK" in green and showing step names like "fetch_page", "extract_info", "summarize" with timing values in cyan. The tree uses clean Unicode box-drawing characters. Lines are well-spaced and organized. A small checkmark icon or a satisfied indicator appears near this terminal. The contrast between chaos and order should be immediately visually striking. No photorealism. Flat vector style.

**Alt Text:** A split-screen comparison: the left side shows a messy, chaotic terminal filled with unstructured verbose logs, while the right side shows a clean, organized AgentLoom trace tree with structured step names, OK statuses, and timing information, illustrating the observability gap.

**Placement:** In the section "The Observability Gap Nobody Talks About," after the paragraph describing the problem.

---

### Image 4: Workflow Building
**Filename:** `agentloom-blog-workflow-building.png`
**Dimensions:** 800x500
**Prompt:**
Create an 800x500 illustration in a flat, minimalist, dark-themed tech style on a deep teal (#0d2137) background. Show three rounded rectangular function cards arranged horizontally from left to right, connected by flowing, glowing cyan (#00bcd4) threads or arrows that curve gently between them, resembling threads being woven through a loom. Each card has a dark (#1a3a4a) background with a subtle cyan border glow. The first card is labeled "@step: fetch_page" with a small globe/download icon, the second "@step: extract_info" with a small magnifying glass icon, and the third "@step: summarize" with a small document/text icon. All text is in white monospaced font. Between the cards, along the connecting threads, show small data-flow indicators: a small "HTML" label between card 1 and 2, and a small "dict" label between card 2 and 3. Below the three cards, a thin horizontal line represents the Workflow container, labeled "Workflow('content-analysis')" in small white text. At the start of the thread (before card 1), show a small input icon with "{url: ...}", and at the end (after card 3), show a small output icon with "ExecutionTrace". The threads should have a subtle weaving texture or pattern where they overlap with the cards. No photorealism. Clean flat vector style with soft glows.

**Alt Text:** Three function cards labeled fetch_page, extract_info, and summarize, each prefixed with @step, connected by flowing cyan threads showing data types flowing between them, all contained within a Workflow container — illustrating how AgentLoom builds pipelines from decorated functions.

**Placement:** In the section "Building Your First Workflow, Step by Step," before or after the code example defining the three steps.

---

### Image 5: Trace Output
**Filename:** `agentloom-blog-trace-output.png`
**Dimensions:** 800x500
**Prompt:**
Create an 800x500 illustration in a flat, minimalist, dark-themed tech style. Show a stylized terminal window with a dark (#0a1628) background, a thin top bar with three colored dots (red, yellow, green) in the top-left corner suggesting a macOS-style terminal chrome. Inside the terminal, render a Rich-style tree trace output using monospaced font. The root node reads "OK  content-analysis  [142.7 ms]" with "OK" rendered in bright green (#4caf50) and the timing in cyan (#00bcd4). Three child nodes branch off with Unicode tree-drawing characters (vertical bars and corner connectors). Child 1: "OK  fetch_page  [128.3 ms]" with sub-lines showing "input: {'url': 'https://example.com'}" and "duration_ms: 128.3" in dim white. Child 2: "OK  extract_info  [0.8 ms]" with sub-lines showing "input:" and "output: {'title': 'Example Domain'...}" in dim white. Child 3: "OK  summarize  [0.1 ms]" with sub-lines showing truncated input/output. Each "OK" badge is green, each timing value is cyan, step names are white, and metadata lines are a dimmer gray-white. The terminal window should float slightly above the deep teal (#0d2137) background with a subtle drop shadow. Add a very faint loom/thread pattern in the background behind the terminal. No photorealism. Clean flat vector illustration.

**Alt Text:** A stylized terminal window displaying an AgentLoom execution trace tree with three steps — fetch_page, extract_info, and summarize — each showing green OK status badges, cyan timing values, and captured input/output data in a clean, structured Rich tree format.

**Placement:** In the section "The Trace Output: What You Get for Free," adjacent to or replacing the ASCII trace example.

---

### Image 6: Decorators vs YAML
**Filename:** `agentloom-blog-decorators-vs-yaml.png`
**Dimensions:** 800x500
**Prompt:**
Create an 800x500 split-screen illustration in a flat, minimalist, dark-themed tech style on a deep teal (#0d2137) background. Divide the image into left and right halves with a bold "VS" in the center, rendered in white with a subtle cyan (#00bcd4) glow. On the LEFT side, labeled "YAML Configuration" in small gray text at the top, show a tall, intimidating stack of four overlapping file icons or document rectangles in dull gray. Each file has visible but illegible lines of YAML-like text (key-colon-value patterns, indentation, dashes for lists) rendered in dim gray monospaced font. The stack looks heavy, cluttered, and oppressive. Small icons around it suggest lost IDE features: a crossed-out magnifying glass (no jump-to-definition), a crossed-out lightbulb (no autocomplete), a crossed-out checkmark (no type checking). On the RIGHT side, labeled "Python + @step" in small cyan text at the top, show a single clean code editor panel with a dark background and syntax-highlighted Python code. The code shows a function definition with `@step(name="process")` as the decorator in cyan, `def process(data: dict) -> str:` in white, and a return statement. The code is clean, short, and readable. Small icons around it suggest preserved IDE features: a glowing magnifying glass, a glowing lightbulb, a glowing checkmark — all in cyan. Thin decorative threads connect the right panel to a small loom icon in the bottom-right corner. No photorealism. Flat vector style.

**Alt Text:** A split comparison: the left side shows a heavy stack of four YAML configuration files with icons indicating lost IDE features, while the right side shows a single clean Python function with the @step decorator and icons confirming preserved autocomplete, type checking, and jump-to-definition capabilities.

**Placement:** In the section "Why Decorators Beat Configuration Files," near the top of that section.

---

### Image 7: 5-Minute Migration
**Filename:** `agentloom-blog-migration.png`
**Dimensions:** 800x500
**Prompt:**
Create an 800x500 illustration in a flat, minimalist, dark-themed tech style on a deep teal (#0d2137) background. Show a visual transformation flowing from left to right. On the LEFT side, display a code block or editor panel with a slightly reddish-gray tint (#2a1a1a background), showing a dense, tall block of stylized LangChain-style Python code — visible lines suggesting multiple imports, PromptTemplate objects, LLMChain instantiations, a SequentialChain constructor with many parameters. A small label reads "LangChain — 15+ lines" in dim red-ish text. A line count indicator on the side shows roughly 15-20 lines. In the CENTER, show a large, elegant arrow or transformation symbol made of braided/woven cyan (#00bcd4) threads, flowing from left to right, with a small clock icon and "5 min" text below it. On the RIGHT side, display a code block or editor panel with a slightly greenish-teal tint (#0d2137 background with cyan border), showing a compact, clean block of AgentLoom-style Python code — fewer lines, visible @step decorators, a short Workflow setup. A small label reads "AgentLoom — 10 lines" in cyan text. A line count indicator shows roughly 10 lines. The right panel should feel lighter, more spacious, and more inviting than the left. The woven arrow in the center reinforces the loom metaphor. No photorealism. Clean flat vector illustration.

**Alt Text:** A before-and-after migration illustration: a dense 15-plus-line LangChain code block on the left transforms through a woven arrow labeled 5 minutes into a compact 10-line AgentLoom code block on the right, showing how migration simplifies the codebase.

**Placement:** In the section "The 5-Minute Migration: From LangChain to AgentLoom," at the beginning of that section.

---

### Image 8: Error Handling
**Filename:** `agentloom-blog-error-handling.png`
**Dimensions:** 800x500
**Prompt:**
Create an 800x500 illustration in a flat, minimalist, dark-themed tech style on a deep teal (#0d2137) background. Show a vertical timeline or sequence flowing from top to bottom, representing retry attempts for a failing step. At the top, display a step card labeled "@step: call_api" with "retries=3" shown as a small badge. Below it, show three attempt indicators arranged vertically, connected by a dotted cyan line. Attempt 1: a small circular node with a red (#e74c3c) "X" and the label "Attempt 1 — ReadTimeout [5002 ms]" in dim red-tinted text. Attempt 2: another red "X" node with "Attempt 2 — ReadTimeout [5008 ms]". Attempt 3: another red "X" node with "Attempt 3 — ReadTimeout [5011 ms]". Below the three failed attempts, show a result card or terminal snippet that is clean and structured, displaying the AgentLoom error trace: "ERR  call_api  [15234.2 ms]" with "ERR" in red, the timing in cyan, and sub-lines showing "input:", "output: None", "error: 'ReadTimeout: timed out'" in a neat, monospaced format. To the right of this clean error card, show a small contrasting ghost/shadow of a long, messy 12-line stack trace that is faded, blurred, and crossed out — representing the framework-heavy alternative that AgentLoom replaces. Thin cyan threads connect the attempt nodes like a woven safety net. No photorealism. Clean flat vector illustration with clear visual hierarchy.

**Alt Text:** A vertical timeline showing three retry attempts for a failing call_api step, each marked with a red X and timeout duration, culminating in a clean structured error trace showing ERR status, total timing, and the exact error message — contrasted against a faded, crossed-out long stack trace in the background.

**Placement:** In the section "Error Handling That Actually Helps You Sleep at Night," after the paragraph introducing the retry and on_error mechanisms.

---

## Usage Notes

- **Generate each image individually** using Gemini's image generation API (Imagen 3 or the latest available model).
- **Post-processing:** After generation, consider adding the AgentLoom logotype or a small watermark in the bottom-right corner of each image for brand consistency.
- **File format:** Export as PNG with transparency where the background allows, or with the solid deep teal background baked in.
- **Responsive sizing:** The hero image (1200x630) is optimized for Open Graph / social sharing. Section images (800x500) are optimized for inline blog display on Medium or similar platforms.
- **Accessibility:** Use the provided alt text for each image in the blog post HTML/Markdown `![alt text](filename)` tags.
- **Consistency check:** After generating all eight images, review them side by side to ensure the color palette, icon style, and overall aesthetic feel cohesive as a set. Regenerate any outliers.
