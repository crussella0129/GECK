# GECK

A tool for generating macro-prompts, as well as a GitHub Repo framework, for use with Agentic CLI tools like Claude Code, Codex, Cursor, Antigravity, and other LLM-powered development assistants involved in software engineering sensitive to preservation of context across turns.

## Contents

- **GECK/** - The Garden of Eden Creation Kit protocol specifications (v1.0, v1.1, v1.2, v1.3)
- **geck_generator/** - A GUI/CLI tool to generate GECK project files (Python reference implementation)
- **crates/** - Rust workspace hosting `geck-core` (library) and `geck-cli` (the `geck` binary)

---

## What is GECK?

**GECK (Garden of Eden Creation Kit)** is a lightweight protocol that gives CLI-based LLM agents structured memory and task management across sessions. It solves the "context amnesia" problem where AI assistants forget what they were working on between conversations.

### The Problem GECK Solves

When working with CLI LLM agents (Claude Code, Aider, Cursor, etc.):
- Each session starts fresh with no memory of previous work
- The AI may repeat mistakes or forget decisions made earlier
- There's no audit trail of what changed and why
- Large projects lose coherence across multiple sessions

### How GECK Works

GECK (v1.3) creates a structured folder in your project:

```
your_project/
└── GECK/
    ├── LLM_init.md         # Project goals, constraints, context budget
    ├── GECK_Inst.md        # Instructions for the AI agent (protocol v1.3)
    ├── env.md              # Environment documentation
    ├── tasks.md            # Typed tasks with stable TASK-NNN IDs
    ├── log.md              # Episodic per-turn log (tightened format)
    ├── log_index.jsonl     # Machine-readable log index (one JSON line per entry)
    ├── decisions.md        # Index of decision records
    ├── decisions/          # Per-decision files (DECISION-NNN.md)
    ├── learnings.md        # Index of learning records
    ├── learnings/          # Per-learning files (LEARNING-NNN.md)
    └── log_archive/        # Rolled-over log entries
```

At the start of each session, you point the AI to these files. It reads only the slice it needs (driven by the declared **Context Budget**), understands what was done before, and continues where it left off.

---

## GECK Generator

The GECK Generator is a tool that helps you create `LLM_init.md` files and initialize GECK folder structures for your projects.

### Installation

#### Option 1: Run from Source (Recommended)

1. Clone this repository:
   ```bash
   git clone https://github.com/crussella0129/GECK.git
   cd GECK
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the generator:
   ```bash
   # GUI mode
   python -m geck_generator --gui

   # Interactive CLI mode
   python -m geck_generator --cli
   ```

#### Option 2: Install via pip (Development Mode)

```bash
git clone https://github.com/crussella0129/GECK.git
cd GECK
pip install -e .
```
Note: the username in the URL will match yours if you forked as a template.
Then run with:
```bash
geck-generator --gui
```

#### Option 3: Create Desktop/Start Menu Shortcuts

After cloning and installing dependencies, create shortcuts for easy access:

```bash
cd GECK

# Create both desktop and start menu shortcuts
python -m geck_generator --install-shortcut

# Or create only desktop shortcut
python -m geck_generator --install-shortcut desktop

# Or create only start menu shortcut
python -m geck_generator --install-shortcut menu
```

To remove shortcuts:
```bash
python -m geck_generator --uninstall-shortcut
```

### Usage

#### GUI Mode

```bash
python -m geck_generator --gui
```

The GUI provides a tabbed interface to:
1. Enter basic project information (name, repo URL, local path)
2. Select a preset profile (Web App, CLI Tool, Data Science, etc.)
3. Define goals and success criteria
4. Preview and save the generated files

#### CLI Mode

```bash
python -m geck_generator --cli
```

Interactive prompts guide you through the same process in your terminal.

To create a full GECK folder structure:
```bash
python -m geck_generator --cli --init-geck
```

#### Quick Generation with Profiles

```bash
# List available profiles
python -m geck_generator --list-profiles

# Generate from a profile
python -m geck_generator --profile web_app --project-name "My App" --goal "Build a REST API" -o ./LLM_init.md
```

---

## Rust Toolchain (`geck` binary)

A second, native implementation of the generator lives under `crates/`. It
ships as a single `geck` binary, targets the same v1.3 protocol, and
produces output byte-equivalent to the Python generator (see
`scripts/check_parity.sh`).

### Build

```bash
cargo build --release --bin geck
# target/release/geck (or target/<triple>/release/geck)
```

### Commands

```bash
# Protocol version this binary targets
geck protocol-version

# List preset profiles (same registry as the Python tool)
geck list-profiles
geck list-profiles --json

# List built-in templates
geck list-templates

# Render an LLM_init.md from flags to stdout
geck generate \
    --project-name "My App" \
    --goal "Build a REST API" \
    --profile api

# Scaffold a full GECK/ folder in a project directory
geck init ./my_project \
    --project-name "My App" \
    --goal "Build a REST API" \
    --profile api
```

### Cross-tool parity

`scripts/check_parity.sh` scaffolds the same project through both the
Python generator and the `geck` binary and asserts that every
deterministic piece of output (file tree, `log_index.jsonl` record,
`GECK_Inst.md`, task lines, `LLM_init.md` modulo the Created-date line,
and the empty decisions/learnings indexes) matches. Run it any time you
touch templates or scaffold logic on either side.

### Why two implementations?

Python remains the reference (and the home of the GUI). Rust gives a
zero-runtime-dependency CLI and a library (`geck-core`) that other Rust
tools — e.g. a future GECK editor — can embed directly.

---

## Using GECK with CLI LLM Agents

### Initial Setup

1. **Create your project repository** and clone it locally

2. **Generate LLM_init.md** using GECK Generator:
   ```bash
   cd your_project
   python -m geck_generator --gui
   ```
   Fill in your project goals, constraints, and success criteria.

3. **Start your CLI LLM agent** (Claude Code, Aider, etc.) and give it this prompt:
   ```
   Read LLM_init.md and initialize the GECK.
   ```

4. The AI will create the `GECK/` folder with all necessary files and summarize its understanding of your project.

### Daily Workflow

**Starting a session:**
```
Read the GECK files and continue working on the project.
```

The AI will:
- Read `LLM_init.md` for goals
- Check `log.md` for what happened last session
- Review `tasks.md` for current work items
- Pick up where you left off

**During work:**
- The AI commits changes incrementally
- Updates `tasks.md` as work progresses
- Logs significant actions to `log.md`

**Ending a session:**
- The AI will update the log with what was accomplished
- Mark tasks complete or note blockers
- State its checkpoint status (CONTINUE/WAIT/ROLLBACK)

### Example Session Prompts

```
# Starting fresh
Read LLM_init.md and initialize the GECK.

# Continuing work
Read the GECK and continue with the next task.

# Checking status
Read tasks.md and summarize what's done and what's remaining.

# After a break
Read the last log entry and remind me where we left off.
```

### Tips for Best Results with GECK Generator

1. **Be specific in LLM_init.md** - Clear success criteria help the AI know when it's done

2. **Use profiles** - The GECK Generator profiles include suggested success criteria and constraints for common project types

3. **Review log entries** - The AI's log entries help you understand its reasoning and catch issues early

4. **Trust the checkpoints** - When the AI says WAIT, it genuinely needs your input. Don't skip these.

5. **Commit the GECK folder** - Keep `GECK/` in version control so the history is preserved

---

## GECK Protocol Versions

| Version | Status | Description |
|---------|--------|-------------|
| v1.3 | Current | Typed tasks (TASK-NNN), decisions/learnings as first-class records, Drift Check, tiered log + JSONL index, Context Budget |
| v1.2 | Stable | Added GECK_Inst.md for AI agent instructions |
| v1.1 | Stable | Work modes, simplified file names |
| v1.0 | Legacy | Initial release |

See `GECK/GECK_Macro_v1.3.md` for the full protocol specification.

### Why v1.3

v1.3 sharpens the protocol around how a fresh agent reconstructs context across sessions:

- **Typed tasks with stable IDs.** Tasks are addressable as `TASK-NNN` with a TYPE/SCOPE/OWNER header, so log entries and decisions can reference them without ambiguity.
- **Decisions and learnings are first-class.** Each is a per-record file under `decisions/` or `learnings/` with YAML frontmatter, indexed by `decisions.md` / `learnings.md` — the same composition pattern used by Claude Code's memory system, adapted clean-room for git.
- **Tightened log + JSONL index.** `log.md` keeps the human-auditable narrative (Did / Files / State / Refs / Next); `log_index.jsonl` gives the next agent a one-line-per-entry index it can scan cheaply.
- **Drift Check.** A short cognitive checksum at session start catches stale assumptions before they propagate.
- **Context Budget.** A `small` / `medium` / `large` parameter declared in `LLM_init.md` tells the next agent how many recent log entries to load (3 / 10 / 25), so the protocol adapts to the model window without per-agent guessing.

---

## Requirements

**Python generator (GUI + CLI + parity-reference):**
- Python 3.10+
- tkinter (usually included with Python)
- jinja2
- questionary (for CLI mode)

Install with:
```bash
pip install -r requirements.txt
```

**Rust `geck` binary (optional, native CLI):**
- Rust 1.75+ (stable)

Build with:
```bash
cargo build --release --bin geck
```

---

## License

See [LICENSE](LICENSE) file.
