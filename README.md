# From Vibe to Value — Markdown Source Files

Edit these files to update the ebook content. Each file corresponds to one chapter.
The PDF can be regenerated from these files at any time.

## File Index

| File | Chapter |
|------|---------|
| `00-introduction.md` | Introduction & How to Use This Guide |
| `01-code-quality.md` | Domain 01: Code Quality & Structure |
| `02-version-control.md` | Domain 02: Version Control & Change Management |
| `03-llm-integration.md` | Domain 03: AI & LLM Integration Patterns |
| `04-context-management.md` | Domain 04: Context Management |
| `05-guardrails.md` | Domain 05: Rules, Memory & Guardrails |
| `06-blast-radius.md` | Domain 06: Blast Radius Discipline |
| `07-testing.md` | Domain 07: Testing & Reliability |
| `08-security.md` | Domain 08: Security & Data Handling |
| `09-production-readiness.md` | Domain 09: Production Readiness |
| `10-conclusion.md` | Conclusion & Next Steps |

## Editing Notes

- Each item follows the same structure: Why it matters / What goes wrong / How to fix it / Technical detail
- Risk levels are `HIGH`, `MEDIUM`, or `LOW` — update these if your assessment changes
- Code blocks use standard markdown fencing (triple backticks)
- Navigation links between files are at the top and bottom of each domain file

## Regenerating the PDF

Run `python3 build_ebook.py` from the project root to regenerate the PDF from the source content.
