# 0014. Diagrams are Mermaid; C4 and use case are approximations, and labelled as such

- **Status:** Accepted
- **Date:** 2026-10-03
- **Relates to:** `docs/02-diseno/arquitectura-c4.md`, `docs/02-diseno/diagrama-casos-uso.md`,
  `docs/02-diseno/modelo-datos.md`, `docs/03-pruebas/plan-pruebas.md` §7, ADR 0011 (generated
  contract, drift fails CI), `AGENTS.md` (Definition of Done)

## Context

Found by looking at the files instead of at the previous report:

1. **Two C4 blocks did not render, at all.** `arquitectura-c4.md` held `C4Context` and
   `C4Container` source in ` ```text ` fences under headings that read "**Mermaid (Level 1)**"
   and "**Mermaid (Level 2)**". GitHub renders a ` ```text ` fence as plain text, so a reader
   saw a wall of PlantUML keywords and no diagram. Both the heading and the fence language
   were wrong.
2. **The check that was run was green while the artefact was broken.** It reported
   `TOTAL 11 PARSED 11 FAILED 0`. The check extracted only ` ```mermaid ` fences; the two
   broken blocks were not among the eleven, so they were *invisible* to it rather than
   passing it. The scope of the check had been set by what was convenient to parse, not by
   what it was supposed to guarantee.
3. **The repository is read on GitHub**, which renders stock Mermaid natively and does not
   render PlantUML. Any diagram written in PlantUML therefore either needs a renderer we
   provide, or becomes text.

Point 2 is the reason this is an ADR rather than a fix. A green check whose scope omits the
failure it should catch is worse than no check, because it converts "we do not know" into
"we verified it".

## Decision

### 1. Mermaid is the only diagram syntax

Every diagram lives in a fence whose language is exactly `mermaid`. No PlantUML, no `text`
fences carrying diagram syntax, no diagram images committed as binaries.

**Mermaid 11 has no UML activity diagram.** This was checked rather than assumed:
`mermaid.parse("activityDiagram\n…")` fails with *"No diagram type detected matching given
configuration"*. So a literal `activityDiagram` block would be a contradiction of this
decision. Activity content is covered instead where it already exists:

| Activity | Existing view | Why no new diagram |
|---|---|---|
| Ingestion | `flujo-datos.md` §2 `flowchart TD`, including retries, gates, the circuit breaker and both bypass entry points | It *is* the activity, expressed with decisions; a second diagram would duplicate it |
| Moderation | `estados.md` §2 `stateDiagram-v2` plus the 11-row transitions table in §3 and rules R1–R8 in §4 | The table already names trigger, actor, side effects and reversibility per transition — what an activity diagram would add is drawn instead as a **sequence** |

What genuinely was missing was the *interaction* view — who talks to whom and in what order —
so two `sequenceDiagram`s were added instead: one for a scheduled ingestion run
(`flujo-datos.md` §2.1) and one for the step-up publish path (`autenticacion.md` §7.4).

### 2. C4 is approximated by `flowchart`, and the document says so

Mermaid ships no C4 notation, and a C4 dialect would have to be installed and rendered by us
— so it would not render for the primary reader.

- **Level 1** becomes `flowchart LR`, with the external systems in an `External systems`
  subgraph.
- **Level 2** becomes `flowchart TB`, with a `subgraph` standing in for C4's
  `System_Boundary`.

The headings no longer claim to be C4 tool output. They read
"**Diagram (Level 1 — system context)**" and "**Diagram (Level 2 — containers)**", and each
states in prose that it is a simplification of the corresponding C4 level.

**What is accepted as lost:** C4 distinguishes `Person`, `System`, `System_External` and
`Container`, and annotates each with its technology, *by notation*. A `flowchart` carries
none of that; the distinctions and technologies are written into node labels instead. A
reader can therefore mistake these for full C4 models — the heading text is what prevents
that, which is why the labelling is part of this decision rather than an editorial nicety.

### 3. The use case picture is a stand-in, and the document states it

Mermaid has no UML use case notation: no stick-figure actors, and no `<<include>>` or
`<<extend>>`. `diagrama-casos-uso.md` uses `graph TB` with subgraphs for actors and use-case
groups, and now carries an explicit note that it is a stand-in rather than a UML diagram.

The **authoritative artefact is the 26-row use case register** in its §2; the picture is a
reading aid. Where one use case implies another, that belongs in the register text, not in a
drawing that cannot express it.

### 4. The check validates every fence, not just Mermaid ones

`scripts/check-diagrams.cjs`:

- extracts **every** fenced block in every `.md`, together with its language tag;
- parses `mermaid` blocks with Mermaid's own parser;
- **fails** when a `text` / `txt` / `plaintext` / `plantuml` / `uml` / bare fence contains
  diagram syntax (`C4Context`, `C4Container`, `@startuml`, `skinparam`, and similar);
- reports a breakdown **by fence language** and **by Mermaid diagram type**;
- exits non-zero on any failure.

The breakdown is what would have exposed the original problem instantly: **30 fenced blocks
existed and the old check looked at 11.**

## Consequences

**Positive**

- Every diagram renders where it is read.
- One syntax, one parser, one gate. The check can be wired into CI as a build-failing step,
  consistent with how ADR 0011 treats OpenAPI drift.
- The false green is structurally prevented: scope is now *all fences*.

**Negative, accepted**

- C4 semantics are conveyed by labels rather than enforced by notation.
- The use case picture is not UML and cannot model include/extend; the register carries that
  weight instead.
- Mermaid's layout is weaker than PlantUML's, so the larger diagrams may need manual node
  ordering to stay readable.
- A diagram in a `text` fence now fails the check, which means **existing prose examples
  written in a diagram-like syntax would also fail.** None exist today; if one appears, it
  must be fenced with a language other than the plain-text set.

## Alternatives considered

1. **PlantUML, rendered externally or exported as images.** Rejected: committed images go
   stale silently and cannot be meaningfully diffed in review, and an external renderer adds
   a dependency to *reading* the documentation. GitHub does not render PlantUML.
2. **A third-party C4 dialect for Mermaid.** Rejected: it requires our own renderer, so the
   diagram would not appear for the reader GitHub is serving.
3. **Keep the ` ```text ` fences and relabel them as code samples.** Rejected: the document
   claimed they were Mermaid diagrams. Relabelling would leave a false claim in place while
   fixing the rendering.
