# Migration Task List (Ralph-compatible)

> This file is consumed by the `ralph` skill.
> Each task has an ID, dependencies, status, and acceptance criteria.

## Phase 1 — Domain Core

### Task 1: Domain types
- **ID**: domain-types
- **Depends on**: (none)
- **Source**: `python-source/models/domain.py`
- **Target**: `go-target/types.go`
- **Acceptance**:
  - [ ] All domain structs with `NewX()` constructors
  - [ ] `Validate() error` on every struct
  - [ ] Table-driven unit tests
  - [ ] `go vet` clean

### Task 2: Repository interfaces
- **ID**: repo-interfaces
- **Depends on**: domain-types
- **Source**: `python-source/repositories/base.py`
- **Target**: `go-target/repository.go`
- **Acceptance**:
  - [ ] Interfaces defined at consumer site
  - [ ] Context on every method
  - [ ] No implementation yet — interfaces only

### Task 3: Search types & scoring
- **ID**: search-types
- **Depends on**: domain-types
- **Source**: `python-source/search/models.py`, `python-source/search/scoring.py`
- **Target**: `go-target/search.go`
- **Acceptance**:
  - [ ] `SearchOptions`, `SearchResult` structs
  - [ ] Reciprocal Rank Fusion function with tests
  - [ ] Numerical parity with Python implementation (use same test vectors)

## Phase 2 — Data Layer

### Task 4: Database store (PostgreSQL)
- **ID**: db-store
- **Depends on**: repo-interfaces
- **Source**: `python-source/repositories/postgres.py`
- **Target**: `go-target/internal/store/postgres.go`
- **Acceptance**:
  - [ ] Implements repository interfaces
  - [ ] Uses `database/sql` + `pgx` driver
  - [ ] Migrations via `golang-migrate`
  - [ ] Integration tests with `//go:build integration`

### Task 5: Embedding client
- **ID**: embedding-client
- **Depends on**: domain-types
- **Source**: `python-source/embeddings/client.py`
- **Target**: `go-target/internal/embeddings/client.go`
- **Acceptance**:
  - [ ] Calls external embedding API (no local model)
  - [ ] Retry with exponential backoff
  - [ ] Vector format matches VectorChord expectations (verify truncation!)
  - [ ] Unit tests with HTTP mock

## Phase 3 — API & Server

### Task 6: HTTP server + routes
- **ID**: http-server
- **Depends on**: db-store, search-types, embedding-client
- **Source**: `python-source/server/app.py`, `python-source/server/routes/`
- **Target**: `go-target/internal/server/server.go`
- **Acceptance**:
  - [ ] All endpoints from Python OpenAPI spec
  - [ ] Pagination on ALL list endpoints (do NOT paginate in-memory)
  - [ ] Request/response types match Python OpenAPI schema
  - [ ] Middleware: logging, recovery, request-id

### Task 7: CLI entrypoint
- **ID**: cli
- **Depends on**: http-server
- **Source**: `python-source/cli/main.py`
- **Target**: `go-target/cmd/kodit/main.go`
- **Acceptance**:
  - [ ] `serve`, `index`, `search` subcommands
  - [ ] Config from env vars via `envconfig`
  - [ ] Single `Config` struct — no scattered `os.Getenv`

## Phase 4 — Public API & Verification

### Task 8: Public client API
- **ID**: public-api
- **Depends on**: http-server
- **Source**: (new — no Python equivalent)
- **Target**: `go-target/kodit.go`, `go-target/search.go`, `go-target/index.go`
- **Acceptance**:
  - [ ] `NewClient(Config) (*Client, error)`
  - [ ] `Client.Search(ctx, SearchOptions) ([]SearchResult, error)`
  - [ ] `Client.Index(ctx, IndexOptions) error`
  - [ ] Godoc examples compile

### Task 9: OpenAPI parity test
- **ID**: openapi-parity
- **Depends on**: http-server
- **Source**: `python-source/openapi.json`
- **Target**: `go-target/internal/server/openapi_test.go`
- **Acceptance**:
  - [ ] Auto-generate OpenAPI from Go server
  - [ ] Diff against Python `openapi.json`
  - [ ] Zero breaking differences

### Task 10: End-to-end smoke test
- **ID**: e2e-smoke
- **Depends on**: cli, public-api
- **Target**: `go-target/e2e_test.go`
- **Acceptance**:
  - [ ] Start server in test
  - [ ] Index a sample repo
  - [ ] Search and verify results match Python baseline
  - [ ] Compare vector distances (cosine, not L2!)

## Phase 5 — Cleanup

### Task 11: Dead-code sweep
- **ID**: dead-code
- **Depends on**: e2e-smoke
- **Acceptance**:
  - [ ] `go vet ./...` clean
  - [ ] `staticcheck ./...` clean
  - [ ] No exported symbol with zero external references
  - [ ] No files with zero imports

---

## Skipped (dead code in Python source)
<!-- Log Python symbols that have zero callers and were intentionally NOT migrated -->

## Session Log
<!-- Ralph appends session summaries here -->
