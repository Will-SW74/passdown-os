# handoff-integrity Specification

## Purpose

Define the requirements and behavioral specifications for session handoff verification, including session lock lifecycle hooks, recovery procedures for unclean session terminations, and single source of truth (SSoT) rules consistency check.

## Requirements

### Requirement: Session lock full lifecycle

The framework SHALL define a session lock file at sessions/.active_lock with a complete lifecycle: created as the first action of the Session Start Protocol, arbitrated on presence at session start, and deleted as the final step of the Session End Protocol. The lock file SHALL contain the session start time (YYYY-MM-DD HH:mm, local machine time), the agent short code, and a unique session identifier (4-8 random alphanumeric characters). The lock SHALL be treated as an advisory concurrency guard: an agent MUST NOT overwrite an existing lock before ownership is arbitrated with the user, MUST re-read the lock immediately after writing it to confirm ownership, and MUST re-check ownership before its first write to any project file. The check-then-write race window SHALL be documented as a known limitation. The lock file SHALL be excluded from version control via .gitignore.

#### Scenario: Clean start with no existing lock

- **WHEN** an agent starts a session and sessions/.active_lock does not exist
- **THEN** the agent creates the lock file with the current session start time, its agent code, and a unique session identifier, re-reads it to confirm ownership, and proceeds with the Session Start Protocol

#### Scenario: Active lock confirmed at session start

- **WHEN** an agent starts a session, sessions/.active_lock already exists, and the user confirms the lock owner is still working
- **THEN** the agent stops immediately without modifying any file and waits for the owner to complete its End Protocol and remove the lock

#### Scenario: Stale lock confirmed at session start

- **WHEN** an agent starts a session, sessions/.active_lock already exists, and the user confirms no other agent is working
- **THEN** the agent treats the previous session's End Protocol as incomplete, reads the most recent session log to repair handoff/CURRENT.md, and only then replaces the stale lock with its own

#### Scenario: Lock ownership changed after startup

- **WHEN** an agent re-reads sessions/.active_lock (immediately after writing it, or before its first write to any project file) and the content is not its own session identifier
- **THEN** the agent stops immediately and re-arbitrates with the user before touching any file

#### Scenario: Lock removed at session end

- **WHEN** an agent completes the final step of the Session End Protocol
- **THEN** sessions/.active_lock no longer exists


<!-- @trace
source: fix-framework-review-findings
updated: 2026-07-12
code:
  - .opencode/skills/spectra-ingest/SKILL.md
  - .opencode/skills/spectra-propose/SKILL.md
  - AGENTS.md
  - GEMINI.md
  - entrypoints/commands/handoff.md
  - entrypoints/hooks/README.md
  - .opencode/skills/spectra-commit/SKILL.md
  - entrypoints/hooks/checkpoint-counter.sh
  - entrypoints/hooks/codex-hooks.json.example
  - memory/decisions.md
  - entrypoints/CLAUDE.md.example
  - .opencode/commands/spectra-commit.md
  - sessions/2026-07-12-1530-cc-wire-hardening-and-startup-rules.md
  - .opencode/skills/spectra-drift/SKILL.md
  - entrypoints/AGENTS.md.example
  - memory/local-agent-sync.md
  - .opencode/commands/spectra-discuss.md
  - handoff/_template.md
  - .opencode/commands/spectra-apply.md
  - .opencode/commands/spectra-audit.md
  - CLAUDE.md
  - .opencode/skills/spectra-audit/SKILL.md
  - .spectra.yaml
  - entrypoints/CODEX.md.example
  - entrypoints/hooks/agy-hooks.json.example
  - CHECKLIST_HANDOFF.md
  - PROTOCOLS.md
  - .opencode/commands/spectra-ask.md
  - .opencode/skills/spectra-ask/SKILL.md
  - README.md
  - .opencode/skills/spectra-discuss/SKILL.md
  - .opencode/commands/spectra-propose.md
  - entrypoints/hooks/settings.json.example
  - handoff/CURRENT.md
  - .opencode/commands/spectra-debug.md
  - .opencode/skills/spectra-archive/SKILL.md
  - CONSTITUTION.md
  - sessions/_template.md
  - .opencode/commands/spectra-archive.md
  - .opencode/commands/spectra-ingest.md
  - .opencode/skills/spectra-apply/SKILL.md
  - .opencode/commands/spectra-drift.md
  - GOLDEN_TEMPLATE.md
  - .opencode/skills/spectra-debug/SKILL.md
