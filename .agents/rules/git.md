---
trigger: always_on
---

# Incienso Shop: Git & Commit Standards

## Conventional Commits

Format:
```text
<type>(<scope>): <short imperative description>

- Detailed bullet point explaining technical rationale
- Another detail or reference
```

Allowed Types:
- `feat`: New user or system capability
- `fix`: Bug resolution
- `docs`: Documentation updates
- `style`: Formatting, Bootstrap 5 classes, CSS tokens, whitespace
- `refactor`: Restructuring without functional behavior change
- `perf`: Performance optimization (ORM queries, SQLite indexes, DiskCache)
- `test`: Adding or updating test cases
- `chore`: Tooling, dependencies, maintenance

Scopes: `users`, `creators`, `streams`, `videos`, `alerts`, `imports`, `analytics`, `core`, `ui`, `docs`.

## Branching

- Feature branches: `feature/<scope>-<description>`
- Bugfixes: `bugfix/<scope>-<description>`
- Hotfixes: `hotfix/<description>`
- Never commit directly to `main`.
