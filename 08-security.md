# Domain 08: Security & Data Handling

*[From Vibe to Value — jjeffers.net]*

[← Domain 07 — Testing](07-testing.md) | [Domain 09 — Production Readiness →](09-production-readiness.md)

---

Security in AI systems has two layers: the traditional application security layer (authentication, authorization, secrets management) and the AI-specific layer (data transmitted to LLM providers, prompt injection, model output risks). Most vibe-coded systems are weak on both.

The traditional layer is often skipped because it feels like overhead when you're moving fast. The AI-specific layer is often unknown — developers don't realize that user data flowing into an LLM API is data leaving their security perimeter.

---

### API keys or secrets committed to the git repository

**`HIGH RISK`**

**Why it matters**

Secrets in git repositories are compromised within minutes of a repository becoming public — automated scanners run continuously looking for exposed credentials. Even in private repositories, secrets in git history are a significant risk: every person with repository access has access to the secrets, and they persist in history even after being removed from current code.

**What goes wrong**

> An LLM API key discovered by a scanner can be used to run up thousands of dollars in API charges before you notice. A database password in git history gives anyone with repo access full database access.

**How to fix it**

Never put secrets in code. Use environment variables loaded from `.env` files (never committed) in development, and a secrets manager in production. If a secret has already been committed: rotate it immediately, then remove it from history using `git filter-repo`.

**Technical detail**

Prevent future accidental commits:

1. Add `.env` to `.gitignore`
2. Install `git-secrets` or `gitleaks` as a pre-commit hook
3. Enable GitHub's secret scanning (free for public repos)

If secrets are already in history:
```bash
pip install git-filter-repo
git filter-repo --path-glob '**/*.env' --invert-paths
# Then force push and rotate all exposed credentials
```

---

### No authentication on internal API endpoints

**`HIGH RISK`**

**Why it matters**

Internal API endpoints are often left unprotected in the assumption that 'nobody knows they exist.' This is security through obscurity, and it fails the moment your API base URL is visible in browser network traffic — which it always is. An unauthenticated endpoint is a publicly accessible endpoint.

**What goes wrong**

> Anyone who finds your API base URL (trivial via browser DevTools) can call your endpoints directly, bypass your frontend, consume your LLM API quota, and access or modify other users' data.

**How to fix it**

Every API endpoint must require authentication. Use JWT tokens issued on login, verified on every request via middleware. Do not rely on the frontend to enforce access control — enforce it in the API.

**Technical detail**

```python
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer

security = HTTPBearer()

async def require_auth(token = Depends(security)):
    user = verify_jwt(token.credentials)
    if not user:
        raise HTTPException(status_code=401)
    return user

@app.post('/api/chat')
async def chat(request: ChatRequest, user = Depends(require_auth)):
    ...
```

---

### User PII sent to LLM APIs without data processing agreements

**`HIGH RISK`**

**Why it matters**

When personally identifiable information — names, email addresses, health data, financial information — flows into an LLM API call, that data leaves your system and enters the provider's. This is a data transfer with legal implications under GDPR, CCPA, HIPAA, and other regulations.

**What goes wrong**

> GDPR fines for unauthorized data transfers can reach 4% of annual global turnover. Enterprise customers will require a Data Processing Agreement before signing — and you may not be able to provide one if you're passing raw PII to providers.

**How to fix it**

First: audit what data flows into your LLM calls. Second: sign a DPA with your LLM provider. Third: minimize PII in LLM context by tokenizing or anonymizing where possible. Fourth: add data handling disclosure to your privacy policy.

**Technical detail**

```python
SENSITIVE_FIELDS = ['email', 'name', 'phone', 'ssn', 'dob', 'address']

def minimize_for_llm(data: dict) -> dict:
    return {
        k: '[REDACTED]' if k in SENSITIVE_FIELDS else v
        for k, v in data.items()
    }
```

---

### No input sanitization before data passed to LLM or stored in DB

**`HIGH RISK`**

**Why it matters**

Raw user input should never be trusted. In databases, unsanitized input leads to SQL injection. In LLM contexts, it enables prompt injection. In rendered output, it enables XSS.

**What goes wrong**

> A SQL injection attack through an unsanitized input field gives an attacker direct database access. An XSS attack through unsanitized LLM output executes malicious code in users' browsers.

**How to fix it**

Sanitize at every boundary: validate and sanitize user input before storing, use parameterized queries for database operations, escape LLM output before rendering in HTML.

**Technical detail**

Three sanitization layers:

```python
# 1. Input validation
user_input = bleach.clean(user_input)  # Strip HTML

# 2. Database — always parameterized
cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
# NEVER: f'SELECT * FROM users WHERE id = {user_id}'

# 3. Output rendering
import html
safe_output = html.escape(llm_response)
```

---

### No data retention or deletion policy for AI-processed data

**`MEDIUM RISK`**

**Why it matters**

AI systems accumulate data: conversation logs, embeddings, cached responses, user context. Without a retention policy, this data grows indefinitely. Under GDPR's 'right to erasure' and CCPA's 'right to delete,' users can request that their data be deleted — and you need a systematic way to honor those requests.

**What goes wrong**

> A user's data deletion request cannot be fulfilled because you don't know where their data is stored. Storage costs grow without bound.

**How to fix it**

Document every place user data is stored. Define a retention period for each. Build a deletion pipeline that removes user data from all stores when a deletion request is received.

**Technical detail**

```python
def delete_user_data(user_id: str):
    db.execute('DELETE FROM conversations WHERE user_id = %s', (user_id,))
    db.execute('UPDATE users SET email=NULL, name=NULL WHERE id = %s', (user_id,))
    vectordb.delete(where={'user_id': user_id})
    cache.delete_pattern(f'user:{user_id}:*')
    audit_log.write('USER_DATA_DELETED', user_id, datetime.now())
```

---

### Audit logs do not exist for sensitive operations

**`HIGH RISK`**

**Why it matters**

An audit log is a tamper-evident record of who did what, when. Without it, you cannot investigate security incidents, prove compliance to regulators, detect abuse patterns, or understand what happened when something goes wrong.

**What goes wrong**

> A security breach cannot be investigated because there's no record of what was accessed. Compliance audits fail because you cannot demonstrate who accessed what data.

**How to fix it**

Implement an append-only audit log for: user authentication events, data access, data modification and deletion, AI agent actions, and administrative operations.

**Technical detail**

```sql
CREATE TABLE audit_log (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  timestamp     TIMESTAMPTZ DEFAULT NOW(),
  user_id       UUID,
  action        VARCHAR(100) NOT NULL,
  resource_type VARCHAR(50),
  resource_id   UUID,
  ip_address    INET,
  result        VARCHAR(20),
  metadata      JSONB
);

-- Make append-only
REVOKE UPDATE, DELETE ON audit_log FROM application_role;
```

---


[← Domain 07 — Testing](07-testing.md) | [Domain 09 — Production Readiness →](09-production-readiness.md)