## ADDED Requirements

### Requirement: Context saturation thresholds use observable signals

The 60 percent defensive-save threshold and 70 percent hard-stop threshold SHALL apply only when the active agent exposes a current context-usage measurement whose source and verification date are recorded in the agent facts table. When no such measurement is available, the agent MUST use 15 conversation turns as the mandatory defensive-save threshold and MUST NOT estimate a percentage from model introspection or nominal context capacity. Verified external tool-call checkpoints SHALL provide earlier reminders but SHALL NOT be converted into context percentages.

#### Scenario: Current usage is externally measurable

- **WHEN** the active agent exposes a verified current context-usage measurement
- **THEN** the agent applies the 60 percent defensive-save threshold and the 70 percent hard-stop threshold to that measurement

#### Scenario: Current usage is not externally measurable

- **WHEN** the agent facts table has no verified current context-usage source for the active agent
- **THEN** the agent starts the save-and-handoff flow at 15 conversation turns and makes no claim about its current percentage

#### Scenario: Tool-call checkpoint fires before the turn limit

- **WHEN** a verified external checkpoint reminder fires before 15 conversation turns
- **THEN** the agent records the requested progress checkpoint without treating the tool-call count as a context-usage percentage

## MODIFIED Requirements

### Requirement: Externally counted checkpoint reminders

The checkpoint trigger SHALL NOT depend on the model counting its own tool calls. Where the agent tool supports lifecycle hooks, a PostToolUse hook MUST increment the counter file sessions/.toolcount after every tool call, and on every 10th call the hook MUST emit a reminder instructing the agent to append a progress line to the current session log. The counter file MUST be initialized or reset to zero at the start of a session, either through a verified SessionStart hook or through the Session Start Protocol when no equivalent event exists. An environment SHALL claim mechanically enforced context injection only when a real lifecycle test has verified that the reminder is visible to the model context. Environments without verified injection SHALL treat the counting rule as best-effort discipline or component-tested automation and MUST NOT claim it is mechanically enforced. The counter file MUST be excluded from version control.

#### Scenario: Verified reminder on every 10th tool call

- **WHEN** a verified PostToolUse hook increments the counter to a multiple of 10
- **THEN** the hook emits a checkpoint reminder that is injected into the agent context

##### Example: counter boundary behavior

| Counter after increment | Reminder emitted | Notes |
| --- | --- | --- |
| 9 | no | below threshold |
| 10 | yes | first checkpoint |
| 11 | no | between checkpoints |
| 20 | yes | second checkpoint |

#### Scenario: Counter reset at session start

- **WHEN** a new session starts in a hook-enabled environment
- **THEN** a verified SessionStart hook or the Session Start Protocol resets sessions/.toolcount to zero before any tool call is counted

#### Scenario: Corrupt or missing counter file

- **WHEN** the PostToolUse hook reads sessions/.toolcount and the file is missing or contains a non-numeric value
- **THEN** the hook treats the current count as zero and continues without error

#### Scenario: Reminder visibility is not verified

- **WHEN** the counter command emits output but no real lifecycle test demonstrates model-context visibility
- **THEN** documentation marks the event component-tested or unverified and retains the discipline fallback
