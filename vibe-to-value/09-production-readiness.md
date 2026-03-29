# Domain 09: Production Readiness

*[From Vibe to Value — jjeffers.net]*

[← Domain 08 — Security](08-security.md) | [Conclusion →](10-conclusion.md)

---

Production readiness is the difference between a product that works and a product that works reliably. These items don't affect how the product behaves on a good day — they determine what happens on a bad one.

They are the systems and practices that let a small team operate a product with confidence: knowing when something breaks, knowing how to fix it, and knowing they can deploy a fix safely. Founders often deprioritize these because they feel like "DevOps overhead." They feel like overhead right up until 2am when the product is down and nobody knows why.

---

### No runbook or incident response plan

**`MEDIUM RISK`**

**Why it matters**

A runbook describes how to handle specific problems. An incident response plan describes how the team coordinates when something goes wrong. Without either, every incident is handled from scratch by whoever is available — under pressure, without a clear process.

**What goes wrong**

> Incidents take 3–5x longer to resolve. The same incidents recur because there's no documented fix. Users experience longer outages because diagnosis is slower.

**How to fix it**

Write a one-page runbook for your three most likely failure modes. For an AI product: LLM API unavailable, database connection failure, and abnormally high error rate.

**Technical detail**

Runbook template per failure mode:

```
## [Failure Mode Name]
Detection:   What alert fires, or what a user reports
Diagnosis:   Step 1: check X / Step 2: check Y / look for Z in logs
Resolution:
  - Fast mitigation: [action that stops the bleeding]
  - Root cause fix:  [action that prevents recurrence]
Escalation:  Who to contact if unresolved in 30 mins
Post-incident: Update this runbook with what you learned
```

---

### No SLO defined — team doesn't know what acceptable uptime means

**`MEDIUM RISK`**

**Why it matters**

A Service Level Objective (SLO) is your commitment to yourself and your users about how the product should perform. Without one, every outage is evaluated subjectively. An SLO gives you a concrete target that makes prioritization answerable.

**What goes wrong**

> The team has no shared definition of success for reliability. Enterprise customers ask for SLAs and you have nothing to base them on.

**How to fix it**

Define two numbers: your availability target (e.g. 99.5% uptime) and your latency target (e.g. 95% of requests complete in under 3 seconds).

**Technical detail**

```python
# Track request outcomes
metrics.increment('requests.total')
if response_time > 3.0:
    metrics.increment('requests.slow')
if error:
    metrics.increment('requests.error')

# Alert if SLO is at risk
availability = 1 - (error_count / total_requests)
if availability < 0.995:
    alert('Availability SLO at risk')
```

---

### Deployment is manual with no CI/CD pipeline

**`MEDIUM RISK`**

**Why it matters**

Manual deployments are slow, error-prone, and inconsistent. Every manual deployment involves human judgment about which files to copy, which environment variables to set, and which services to restart. Over time, production drifts from development and deployment becomes a source of incidents.

**What goes wrong**

> Deploying a hotfix during an incident requires careful manual work under pressure. The team dreads deploying.

**How to fix it**

Set up a minimal CI/CD pipeline: a GitHub Action that runs your tests on every push, and deploys to production automatically when tests pass on the main branch.

**Technical detail**

```yaml
# .github/workflows/deploy.yml
on:
  push:
    branches: [main]
jobs:
  test-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: pip install -r requirements.txt
      - run: pytest tests/
      - name: Deploy
        if: success()
        run: railway up  # or fly deploy, eb deploy, etc.
```

---

### Only one person knows how to deploy or has production access

**`HIGH RISK`**

**Why it matters**

Bus factor one is the most dangerous organizational risk in a small startup. If the one person who knows how to deploy is sick, traveling, or no longer with the company, the product cannot be updated. A critical security patch cannot be deployed.

**What goes wrong**

> A critical bug is discovered when the only person who can deploy is unreachable. A key person departure causes operational paralysis.

**How to fix it**

Document your deployment process completely. Ensure at least two people can perform every operational task. Store all credentials in a shared password manager with proper access controls.

**Technical detail**

Minimum operational knowledge documentation:

1. How to deploy a new version
2. How to roll back a deployment
3. How to access production logs
4. How to connect to the production database
5. How to rotate API keys if compromised
6. How to scale up infrastructure during traffic spikes

Store in a private wiki (Notion, Confluence). Review and update quarterly.

---

### No observability — can't tell if the product is working in real-time

**`HIGH RISK`**

**Why it matters**

Observability is the ability to understand the internal state of your system from its external outputs. Without it, you learn that your product is broken when users tell you. For AI systems, observability includes both traditional metrics (error rates, latency) and AI-specific signals (LLM call success rate, token usage, response quality).

**What goes wrong**

> A silent failure affects users for hours before anyone notices. You cannot answer 'is the product working right now?' without manually testing it.

**How to fix it**

Implement a minimal observability stack: structured logging, key metrics tracking, and a simple dashboard. Connect at least one alert that fires if the error rate spikes.

**Technical detail**

Four key observability signals for AI products:

1. **Request rate** — are users making requests?
2. **Error rate** — what percentage are failing?
3. **Latency** — how long do requests take?
4. **LLM success rate** — what percentage of LLM calls succeed?

Free stack: structured logs to CloudWatch/GCP Logging + Grafana Cloud dashboard. One-day setup, permanent operational visibility.

---

### Velocity has slowed — new features break existing ones

**`HIGH RISK`**

**Why it matters**

Slowing velocity is the most honest signal that technical debt has reached a critical threshold. When adding a new feature consistently breaks something else, the codebase has accumulated enough coupling, missing tests, and undocumented behavior that every change is risky.

**What goes wrong**

> Features take 3–5x longer to build than they should. Engineers are afraid to make changes. The product falls behind competitors who are moving faster.

**How to fix it**

Velocity collapse is a structural problem requiring structural solutions. Prioritize the HIGH risk items in the domains with the most flags, and address them systematically rather than continuing to patch symptoms.

**Technical detail**

Measure velocity objectively:

- **Cycle time:** PR open to merge (target: < 1 day for routine changes)
- **Rollback rate:** % of deployments requiring rollback within 24h
- **Bug escape rate:** bugs found by users vs. caught in review/staging

If cycle time > 3 days, rollback rate > 10%, or bug escape rate > 30%, you have a velocity crisis that warrants a dedicated remediation sprint before new feature development.

---


[← Domain 08 — Security](08-security.md) | [Conclusion →](10-conclusion.md)