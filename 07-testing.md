# Domain 07: Testing & Reliability

*[From Vibe to Value — jjeffers.net]*

[← Domain 06 — Blast Radius](06-blast-radius.md) | [Domain 08 — Security & Data →](08-security.md)

---

AI systems are harder to test than traditional software because their outputs are non-deterministic. You cannot write a test that checks 'the LLM returned exactly this string.' But that doesn't mean testing is impossible — it means testing looks different.

The goal of testing an AI system is not to verify exact outputs, but to verify behavior stays within acceptable bounds, quality doesn't regress, and the system fails gracefully when things go wrong. Most vibe-coded systems have none of this infrastructure, which means every change is a deployment into the unknown.

---

### No unit tests for any business logic functions

**`HIGH RISK`**

**Why it matters**

Business logic is the part of your system that doesn't involve the LLM — data validation, calculations, routing decisions, data transformation. These functions are fully deterministic and fully testable. Having no unit tests for them means that every change to business logic could break the system, and you won't know until a user tells you.

**What goes wrong**

> A refactor that changes a validation function breaks a downstream process silently. A calculation error in billing logic goes undetected. Simple regressions that a 30-second test would catch reach production.

**How to fix it**

Start with your most critical business logic functions — the ones where a bug would be most costly — and write unit tests for them. 20% coverage of the most important paths is dramatically better than zero.

**Technical detail**

Prioritize testing: input validation functions, data transformation pipelines, pricing and billing calculations, permission and authorization checks, prompt construction functions (pure string manipulation — fully testable). Use pytest (Python) or Jest (JS).

---

### No evaluation suite for LLM output quality

**`HIGH RISK`**

**Why it matters**

Evals are to AI systems what unit tests are to traditional software. They define what 'good' output looks like and give you a way to detect when a change (in your prompts, model, or configuration) degrades quality. Without evals, you are making changes to your AI system without any systematic way to know if those changes made things better or worse.

**What goes wrong**

> A prompt change that improves behavior for one use case silently degrades it for another. A model version upgrade changes behavior in ways you don't notice until users complain.

**How to fix it**

Build a minimal eval suite: 20–50 representative input/output pairs that capture your product's core behaviors. Define pass/fail criteria for each. Run these evals before every significant prompt or model change.

**Technical detail**

```python
EVALS = [
  {
    'input': 'Summarize this text in 3 bullet points: [text]',
    'criteria': [
      lambda r: len(r.split('\n')) >= 3,
      lambda r: len(r) < 500,
    ]
  }
]

def run_evals(evals, model):
    results = []
    for eval in evals:
        response = model.complete(eval['input'])
        passed = all(c(response) for c in eval['criteria'])
        results.append({'input': eval['input'], 'passed': passed})
    return results
```

---

### No staging environment — testing happens in production

**`HIGH RISK`**

**Why it matters**

Testing in production means that every bug discovery, every configuration mistake, and every integration failure happens in front of real users. For AI systems, this is especially problematic because prompt changes, model updates, and configuration changes can alter behavior for all users simultaneously.

**What goes wrong**

> Every deployment is a gamble. A broken prompt update reaches all users before it's caught. Developers are afraid to make changes because any mistake is immediately live.

**How to fix it**

Create a staging environment that mirrors production as closely as possible: a separate database, a separate API key with spending limits, and a separate deployment that internal team members test before changes go to production users.

**Technical detail**

Minimum staging requirements for AI systems: (1) Separate LLM API key with a $10/month spending cap, (2) Separate database with anonymized production data, (3) Feature flags to roll out changes to a percentage of users, (4) Separate monitoring and alerting.

---

### Changes tested manually by the person who wrote them

**`MEDIUM RISK`**

**Why it matters**

Manual testing by the author is the least reliable form of quality assurance. Authors know what they intended, so they unconsciously test the happy path. They don't test the edge cases they didn't think of. And their testing is not reproducible.

**What goes wrong**

> Bugs that another tester would immediately find reach production. The same manual tests are repeated by different people at different times, with different results.

**How to fix it**

Establish a minimum testing protocol: automated tests run on every PR, and a checklist of manual test cases that runs before merging.

**Technical detail**

```yaml
# .github/workflows/test.yml
on: [pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: pip install -r requirements.txt
      - run: pytest tests/ -v
```

---

### No alerting when error rates spike or latency degrades

**`MEDIUM RISK`**

**Why it matters**

Without monitoring and alerting, you find out about production problems when users tell you — which means the problem has already been affecting them for minutes or hours.

**What goes wrong**

> A silent failure affects users for hours before anyone notices. An LLM latency spike makes your product feel broken but generates no alert.

**How to fix it**

Implement basic application monitoring with alerts. At minimum: error rate alert, latency alert, and LLM cost alert.

**Technical detail**

Key metrics to track for AI systems:

- `llm_call_latency_ms` (p50, p95, p99)
- `llm_error_rate` (errors / total calls)
- `llm_cost_per_hour`
- `llm_tokens_per_request`

Free options: Sentry (error tracking), Grafana Cloud (metrics), or structured logs to CloudWatch with threshold alerts.

---


[← Domain 06 — Blast Radius](06-blast-radius.md) | [Domain 08 — Security & Data →](08-security.md)