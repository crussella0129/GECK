# Animus_GECK Refactor Plan — From Memory Protocol to Sprint Zero Launcher

**Status:** PLAN ONLY — no code has been touched.
**Written:** 2026-07-21
**Scope:** Animus_GECK only. Companion changes to Animus_Sprint_Loops are listed
in §9 as explicitly out-of-scope follow-ups.

---

## 1. The thesis

The GECK protocol (v1.0–v1.3) and Animus Sprint Loops solve the same problem —
cross-session context persistence for CLI coding agents — and Sprint Loops
solves it better. Every GECK protocol concept has a Sprint Loops successor:

| GECK v1.3 concept | Sprint Loops successor |
|---|---|
| `GECK/tasks.md` (typed TASK-NNN) | `agent-tasks/agent-tasks.md` (T-NNN, sprint/backlog tags) |
| `GECK/log.md` + `log_index.jsonl` | Per-task git commits + `sprints/sN/` artifacts |
| `GECK/decisions/` (DECISION-NNN) | `decisions.md` (ADR-lite, root-level) |
| `GECK/learnings/` | `decisions.md` + research reports |
| Drift Check at session start | Decisions-reviewed gate in `finalize-plan.sh` |
| Context Budget (small/medium/large) | Research budget (20 files / 5 sources, enforced) |
| Checkpoint CONTINUE/WAIT/ROLLBACK | Phase state machine + stop criterion + safety floor |
| `GECK/env.md` | (not needed — harness provides environment) |
| **`LLM_init.md` — the mission document** | **NOTHING. This is the gap.** |

The one GECK artifact with *no* Sprint Loops counterpart is exactly the one
worth keeping: the human-authored mission document. Today a Sprint Loop's goal
enters as ephemeral prompt text (`/sprint-loop start "<goal>"`) and survives
only as a one-line `Summary:` in `sprint-meta.md` — which lives in `sprints/`,
which `init-sprint.sh` **gitignores**. The full intent behind a loop is
retained nowhere tracked. Launching Sprint 0 "properly" currently means
hand-writing a rich prompt from scratch every time, and that context evaporates
the moment the session ends.

**The refactor:** delete the GECK protocol; repurpose the GECK generator
machinery (wizard, profiles, templates, CLI) into a **Sprint Zero launcher**
that emits two artifacts:

1. **`mission-spec.md`** — a durable, tracked, root-level spec document: the
   full mission context (goal, success criteria, constraints, working
   agreement, backlog seeds). The drift baseline every sprint can be compared
   against as building happens.
2. **The launch prompt** — the complete instructional prompt you paste into
   Claude Code / Codex / an open harness to start Sprint 0 correctly: it wires
   the spec into Sprint Loops' existing persistence machinery so the mission
   context flows into every subsequent sprint automatically.

Thematically nothing changes: the Garden of Eden Creation Kit still creates
the world. It just now creates the world *the loop lives in*, instead of
competing with the loop.

---

## 2. What exists today (investigation summary)

### Animus_GECK (~9,600 lines)

| Area | Size | Contents |
|---|---|---|
| `GECK/` | 4 spec docs + 1 report | Protocol v1.0–v1.3 specs, feasibility report — **vestigial** |
| `geck_generator/` | ~4,650 lines Python | tkinter GUI, questionary CLI wizard, jinja2 templates, profiles, git utils, Windows shortcuts, validators, "Repor" exploration feature |
| `tests/` | ~1,925 lines Python | pytest for the Python generator |
| `crates/geck-core` | ~2,000 lines Rust | Tera template engine (9 templates), 21-profile registry (`profiles.json`), scaffold + env detection, frontmatter parser, protocol modules (tasks/log_index/decisions/learnings), validate stub |
| `crates/geck-cli` | ~1,055 lines Rust | clap CLI (`protocol-version`, `list-profiles`, `list-templates`, `generate`, `init`), 750-line inquire menu-driven wizard |
| `scripts/check_parity.sh` | 150 lines | Byte-parity harness between Python and Rust output |
| Root `log.md` | — | An Animus Phase 1 findings essay (cloud vs. local) — content worth preserving, wrong home |
| `GECK_Suggestions.md` | — | Historical v1.2→v1.3 design doc — vestigial |

