# GECK

The Sprint Zero launcher for [Animus Sprint Loops](https://github.com/crussella0129/Animus_Sprint_Loops).

GECK generates the two artifacts that start a Sprint Loop with full context:

- **`mission-spec.md`** — a durable, tracked, root-level mission document
  (goal, success criteria, constraints, working agreement, backlog seeds).
  This is the drift baseline every sprint compares against as building
  happens.
- **`launch-prompt.md`** — the complete instructional prompt you paste into
  Claude Code, Codex CLI, or an open harness to start Sprint 0 correctly,
  wired into Sprint Loops' own persistence machinery.

It also seeds the target project's Sprint Loops state — `decisions.md`
(an ADR pointing at the spec), `agent-tasks/agent-tasks.md` (backlog seeds),
and `confidence.txt` — deterministically and idempotently, so the mission
context flows into every subsequent sprint automatically.

## Why this exists

Animus Sprint Loops already solves cross-session persistence well: typed
backlog tasks, per-task git commits, an ADR log, an enforced research budget.
The one thing it doesn't durably keep is the *mission* — a sprint's goal
today enters as ephemeral prompt text and survives only as a one-line summary
in a gitignored `sprints/` directory. Launching Sprint 0 "properly" meant
hand-writing a rich prompt from scratch every time, with the full intent
evaporating once the session ended.

GECK closes that gap. `mission-spec.md` is the one thing worth keeping from
GECK's earlier incarnation as a standalone memory protocol (see
[`v1.3-protocol-final`](../../tree/v1.3-protocol-final) for that history) —
repurposed as the upstream launcher for a protocol that already does
everything else better.

Because Sprint Loops' `finalize-plan.sh` already forces every Research Phase
to review `decisions.md`, the ADR GECK seeds (`ADR-000`) makes every future
sprint re-read the mission spec and report drift automatically — no changes
to Sprint Loops required.

## Install

```bash
git clone https://github.com/crussella0129/Animus_GECK.git
cd Animus_GECK
cargo build --release --bin geck
# target/release/geck (or target/<triple>/release/geck)
```

Requires Rust 1.75+. `geck` is a single native binary with no other runtime
dependency — it does not itself need Git Bash or WSL (Sprint Loops' shell
scripts do; see the harness-specific notes in the generated prompt).

## Quick start

```bash
# Interactive wizard — no flags launches it
geck launch

# Or fully non-interactive
geck launch \
  --path ./my-project \
  --project-name "My Project" \
  --goal "Ship a REST API with auth, rate limiting, and OpenAPI docs." \
  --profile api \
  --criterion "All endpoints have integration tests" \
  --non-goal "Not building a frontend" \
  --harness claude-code \
  --merge-mode approve \
  --work-branch dev \
  --charter "Survey the existing auth middleware before designing the new API." \
  --backlog-seed "Add rate limiting middleware"
```

This writes `my-project/mission-spec.md` and `my-project/launch-prompt.md`,
and seeds `my-project/decisions.md`, `my-project/agent-tasks/agent-tasks.md`,
and `my-project/confidence.txt`. Paste the contents of `launch-prompt.md`
into your agent session to start Sprint 0. See [`docs/example/`](docs/example/)
for a worked pair of artifacts.

### Re-rendering the prompt

If you hand-edit `mission-spec.md`, or the installed Sprint Loops skill has
moved on since you launched, regenerate just the prompt:

```bash
geck prompt --path ./my-project
geck prompt --path ./my-project --harness codex-cli   # switch target harness
```

`mission-spec.md`'s YAML frontmatter is the source of truth `geck prompt`
re-parses — it never re-derives the prompt from anything else.

## Commands

| Command | Behavior |
|---|---|
| `geck launch` | No args → interactive wizard. With flags → non-interactive. Writes `mission-spec.md` + `launch-prompt.md`, seeds the project. |
| `geck prompt [--path .] [--harness <name>] [--output <path>]` | Re-render `launch-prompt.md` from an existing `mission-spec.md`. |
| `geck list-profiles [--json]` | List the 21 built-in project-shape profiles (languages, frameworks, suggested criteria). |
| `geck spec-version` | Print the mission-spec format version this binary targets. |

Run `geck launch --help` for the full non-interactive flag list.

## The wizard

`geck launch` with no arguments opens a menu-driven wizard: every section —
project name, path, repo URL (auto-detected from git when the path *is* a
repo root), profile, goal, success criteria, non-goals, languages,
must-use/must-avoid, platforms, harness, merge mode, work branch, Sprint 0
charter, backlog seeds, extra stop-checkpoints, and a seed toggle — is
visible on the menu at all times. Edit any section in any order, preview
both generated artifacts, then save.

## `mission-spec.md`

```markdown
---
geck: '2.0'
project: My Project
created: 2026-07-21
profile: api
harness: claude-code
merge_mode: approve
work_branch: dev
repo: https://github.com/you/my-project.git
sprint_loops_ref: 2026-07-21
---
# Mission: My Project

## Goal
...

## Success Criteria
Mission-level definition of done. Checked off across sprints, not per-sprint.
- [ ] ...

## Non-Goals
...

## Constraints
...

## Working Agreement
- **Merge mode:** approve — a human approves each sprint's PR before it merges.
- **Work branch:** dev

## Sprint 0 Charter
...

## Backlog Seeds
- T-101 (backlog): ...

## Amendment Protocol
This file is amended by humans only. ...
```

The frontmatter is machine-readable (what `geck prompt` re-parses); the body
is the human-readable mission document. **This file is amended by humans
only** — an agent proposing a change records an ADR in `decisions.md`
referencing the relevant section instead of editing the spec directly.

## Relationship to Animus Sprint Loops

GECK is a **launcher**, not an adapter. [Animus Sprint Loops](https://github.com/crussella0129/Animus_Sprint_Loops)
remains the canonical protocol — its `open-harnesses/`, `claude-code/`, and
`codex-cli/` bundles are unmodified by this project. GECK only writes into a
Sprint-Loops-shaped project *before* Sprint 0 starts: the seeds it writes
(`decisions.md`, `agent-tasks/`, `confidence.txt`) use the exact schemas
Sprint Loops itself defines, and `init-sprint.sh`'s own `[ -f ]` guards mean
it never clobbers what GECK seeded.

## Profiles

21 built-in profiles (website, web_app, api, cli_tool, data_science, devops,
game, embedded, blockchain, and more) seed a spec's languages, frameworks,
platforms, and suggested success/must-use/must-avoid criteria. List them
with `geck list-profiles`; profile values only fill fields you haven't set
explicitly.

## Development

```bash
cargo build --workspace
cargo test --workspace
cargo fmt --all
cargo clippy --workspace --all-targets
```

Two crates: `geck-core` (the library — spec model, templates, scaffolding,
profiles) and `geck-cli` (the `geck` binary — CLI + wizard).

## License

See [LICENSE](LICENSE) file.
