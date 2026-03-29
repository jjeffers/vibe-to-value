---
description: Build the ebook PDF and open it in the Document Viewer
---

This workflow automates building the Vibe-to-Value PDF ebook from its markdown source files, and then launching it in Evince (Document Viewer).


1. Run the build script using the established virtual environment. This generates the PDF and automatically opens it.
// turbo
```bash
.venv/bin/python build_ebook.py
```