No CI. Remote: `https://github.com/crussella0129/Animus_GECK`.

### Animus_Sprint_Loops (relevant facts for the launcher)

- Four self-contained bundles (open-harnesses = canonical, claude-code plugin,
  codex-cli, antigravity-ide) sharing identical phases/schemas/scripts.
- `init-sprint.sh` scaffolds `sprints/sN/`, creates persistent
  `agent-tasks/{agent-tasks,completed-tasks}.md`, `decisions.md` — **all
  guarded by `[ -f ]`, so pre-seeding by an external tool is safe** — and
  drops a marker-guarded `.gitignore` block excluding only `sprints/` and
  `*.tmp`. Root-level files stay tracked.
- Research Phase **must** read `decisions.md` and write a `## Decisions
  Reviewed` section; `finalize-plan.sh` enforces this whenever `decisions.md`
  is non-empty. → *Any ADR that points at `mission-spec.md` guarantees every
  future sprint re-touches the mission. This is the drift-comparison hook, and
  it requires zero changes to Sprint Loops.*
- `agent-tasks.md` schema: `- [ ] T-1xx (backlog): <desc> — touches: <files>`
  entries never affect phase routing → safe to pre-seed.
- ROADMAP §9 (user-requested, sprint 11): elicit **merge mode**
  (approve-merge vs auto-merge) and a **dev-branch working model** at launch
  "unless the initial prompt already specified it." → The launcher
  questionnaire is the natural place to capture both; the generated prompt
  *is* the "initial prompt that already specified it."
- Sprint Loops' README already anticipated integration ("If folded into GECK,
  'GECK Loops' becomes a fourth adapter"). This plan inverts that: GECK
  doesn't *host* the protocol, it *launches* it. The bundles stay canonical
  in Animus_Sprint_Loops.

---

## 3. Target design

### 3.1 The flow

```
$ geck launch                      # interactive wizard (or all-flags non-interactive)
  → writes  <project>/mission-spec.md
  → writes  <project>/launch-prompt.md  (+ prints to stdout)
  → seeds   <project>/decisions.md          (ADR-000: mission spec adopted)
            <project>/agent-tasks/agent-tasks.md   (backlog seeds)
            <project>/confidence.txt              (1.0)

$ # user pastes launch-prompt.md into Claude Code / Codex / harness
  → agent reads mission-spec.md, runs /sprint-loop start "<goal>", Sprint 0
    proceeds with full context; every later sprint re-reads the mission via
    the ADR-000 → decisions-reviewed gate.
```

### 3.2 Artifact 1: `mission-spec.md`

Root-level, tracked (sibling of `decisions.md` / `confidence.txt` — the
`.gitignore` block only excludes `sprints/`). Single source of truth: the
launch prompt is *derived from* the spec, never the reverse.

**Structure — YAML frontmatter (machine-readable) + markdown body (human-readable):**

```markdown
---
geck: 2.0                       # spec format version
project: <name>
created: 2026-07-21
profile: cli_tool               # GECK profile used, if any
harness: claude-code            # claude-code | codex-cli | open-harness | antigravity
merge_mode: approve             # approve | auto   (ROADMAP §9 election)
work_branch: dev                # long-lived work branch name
repo: https://github.com/...    # detected from git remote
sprint_loops_ref: <date or commit the prompt text targets>
---

# Mission: <project>

## Goal
One-to-three paragraphs. The full intent, not a one-liner.

## Success Criteria (mission-level definition of done)
- [ ] ...          # checked off across sprints, not per-sprint
- [ ] ...

## Non-Goals
Explicit exclusions — the anti-drift fence.

## Constraints
- Languages / Frameworks / Platforms (profile-seeded, user-edited)
- Must use / Must avoid

## Working Agreement
- Merge mode, branch model, autonomy posture (mirrors frontmatter, prose form)
- Extra stop-criterion checkpoints beyond SKILL.md's four (e.g. "stop before
  any schema migration")

## Sprint 0 Charter
What Sprint 0 specifically should research and build first.

## Backlog Seeds
- T-101 (backlog): ...
- T-102 (backlog): ...

## Amendment Protocol
This file is amended by humans only. Agents proposing a change record an ADR
in decisions.md referencing the section; the spec itself is edited by the
human. Each sprint's Research Phase re-reads this file and reports drift.
```