4. **Keep checking only `mermaid` fences.** Rejected — that *is* the current behaviour, and
   it returned a green result for a document with two broken diagrams.

## Amendment — 2026-10-04

Recorded once the validator became runnable, which is what made these claims checkable. The
decision stands. **Two of its stated reasons did not survive checking.**

**Falsified — §2's "Mermaid ships no C4 notation".** Against the version this repository now
pins, `mermaid@12.1.0`, `mermaid.parse()` **accepts** a valid `C4Context` block. Mermaid gained
native C4 support after this ADR was written, so §2's premise is no longer true of the tool we
use. §4's breakdown was also blind to it: `C4Context` was reported as `(unknown: C4Context)`
while parsing successfully, because the diagram-type regex had not been taught C4.

**Still true — §1's "Mermaid 11 has no UML activity diagram".** Re-verified against the same
version: `mermaid.parse("activityDiagram…")` fails with *"No diagram type detected matching
given configuration"*.

**Why the C4 approximation is kept anyway.** The reader is GitHub, not us. GitHub renders
Mermaid with **its own pinned version**, which this repository neither controls nor has
verified. If that renderer predates C4 support, a `C4Context` fence renders as a syntax error
rather than a diagram — the exact failure this ADR exists to prevent, reintroduced by its own
fix. A `flowchart` approximation renders on every Mermaid version the project will outlive, and
the diagrams are written and reviewed that way already.

So §2's **decision** stands and only its **reason** was wrong. Verifying the open question is
cheap: put one `C4Context` block on a scratch branch, open the rendered page on GitHub, and
look. Until somebody does, the conservative approximation stays and nobody should read this
amendment as "C4 is available, switch over".

## Verification

- `npm ci && npm run check:diagrams` runs the validator from a clean checkout. It prints both
  breakdowns and exits non-zero on any failure.
- Dependencies are pinned in `package.json` and `package-lock.json` (`mermaid@12.1.0`,
  `jsdom@29.1.1` as of 2026-10-04). `node_modules/` is gitignored; the lockfile is committed.
  **That `package.json` is documentation tooling only** — the backend is Python and the public
  site becomes a separate package under `frontend/`. It must not grow into an application
  manifest.
- The validator skips dependency and build directories, and that was a real defect rather than
  a precaution. The first run with `node_modules` present walked into `mermaid`'s own
  `README.md`, found PlantUML C4 blocks there, and failed on a third party's documentation. A
  check has to see the repository, not the tools it installs.
- Current result: **37 fenced blocks, 20 Mermaid diagrams, 0 failures.** The 20 is
  cross-checkable — a repository-wide search for lines that open a `mermaid` fence also
  returns 20.
- The CI job that runs this on every push still lands with Sprint 01, alongside the first real
  pipeline.
