# handoff-integrity Specification

## Purpose

Define the requirements and behavioral specifications for session handoff verification, including session lock lifecycle hooks, recovery procedures for unclean session terminations, and single source of truth (SSoT) rules consistency check.

## Requirements

### Requirement: Session lock full lifecycle

The framework SHALL define a session lock file at sessions/.active_lock with a complete lifecycle: created as the first action of the Session Start Protocol, checked for stale presence at session start, and deleted as the final step of the Session End Protocol. The lock file SHALL contain the session start time (YYYY-MM-DD HH:mm, local machine time) and the agent short code. The lock file SHALL be excluded from version control via .gitignore.

#### Scenario: Clean start with no stale lock

- **WHEN** an agent starts a session and sessions/.active_lock does not exist
- **THEN** the agent creates the lock file with the current session start time and its agent code, and proceeds with the Session Start Protocol

#### Scenario: Stale lock detected at session start

- **WHEN** an agent starts a session and sessions/.active_lock already exists
- **THEN** the agent treats the previous session's End Protocol as incomplete, reads the most recent session log to repair handoff/CURRENT.md before continuing, and replaces the stale lock with its own

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

The Session Start Protocol SHALL verify handoff integrity by comparing the filename of the most recent log in sessions/ (excluding archive/) against the first entry of the Direct Memory Source field in handoff/CURRENT.md. Timestamp comparison SHALL NOT be the primary integrity check. Session log filenames SHALL use the session start time as their timestamp component.

#### Scenario: Handoff is consistent

- **WHEN** the most recent session log filename matches the first Direct Memory Source entry in CURRENT.md
- **THEN** the handoff is treated as complete and the agent proceeds without recovery

#### Scenario: Handoff is inconsistent

- **WHEN** the most recent session log filename does not match the first Direct Memory Source entry in CURRENT.md
- **THEN** the agent enters the recovery flow: it reads the most recent session log, repairs CURRENT.md to reflect the true state, and records the recovery in its own session log

##### Example: newest log not referenced

- **GIVEN** sessions/ contains 2026-07-11-0900-cc-fix-parser.md and 2026-07-11-1400-codex-add-tests.md, and CURRENT.md Direct Memory Source lists 2026-07-11-0900-cc-fix-parser.md
- **WHEN** an agent runs the integrity check at session start
- **THEN** the check fails because the newest log (1400-codex) is not referenced, and the recovery flow starts from 2026-07-11-1400-codex-add-tests.md


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

Code Symbol Anchor examples and instructions in templates and protocols SHALL use repository-relative paths together with a symbol name. Absolute paths (including file:/// URIs) SHALL NOT be used in anchor examples. Anchors SHALL name the symbol so the target remains locatable after line numbers drift.

#### Scenario: Anchor written during handoff

- **WHEN** an agent records a Code Symbol Anchor in CURRENT.md or a session log
- **THEN** the anchor uses a repository-relative path with a symbol name and line range, and contains no machine-specific absolute path


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