## MODIFIED Requirements

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
