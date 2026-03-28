# Domain 01: Code Quality & Structure

*[From Vibe to Value — jjeffers.net]*

[← Introduction](00-introduction.md) | [Domain 02 — Version Control →](02-version-control.md)

---

Vibe-coded systems often start life as a single file, a Jupyter notebook, or a rapid prototype that "just worked." The problem isn't that they started messy — it's that they stayed messy. Code quality isn't about aesthetics; it's about your team's ability to reason about the system six months from now, when the person who wrote it has moved on or simply forgotten what they were thinking.

Every item in this domain is a structural risk that compounds over time.

---

### No consistent naming conventions across files or modules

**`MEDIUM RISK`**

**Why it matters**

Naming conventions are the first communication layer of a codebase. When a function is called `get_data` in one file, `fetchData` in another, and `load_records` in a third — all doing similar things — every engineer spends cognitive effort just parsing intent before they've written a single line. In AI-assisted codebases this is endemic, because each LLM session generates code in whatever style felt natural to the prompt.

**What goes wrong**

> Onboarding new engineers takes 2–3x longer. Code review becomes harder. Refactoring is error-prone because grep-based searches miss inconsistent names. Technical debt accumulates in every pull request.

**How to fix it**

Define a naming standard document — even a one-page README in your repo root covering: file naming (snake_case vs camelCase), function naming patterns, variable naming for AI-specific concepts (`prompt`, `context`, `response`, `completion`), and directory structure conventions. Then enforce it in code review. You don't need a linter on day one; you need a written agreement.

**Technical detail**

For Python projects: adopt PEP 8 as your baseline. For TypeScript/JS: adopt a shared ESLint config (Airbnb or Google style). Key AI-specific conventions to define: name your prompt variables `prompt_` prefixed, response objects `response_`, and any LLM client instances `llm_` or `model_`. This makes grep and search dramatically more effective.

---

### Functions exceed 100 lines with mixed responsibilities

**`MEDIUM RISK`**

**Why it matters**

A function that does more than one thing is a function that is hard to test, hard to debug, and impossible to safely change. LLMs are notorious for generating long, monolithic functions because they optimize for 'working code' rather than 'maintainable code.' The result is functions that validate input, call an LLM, parse the response, write to a database, and send an email — all in one 200-line block.

**What goes wrong**

> When something breaks (and it will), you cannot isolate the failure. You cannot write a unit test that covers just one behavior. Every change to the function risks breaking unrelated functionality.

**How to fix it**

Apply the Single Responsibility Principle (SRP): each function should do exactly one thing and do it well. Start by identifying your largest functions and extracting logical units into named helper functions. If you can't name a function clearly in 3–4 words, it's probably doing too much.

**Technical detail**

A useful heuristic: if a function has more than 2 levels of indentation or more than 3 distinct "phases" (validate, process, output), split it. For LLM-related code specifically, separate:

- `build_prompt()` — input preparation
- `call_llm()` — model invocation
- `parse_response()` — response parsing
- `save_to_db()`, `send_notification()` — side effects

Each of these becomes a distinct, testable function.

---

### Duplicated logic in 3+ places with no shared abstraction

**`HIGH RISK`**

**Why it matters**

Duplication is the original sin of software engineering, and AI code generation makes it worse. When you ask an LLM to 'add a feature similar to the one we built last week,' it often regenerates similar logic from scratch rather than referencing existing code. You end up with three slightly different implementations of the same validation logic — and when a bug exists in the pattern, you have to find and fix it in three places.

**What goes wrong**

> Bug fixes applied in one location silently leave the bug alive in duplicated copies. Behavior becomes inconsistent across features. The codebase grows faster than it should, increasing cognitive load for everyone.

**How to fix it**

Conduct a duplication audit: search for repeated patterns (especially prompt construction, API call wrappers, error handling blocks, and response parsing). Extract each into a shared utility module. A single source of truth means a single place to fix, improve, and test.

**Technical detail**

