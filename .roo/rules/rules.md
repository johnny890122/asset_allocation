# rule.md — Specification‑Driven Development (SDD)

This repo uses a **Specification‑Driven Development** workflow. The AI assistant (that’s me) updates design and task specs before any coding begins. This keeps requirements, architecture, and implementation steps tightly aligned.

---

## Purpose & Scope

* **Purpose**: Turn feature requests into a concrete technical plan and an actionable task list, every time, in a repeatable way.
* **Scope**: This file defines the process. The assistant maintains **exactly two project docs** under `docs/`:

  * `docs/design.md` – the technical design and system architecture
  * `docs/tasks.md` – the development checklist derived from the design

> Note: While this file is the process contract, **`design.md`** and **`tasks.md`** are the only living specs the assistant edits during day‑to‑day work.

---

## Golden Rules

1. **Specs before code.** No coding discussion without a matching design & tasks update.
2. **One source of truth.** Design details live in `design.md`. Work items live in `tasks.md`.
3. **Traceability.** Every task must map back to a design section.
4. **Small, testable steps.** Tasks must be discrete and independently verifiable.
5. **Plain language.** Favor clear, jargon‑free writing and simple diagrams.

---

## Workflow (Follow in Order)

### 0) Input

When you (the PM/dev) provide a **new feature or change**, include: goal, context, constraints, any API/DB hints. If missing, the assistant will make reasonable assumptions and call them out in **Assumptions**.

### 1) Update `docs/design.md`

The assistant **creates or modifies** the design so it directly reflects the latest requirement. The design must include:

* **Summary** – one paragraph: problem & outcome.
* **Goals / Non‑Goals** – crisp bullets.
* **Assumptions** – things we’re taking as given.
* **Architecture** – module breakdown and interactions (Mermaid allowed).
* **Data Model** – key entities, fields, and relationships.
* **APIs & Contracts** – request/response shapes, status codes, errors.
* **Flows** – user/system flows, edge cases, retries, timeouts.
* **Security & Privacy** – authn/z, PII handling, logging boundaries.
* **Observability** – metrics, logs, traces, feature flags.
* **Testing Strategy** – unit, integration, E2E; fixtures; mocks.
* **Rollout Plan** – migration, backward compatibility, flags, guardrails.
* **Open Questions / Risks** – unknowns with proposals.

### 2) Update `docs/tasks.md`

The assistant breaks the approved design into an **ordered checklist** of work items:

* Each task is **atomic**, includes a short description, acceptance criteria, and (optionally) dependencies.
* Tasks reference the design using `[#section-id]` anchors.
* Include **test tasks** and **observability tasks**, not just code.

---

## Definition of Done (DoD)

* **Design** updated to reflect the intended behavior and edge cases.
* **Tasks** list covers implementation, tests, instrumentation, and rollout.
* **Traceability**: every task maps to a design anchor (or explicitly N/A).
* **Review**: another human has skim‑checked design & tasks for clarity.

---

## Minimal Writing Style

* Short sentences. Action verbs. No marketing language.
* Prefer tables and lists over paragraphs.
* Diagrams: use simple Mermaid when helpful.

---

## Templates (Copy into the real files)

### `docs/design.md` starter

````markdown
# Design — <Feature Name>

## Summary
One paragraph on the problem and intended outcome.

## Goals
-

## Non‑Goals
-

## Assumptions
-

## Architecture
```mermaid
flowchart TD
  U[User] --> A[Module A]
  A --> B[Module B]
  B --> DB[(Database)]
````

## Data Model

| Entity | Field | Type | Notes |
| ------ | ----- | ---- | ----- |
|        |       |      |       |
