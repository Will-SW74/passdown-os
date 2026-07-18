# codex-hook-resilience Specification

## Purpose

TBD - created by archiving change 'fix-claude-review-findings'. Update Purpose after archive.

## Requirements

### Requirement: Windows SessionStart remains observable during recoverable filesystem failures

The Codex Windows SessionStart hook SHALL invoke a testable Python adapter with an explicit Passdown OS root. The adapter MUST attempt to reset `sessions/.toolcount` to zero, but a missing or unwritable counter directory MUST NOT prevent it from emitting the contents of `handoff/CURRENT.md`. If CURRENT.md is missing or unreadable, the adapter SHALL emit an explicit warning without an unhandled traceback.

#### Scenario: Counter reset and handoff injection succeed

- **WHEN** the configured Passdown OS root contains writable `sessions/` and readable `handoff/CURRENT.md`
- **THEN** the adapter writes `0` to `sessions/.toolcount`, emits the CURRENT.md content, and exits successfully

#### Scenario: Counter reset fails but handoff remains readable

- **WHEN** the adapter cannot create or overwrite `sessions/.toolcount` and `handoff/CURRENT.md` is readable
- **THEN** it emits a reset warning followed by the CURRENT.md content, produces no Python traceback, and exits successfully

#### Scenario: Handoff file is unavailable

- **WHEN** `handoff/CURRENT.md` is missing or unreadable
- **THEN** the adapter emits an explicit handoff warning, produces no Python traceback, and exits successfully

---
### Requirement: Windows PostToolUse locates Git Bash without assuming one git.exe layout

The Codex Windows PostToolUse hook SHALL invoke the Python adapter with an explicit Passdown OS root. The adapter MUST prefer a valid `sh` discovered on PATH. If PATH has no valid `sh`, it SHALL inspect the valid `git.exe` path and its ancestor directories for `bin/sh.exe` and `usr/bin/sh.exe`. It MUST invoke `entrypoints/hooks/checkpoint-counter.sh --json` with the first valid shell candidate. If no valid shell exists, it SHALL exit zero without invoking a subprocess or emitting a traceback.

#### Scenario: sh is available on PATH

- **WHEN** PATH resolves `sh` to a regular executable file
- **THEN** the adapter invokes that shell with the checkpoint script and `--json`

#### Scenario: git resolves through the cmd layout

- **WHEN** PATH has no valid `sh`, `git.exe` resolves under `<GitRoot>/cmd/`, and `<GitRoot>/bin/sh.exe` exists
- **THEN** the adapter invokes `<GitRoot>/bin/sh.exe` with the checkpoint script and `--json`

#### Scenario: git resolves through the mingw64 layout

- **WHEN** PATH has no valid `sh`, `git.exe` resolves under `<GitRoot>/mingw64/bin/`, and `<GitRoot>/usr/bin/sh.exe` exists
- **THEN** the adapter invokes `<GitRoot>/usr/bin/sh.exe` with the checkpoint script and `--json`

#### Scenario: git is a shim with no discoverable shell

- **WHEN** PATH resolves `git.exe` to a shim location whose ancestors contain neither `bin/sh.exe` nor `usr/bin/sh.exe`
- **THEN** the adapter exits zero without invoking a subprocess or emitting a traceback

---
### Requirement: Source and downstream Codex hook layouts use the same adapter contract

The source repository `.codex/hooks.json` SHALL invoke the adapter with `.` as the Passdown OS root. The downstream `entrypoints/hooks/codex-hooks.json.example` SHALL invoke the payload copy of the adapter with `passdown-os` as the root. Both hook JSON files MUST remain parseable and MUST preserve their existing POSIX commands and Codex Stop transcript commands.

#### Scenario: Hook configurations are parsed after migration

- **WHEN** both Codex hook JSON files are loaded after the adapter migration
- **THEN** each Windows SessionStart and PostToolUse command targets the correct layout, both JSON documents parse successfully, and the POSIX and Stop commands are unchanged
