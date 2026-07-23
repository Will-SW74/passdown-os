## ADDED Requirements

### Requirement: Safe project initialization
The setup workflow SHALL create the minimal Passdown directory from a single shared template source when the target directory does not exist. It SHALL create the constitution, initialized current state, handoff template, session template, decisions memory, and known-issues memory. It SHALL NOT overwrite an existing incompatible target.

#### Scenario: Initialize an empty project
- **WHEN** the setup workflow runs in a project without a `passdown-os` directory
- **THEN** all required Passdown files are created without unresolved placeholders

#### Scenario: Re-run setup on a complete installation
- **WHEN** the setup workflow runs against a complete compatible installation
- **THEN** it validates the installation and leaves every existing file unchanged

#### Scenario: Detect an incompatible existing target
- **WHEN** the target directory contains files that do not satisfy the required structure
- **THEN** the workflow lists the conflicting or missing files and stops without overwriting content

### Requirement: Durable current-state contract
The current state and session log SHALL record `handoff_id`, `updated_at`, `agent_id`, active work, prior stopping point, one concrete next step, context anchors, blockers, and suggested skills. A session log SHALL additionally record work performed, verification evidence, and an unfinished reason. The next concrete step MUST identify one executable and verifiable action.

#### Scenario: Persist a complete current state
- **WHEN** an agent records a handoff with durable project changes
- **THEN** the current state and new session log contain every required field and share the same unique `handoff_id`

#### Scenario: Reject an unusable next step
- **WHEN** the next concrete step is empty, contains an unresolved placeholder, or only says to continue the work
- **THEN** the handoff fails validation and identifies the invalid field

### Requirement: Deterministic resume and recovery
The resume workflow SHALL read the constitution and current state before loading referenced artifacts. It SHALL compare the current state with the newest complete session log using `handoff_id` and `updated_at`. It SHALL reconstruct the current state only when the newer complete log provides every required field; otherwise it SHALL surface a recovery-required blocker without inventing data.

#### Scenario: Resume a consistent handoff
- **WHEN** the current state and newest session log have the same `handoff_id`
- **THEN** the workflow reports active work, stopping point, next step, anchors, blockers, and suggested skills from the current state

#### Scenario: Recover from a newer complete log
- **WHEN** the newest complete session log has a later `updated_at` than the current state and contains every required field
- **THEN** the workflow reconstructs the current state from that log and verifies the reconstructed content by reading it back

#### Scenario: Stop on ambiguous recovery data
- **WHEN** the current state and newest log conflict and the newer source is incomplete or cannot be determined
- **THEN** the workflow reports recovery-required with the conflicting fields and does not synthesize a replacement state

### Requirement: Event-driven handoff logging
The handoff workflow SHALL add a session log when code, artifacts, decisions, blockers, the concrete next step, or project direction has changed durably. It SHALL NOT add a session log for a conversation that produces no durable state change. Switching agents, switching work items, preparing context compression, or an explicit handoff request SHALL trigger evaluation of the handoff workflow.

#### Scenario: Record durable work
- **WHEN** at least one durable state category changed during the session
- **THEN** the workflow updates current state and adds exactly one session log for that handoff

#### Scenario: Avoid an empty audit entry
- **WHEN** a session contains only explanatory discussion and does not change any durable state category
- **THEN** the workflow reports no durable state change and does not modify current state or add a session log

### Requirement: Read-back verification
Every setup, recovery, or handoff write SHALL be followed by a read-back that verifies required files, fields, identifiers, unresolved placeholders, and referenced project-relative paths. The workflow SHALL report partial-write details when verification fails.

#### Scenario: Verify a successful handoff
- **WHEN** current state and a session log are written successfully
- **THEN** read-back confirms matching identifiers, complete fields, and existing local anchor paths before completion is reported

#### Scenario: Detect a partial write
- **WHEN** only one side of the current-state and session-log pair is persisted
- **THEN** the workflow reports which artifact exists, which artifact is missing, and that the next resume requires recovery
