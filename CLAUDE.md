# SysMLv2 Workspace

This workspace contains SysML v2 / KerML research and transformation work, plus local clones of Modelio-related repos from the `Modelio-R-D` GitHub org.

## Workspace Map

Root-owned project material:

- `deck-implementation-plan/` — design decisions, implementation notes, and slide-deck bundles. Keep each deck's Markdown source and rendered exports together in its existing subfolder.
- `docs/` — consolidated KerML/SysML metamodel reference.
- `icons-study/` — icon inventory and SysML/UML mapping research.
- `specs/` — normative OMG XMI and text snapshots, plus examples. Treat these as source material; do not regenerate or overwrite them from `reference/design`.
- `reference-design-transform/` — Modelio transformation and repair scripts, audit evidence, and process notes. Scripts may modify and save the live Modelio project; do not run them as a batch.
- `SemGen_Outil.docx` — related SemGen reference document.

The three repository folders below are independent Git checkouts, not subfolders to merge into the root project. Preserve their locations and their own Git history. Each may have local work that must be checked before cleanup or synchronization.

## Repos

- `ModelioSkill/` — the Modelio Claude Code skill (Jython scripting for model automation). Contains the released skill under `skills/modelio/`, slash commands under `commands/`, and docs/tests. See its own CLAUDE.md and README.md for details.
- `Modelio-API-Markdown-CHUB/` — Modelio API documentation knowledge base structured for the Context Hub CLI (`chub`). Includes scraped UML/BPMN docs and generation scripts (`generate_docs.py`, `generate_chub_uml.py`, `scrapper_modelio.py`).
- `ModelioSaaS_ScriptServer/` — Modelio module providing a TCP socket server (default port 9999) for remote Jython script execution against Modelio SaaS 6.1.01. Used by ModelioSkill and other tools/agents to run scripts against a running Modelio instance. Built with Maven (JDK 17 required).

Repos have their own CLAUDE.md files with repo-specific instructions — read those when working inside each repo.

Several Modelio scripts contain absolute paths rooted at this workspace or its sibling `H:\modelio` checkout. Do not rename or move workspace folders or repo clones without first updating and checking their consumers. Retain generated-looking audit files and rendered deck exports unless their owners confirm they are disposable.

## Access

Cloned via `gh repo clone` using the authenticated `gh` CLI (account: juancadavid). To pull updates: `git -C <repo-name> pull`.