Tools like `jscpd` (JavaScript) or pylint's duplicate-code checker can identify duplication automatically. Run them as part of a periodic code health check. For LLM projects specifically, your **prompt-building logic** and **API retry logic** are the two most commonly duplicated patterns — prioritize abstracting these first.

---

### No clear separation between business logic, I/O, and AI calls

**`HIGH RISK`**

**Why it matters**

This is the architectural issue that kills AI startups' ability to scale. When your business logic (what the product does) is tangled with your I/O (reading/writing data) and your AI calls (calling an LLM), you cannot change any one of them without risking the others. Swapping your LLM provider, migrating your database, or changing your core logic all become major operations.

**What goes wrong**

> You cannot test your business logic without a live LLM connection. You cannot swap providers without rewriting core code. You cannot optimize performance without touching business rules. Every change is a risky, interconnected operation.

**How to fix it**

Adopt a layered architecture, even a simple one. Create distinct layers: a **service layer** (business logic), a **data layer** (database reads/writes), and an **AI layer** (all LLM calls). Each layer should only know about the layer directly below it. Your business logic should receive a string response — it should not know or care which model produced it.

**Technical detail**

A minimal pattern: define an `AIProvider` interface/protocol with a single method: `complete(prompt: str) -> str`. Your business logic calls this interface. Your actual implementation (`OpenAIProvider`, `AnthropicProvider`) lives separately. This means switching providers is a one-line config change, and you can mock the AI layer entirely in tests.

---

### Hard-coded values scattered throughout the code

**`HIGH RISK`**

**Why it matters**

Hard-coded values — API keys, model names, temperature settings, token limits, thresholds, URLs — are a security and maintainability disaster. They couple your code to specific configurations, make environment-specific deployments fragile, and often result in secrets being committed to version control.

**What goes wrong**

> API keys in source code are routinely discovered by automated scanners and exploited within hours of a public repository exposure. Model name changes require code deployments. Tuning a temperature setting means touching production code.

**How to fix it**

Move all configuration to environment variables and a centralized config module. Use `.env` files locally (never committed to git) and environment variable management (AWS Secrets Manager, Doppler, or similar) in production. Define all AI-specific settings — model name, temperature, max_tokens, timeout — in a single config file.

**Technical detail**

Create a `config.py` or `config.ts` that reads from environment variables with sensible defaults:

```python
MODEL_NAME  = os.getenv('LLM_MODEL', 'claude-sonnet-4-20250514')
MAX_TOKENS  = int(os.getenv('LLM_MAX_TOKENS', '1000'))
TEMPERATURE = float(os.getenv('LLM_TEMP', '0.7'))
```

This makes every AI parameter tuneable without a code deployment.

---

### No documented architecture diagram or system map

**`MEDIUM RISK`**

**Why it matters**

If the only person who understands how your system fits together is the person who built it, your system is a liability. Architecture diagrams aren't just documentation — they're a forcing function for clear thinking. Drawing the system often reveals assumptions, missing error paths, and circular dependencies that weren't obvious in the code.

**What goes wrong**

> Every new engineer or contractor spends weeks reverse-engineering what should take hours to explain. Incident response is slower because nobody has a mental model of how components interact. Technical decisions are made without understanding downstream consequences.

**How to fix it**

Create a single-page system diagram covering: your main components (frontend, backend, database, LLM API), how data flows between them, where AI calls happen, and where user data is stored or transmitted. It doesn't have to be perfect — a good-enough diagram updated quarterly is worth more than a perfect diagram that never gets made.

**Technical detail**

**Tools:** Mermaid (text-based, lives in your repo), Excalidraw (free, collaborative), or Lucidchart. For AI systems specifically, your diagram should show: prompt construction points, LLM API call locations, response parsing steps, memory/context stores, and any agent decision loops. This becomes your incident response map.

---


[← Introduction](00-introduction.md) | [Domain 02 — Version Control →](02-version-control.md)