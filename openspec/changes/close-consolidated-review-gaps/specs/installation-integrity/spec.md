## ADDED Requirements

### Requirement: Template payload preserves executable line endings

The installation payload SHALL include .gitattributes alongside .gitignore. The installed .gitattributes MUST contain a rule equivalent to *.sh text eol=lf, and every shell script shipped under entrypoints/hooks MUST use LF line endings.

#### Scenario: Framework is copied into a target project

- **WHEN** an agent follows INSTALL.md to copy the framework payload
- **THEN** the target passdown-os directory contains .gitattributes with the shell LF rule and all copied shell scripts contain no CRLF byte sequence

#### Scenario: Line-ending protection is missing

- **WHEN** the installed .gitattributes file is absent, lacks the shell LF rule, or a shipped shell script contains CRLF
- **THEN** installation validation fails with a diagnostic that identifies the missing rule or affected repository-relative script path

### Requirement: Agent entrypoints are verified after installation

For every enabled agent, the installer SHALL open a fresh agent session and verify that the Passdown OS entrypoint instructions are loaded before marking that agent as installed. For agy, the installer MUST test .agents/AGENTS.md first; if that location is not loaded, the installer MUST merge the same authoritative section into the repository-root AGENTS.md and test again. The final report MUST name the path that was proven effective and MUST NOT leave two unlabelled authoritative copies of the Passdown OS section.

#### Scenario: agy loads the candidate entrypoint

- **WHEN** a fresh agy session demonstrates that .agents/AGENTS.md was loaded
- **THEN** the installer records .agents/AGENTS.md as the effective path and does not create a duplicate root section

#### Scenario: agy requires the root fallback

- **WHEN** a fresh agy session does not load .agents/AGENTS.md
- **THEN** the installer merges the authoritative section into AGENTS.md, verifies it in another fresh session, and records AGENTS.md as the effective path

#### Scenario: Neither agy path is proven

- **WHEN** neither candidate path can be demonstrated in a fresh agy session
- **THEN** the installer reports the agy entrypoint as unverified and does not claim that Passdown OS startup rules are active

### Requirement: Hook automation claims are evidence-gated

The hook documentation SHALL maintain a verification matrix with agent, lifecycle event, output format, expected visibility, status, and verification date. Status MUST be one of verified, component-tested, or unverified. An event SHALL be marked verified only after a real agent lifecycle event demonstrates that the emitted content is visible to the model context. Script-only, fixture-only, or transcript-only evidence MUST be marked component-tested and MUST NOT support a claim of mechanized context injection.

#### Scenario: Real context injection is observed

- **WHEN** a real lifecycle event fires and the agent response demonstrates that the emitted reminder entered model context
- **THEN** the matrix marks that event verified with the verification date and the protocol can describe that event as mechanized injection

#### Scenario: Only the command component is tested

- **WHEN** a hook command succeeds against fixture input but no real agent lifecycle event proves model visibility
- **THEN** the matrix marks the event component-tested and the protocol retains a discipline fallback

#### Scenario: Verification cannot be performed

- **WHEN** the current environment cannot trigger an agent lifecycle event
- **THEN** the matrix keeps the event unverified and the installation report names the unverified event explicitly

### Requirement: Installation lint is deterministic

The source repository SHALL provide tools/passdown-lint.py using only the Python standard library. The installer SHALL run that source-side command against the target with --root; tools/ MUST NOT be copied into the target payload and the checker MUST NOT run during normal handoffs. The command interface SHALL be python tools/passdown-lint.py [--root PATH] [--json]. It MUST validate required payload files, the shell LF attribute and shell bytes, hook example JSON, repository-relative hook script references, unresolved placeholders in handoff/CURRENT.md and PROJECT_MANIFEST.md, non-archived local Markdown link targets, Markdown self-references, session index row targets, and handoff memory-anchor targets. It MUST exclude openspec/changes/archive, sessions/archive, references, and transcripts from content checks.

#### Scenario: Session index or Markdown navigation would loop or dead-end

- **WHEN** a Markdown link points back to its own source file, or a session index data row is a placeholder, lacks exactly one valid link, repeats a target, or points outside sessions/
- **THEN** installation validation fails with a stable diagnostic identifying the source document or index rule

#### Scenario: Source checker validates a target without entering the payload

- **WHEN** an installation agent runs the source repository checker with --root pointing to an installed passdown-os directory
- **THEN** validation can pass while the target contains no tools directory, and subsequent handoffs do not execute the checker

#### Scenario: Clean template passes

- **WHEN** the command runs against a valid Passdown OS template
- **THEN** it exits with code 0 and reports every required check as passed

#### Scenario: A required check fails

- **WHEN** any required file, rule, JSON document, script reference, placeholder rule, link target, anchor target, or LF invariant fails
- **THEN** the command exits with code 1 and emits an error containing a stable code, repository-relative path, and actionable message without an unhandled traceback

#### Scenario: JSON output is requested

- **WHEN** the command runs with --json
- **THEN** it emits one JSON object with boolean ok, string root, array checks, and array errors, where each error contains code, path, and message
