# SysMLv2 Workspace

This workspace hosts local clones of Modelio-related repos from the `Modelio-R-D` GitHub org.

## Repos

- `ModelioSkill/` — the Modelio Claude Code skill (Jython scripting for model automation). Contains the released skill under `skills/modelio/`, slash commands under `commands/`, and docs/tests. See its own CLAUDE.md and README.md for details.
- `Modelio-API-Markdown-CHUB/` — Modelio API documentation knowledge base structured for the Context Hub CLI (`chub`). Includes scraped UML/BPMN docs and generation scripts (`generate_docs.py`, `generate_chub_uml.py`, `scrapper_modelio.py`).
- `ModelioSaaS_ScriptServer/` — Modelio module providing a TCP socket server (default port 9999) for remote Jython script execution against Modelio SaaS 6.1.01. Used by ModelioSkill and other tools/agents to run scripts against a running Modelio instance. Built with Maven (JDK 17 required).

Repos have their own CLAUDE.md files with repo-specific instructions — read those when working inside each repo.

## Access

Cloned via `gh repo clone` using the authenticated `gh` CLI (account: juancadavid). To pull updates: `git -C <repo-name> pull`.
