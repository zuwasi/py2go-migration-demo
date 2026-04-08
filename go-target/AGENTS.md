# Go Target — Directory-Scoped Instructions

<instructions>

## Coding Standards (Go-specific)

- **Naming**: Exported = `PascalCase`, unexported = `camelCase`. No `Get` prefix on getters.
- **Errors**: Always `fmt.Errorf("methodName: %w", err)` — never bare `return err`.
- **Interfaces**: Define at the *consumer* site, not the provider. Keep to 1–2 methods max.
- **Constructors**: `NewFoo(deps) (*Foo, error)` — validate inputs, return error.
- **Immutability**: Prefer value receivers. Use pointer receivers only when mutation is required.
- **No `init()`** functions — wire everything in `main()` or a `Setup()` function.
- **Table-driven tests** — every test file uses `tests := []struct{ … }` pattern.
- **Context propagation** — first parameter of any I/O function is `ctx context.Context`.

## Package Rules

| Package            | May import                     | Must NOT import        |
|--------------------|--------------------------------|------------------------|
| `kodit.go` (root)  | `internal/*`                   | `cmd/*`                |
| `internal/store`   | `database/sql`, domain types   | `net/http`, `internal/server` |
| `internal/server`  | root package, `internal/store` | —                      |
| `cmd/kodit`        | root package only              | `internal/*` directly  |

## File Naming

- One primary type per file: `search.go` holds `type SearchService struct`.
- Tests: `search_test.go` in the same package.
- Integration tests: `search_integration_test.go` with `//go:build integration` tag.

</instructions>
