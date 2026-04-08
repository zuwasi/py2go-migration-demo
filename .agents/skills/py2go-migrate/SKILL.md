---
name: py2go-migrate
description: >
  Executes a Python-to-Go codebase migration using Amp's tools.
  Handles discovery, translation, verification, dead-code sweeps,
  and smoke tests. Triggers on: migrate python to go, py2go, 
  python go migration.
---

# Python → Go Migration Skill

## Overview
This skill drives a full Python-to-Go migration using Amp's native tools,
replacing the manual bash-loop + CLAUDE.md approach with structured automation.

## Phase 0 — Discovery (run once)

Use `finder` and `Read` in parallel to scan the Python source:

1. **Codebase scan** — `finder` to map all `.py` files, entry points, test setup
2. **Bounded contexts** — `finder` to identify logical groupings
3. **Call-graph analysis** — `Grep` for every class/function definition, then
   `Grep` for every call site. Symbols with **zero callers** → mark as dead code.
   This prevents the "phantom features" problem.
4. **Dependency inventory** — `Read` `requirements.txt` / `pyproject.toml`

### Dead-Code Pre-Filter (prevents phantom features)
```
For each symbol in python-source/:
  1. Grep for its definition
  2. Grep for all references (excluding the definition)
  3. If references == 0 → add to "Skipped (dead code)" in MIGRATION_TASKS.md
  4. Do NOT migrate it
```

> **This step alone would have prevented the biggest bug in the Winder.ai article**
> (phantom `snippets` table rebuilt from dead references).

## Phase 1–5 — Task Execution

Use the **ralph** skill to iterate through `MIGRATION_TASKS.md`:

1. Ralph picks the next ready task (all dependencies satisfied)
2. For each task:
   a. `Read` the Python source files listed in the task
   b. `finder` to understand how the Python code connects to other modules
   c. Write Go **test first** → `create_file`
   d. Write Go **implementation** → `create_file`
   e. Verify:
      ```
      cd go-target && go build ./...
      cd go-target && go test ./... -count=1
      cd go-target && go vet ./...
      ```
   f. Dead-code sweep (after every task, not just at the end):
      ```
      Grep for all exported symbols in the new file
      Grep for references to each symbol across go-target/
      Flag any with zero references
      ```
   g. Mark task complete in `MIGRATION_TASKS.md`
   h. `git add` only the changed files → `git commit`

### Cross-Cutting Tasks (pagination, middleware, etc.)

When a task touches many files (e.g., "add pagination to all list endpoints"):

- **Do NOT attempt in a single context window**
- Use `Task` tool to spawn **one sub-agent per endpoint**:
  ```
  Task 1: "Add pagination to GET /api/v1/repositories — read the route, 
           add limit/offset params, update the store query, add test"
  Task 2: "Add pagination to GET /api/v1/enrichments — same pattern"
  Task 3: "Add pagination to GET /api/v1/searches — same pattern"
  ```
- Each sub-agent gets the pagination pattern in its prompt (from AGENTS.md)
- They run in **parallel** — no context window pressure

## Phase 4 — Smoke Testing

Use the `tmux` skill to run integration tests:

```
1. tmux new-session -d -s kodit "cd go-target && go run ./cmd/kodit serve"
2. Sleep 3 seconds
3. Bash: curl -sf http://localhost:8080/health
4. Bash: curl -sf http://localhost:8080/api/v1/search -d '{"query":"test"}'
5. Compare response against python-source baseline (stored in testdata/)
6. tmux kill-session -t kodit
```

> This closes the "unit tests pass but system doesn't work" gap.

## Phase 5 — Final Dead-Code Sweep

```
1. go vet ./...
2. staticcheck ./...
3. For every exported symbol:
   - Grep for references outside its own file
   - If zero → delete or unexport
4. For every .go file:
   - If no other file imports its package → flag for removal
```

## Key Advantages Over Manual Bash Loop

| Problem from article           | Amp solution                                        |
|-------------------------------|-----------------------------------------------------|
| Context window blowup          | `Task` sub-agents for cross-cutting work            |
| Dead code accumulation         | Automated sweep after EVERY task, not just at end   |
| Phantom features               | Pre-migration call-graph analysis filters dead code |
| No integration tests           | `tmux` skill spins up server + curls endpoints      |
| Architectural drift            | Directory-scoped `AGENTS.md` enforces package rules |
| Stateless resumption via file  | `ralph` skill manages task list + dependencies      |
| Manual bash loop + git         | `ralph` loop with structured commits                |
| Config scattered everywhere    | AGENTS.md rule: single Config struct enforced       |
