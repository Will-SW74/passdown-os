# session-liveness-signals Specification

## Purpose

Define the requirements and behavioral specifications for session lifecycle locks (.active_lock) and PostToolUse checkpoint reminders (.toolcount) to mechanically prevent context window overload and trace unclean session terminations.

## Requirements

### Requirement: Session lock lifecycle

The framework SHALL treat `sessions/.active_lock` as a liveness marker (duty tag) and advisory concurrency guard, not a record. The lock MUST contain the agent code, session start timestamp (`YYYY-MM-DD HH:mm`), and a unique session identifier (4-8 random alphanumeric characters). An agent starting a session MUST first check whether the lock exists and MUST NOT overwrite an existing lock until the user confirms that no other agent is still working. After writing its lock, the agent MUST re-read it immediately and again before its first write to any project file; an ownership mismatch MUST stop the agent before it modifies project state. The check-then-write race window MUST be documented as a known limitation. An agent completing the Session End Protocol MUST delete the lock as the final step, after all handoff artifacts pass read-back verification. The lock file MUST be excluded from version control.

#### Scenario: Normal session lifecycle

- **WHEN** an agent starts a session and no `.active_lock` exists
- **THEN** the agent creates the lock with its agent code, start timestamp, and unique session identifier, re-reads it to confirm ownership, and deletes it as the final step of the Session End Protocol

#### Scenario: Active lock confirmed at session start

- **WHEN** an agent starts a session, `.active_lock` already exists, and the user confirms that its owner is still working
- **THEN** the agent stops without modifying any file and waits for the owner to complete the Session End Protocol

#### Scenario: Stale lock confirmed at session start

- **WHEN** an agent starts a session, `.active_lock` already exists, and the user confirms that no other agent is working
- **THEN** the agent treats the previous session as abnormally terminated, reads the latest session log under `sessions/` (excluding `archive/`), repairs `handoff/CURRENT.md` to reflect the true state, and only then replaces the stale lock with its own

#### Scenario: Lock ownership changes during startup

- **WHEN** the agent re-reads `.active_lock` immediately after writing it or before its first project-file write and the unique identifier is not its own
- **THEN** the agent stops without modifying project state and asks the user to arbitrate ownership again

#### Scenario: Forced interruption preserves the signal

- **WHEN** a session is interrupted before the Session End Protocol completes
- **THEN** the lock remains on disk, and no handoff content is lost by its presence, because all records live in `sessions/*.md` and the lock contains only the agent code, start timestamp, and unique session identifier


<!-- @trace
source: wire-v02-hardening-and-startup-rules
updated: 2026-07-13
code:
  - .opencode/commands/spectra-ingest.md
  - entrypoints/CODEX.md.example
  - entrypoints/hooks/archive-transcript.sh
  - GOLDEN_TEMPLATE.md
  - PROTOCOLS.md
  - .opencode/skills/spectra-audit/SKILL.md
  - .opencode/commands/spectra-archive.md
  - sessions/INDEX.md
  - .opencode/skills/spectra-debug/SKILL.md
  - .opencode/commands/spectra-discuss.md
  - .opencode/commands/spectra-propose.md
  - .opencode/commands/spectra-apply.md
  - .opencode/skills/spectra-discuss/SKILL.md
  - .opencode/skills/spectra-archive/SKILL.md
  - README.md
  - transcripts/.gitkeep
  - .opencode/skills/spectra-apply/SKILL.md
  - entrypoints/CLAUDE.md.example
  - entrypoints/hooks/checkpoint-counter.sh
  - entrypoints/hooks/settings.json.example
  - handoff/CURRENT.md
  - sessions/_template.md
  - entrypoints/hooks/agy-hooks.json.example
  - .opencode/skills/spectra-drift/SKILL.md
  - CLAUDE.md
  - memory/decisions.md
  - entrypoints/hooks/codex-hooks.json.example
  - .opencode/commands/spectra-commit.md
  - sessions/2026-07-12-1530-cc-wire-hardening-and-startup-rules.md
  - .opencode/skills/spectra-commit/SKILL.md
  - .opencode/skills/spectra-ingest/SKILL.md
  - INSTALL.md
  - .opencode/skills/spectra-ask/SKILL.md
  - CONSTITUTION.md
  - GEMINI.md
  - CHECKLIST_HANDOFF.md
  - handoff/_template.md
  - sessions/2026-07-13-0010-agy-resolve-antigravity-hook-standards.md
  - entrypoints/AGENTS.md.example
  - entrypoints/commands/handoff.md
  - entrypoints/hooks/README.md
  - DISPATCH.md
  - transcripts/README.md
  - AGENTS.md
  - .opencode/commands/spectra-drift.md
  - .opencode/skills/spectra-propose/SKILL.md
  - .opencode/commands/spectra-ask.md
  - .opencode/commands/spectra-audit.md
  - .opencode/commands/spectra-debug.md
  - .spectra.yaml
  - memory/local-agent-sync.md
