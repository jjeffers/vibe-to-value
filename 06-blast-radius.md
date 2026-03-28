# Domain 06: Blast Radius Discipline

*[From Vibe to Value — jjeffers.net]*

[← Domain 05 — Guardrails](05-guardrails.md) | [Domain 07 — Testing & Reliability →](07-testing.md)

---

Blast radius is a concept from infrastructure engineering: when something goes wrong, how much damage can it do? AI agents are uniquely dangerous because they can take real-world actions at machine speed — writing to databases, calling APIs, sending emails, deleting files — and they do so based on probabilistic reasoning, not deterministic logic.

Blast radius discipline means designing your system so that when the AI does something wrong (not if), the damage is contained.

---

### AI agent can write to production databases without human approval

**`HIGH RISK`**

**Why it matters**

An AI agent that can directly modify production data is a loaded gun in a system that makes probabilistic decisions. The model might misunderstand the user's intent, confuse IDs, make incorrect inferences, or be manipulated through prompt injection. Any of these errors, applied directly to a production database, can cause immediate, irreversible data loss.

**What goes wrong**

> An agent deletes a user's account when asked to 'clean up old data.' A prompt injection attack triggers a malicious database write. Data is lost with no recovery path.

**How to fix it**

Implement a human-in-the-loop approval step for any write, update, or delete operation initiated by an AI agent. The agent proposes the action; a human confirms; only then does it execute.

**Technical detail**

```python
class AgentAction:
    action_type: str  # 'UPDATE', 'DELETE', 'CREATE'
    target: str       # Table and record ID
    payload: dict     # Proposed changes
    preview: str      # Human-readable description

def execute_with_approval(action: AgentAction, user_id: str):
    pending_actions.create(action, status='PENDING_APPROVAL')
    notify_user(user_id, action.preview)
    # Execute only after explicit confirmation
```

---

### No circuit-breaker — a looping agent runs until cost limit hit

**`HIGH RISK`**

**Why it matters**

Agentic systems that call themselves recursively, retry indefinitely, or get stuck in a decision loop can run for minutes or hours before anything stops them — accumulating API costs, consuming resources, and potentially taking repeated real-world actions.

**What goes wrong**

> A looping agent generates a $500 API bill overnight. Repeated actions (sending the same email 400 times) cause real-world damage. The system becomes unresponsive as resources are consumed.

**How to fix it**

Implement a circuit breaker on every agent loop: a hard cap on the number of iterations, a maximum elapsed time, and a maximum cost per session.

**Technical detail**

```python
MAX_ITERATIONS      = 10
MAX_ELAPSED_SECONDS = 60
MAX_COST_USD        = 0.50

def run_agent(task: str):
    start_time = time.time()
    total_cost = 0.0
    for iteration in range(MAX_ITERATIONS):
        if time.time() - start_time > MAX_ELAPSED_SECONDS:
            return AgentResult(status='TIMEOUT')
        if total_cost > MAX_COST_USD:
            return AgentResult(status='BUDGET_EXCEEDED')
        result = agent_step(task)
        total_cost += result.cost
        if result.is_complete:
            return result
```

---

### No dry-run or simulation mode before destructive operations

**`HIGH RISK`**

**Why it matters**

Before any irreversible operation — sending an email, deleting a record, making a payment, calling an external API — an agent should be able to simulate what it would do without actually doing it. This allows humans to verify intent before consequences occur.

**What goes wrong**

> An agent sends a test email to real customers. A destructive operation executes on production data when the developer intended to test it.

**How to fix it**

Build a dry-run mode into every agent that has side effects. In dry-run mode, the agent executes its full reasoning and planning, but replaces all side-effecting operations with logging calls.

**Technical detail**

```python
def send_email(to: str, subject: str, body: str, dry_run: bool = False):
    if dry_run:
        log.info(f'[DRY RUN] Would send email to {to}: {subject}')
        return DryRunResult(action='send_email', params={'to': to})
    return email_client.send(to, subject, body)
```

---

### A single agent affects all users, not just one session

**`HIGH RISK`**

**Why it matters**

If your agent operates on shared resources without user-level scoping, a mistake in one session can affect all sessions. Shared state, shared databases, shared external API accounts — any of these mean that an agent acting on behalf of one user can inadvertently affect others.

**What goes wrong**

> An agent writing to a shared database updates records belonging to a different user. Rate limits triggered by one session block all users.

**How to fix it**

Scope every agent operation to the current user's resources. Pass user context explicitly through every tool call. Use row-level security in your database.

**Technical detail**

```python
def database_write_tool(user_id: str, table: str, data: dict):
    # user_id injected by the system, never from agent output
    db.write(table, data, where={'user_id': user_id})

# The agent never decides user_id — it's injected from authenticated session
agent_tools = [partial(database_write_tool, user_id=current_user.id)]
```

---

### No rollback or undo capability for agent-initiated changes

**`HIGH RISK`**

**Why it matters**

When a human makes a mistake in your product, there's often an 'undo' path. When an AI agent makes a mistake at machine speed — potentially affecting many records or triggering many external actions — there is no undo unless you designed one in.

**What goes wrong**

> An agent error causes data corruption with no recovery path. The only response to a major agent error is manual intervention and data reconciliation.

**How to fix it**

Design for reversibility: use soft deletes instead of hard deletes, maintain an action log that can be replayed or reversed, and implement compensating transactions for external actions.

**Technical detail**

```sql
CREATE TABLE agent_actions (
  id           UUID PRIMARY KEY,
  user_id      UUID NOT NULL,
  action_type  VARCHAR(50),
  target_table VARCHAR(50),
  target_id    UUID,
  before_state JSONB,
  after_state  JSONB,
  created_at   TIMESTAMPTZ DEFAULT NOW(),
  rolled_back_at TIMESTAMPTZ
);
```

To rollback: restore `before_state` for the target record, mark the action `rolled_back_at`.

---

### External API calls not rate-limited or scoped by user

**`MEDIUM RISK`**

**Why it matters**

When your agent calls external APIs on behalf of users, those calls consume shared quotas. One user triggering excessive agent activity can exhaust your API quota for all users, or cause your API account to be rate-limited or suspended.

**What goes wrong**

> One heavy user's agent activity blocks all users from a feature. External API costs spike unpredictably.

**How to fix it**

Implement per-user rate limits on all external API calls made by agents. Track usage per `user_id` and reject requests that exceed the limit.

**Technical detail**

```python
def check_rate_limit(user_id: str, api_name: str, limit: int, window: int):
    key = f'rate:{user_id}:{api_name}'
    count = redis.incr(key)
    if count == 1:
        redis.expire(key, window)
    if count > limit:
        raise RateLimitExceeded(f'{api_name} limit reached')

# Usage:
check_rate_limit(user.id, 'external_search', limit=20, window=3600)
```

---


[← Domain 05 — Guardrails](05-guardrails.md) | [Domain 07 — Testing & Reliability →](07-testing.md)