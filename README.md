# Python → Go Migration with Amp

A ready-to-use project scaffold for migrating a Python codebase to Go using [Amp](https://ampcode.com) as your AI coding agent.

Inspired by [Winder.ai's field report](https://winder.ai/python-to-go-migration-with-claude-code/) on migrating Kodit from Python to Go with Claude Code — this project shows how Amp's native tools solve the problems they encountered.

## Why This Exists

The Winder.ai article documented five recurring problems with AI-assisted migration:

| Problem | What happened | How this scaffold prevents it |
|---------|--------------|-------------------------------|
| **Phantom features** | AI rebuilt a deprecated `snippets` table from dead code references | Pre-migration call-graph analysis skips dead symbols automatically |
| **Context window blowup** | Cross-cutting tasks (e.g., pagination) missed half the endpoints | Parallel `Task` sub-agents — one per endpoint, no shared context pressure |
| **Architectural drift** | Everything landed in `internal/` — no public API | Public API layout defined upfront in `AGENTS.md` |
| **Dead code accumulation** | Orphaned functions after refactors went unnoticed for days | Dead-code sweep runs after **every task**, not as an afterthought |
| **No integration tests** | Unit tests passed, but the system returned wrong search results | `tmux`-based smoke tests start the server and hit real endpoints after each phase |

## Project Structure

```
py2go-migration-demo/
├── AGENTS.md                           # Project-wide migration rules, translation tables, verification workflow
├── MIGRATION_TASKS.md                  # Dependency-aware task list (consumed by Ralph skill)
├── python-source/                      # DROP YOUR PYTHON CODE HERE (read-only during migration)
│   └── example/                        # Sample Python files to demonstrate the workflow
│       ├── models.py
│       ├── repository.py
│       └── server.py
├── go-target/                          # Generated Go code lands here
│   └── AGENTS.md                       # Directory-scoped Go coding standards & package rules
└── .agents/
    └── skills/
        └── py2go-migrate/
            └── SKILL.md                # Custom Amp skill that drives the entire migration
```

## Quick Start

### Prerequisites

- [Amp CLI](https://ampcode.com) installed
- Go 1.22+ installed
- Your Python source code

### Step 1: Clone and add your code

```bash
git clone https://github.com/zuwasi/py2go-migration-demo.git
cd py2go-migration-demo

# Replace the example files with your actual Python project
rm -rf python-source/example/
cp -r /path/to/your/python/project/* python-source/
```

### Step 2: Customize the migration config

Edit these files for your project:

1. **`AGENTS.md`** — Update the translation rules table and dependency map for your specific Python libraries and their Go equivalents.

2. **`MIGRATION_TASKS.md`** — Replace the example tasks with your actual source→target file mappings. Keep the dependency structure (`Depends on:` fields).

3. **`go-target/AGENTS.md`** — Adjust the package rules table to match your Go module layout.

### Step 3: Run the migration

Open Amp in the project directory and either:

**Option A — Use the custom skill (recommended):**
```
> load the py2go-migrate skill and start the migration
```

**Option B — Use Ralph for task-by-task execution:**
```
> run ralph on MIGRATION_TASKS.md
```

**Option C — Run tasks manually:**
```
> Migrate python-source/models.py to Go following the translation rules in AGENTS.md
```

## How It Works

### AGENTS.md (replaces CLAUDE.md)

Amp's `AGENTS.md` system is **hierarchical and directory-scoped**. The root `AGENTS.md` contains project-wide rules (translation tables, golden rules, verification workflow), while `go-target/AGENTS.md` contains Go-specific coding standards that only apply to files in that directory.

This means the AI automatically gets the right context for the right files — no need to load a single monolithic instruction file.

### MIGRATION_TASKS.md (replaces MIGRATION.md)

A structured task list with:
- **Dependency tracking** — tasks specify what must complete first
- **Acceptance criteria** — checkboxes the agent must satisfy
- **Phase grouping** — smoke tests run at phase boundaries
- **Dead code log** — skipped Python symbols are recorded, not silently ignored

### py2go-migrate Skill

A custom Amp skill that encodes the entire migration workflow:

1. **Discovery** — scans the Python codebase, builds a call graph, identifies dead code
2. **Pre-filter** — dead symbols are logged and excluded *before* any Go code is written
3. **Task loop** — Ralph picks the next ready task, executes it, verifies, sweeps for dead code
4. **Cross-cutting work** — spawns parallel sub-agents when a task touches many files
5. **Smoke tests** — starts the server via tmux, hits endpoints, compares against Python baseline

### Parallel Sub-Agents for Cross-Cutting Tasks

When a task touches many files (e.g., "add pagination to all list endpoints"), the skill spawns one `Task` sub-agent per endpoint:

```
Task 1: "Add pagination to GET /repositories — add limit/offset, update store query, add test"
Task 2: "Add pagination to GET /enrichments — same pattern"
Task 3: "Add pagination to GET /searches — same pattern"
```

Each runs in its own context window — no blowup, no missed endpoints.

## Adapting for Your Project

### Different source language?

The translation rules table in `AGENTS.md` is language-agnostic in structure. Replace the Python→Go mappings with your source→target equivalents (e.g., Java→Rust, TypeScript→Go).

### Different target language?

Replace `go-target/AGENTS.md` with coding standards for your target language. Update the verification commands in the root `AGENTS.md` (e.g., `cargo build` instead of `go build`).

### Larger codebase?

Add more tasks to `MIGRATION_TASKS.md` with proper dependency chains. The Ralph skill handles any number of tasks — it just picks the next one with all dependencies satisfied.

## Key Differences from the Bash-Loop Approach

| Aspect | Bash loop + Claude Code | Amp scaffold |
|--------|------------------------|--------------|
| Resumption | Stateless — reads file each session | Ralph tracks state with dependencies |
| Context management | Single context window for everything | Sub-agents for cross-cutting work |
| Coding standards | Single CLAUDE.md file | Hierarchical, directory-scoped AGENTS.md |
| Dead code detection | Manual "ask Claude to check" | Automated after every task |
| Integration testing | None during migration | tmux smoke tests at phase boundaries |
| Phantom feature prevention | "Clean up dead refs" (advice) | Call-graph pre-filter (automated) |

## License

MIT — use this scaffold for any migration project.

## Credits

- Migration methodology inspired by [Dr. Phil Winder's article](https://winder.ai/python-to-go-migration-with-claude-code/)
- Built for [Amp](https://ampcode.com) by [ESL](https://github.com/zuwasi)
