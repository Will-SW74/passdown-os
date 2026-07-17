## Context

The verified Codex hook interface has no SessionEnd event. Its turn-scoped `Stop` event includes `session_id`, `transcript_path`, `cwd`, and `hook_event_name`, so a continuous snapshot is the honest lifecycle model. Codex transcript format is not stable enough to parse as an application contract; the archiver therefore treats the source as opaque bytes.

## Goals / Non-Goals

**Goals:** automatically update one local snapshot per Codex task, work on Windows and POSIX, fail without damaging prior snapshots, and install correctly in downstream projects.

**Non-Goals:** parse or clean Codex JSONL, claim Stop is SessionEnd, commit transcripts, backfill every historical task, or implement equivalent AGY behavior.

## Decisions

### Use Stop as a continuous snapshot trigger

Each assistant turn updates the same destination for a session. Documentation explicitly distinguishes this from session termination.

### Copy opaque bytes through an atomic replacement

The archiver writes a temporary file in the destination directory, flushes it, and uses `os.replace`. A failed write or replacement leaves the existing snapshot intact.

### Recognize only explicit Passdown layouts

Downstream projects must contain `<cwd>/passdown-os/CONSTITUTION.md` and its transcripts directory. The source repo root layout is accepted only when the running archiver resolves to that root's `entrypoints/hooks/`, preventing an arbitrary directory with marker-like names from opting in.

### Keep names stable across turns

The normal name is `YYYY-MM-DD-HHmm-codex-<id8>.jsonl`, derived from the rollout start time and sanitized session id. Creation time and a basename hash provide portable fallbacks.

## Implementation Contract

### Behavior

- Valid Stop input creates or atomically updates one byte-identical snapshot.
- Repeated Stop input for one task keeps the same destination name.
- Invalid JSON, event, source, cwd, or replacement returns non-zero without transcript content in stderr and without damaging an old snapshot.
- The source repo and downstream hook JSON both retain SessionStart and PostToolUse while adding Stop.

### Acceptance criteria

- Standard-library tests cover the two recognized layouts, opaque copy, repeated update, normal/fallback naming, malformed input, invalid source/event/cwd, and replacement failure.
- Both hook JSON files parse with only the accepted root `hooks` field and reference deployed files.
- `python -m unittest discover -s tools -p 'test_*.py'`, `python tools/passdown-lint.py`, `spectra validate --all --strict`, and `git diff --check` pass.
- Fresh Windows Codex CLI evidence shows a trusted Stop hook produced a parseable snapshot matching its session id and source byte prefix.

## Risks / Trade-offs

- Copying the full transcript on every Stop adds I/O, accepted initially for correctness and simplicity.
- A source can append the hook-completion event after the copy; the snapshot is valid at copy time and the next Stop refreshes it.
- Raw transcripts can contain secrets, so they remain gitignored and must not be shared uncleaned.