-->

---
### Requirement: Externally counted checkpoint reminders

The checkpoint trigger SHALL NOT depend on the model counting its own tool calls. Where the agent tool supports lifecycle hooks, a PostToolUse hook MUST perform one read-increment-write attempt on `sessions/.toolcount` after every tool call, and on every observed multiple of 10 the hook MUST emit a reminder instructing the agent to append a progress line to the current session log. The counter file MUST be initialized or reset to zero at the start of a session, either through a SessionStart hook or through deletion by the previous Session End Protocol. Environments without hooks SHALL treat the counting rule as best-effort discipline and MUST NOT claim it is mechanically enforced. The counter file MUST be excluded from version control.

The framework MUST document that parallel PostToolUse processes can read the same value and overwrite one another, so the observed counter is advisory and is not exact telemetry. The `--json` mode MUST emit no output outside checkpoint boundaries. At a checkpoint boundary it SHALL emit one JSON object whose `hookSpecificOutput.hookEventName` equals `PostToolUse` and whose `hookSpecificOutput.additionalContext` is a non-empty string. Reminder text changes MUST preserve JSON parsing, including correct handling of double quotes and backslashes.

#### Scenario: Reminder on every observed 10th tool call

- **WHEN** the PostToolUse hook runs and the incremented counter value is a multiple of 10
- **THEN** the hook emits a checkpoint reminder for injection into the agent context

##### Example: sequential counter boundary behavior

| Counter after increment | Reminder emitted | Notes |
| --- | --- | --- |
| 9 | no | below threshold |
| 10 | yes | first checkpoint |
| 11 | no | between checkpoints |
| 20 | yes | second checkpoint |

#### Scenario: Counter reset at session start

- **WHEN** a new session starts in a hook-enabled environment
- **THEN** the SessionStart hook or the natural cleanup of the counter file from the previous session resets `sessions/.toolcount` to zero before any tool call is counted

#### Scenario: Corrupt or missing counter file

- **WHEN** the PostToolUse hook reads `sessions/.toolcount` and the file is missing or contains a non-numeric value
- **THEN** the hook treats the current count as zero and continues without error

#### Scenario: JSON checkpoint output is parsed

- **WHEN** `checkpoint-counter.sh --json` reaches an observed counter value of 10
- **THEN** standard JSON parsing succeeds, `hookEventName` equals `PostToolUse`, and `additionalContext` is non-empty

#### Scenario: JSON mode between checkpoints is silent

- **WHEN** `checkpoint-counter.sh --json` reaches an observed counter value that is not a multiple of 10
- **THEN** the hook emits no stdout payload

#### Scenario: Parallel increments collide

- **WHEN** two PostToolUse hook processes read the same counter value before either write completes
- **THEN** the framework permits the final counter to reflect one increment, documents the lost-update limitation, and does not represent the counter as exact telemetry
