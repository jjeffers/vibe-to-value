# Domain 03: AI & LLM Integration Patterns

*[From Vibe to Value — jjeffers.net]*

[← Domain 02 — Version Control](02-version-control.md) | [Domain 04 — Context Management →](04-context-management.md)

---

Calling an LLM API looks deceptively simple: send a string, get a string back. But production AI integration is a discipline of its own. LLMs are non-deterministic, rate-limited, expensive, occasionally down, and capable of returning outputs that break downstream code in ways traditional APIs never would.

Most vibe-coded integrations treat LLM calls like database queries — synchronous, reliable, cheap, and predictable. They are none of these things. The patterns in this domain are what separate a demo from a product.

---

### LLM calls made with no retry, timeout, or fallback logic

**`HIGH RISK`**

**Why it matters**

LLM APIs fail. They rate-limit, they time out, they return 500 errors, and they occasionally go down for maintenance. A production integration that makes a single API call with no error handling will fail for real users at the worst possible moment. The failure mode is often silent — the call hangs indefinitely, blocking the user's request.

**What goes wrong**

> Users see spinning loaders that never resolve. Features silently break when the LLM provider has an outage. Rate limit errors during traffic spikes take down the entire feature rather than gracefully degrading.

**How to fix it**

Wrap every LLM call in: a **timeout** (set a maximum wait time), a **retry with exponential backoff** (retry on transient failures, wait longer between each retry), and a **fallback behavior** (define what the product does when the AI is unavailable — a cached response, a simpler rule-based answer, or a clear error message).

**Technical detail**

Python pattern using `tenacity`:

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3),
       wait=wait_exponential(multiplier=1, min=2, max=10))
def call_llm(prompt: str) -> str:
    response = client.messages.create(...)
    return response.content[0].text
```

Set your HTTP timeout to 30 seconds maximum. Define a `FALLBACK_RESPONSE` constant for when all retries are exhausted.

---

### Model outputs trusted and used directly with no validation layer

**`HIGH RISK`**

**Why it matters**

LLMs hallucinate. They return malformed JSON when asked for JSON. They make up field names. They include markdown formatting when you asked for plain text. They occasionally return empty strings or truncated responses. Trusting raw LLM output as reliable structured data is a category error — it's a probabilistic system being used as a deterministic one.

**What goes wrong**

> A `JSON.parse()` call on malformed LLM output throws an unhandled exception in production. A hallucinated URL gets displayed to users as a real link. A truncated response gets saved to the database as the complete result.

**How to fix it**

Build a validation layer between every LLM response and your application logic. At minimum: check that the response is non-empty, validate structure if you expect JSON, sanitize before rendering to users, and define explicit fallback behavior for validation failures.

**Technical detail**

```python
import json
from jsonschema import validate, ValidationError

def parse_llm_json(raw: str, schema: dict) -> dict:
    try:
        data = json.loads(raw.strip())
        validate(instance=data, schema=schema)
        return data
    except (json.JSONDecodeError, ValidationError) as e:
        log.error(f'LLM output invalid: {e}, raw: {raw[:200]}')
        return DEFAULT_RESPONSE
```

Alternatively, use structured output APIs (Anthropic, OpenAI) that constrain the model's output format.

---

### Prompts are hard-coded with no versioning

**`MEDIUM RISK`**

**Why it matters**

Your prompts are product logic. They define how your AI behaves, what it knows about your domain, and what constraints it operates under. Treating them as throwaway strings rather than versioned artifacts means you cannot track what changed, cannot roll back a prompt regression, and cannot run systematic experiments.

**What goes wrong**

> A prompt change that degrades output quality ships silently. You cannot identify when a quality issue started. A/B testing is impossible. The best prompt you ever had is lost because you overwrote it.

**How to fix it**

Store prompts as versioned files in your repository — not as string literals in your code. Give each prompt a name, a version, and a changelog entry. Load them at runtime from your config or a `/prompts` directory.

**Technical detail**

Create a `/prompts` directory with files like `system_v1.txt`, `classification_v3.txt`. Load them:

```python
def load_prompt(name: str) -> str:
    path = Path('prompts') / f'{name}.txt'
    return path.read_text()
