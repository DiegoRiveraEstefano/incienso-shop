---
trigger: always_on
---

# Incienso Shop: Living Documentation

1. **Single Source of Truth**:
   - Root markdown files (`README.md`, `DOCS.md`, `GUIDELINES.md`, `STYLE_GUIDE.md`, `DESING.md`, `SECURITY.md`, `CONTRIBUTING.md`, `CHANGELOG.md`, `AGENTS.md`) and the `/docs` folder contain the canonical specification of the system.
   - `/old-migrations/` is kept strictly as historical reference for the legacy domain schema.
2. **Synchronous Updates**:
   - If a model, service signature, role permission, table, filter, or environment variable changes, the corresponding root `.md` documentation must be updated in the same pull request.
3. **No Outdated Artifacts**:
   - Outdated specifications must be updated immediately, never silently abandoned.
