# codex-transcript-archiving Specification

## Purpose

TBD - created by archiving change 'fix-codex-transcript-archiving'. Update Purpose after archive.

## Requirements

### Requirement: Codex Stop events create a project-local transcript snapshot

A trusted Codex Stop hook SHALL copy the opaque file referenced by `transcript_path` into the Passdown OS `transcripts/` directory. Repeated Stop events for the same `session_id` SHALL update the same destination file rather than create one file per turn. A downstream installation SHALL use `<cwd>/passdown-os/transcripts/`; the source repo deployment SHALL use `<cwd>/transcripts/` only when the archiver itself is located under that repo's `entrypoints/hooks/`.

#### Scenario: First Stop creates a snapshot

- **WHEN** a Stop hook receives a valid `session_id`, an existing transcript file, and a cwd containing a recognized Passdown OS layout
- **THEN** the archiver exits with code 0 and creates one non-empty JSONL snapshot whose bytes equal the source bytes at copy time

#### Scenario: Later Stop updates the same snapshot

- **WHEN** the source transcript grows and a later Stop hook receives the same `session_id`, `transcript_path`, and cwd
- **THEN** the archiver atomically replaces the prior destination content and retains the same destination filename

---
### Requirement: Snapshot naming is stable and portable

The archiver SHALL name normal Codex rollout snapshots `YYYY-MM-DD-HHmm-codex-<id8>.jsonl`, using the rollout start date and minute plus the first eight sanitized session-id characters. If the rollout filename lacks a parseable timestamp, the archiver MUST use the source creation time. If the session id is empty or unsafe, the archiver MUST use the first eight hexadecimal characters of a SHA-256 hash of the source filename.

#### Scenario: Normal rollout filename is converted

- **WHEN** the source basename is `rollout-2026-07-17T13-30-40-019f6e8e-1ebc-76f2-b719-93570b8661df.jsonl` and the session id begins with `019f6e8e`
- **THEN** the destination basename is `2026-07-17-1330-codex-019f6e8e.jsonl`

---
### Requirement: Archiving fails closed without damaging an existing snapshot

The archiver MUST reject malformed JSON, an event other than Stop, a null or missing transcript, a source that is not a regular file, or a cwd that is not a recognized Passdown project. Failure MUST return a non-zero exit code, emit a single-line diagnostic on stderr without transcript content, and MUST NOT delete or truncate an existing snapshot.

#### Scenario: Replacement failure preserves the old snapshot

- **WHEN** a valid destination snapshot exists but the temporary write or atomic replacement fails
- **THEN** the existing destination remains unchanged and the archiver exits non-zero

##### Example: Atomic replace is denied

- **GIVEN** an existing destination containing bytes `old` and a valid source containing bytes `new`
- **WHEN** the operating system denies the atomic replacement
- **THEN** the destination still contains exactly `old` and the process exits non-zero

---
### Requirement: Installed Codex configuration enables continuous snapshots transparently

The source repo hook configuration and downstream Codex hook template SHALL contain a Stop command that invokes the shared Python archiver. Installation documentation MUST require hook review and trust after installation or modification and MUST distinguish component testing from a fresh Codex task proving a real Stop event updates the snapshot. Hook JSON SHALL contain only fields accepted by the Codex hook schema.

#### Scenario: New project installs the Stop hook

- **WHEN** an installer follows Passdown OS INSTALL instructions for Codex
- **THEN** the target `.codex/hooks.json` contains SessionStart, PostToolUse, and Stop hooks that reference files included in the target payload

---
### Requirement: Transcript snapshots remain local sensitive artifacts

The Passdown OS ignore rules SHALL exclude transcript JSONL files while retaining `transcripts/README.md` and `.gitkeep`. Documentation MUST state that snapshots can contain credentials, local paths, private conversations, and proprietary data; unclean snapshots MUST NOT be committed or shared.

#### Scenario: Snapshot is ignored by version control

- **WHEN** a JSONL snapshot is created under `transcripts/`
- **THEN** repository ignore evaluation excludes the snapshot while retaining the README and `.gitkeep` files

---
### Requirement: Session semantics are documented without overstating lifecycle support

Passdown OS documentation SHALL define one Codex task/thread as one transcript snapshot. A resumed task SHALL continue updating the same snapshot. Starting a new Passdown session that requires a separate raw transcript MUST use a new Codex task. Documentation MUST state that Stop is turn-scoped and that Codex has no SessionEnd event in the verified interface.

#### Scenario: Operator needs one transcript per work session

- **WHEN** an operator wants the next work session to have a separate raw transcript file
- **THEN** the usage documentation instructs the operator to start a new Codex task instead of resuming the prior task

##### Example: Work resumes on the next day

- **GIVEN** yesterday's Codex task already maps to one transcript snapshot
- **WHEN** the operator wants today's Passdown work to have a separate raw transcript
- **THEN** the operator starts a new Codex task and trusts the project hooks there