```

For teams doing significant prompt engineering, tools like Langsmith, PromptLayer, or even a simple Google Sheet with version history provide structured prompt management with evaluation tracking.

---

### No logging of LLM inputs/outputs

**`HIGH RISK`**

**Why it matters**

Without logging, you are operating blind. When a user reports that the AI gave them a wrong or harmful answer, you have no way to reproduce it, understand what caused it, or prove that it happened. Logs are your audit trail, your debugging tool, and your evidence base for improving the system.

**What goes wrong**

> User complaints about AI behavior cannot be investigated. Regressions after prompt changes cannot be diagnosed. Compliance requirements for AI systems (increasingly common in enterprise and regulated industries) cannot be met without audit logs.

**How to fix it**

Log every LLM interaction: the full prompt (or a hash of it), the model and parameters used, the response (or first 500 characters), the latency, the token count, and the user session ID. Store logs in a structured format (JSON) that can be queried.

**Technical detail**

Minimum log structure:

```json
{
  "timestamp": "2025-06-01T14:23:11Z",
  "session_id": "usr_abc123",
  "model": "claude-sonnet-4-20250514",
  "prompt_hash": "sha256:...",
  "input_tokens": 420,
  "output_tokens": 183,
  "latency_ms": 1840,
  "response_preview": "Here are the three options..."
}
```

Do **not** log full user data or PII in prompt content — log a session ID that maps to user data stored separately.

---

### Token usage and cost not monitored or capped

**`MEDIUM RISK`**

**Why it matters**

LLM costs scale directly with usage, and usage patterns are unpredictable. A single runaway agent loop, an unexpectedly large context window, or a traffic spike can result in a bill thousands of dollars higher than expected — with no warning until the invoice arrives.

**What goes wrong**

> Unexpected cost spikes with no visibility into their cause. No ability to set per-user or per-session cost limits. A single misbehaving user or process can consume the majority of your monthly budget.

**How to fix it**

Implement token tracking on every LLM call. Set hard limits at the API key level (most providers support spending limits) and soft limits in your application (warn when a session exceeds a threshold, hard-stop if it exceeds another).

**Technical detail**

```python
COST_PER_1K_INPUT  = 0.003  # Update per your model's pricing
COST_PER_1K_OUTPUT = 0.015

cost = (input_tokens/1000  * COST_PER_1K_INPUT) + \
       (output_tokens/1000 * COST_PER_1K_OUTPUT)
```

Store cumulative cost per `user_id` and trigger alerts when daily spend exceeds a threshold. Set API-level monthly spending caps as a hard backstop.

---

### Single model provider with no contingency

**`MEDIUM RISK`**

**Why it matters**

Every major LLM provider has had outages. When your product's core functionality depends on a single external API with no fallback, their downtime is your downtime — regardless of your own system's health.

**What goes wrong**

> LLM provider outage = complete feature unavailability for all users. No ability to maintain service level agreements. No leverage in pricing negotiations.

**How to fix it**

Design your AI layer around an interface rather than a specific provider. At minimum, define a fallback behavior for provider unavailability. Ideally, implement a secondary provider that can be activated when the primary is down.

**Technical detail**

```python
class LLMProvider(Protocol):
    def complete(self, prompt: str, **kwargs) -> str: ...

class AnthropicProvider(LLMProvider): ...
class OpenAIProvider(LLMProvider): ...

def get_provider(primary='anthropic') -> LLMProvider:
    try:
        return AnthropicProvider()
    except ProviderUnavailable:
        return OpenAIProvider()  # fallback
```

---


[← Domain 02 — Version Control](02-version-control.md) | [Domain 04 — Context Management →](04-context-management.md)