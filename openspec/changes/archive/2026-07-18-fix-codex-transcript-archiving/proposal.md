## Why

Codex installations previously configured SessionStart and PostToolUse hooks but left raw transcript archiving as a manual copy step. This made `transcripts/` appear enabled while remaining empty, and downstream projects could not rely on Passdown OS to retain a local forensic snapshot.

## What Changes

- Add a cross-platform Python archiver driven by Codex's turn-scoped `Stop` hook.
- Update the source repo deployment and downstream hook template without using unsupported comment fields in `hooks.json`.
- Support the downstream `passdown-os/` layout and the source repo's root layout with explicit marker checks.
- Document task/thread semantics, trust requirements, runtime prerequisites, and raw transcript sensitivity.
- Add standard-library regression tests for copying, stable naming, repeated updates, layout detection, and safe failure.

## Capabilities

### New Capabilities

- `codex-transcript-archiving`: Continuous, local, failure-safe Codex transcript snapshots for Passdown OS.

### Modified Capabilities

None.

## Impact

- Runtime: `entrypoints/hooks/archive-codex-transcript.py`
- Hook configuration: `.codex/hooks.json`, `entrypoints/hooks/codex-hooks.json.example`
- Tests: `tools/test_codex_transcript_archiver.py`
- Documentation: `INSTALL.md`, `GOLDEN_TEMPLATE.md`, `CONSTITUTION.md`, `PROTOCOLS.md`, `CHECKLIST_HANDOFF.md`, `entrypoints/hooks/README.md`, `transcripts/README.md`
- Runtime JSONL snapshots remain gitignored and are not committed.
