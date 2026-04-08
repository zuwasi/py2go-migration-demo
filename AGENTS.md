# Python → Go Migration — Project AGENTS.md

<instructions>

## Project Structure

```
py2go-migration-demo/
├── python-source/     # Original Python codebase (READ-ONLY — never modify)
├── go-target/         # New Go implementation
├── AGENTS.md          # THIS FILE — project-wide migration rules
├── go-target/AGENTS.md  # Go-specific coding standards (scoped)
└── MIGRATION_TASKS.md # Ralph task list with dependencies
```

## Golden Rules

1. **Never modify `python-source/`** — it is the single source of truth.
2. **Test-first** — write the Go test before the implementation.
3. **Dead-code sweep after every refactor** — run `go vet ./...` and search for unreferenced exported symbols.
4. **Smoke-test after every phase** — start the server, hit `/health`, run a sample query.
5. **No phantom features** — only migrate code that is *actively called*. If a Python symbol has zero callers, skip it and log it in `MIGRATION_TASKS.md` under "Skipped (dead code)".

## Translation Rules

| Python                        | Go equivalent                              | Notes                                              |
|-------------------------------|--------------------------------------------|----------------------------------------------------|
| `class Foo(Base):`            | `type Foo struct{ Base }` or interface     | Prefer composition; interfaces stay small           |
| `@dataclass`                  | `type Foo struct{}` + `NewFoo()` ctor      | Constructor returns `(*Foo, error)` for validation  |
| `raise ValueError(msg)`      | `return fmt.Errorf("foo: %w", err)`        | Always wrap with context                           |
| `try/except`                  | `if err != nil { … }`                      | Check immediately; no naked returns                |
| `Optional[T]`                | `*T` or `(T, bool)` return                | Pointer for struct fields; bool-pair for lookups   |
| `list comprehension`          | `for` loop + `append`                      | Pre-allocate with `make([]T, 0, cap)` when known   |
| `@abstractmethod`            | Interface with single method               | Name: `Verber` (e.g., `Searcher`, `Indexer`)       |
| `async def` / `asyncio`      | goroutine + channel or `errgroup`          | Prefer `errgroup` for fan-out                      |
| `Dict[str, Any]`             | Typed struct — **never `map[string]any`**  |                                                    |
| `logging.getLogger(__name__)` | `slog.Logger` via dependency injection     |                                                    |
| Pydantic model                | struct + `Validate() error` method         |                                                    |
| SQLAlchemy model              | SQLC or raw `database/sql` with struct scan|                                                    |
| FastAPI router                | `net/http.ServeMux` or chi router          |                                                    |
| pytest fixture                | `testing.T` + helper returning cleanup fn  |                                                    |

## Dependency Map

| Python package     | Go equivalent            |
|--------------------|--------------------------|
| FastAPI            | `net/http` + `chi`       |
| SQLAlchemy         | `database/sql` + `sqlc`  |
| Pydantic           | struct + validate method  |
| numpy              | `gonum.org/v1/gonum`     |
| sentence-transform | External embedding API   |
| pytest             | `testing` stdlib         |
| httpx              | `net/http` stdlib        |
| alembic            | `golang-migrate/migrate` |

## Public API Design (prevent architectural drift)

The Go module **must** expose a public client package:

```
go-target/
├── kodit.go           # Public entry: NewClient(), top-level types
├── search.go          # Public: Search(), SearchOptions
├── index.go           # Public: Index(), IndexOptions
├── internal/          # Private implementation only
│   ├── store/
│   ├── embeddings/
│   └── server/
└── cmd/kodit/main.go  # CLI + HTTP server
```

> Anything in `internal/` must be accessed **only** through the public API types.
> The AI must never move a public type into `internal/`.

## Configuration Management

- All config lives in a single `type Config struct` with `envconfig` tags.
- Defaults are set in `NewDefaultConfig()`.
- Validation is in `Config.Validate() error`.
- **No** scattered `os.Getenv()` calls in downstream code.

## Verification Workflow (every task)

After completing each migration task the agent MUST:

1. `go build ./...`
2. `go test ./... -count=1`
3. `go vet ./...`
4. `staticcheck ./...` (if available)
5. Search for dead code: `grep -rn` for exported symbols with zero external references
6. If the task completes a **phase**, also run the smoke-test script:
   ```
   go run ./cmd/kodit serve &
   sleep 2
   curl -sf http://localhost:8080/health
   curl -sf http://localhost:8080/api/v1/search -d '{"query":"test"}'
   kill %1
   ```

</instructions>
