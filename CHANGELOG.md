# Changelog

All notable changes to Basis are recorded here. The project uses semantic versioning.

## 0.2.0 — 2026-11-09

### Changed

- Concise findings and a readable repair are now the default for pasted text.
- Exact excerpts and supported claims remain available through full-ledger mode.
- Audit-only responses use concise findings unless a full ledger is necessary or requested.

### Added

- Dependency-free npm commands for validation, unit tests, skill discovery, and agent-specific installation.
- `npm test` coverage in continuous integration.

## 0.1.0 — 2026-11-09

### Added

- Portable agent skill with provided-source, open-research, and no-source modes.
- Claim ledger with six statuses, four severity levels, exact evidence, and conservative repairs.
- Twenty-four checks covering evidence fit, citations, quotations, numbers, dates, reasoning, and draft consistency.
- Prompt-injection and private-source safeguards.
- Claude Code, Cursor, Skills CLI, and OpenAI-compatible package metadata.
- JSON Schema and a dependency-free report validator with cross-reference and count checks.
- Fictional worked example, eight development evaluation cases, unit tests, and GitHub Actions validation.
- Contribution, agent-maintenance, security, and launch documentation.