-->

---
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

---
### Requirement: Single source of truth for every rule

Every rule in the framework SHALL have exactly one authoritative location. A file that restates a procedure SHALL either be merged back into the authoritative file and removed, or be kept as a derived view that explicitly names its authoritative source at the top and defers to it on any inconsistency. A derived view SHALL NOT introduce normative content absent from its source.

#### Scenario: Unmarked duplicate is merged

- **WHEN** a file restates steps already defined in CONSTITUTION.md or PROTOCOLS.md without declaring an authoritative source
- **THEN** any non-duplicated content is merged into the authoritative file and the duplicate file is deleted from the repository

#### Scenario: Derived checklist declares its source

- **WHEN** a checklist file is kept as an operational check-off view of a protocol
- **THEN** it names its authoritative source at the top, defers to it on inconsistency, and contains no rules absent from the source


<!-- @trace
source: fix-framework-review-findings
updated: 2026-07-12
code:
  - .opencode/skills/spectra-ingest/SKILL.md
  - .opencode/skills/spectra-propose/SKILL.md
  - AGENTS.md
  - GEMINI.md
  - entrypoints/commands/handoff.md
  - entrypoints/hooks/README.md
  - .opencode/skills/spectra-commit/SKILL.md
  - entrypoints/hooks/checkpoint-counter.sh
  - entrypoints/hooks/codex-hooks.json.example
  - memory/decisions.md
  - entrypoints/CLAUDE.md.example
  - .opencode/commands/spectra-commit.md
  - sessions/2026-07-12-1530-cc-wire-hardening-and-startup-rules.md
  - .opencode/skills/spectra-drift/SKILL.md
  - entrypoints/AGENTS.md.example
  - memory/local-agent-sync.md
  - .opencode/commands/spectra-discuss.md
  - handoff/_template.md
  - .opencode/commands/spectra-apply.md
  - .opencode/commands/spectra-audit.md
  - CLAUDE.md
  - .opencode/skills/spectra-audit/SKILL.md
  - .spectra.yaml
  - entrypoints/CODEX.md.example
  - entrypoints/hooks/agy-hooks.json.example
  - CHECKLIST_HANDOFF.md
  - PROTOCOLS.md
  - .opencode/commands/spectra-ask.md
  - .opencode/skills/spectra-ask/SKILL.md
  - README.md
  - .opencode/skills/spectra-discuss/SKILL.md
  - .opencode/commands/spectra-propose.md
  - entrypoints/hooks/settings.json.example
  - handoff/CURRENT.md
  - .opencode/commands/spectra-debug.md
  - .opencode/skills/spectra-archive/SKILL.md
  - CONSTITUTION.md
  - sessions/_template.md
  - .opencode/commands/spectra-archive.md
  - .opencode/commands/spectra-ingest.md
  - .opencode/skills/spectra-apply/SKILL.md
  - .opencode/commands/spectra-drift.md
  - GOLDEN_TEMPLATE.md
  - .opencode/skills/spectra-debug/SKILL.md
-->

---
### Requirement: File map completeness

Every file and directory in the framework root SHALL be listed in the CONSTITUTION.md file map with its purpose and read-trigger, and SHALL be referenced by at least one protocol step, template, or guide. A file that no protocol ever points to SHALL be either wired into a protocol or removed.

#### Scenario: New file is added to the framework

- **WHEN** a new file is introduced into the framework
- **THEN** the file map gains a row for it and at least one protocol step or guide references it

#### Scenario: Template application preserves mapped files

- **WHEN** a user follows the GOLDEN_TEMPLATE.md reset checklist on a fresh copy
- **THEN** no file listed in the file map is deleted by following the checklist as written