The frontmatter is what `geck prompt` re-parses to regenerate the launch
prompt later — no separate state file (`geck.toml` etc.), no duplicate truth.
`geck-core/src/frontmatter.rs` already exists and gets reused for exactly
this.

### 3.3 Artifact 2: `launch-prompt.md`

Written next to the spec *and* printed to stdout. Contents, per target
harness:

1. **Preamble** — install/verify lines for the chosen harness (the Quick
   Start blocks from Sprint Loops' README, templated per `harness:` value).
2. **The invocation** — e.g. for claude-code:
   `/sprint-loop start "<one-line goal distillation> — full mission in mission-spec.md"`.
3. **Wiring instructions** (the part that makes Sprint 0 "proper"):
   - Read `mission-spec.md` in full before the Init phase.
   - Verify/complete the seeds: ADR-000 in `decisions.md`, backlog entries in
     `agent-tasks/agent-tasks.md`, `confidence.txt` (the launcher already
     wrote them; the agent confirms rather than creates — deterministic work
     stays tool-side, matching Sprint Loops' own script-first philosophy).
   - Establish the `work_branch` per the Working Agreement; record merge mode
     and branch model in `sprint-meta.md` (satisfies ROADMAP §9's election).
   - Treat the spec's Success Criteria as the mission-level definition of
     done: each Loop Phase, check off any criterion the sprint completed.
   - Each Research Phase: re-read `mission-spec.md`, report drift in the
     research report (rides the existing decisions-reviewed gate via ADR-000).
4. **Autonomy footer** — how to run unattended (`/loop /sprint-loop
   continue`, auto-accept at ExitPlanMode), quoted from SKILL.md so the text
   matches the installed skill; plus a note that Sprint Loops' shell scripts
   need Git Bash on Windows.

### 3.4 Seeding (deterministic, idempotent)

`geck launch` (default on; `--no-seed` to skip) writes into the target project:

- `decisions.md` — create if missing; append **ADR-000** (marker-guarded,
  grep-before-append, mirroring `init-sprint.sh`'s own idempotence pattern):

  ```markdown
  ## <date> — Mission spec adopted: mission-spec.md is the drift baseline (sprint 0)
  - **Context:** Project launched via GECK Sprint Zero launcher.
  - **Decision:** mission-spec.md at the project root is the authoritative
    mission document. Research Phases re-read it and report drift.
  - **Alternatives considered:** goal-in-prompt only — rejected: not durable.
  - **Consequences:** Every sprint's decisions-reviewed gate re-surfaces the
    mission. Spec amendments are human-only.
  ```

- `agent-tasks/agent-tasks.md` — create if missing with schema header; append
  the spec's Backlog Seeds as `T-1xx (backlog)` entries (idempotent by ID).
- `confidence.txt` — create with `1.0` if missing.

All compatible with a later `init-sprint.sh` run (its `[ -f ]` guards mean it
never clobbers). Seeding never touches `sprints/` — that's the protocol's job.

### 3.5 CLI surface after refactor

| Command | Behavior |
|---|---|
| `geck launch` | No args → wizard. With flags → non-interactive. Writes spec + prompt, seeds project. Flags: `--project-name`, `--goal`, `--profile`, `--criterion`(rep.), `--non-goal`(rep.), `--languages`, `--must-use`, `--must-avoid`, `--platform`(rep.), `--framework`(rep.), `--harness`, `--merge-mode`, `--work-branch`, `--backlog-seed`(rep.), `--path <project-root>`, `--no-seed`, `--stdout-only` |
| `geck prompt [--path .]` | Re-render `launch-prompt.md` from an existing `mission-spec.md` (frontmatter-driven). For when the spec was hand-edited or the harness target changes (`--harness` override). |
| `geck list-profiles [--json]` | Kept as-is. |
| `geck spec-version` | Replaces `protocol-version`; prints the spec format version. |
| *(stretch, later)* `geck status` | Read a launched project: spec vs. checked-off criteria vs. `decisions.md` drift ADRs — a mission dashboard. Not in initial scope. |

Dropped: `generate` (folded into `launch`), `init` (GECK-folder scaffolding is
gone), `list-templates` (internal detail).

### 3.6 Wizard rework

The 750-line inquire wizard's menu-driven, edit-any-section-then-preview-save
shape is exactly right — keep the skeleton, swap the sections:

- **Keep:** project name, path, repo URL (auto-detect from git remote),
  profile, goal, success criteria (profile-suggested + custom), languages,
  must-use/must-avoid, platforms, preview, save.
- **Add:** harness target (select), merge mode (select: approve/auto, with
  one-line consequence text), work branch (default `dev`), non-goals,
  Sprint 0 charter, backlog seeds (repeating entry like criteria), extra
  stop-checkpoints, seed toggle.
- **Remove:** context budget, initial task, frameworks-as-separate-step
  (fold into constraints editing).
- Preview now shows *both* artifacts (spec, then prompt).

---

## 4. File-by-file disposition

### Delete outright (history preserved by the Phase-0 tag)

| Path | Note |
|---|---|
| `GECK/` (all 5 files) | Protocol specs v1.0–v1.3 + feasibility report |
| `GECK_Suggestions.md` | v1.3 design history |
| `geck_generator/` (entire package) | Python implementation incl. GUI and Repor feature |
| `tests/` (all Python tests) | Tested the deleted implementation |
| `setup.py`, `requirements.txt`, `pytest.ini` | Python packaging |
| `scripts/check_parity.sh` | No second implementation to keep parity with |
| `crates/geck-core/src/{tasks,log_index,decisions,learnings}.rs` | Protocol artifact machinery |
| `crates/geck-core/templates/{geck_inst,env,log,log_index,tasks,decisions_index,learnings_index,repor}.tera` | Protocol templates |
| `geck_generator/repor_inst.md` | Repor feature doc |

### Repurpose

| Path | Becomes |
|---|---|
| `crates/geck-core/templates/llm_init.tera` | `mission_spec.tera` (new structure per §3.2) |
| *(new)* | `launch_prompt.tera` (+ small per-harness partials for the preamble) |
| *(new)* | `adr_000.tera`, `backlog_seed.tera` (seeding snippets) |
| `crates/geck-core/src/scaffold.rs` | Keep `detect_environment` + write plumbing; replace `init_geck_folder` with `write_spec`, `write_prompt`, `seed_project` (idempotent) |
| `crates/geck-core/src/frontmatter.rs` | Kept — parses `mission-spec.md` frontmatter for `geck prompt` |
| `crates/geck-core/src/validate.rs` (3-line stub) | Grows into spec validation (required fields, enum values for harness/merge-mode) |
| `crates/geck-core/src/templates.rs` | Kept; template registry updated |
| `crates/geck-core/src/profiles.rs` + `data/profiles.json` | Kept as-is (21 profiles keep seeding constraints/criteria). Later: optionally add per-profile suggested backlog seeds |
| `crates/geck-cli/src/main.rs` | New subcommand set per §3.5 |
| `crates/geck-cli/src/wizard.rs` | Section swap per §3.6 |
| `README.md` | Full rewrite: GECK = Sprint Zero launcher for Animus Sprint Loops |
| Root `log.md` | **Not code, not GECK's.** Move content to `docs/animus-phase1-findings.md` (or relocate to wherever Animus notes live — flagged as Decision D5) |
| `.gitignore`, `Cargo.toml`, `Cargo.lock`, `LICENSE`, `GECK icon.png` | Keep (workspace members unchanged: `geck-core`, `geck-cli`) |

Estimated end state: ~2,500–3,500 lines of Rust + templates, down from ~9,600
mixed Python/Rust. One implementation, one language — consistent with the
Rust-first preference.

---

## 5. Execution phases

Each phase is a coherent, independently-committable unit. (These map cleanly
onto Sprint Loops sprints if you dogfood — see §8.)

**Phase 0 — Preserve history (5 min).**
Tag `git tag v1.3-protocol-final` on current `main`, push the tag. Create
branch `refactor/sprint-zero-launcher`. Everything below happens on the
branch; the tag is the archive — no `docs/legacy/` clutter needed.

**Phase 1 — Prune.**
Delete everything in §4's delete table. Update `Cargo.toml`/workspace so
`cargo build` still passes with the surviving modules stubbed (comment out
dead `pub mod` lines in `lib.rs`, remove dead template registrations, delete
the `generate`/`init` arms or stub them). Exit: `cargo build` green, repo
contains only the Rust toolchain + docs to be rewritten.

**Phase 2 — Core model + templates.**
- New `MissionSpec` struct in geck-core (replaces `InitConfig`): all §3.2
  frontmatter fields + body sections. `serde` round-trip to/from frontmatter.
- `mission_spec.tera`, `launch_prompt.tera` (+ harness partials), seeding
  snippets. Golden-file tests for each rendered artifact (fixed `EnvInfo`
  for determinism — the pattern `scaffold.rs` already uses).
- Spec parser: read `mission-spec.md` → `MissionSpec` (frontmatter authoritative;
  body not parsed except Backlog Seeds section for re-seeding).
- Rework `validate.rs`: required fields, enum domains, non-empty goal.
Exit: `cargo test` green with golden tests for spec + prompt + seeds.

**Phase 3 — Seeding + environment.**
- `seed_project(root, &spec)` in scaffold.rs: ADR-000 append (marker-guarded),
  backlog seeds (ID-guarded), `confidence.txt`. Idempotence test: run twice,
  assert byte-identical.
- Compatibility test: temp git repo → `seed_project` → run Sprint Loops'
  `init-sprint.sh` (fixture copy vendored under `tests/fixtures/`) → assert
  seeds survive and init still succeeds. Mark `#[ignore]`-by-default on
  Windows if bash is unavailable; run in CI (ubuntu).
- `detect_environment` extended: git remote URL, current branch.
Exit: seeding tests green.

**Phase 4 — CLI + wizard.**
- `main.rs`: `launch` (flags + wizard dispatch), `prompt`, `list-profiles`,
  `spec-version`.
- `wizard.rs` section swap per §3.6.
Exit: manual smoke — `geck launch` wizard end-to-end on a scratch dir
produces both artifacts + seeds; `geck prompt --harness codex-cli` re-renders.

**Phase 5 — Docs.**
- README rewrite: what GECK is now, the two artifacts, the flow diagram,
  per-harness quick starts, relationship to Animus_Sprint_Loops (launcher,
  not adapter; bundles stay canonical over there).
- `docs/example/` with a worked `mission-spec.md` + `launch-prompt.md`.
- Move the Animus essay out of root `log.md` per D5.
Exit: README accurate; no references to protocol v1.x remain anywhere
(`grep -ri "protocol" --include="*.md"` sweep).

**Phase 6 — QA + CI.**
- `cargo fmt`, `cargo clippy` clean (fix, don't acknowledge).
- New `.github/workflows/ci.yml`: fmt + clippy + test on ubuntu + windows
  (the binary's primary user is on Windows; Sprint Loops' own CI is the
  precedent).
- **Acceptance test (manual, the real one):** on a scratch repo with the
  sprint-loop plugin installed, run `geck launch`, paste the prompt into
  Claude Code, and verify Sprint 0 runs Init→Research with the spec context:
  research report cites ADR-000 in Decisions Reviewed, work branch created,
  merge mode recorded in sprint-meta.
- Merge `refactor/sprint-zero-launcher` → `main` via PR.

---

## 6. Decision points (defaults chosen; flag if you disagree)

| # | Decision | Recommendation | Alternatives |
|---|---|---|---|
| D1 | Python implementation + tkinter GUI | **Delete entirely.** Rust-first; the inquire wizard replaces the GUI's job. Keeping parity doubled every change. | Keep GUI as thin shell over `geck` (deferred; Electron/Tauri front-end is a separate future project if ever wanted) |
| D2 | Spec filename | **`mission-spec.md`** at project root — describes content, harness-neutral, sits naturally beside `decisions.md` | `GECK.md` (brand-forward), `SPRINT_SPEC.md` |
| D3 | Launch prompt persistence | **Write `launch-prompt.md` + print to stdout.** Derived artifact but cheap to track and reviewable in PRs | stdout-only (`--stdout-only` flag covers this) |
| D4 | Repo/binary naming | **Keep `Animus_GECK` repo, `geck` binary, crate names.** README reframes the meaning; zero churn | Rename repo to `Animus_GECK_Launcher` etc. — churn, no payoff |
| D5 | Root `log.md` essay | **Move to `docs/animus-phase1-findings.md`** — preserve, don't delete; it's Animus research, not GECK code | Move to a separate Animus notes repo if one exists |
| D6 | Seeding default | **On by default** (`--no-seed` opt-out). Deterministic work belongs to the tool, matching Sprint Loops' script-first philosophy | Prompt-instructed seeding (agent does it) — less deterministic |
| D7 | Sprint Loops coupling | **Reference, don't vendor.** The prompt targets the user's installed skill; spec frontmatter records `sprint_loops_ref` so prompt/protocol skew is diagnosable | Vendor the bundles into GECK ("GECK Loops") — rejected: Animus_Sprint_Loops stays canonical |

## 7. Risks

- **Prompt/protocol skew.** The launch prompt embeds Sprint Loops invocation
  details (`/sprint-loop start`, auto-accept mechanics). If the skill evolves,
  the prompt text can lag. Mitigation: all harness-specific text lives in
  dedicated template partials; `sprint_loops_ref` in frontmatter records what
  the prompt targeted; `geck prompt` regenerates cheaply after a template
  update.
- **Seeding into a non-empty project.** Appending ADR-000 to an existing,
  populated `decisions.md` is correct (dated ADRs are append-only), and
  marker-guards make it idempotent — but `geck launch` should print a clear
  diff-style summary of what it wrote/skipped.
- **Windows.** `geck` itself is native (good — no bash needed to launch), but
  Sprint Loops' scripts require Git Bash; the prompt preamble states this so
  Sprint 0 doesn't stall on a missing dependency.
- **Wizard scope creep.** The new questionnaire is ~6 sections longer. Keep
  the menu-driven shape (nothing is mandatory except name + goal; everything
  else has profile/sane defaults) so a fast launch is still <2 minutes.

## 8. Dogfooding option

This refactor is itself a well-specified mission: this document's §1–§5 are a
mission-spec in prose form. Once Phase 1–2 exist in rough form, the remaining
phases could be run as Sprint Loops sprints in this repo (`/sprint-loop start`
with this plan as the referenced spec) — the acceptance test in Phase 6 then
partially validates itself. Optional, but it would make Animus_GECK the first
project launched the way GECK will launch everything else.

## 9. Out of scope — companion notes for Animus_Sprint_Loops (later, separate)

None of these are required for the launcher to work (the ADR-000 mechanism
rides existing gates), but they'd tighten the integration:

1. `02-research-phase.md` + `research-report.md` schema: one sentence — "if
   `mission-spec.md` exists at the project root, re-read it and note any
   drift in the report."
2. README's "If folded into GECK, 'GECK Loops' becomes a fourth adapter"
   note → update to reflect GECK's actual role: upstream launcher, not
   adapter.
3. ROADMAP §9 (merge-mode election): the generated launch prompt *is* the
   "initial prompt that already specified it" — when §9 is implemented, its
   elicitation should skip when `mission-spec.md` frontmatter carries
   `merge_mode`.
