# Domain 02: Version Control & Change Management

*[From Vibe to Value — jjeffers.net]*

[← Domain 01 — Code Quality](01-code-quality.md) | [Domain 03 — AI & LLM Integration →](03-llm-integration.md)

---

Version control isn't just about tracking changes — it's your safety net, your audit trail, and your collaboration framework. In vibe-coded projects, it's often an afterthought: code gets committed in bulk with vague messages, directly to the main branch, with no process for reviewing what's actually going into production.

When something breaks (not if), the ability to trace exactly what changed, when, and why is the difference between a 20-minute fix and a 3-day incident.

---

### No branching strategy — all work goes directly to main

**`HIGH RISK`**

**Why it matters**

Committing directly to main means every work-in-progress change is immediately the production version of your code. There is no review gate, no staging checkpoint, and no safe place to develop features without risking live user-facing behavior. In AI systems, where a single prompt change can dramatically alter product behavior, this is especially dangerous.

**What goes wrong**

> A developer testing a new prompt template pushes to main and breaks the product for all users. There is no clean 'last known good' state to roll back to. Multiple developers working simultaneously create conflicts that overwrite each other's changes.

**How to fix it**

Adopt a simple branching model immediately. The minimum viable approach: `main` is always production-ready; all development happens on feature branches (`feature/your-description`); changes merge to `main` only via pull request. This single change adds a review gate and a rollback point with almost no overhead.

**Technical detail**

**GitHub Flow** is the simplest model that works: branch from main, commit your changes, open a pull request, review and merge. For a solo developer or small team, even self-review before merge adds meaningful protection. Configure branch protection rules in GitHub/GitLab: require at least one approval before merging to main, and block direct pushes.

---

### AI-generated code deployed without automated pipeline verification

**`HIGH RISK`**

**Why it matters**

LLM-generated code is plausible by design — it looks correct, follows patterns, and frequently passes casual human inspection. But it can contain subtle bugs, security vulnerabilities, or logic that works for the happy path but fails on edge cases. Expecting a human to manually review every single line of AI-generated code is an ideal standard, but fundamentally broken and impractical at scale. The focus must shift from manual inspection to **automated verification**.

**What goes wrong**

> Security vulnerabilities enter production undetected. Codebase quality degrades because a human reviewer rubber-stamped a massive AI-generated PR they didn't have time to actually read. Over time, the system contains large sections lacking both tests and human comprehension.

**How to fix it**

Implement a "Verify by System, Review by Exception" methodology. Rely heavily on Static Application Security Testing (SAST), strict linters, and dependency scanners in your CI/CD pipeline to catch clumsy, inefficient, or unsafe code automatically. Implement an AI-powered PR reviewer (like CodeRabbit or GitHub Copilot Workspaces) to perform the first-pass mechanical review. 

**Technical detail**

The human reviewer's job shifts from reading loops and syntax to verifying **architectural intent, business logic, and test coverage correctness**. In your CI/CD configuration (e.g., GitHub Actions), enforce quality gates that block merges if static analysis fails, security vulnerabilities are detected, or test coverage drops.

This three-line comment takes 30 seconds and saves hours of future archaeology.

---

### No automated and architectural pull request review process

**`HIGH RISK`**

**Why it matters**

Code review is still a vital defect detection technique, but its nature has changed. In an AI-assisted team, the code review serves as the primary gateway for knowledge sharing and system design validation. Instead of hunting for syntax errors, it's the moment where human engineers ensure the AI matched the architectural vision.

**What goes wrong**

> Bugs that a second pair of eyes would catch in 5 minutes reach production. Knowledge silos form — only the author understands their own code. Security vulnerabilities and architectural mistakes go unchallenged because reviews focused too much on syntax and forgot the bigger picture.

**How to fix it**

Even if you're a team of two, require that every change to main goes through a pull request with at least one human review focused on macro-level logic. For solo developers, establish a self-review checklist: Have the automated quality gates passed? Is the high-level architecture safe? Does a robust test suite validate the AI's logic?

**Technical detail**

Create a PR template in your repository (`.github/pull_request_template.md`):

```markdown
- [ ] Automated quality gates, SAST, and linters passed
- [ ] Core business logic and architectural boundaries verified by human
- [ ] Robust test suite generated and successfully validates the AI's logic
- [ ] New dependencies audited
```

---

### No changelog or release notes maintained

**`MEDIUM RISK`**

**Why it matters**

A changelog is your record of intent — what changed, why it changed, and what it's supposed to do differently. Without it, when users report unexpected behavior, you have no way to correlate it with a specific change. When you need to roll back, you don't know what 'back' means.

**What goes wrong**

> User-reported bugs are impossible to trace to a specific change. Support conversations become archaeological digs. When a production incident occurs, the team spends the first hour just figuring out what changed recently.

**How to fix it**

Maintain a `CHANGELOG.md` in your repository root. Follow the [Keep a Changelog](https://keepachangelog.com) format: each release gets a dated entry with sections for Added, Changed, Fixed, and Removed. This takes 5 minutes per release and is invaluable during incidents and user support.

**Technical detail**

Automate it: tools like `conventional-commits` + `semantic-release` can generate changelogs automatically from commit messages. The investment in commit message discipline pays dividends here — meaningful commit messages become meaningful release notes.

---

### Commit messages are non-descriptive

**`LOW RISK`**

**Why it matters**

Commit messages are your future self's documentation. 'fix stuff' and 'update code' tell you nothing about what changed or why. Good commit messages make `git blame` and `git log` into powerful debugging tools.

**What goes wrong**

> Debugging a production issue by reviewing git history becomes impossible. The reasoning behind decisions is permanently lost. Automated changelog generation produces useless output.

**How to fix it**

Adopt the [Conventional Commits](https://www.conventionalcommits.org) standard: `type(scope): description`. Examples: `feat(auth): add OAuth2 login flow`, `fix(llm): handle empty response from API`, `refactor(prompts): extract system prompt to config`.

**Technical detail**

Install `commitlint` to enforce commit message format: `npm install --save-dev @commitlint/cli @commitlint/config-conventional`. Add a Git hook (using Husky) to reject commits that don't follow the pattern. This is a low-friction way to build the habit across the whole team.

---


[← Domain 01 — Code Quality](01-code-quality.md) | [Domain 03 — AI & LLM Integration →](03-llm-integration.md)