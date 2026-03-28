# Domain 04: Context Management

*[From Vibe to Value — jjeffers.net]*

[← Domain 03 — LLM Integration](03-llm-integration.md) | [Domain 05 — Rules, Memory & Guardrails →](05-guardrails.md)

---

Context is the memory of your AI system. It's what tells the model who the user is, what they've asked before, and what constraints they're operating under. Managing context badly is the most common source of unexpected AI behavior in production: the model forgets what it was told, runs out of space and starts ignoring earlier instructions, or — most dangerously — carries sensitive information from one user's session into another's.

These are not edge cases. They are predictable failure modes with known solutions.

---

### Full conversation history passed to the model on every call

**`HIGH RISK`**

**Why it matters**

Context windows have hard limits. Sending the full conversation history on every API call is a pattern that works in demos (where conversations are short) and breaks in production (where they aren't). As context grows, costs increase linearly, latency increases, and eventually the request fails entirely when the context limit is exceeded.

**What goes wrong**

> Long user sessions become prohibitively expensive. API calls start failing for power users with long conversation histories. The model begins ignoring early instructions as the context fills — a behavior called 'lost in the middle' that is well-documented and predictable.

**How to fix it**

Implement a context management strategy. Options range from simple (keep only the last N turns) to sophisticated (summarize older turns into a compressed history). At minimum, track token count and truncate or summarize before hitting the limit.

**Technical detail**

```python
MAX_HISTORY_TOKENS = 4000

def trim_history(messages: list, max_tokens: int) -> list:
    total = count_tokens(messages)
    while total > max_tokens and len(messages) > 1:
        messages.pop(0)  # Remove oldest
        total = count_tokens(messages)
    return messages
```

For better quality, summarize removed turns: *"Earlier in this conversation, the user asked about X and was told Y."*

---

### Sensitive user data included in raw context without scrubbing

**`HIGH RISK`**

**Why it matters**

When user data flows directly into your LLM context — email addresses, names, account numbers, health information, financial data — that data is transmitted to a third-party service. This has GDPR implications, HIPAA implications (if health data), and general data minimization requirements under most privacy frameworks.

**What goes wrong**

> PII transmitted to LLM provider APIs without a Data Processing Agreement creates regulatory liability. A prompt injection attack that reveals context exposes other users' sensitive data.

**How to fix it**

Implement a context sanitization step before every LLM call. Replace sensitive values with tokens or placeholders, pass only what the model needs to complete its task, and reconstruct the real values after the response is returned.

**Technical detail**

```python
def sanitize_context(text: str, user_data: dict) -> tuple[str, dict]:
    tokens = {}
    result = text
    for key, value in user_data.items():
        if is_sensitive(key):  # email, ssn, dob, etc.
            token = f'[{key.upper()}_TOKEN]'
            tokens[token] = value
            result = result.replace(str(value), token)
    return result, tokens
```

---

### No strategy for context window overflow

**`HIGH RISK`**

**Why it matters**

When a request exceeds the context window limit, the API returns an error. If your code doesn't handle this error explicitly, it propagates as an unhandled exception. More insidiously, some implementations silently truncate from the beginning — dropping your system prompt and core instructions while retaining recent messages.

**What goes wrong**

> User-facing errors when conversations get long. Silent loss of system prompt instructions, causing the model to behave without its constraints. Inconsistent behavior that is nearly impossible to debug without understanding context window mechanics.

**How to fix it**

Count tokens before every API call. Define explicit behavior when you approach the limit — truncate, summarize, or split — and handle context overflow errors as a specific, expected code path.

**Technical detail**

```python
count = client.messages.count_tokens(
    model='claude-sonnet-4-20250514',
    messages=messages
)
if count.input_tokens > MAX_CONTEXT_TOKENS:
    messages = summarize_history(messages)
```

Always preserve: system prompt, most recent user message, any critical context. Summarize or drop: middle turns of conversation.

---

### No distinction between short-term and long-term memory

**`MEDIUM RISK`**

**Why it matters**

Not all context is equal. A user's preference for formal language is relevant forever. Their specific question from three turns ago may not be. Without distinguishing between ephemeral context (this conversation) and persistent context (this user's profile and history), you either send too much to the model or lose valuable user-specific information between sessions.

**What goes wrong**

> Users have to repeat themselves every session. Personalization is impossible. The model cannot build on previous interactions to improve its responses over time.

**How to fix it**

Implement two-tier context: **short-term** (this conversation's message history, in-memory) and **long-term** (user preferences, past decisions, relevant history, stored in a database and retrieved selectively). Load long-term context into the system prompt, not the conversation history.

**Technical detail**

```python
user_context = {
  'preferences': {'tone': 'formal', 'detail_level': 'high'},
  'history_summary': 'User is building a SaaS product...',
  'key_facts': ['uses PostgreSQL', 'team of 3', 'Series A']
}
```

Inject this at the top of the system prompt. Update it periodically by asking the LLM to extract and summarize key facts from the conversation.

---

### User session state not persisted across page reloads

**`MEDIUM RISK`**

**Why it matters**

If a user's context is only held in memory, any page reload, browser crash, or session expiry destroys it. They return to a blank slate. For products where conversation history is part of the value — research tools, drafting assistants, decision support systems — this is a significant usability failure.

**What goes wrong**

> Users lose work when they navigate away. Long conversations cannot be resumed. Support conversations cannot be reviewed.

**How to fix it**

Persist conversation state server-side, keyed to a user session ID. Retrieve it on session start.

**Technical detail**

```sql
CREATE TABLE sessions (
  session_id UUID PRIMARY KEY,
  user_id    UUID REFERENCES users(id),
  messages   JSONB NOT NULL DEFAULT '[]',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

Append new messages on each turn. Load and restore on session resume. Add a TTL or archival strategy for old sessions.

---


[← Domain 03 — LLM Integration](03-llm-integration.md) | [Domain 05 — Rules, Memory & Guardrails →](05-guardrails.md)