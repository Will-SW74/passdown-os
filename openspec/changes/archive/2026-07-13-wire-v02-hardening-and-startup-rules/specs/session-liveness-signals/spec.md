## ADDED Requirements

### Requirement: Session lock lifecycle

The framework SHALL treat `sessions/.active_lock` as a liveness marker (duty tag), not a record. An agent starting a session MUST first check whether the lock exists, then overwrite it with its agent code and session start timestamp (`YYYY-MM-DD HH:mm`). An agent completing the Session End Protocol MUST delete the lock as the final step, after all handoff artifacts pass read-back verification. The lock file MUST be excluded from version control.

#### Scenario: Normal session lifecycle

- **WHEN** an agent starts a session and no `.active_lock` exists
- **THEN** the agent creates the lock with its agent code and start timestamp, and deletes it as the final step of the Session End Protocol

#### Scenario: Residual lock detected at session start

- **WHEN** an agent starts a session and `.active_lock` already exists
- **THEN** the agent treats the previous session as abnormally terminated, reads the latest session log under `sessions/` (excluding `archive/`), repairs `handoff/CURRENT.md` to reflect the true state, and only then overwrites the lock for its own session

#### Scenario: Forced interruption preserves the signal

- **WHEN** a session is interrupted before the Session End Protocol completes
- **THEN** the lock remains on disk, and no handoff content is lost by its presence, because all records live in `sessions/*.md` and the lock contains only the agent code and start timestamp

### Requirement: Externally counted checkpoint reminders

The checkpoint trigger SHALL NOT depend on the model counting its own tool calls. Where the agent tool supports lifecycle hooks, a PostToolUse hook MUST increment the counter file `sessions/.toolcount` after every tool call, and on every 10th call the hook MUST emit a reminder instructing the agent to append a progress line to the current session log. A SessionStart hook MUST reset the counter to zero. Environments without hooks SHALL treat the counting rule as best-effort discipline and MUST NOT claim it is mechanically enforced. The counter file MUST be excluded from version control.

#### Scenario: Reminder on every 10th tool call

- **WHEN** the PostToolUse hook runs and the incremented counter value is a multiple of 10
- **THEN** the hook emits a checkpoint reminder for injection into the agent context

##### Example: counter boundary behavior

| Counter after increment | Reminder emitted | Notes |
| --- | --- | --- |
| 9 | no | below threshold |
| 10 | yes | first checkpoint |
| 11 | no | between checkpoints |
| 20 | yes | second checkpoint |

#### Scenario: Counter reset at session start

- **WHEN** a new session starts in a hook-enabled environment
- **THEN** the SessionStart hook resets `sessions/.toolcount` to zero before any tool call is counted

#### Scenario: Corrupt or missing counter file

- **WHEN** the PostToolUse hook reads `sessions/.toolcount` and the file is missing or contains a non-numeric value
- **THEN** the hook treats the current count as zero and continues without error
