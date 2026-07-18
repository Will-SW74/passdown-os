## MODIFIED Requirements

### Requirement: Semantic handoff integrity check

The Session Start Protocol SHALL verify handoff integrity by comparing the filename of the most recent eligible session log against the first entry of the Direct Memory Source field in `handoff/CURRENT.md`. Eligible logs MUST be direct children of `sessions/`, MUST match `YYYY-MM-DD-HHmm-<agent>-<slug>.md`, and MUST NOT be inside `sessions/archive/`. `INDEX.md`, `_template.md`, dotfiles, and Markdown files outside that naming contract MUST NOT participate in newest-log selection. Timestamp comparison between CURRENT.md and a log SHALL NOT be the primary integrity check. Session log filenames SHALL use the session start time as their timestamp component.

#### Scenario: Handoff is consistent

- **WHEN** the most recent eligible session log filename matches the first Direct Memory Source entry in CURRENT.md
- **THEN** the handoff is treated as complete and the agent proceeds without recovery

#### Scenario: Handoff is inconsistent

- **WHEN** the most recent eligible session log filename does not match the first Direct Memory Source entry in CURRENT.md
- **THEN** the agent enters the recovery flow: it reads the most recent eligible session log, repairs CURRENT.md to reflect the true state, and records the recovery in its own session log

##### Example: newest log not referenced

- **GIVEN** `sessions/` contains `2026-07-11-0900-cc-fix-parser.md` and `2026-07-11-1400-codex-add-tests.md`, and CURRENT.md Direct Memory Source lists `2026-07-11-0900-cc-fix-parser.md`
- **WHEN** an agent runs the integrity check at session start
- **THEN** the check fails because the newest eligible log is `2026-07-11-1400-codex-add-tests.md`, and the recovery flow starts from that file

#### Scenario: Index and template are newer than the latest log

- **WHEN** `sessions/INDEX.md` or `sessions/_template.md` has a newer modification time than every eligible session log
- **THEN** the integrity check ignores those files and compares CURRENT.md against the most recent eligible session log

### Requirement: Portable memory anchors

Direct Memory Source entries written as backticked paths SHALL be relative to the Passdown OS root. Markdown links SHALL be relative to the directory containing the Markdown source file, matching standard Markdown resolution and the lint implementation. Code Symbol Anchors SHALL include a symbol name and MUST NOT use machine-specific absolute paths or `file:///` URIs. Line ranges SHALL remain optional navigation aids and MUST NOT be the only way to identify code.

#### Scenario: Direct Memory Source is written during handoff

- **WHEN** an agent records a session log in the Direct Memory Source field of `handoff/CURRENT.md`
- **THEN** it writes a backticked Passdown-root-relative path such as `sessions/2026-07-18-0900-codex-fix-hooks.md`

#### Scenario: Markdown anchor points from handoff to source-repo code

- **WHEN** source-repo `handoff/CURRENT.md` links to the `run` symbol in `tools/passdown-lint.py`
- **THEN** the Markdown target is relative to the handoff file, such as `../tools/passdown-lint.py`, and the anchor text or adjacent prose names `run`

#### Scenario: Markdown anchor points from downstream payload to project code

- **WHEN** `passdown-os/handoff/CURRENT.md` links to the `parseHeader` symbol in project-root `src/parser.js`
- **THEN** the Markdown target begins with `../../src/parser.js`, contains no machine-specific absolute path, and the anchor text or adjacent prose names `parseHeader`
