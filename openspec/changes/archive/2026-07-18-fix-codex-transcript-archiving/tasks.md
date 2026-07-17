## 1. Archiver and tests

- [x] 1.1 Implement "Codex Stop events create a project-local transcript snapshot" and "Snapshot naming is stable and portable" in `entrypoints/hooks/archive-codex-transcript.py`; verify the design topics "Use Stop as a continuous snapshot trigger", "Copy opaque bytes through an atomic replacement", "Recognize only explicit Passdown layouts", "Keep names stable across turns", and "Behavior" with archiver unit tests.
- [x] 1.2 Cover "Archiving fails closed without damaging an existing snapshot" through repeated updates, fallback identity, invalid JSON/event/source/cwd, and replacement preservation in `tools/test_codex_transcript_archiver.py`; verify with unittest discovery.

## 2. Hooks and installation

- [x] 2.1 Deliver "Installed Codex configuration enables continuous snapshots transparently" by adding Stop commands to source and downstream Codex hook JSON while retaining SessionStart/PostToolUse and removing unsupported root comment fields; verify both files parse and match the accepted schema shape.
- [x] 2.2 Update installation and golden-template guidance so Python, payload paths, `/hooks` review/trust, and fresh-task verification are explicit; verify with content review and passdown-lint.

## 3. Documentation and safety

- [x] 3.1 Document "Transcript snapshots remain local sensitive artifacts" and "Session semantics are documented without overstating lifecycle support" across the authoritative protocols and derived checklist; verify Markdown links and payload lint.
- [x] 3.2 Record the Windows fresh-task lifecycle evidence without committing its JSONL artifact; verify session id, JSONL parse, and source byte-prefix relationship.

## 4. Validation

- [x] 4.1 Verify the design "Acceptance criteria" by running all upstream tests, payload lint, Python compile, hook JSON checks, Spectra validation, and diff checks before publishing.