<!-- @trace
source: fix-framework-review-findings
updated: 2026-07-12
code:
  - .opencode/skills/spectra-ingest/SKILL.md
  - .opencode/skills/spectra-propose/SKILL.md
  - AGENTS.md
  - GEMINI.md
  - entrypoints/commands/handoff.md
  - entrypoints/hooks/README.md
  - .opencode/skills/spectra-commit/SKILL.md
  - entrypoints/hooks/checkpoint-counter.sh
  - entrypoints/hooks/codex-hooks.json.example
  - memory/decisions.md
  - entrypoints/CLAUDE.md.example
  - .opencode/commands/spectra-commit.md
  - sessions/2026-07-12-1530-cc-wire-hardening-and-startup-rules.md
  - .opencode/skills/spectra-drift/SKILL.md
  - entrypoints/AGENTS.md.example
  - memory/local-agent-sync.md
  - .opencode/commands/spectra-discuss.md
  - handoff/_template.md
  - .opencode/commands/spectra-apply.md
  - .opencode/commands/spectra-audit.md
  - CLAUDE.md
  - .opencode/skills/spectra-audit/SKILL.md
  - .spectra.yaml
  - entrypoints/CODEX.md.example
  - entrypoints/hooks/agy-hooks.json.example
  - CHECKLIST_HANDOFF.md
  - PROTOCOLS.md
  - .opencode/commands/spectra-ask.md
  - .opencode/skills/spectra-ask/SKILL.md
  - README.md
  - .opencode/skills/spectra-discuss/SKILL.md
  - .opencode/commands/spectra-propose.md
  - entrypoints/hooks/settings.json.example
  - handoff/CURRENT.md
  - .opencode/commands/spectra-debug.md
  - .opencode/skills/spectra-archive/SKILL.md
  - CONSTITUTION.md
  - sessions/_template.md
  - .opencode/commands/spectra-archive.md
  - .opencode/commands/spectra-ingest.md
  - .opencode/skills/spectra-apply/SKILL.md
  - .opencode/commands/spectra-drift.md
  - GOLDEN_TEMPLATE.md
  - .opencode/skills/spectra-debug/SKILL.md
-->

---
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

---
### Requirement: Pre-compaction save is mechanized for Claude Code

The framework's hook templates SHALL include a PreCompact hook for Claude Code that reminds the agent to complete the Session End Protocol memory sync before any manual or automatic compaction, and the hooks guide SHALL document the hook's behavior and its verification status (verified or pending live-session testing) with a date.

#### Scenario: Compaction triggered in a cc session

- **WHEN** a Claude Code session with the hook installed is about to compact
- **THEN** the hook injects a reminder to save handoff state before compaction proceeds

<!-- @trace
source: fix-framework-review-findings
updated: 2026-07-12
code:
  - .opencode/skills/spectra-ingest/SKILL.md
  - .opencode/skills/spectra-propose/SKILL.md
  - AGENTS.md
  - GEMINI.md
  - entrypoints/commands/handoff.md
  - entrypoints/hooks/README.md
  - .opencode/skills/spectra-commit/SKILL.md
  - entrypoints/hooks/checkpoint-counter.sh
  - entrypoints/hooks/codex-hooks.json.example
  - memory/decisions.md
  - entrypoints/CLAUDE.md.example
  - .opencode/commands/spectra-commit.md
  - sessions/2026-07-12-1530-cc-wire-hardening-and-startup-rules.md
  - .opencode/skills/spectra-drift/SKILL.md
  - entrypoints/AGENTS.md.example
  - memory/local-agent-sync.md
  - .opencode/commands/spectra-discuss.md
  - handoff/_template.md
  - .opencode/commands/spectra-apply.md
  - .opencode/commands/spectra-audit.md
  - CLAUDE.md
  - .opencode/skills/spectra-audit/SKILL.md
  - .spectra.yaml
  - entrypoints/CODEX.md.example
  - entrypoints/hooks/agy-hooks.json.example
  - CHECKLIST_HANDOFF.md
  - PROTOCOLS.md
  - .opencode/commands/spectra-ask.md
  - .opencode/skills/spectra-ask/SKILL.md
  - README.md
  - .opencode/skills/spectra-discuss/SKILL.md
  - .opencode/commands/spectra-propose.md
  - entrypoints/hooks/settings.json.example
  - handoff/CURRENT.md
  - .opencode/commands/spectra-debug.md
  - .opencode/skills/spectra-archive/SKILL.md
  - CONSTITUTION.md
  - sessions/_template.md
  - .opencode/commands/spectra-archive.md
  - .opencode/commands/spectra-ingest.md
  - .opencode/skills/spectra-apply/SKILL.md
  - .opencode/commands/spectra-drift.md
  - GOLDEN_TEMPLATE.md
  - .opencode/skills/spectra-debug/SKILL.md
-->
