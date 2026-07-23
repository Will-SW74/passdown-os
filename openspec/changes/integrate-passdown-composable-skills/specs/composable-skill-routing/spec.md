## ADDED Requirements

### Requirement: Grounded skill suggestions
A handoff SHALL represent each suggested skill with `name`, `reason`, and `availability`. The reason SHALL connect the skill to the concrete next step or a named blocker. The availability value MUST be either `available` or `unverified`.

#### Scenario: Suggest a skill visible in the current environment
- **WHEN** the current environment lists a skill that directly supports the next step
- **THEN** the handoff records the skill name, a task-specific reason, and availability `available`

#### Scenario: Preserve an unverified recommendation
- **WHEN** a relevant skill is known by name but its installation cannot be verified
- **THEN** the handoff records availability `unverified` and does not claim that the skill is installed

#### Scenario: Omit irrelevant suggestions
- **WHEN** no skill has a direct relationship to the next step or blockers
- **THEN** the handoff records an empty suggested-skills list

### Requirement: Artifact references without duplication
A handoff SHALL reference existing project artifacts by project-root-relative path or URL and SHALL state why each reference matters to the next step. It SHALL NOT copy the full content of specs, plans, ADRs, issues, commits, diffs, or third-party skills into the handoff.

#### Scenario: Reference an existing project specification
- **WHEN** the next step depends on an existing specification
- **THEN** the handoff records the specification path and its relevance without reproducing the specification body

#### Scenario: Reference an external issue
- **WHEN** the next step depends on an external issue or document
- **THEN** the handoff records its URL and relevance without copying the external document body

### Requirement: Routing remains optional and non-blocking
Suggested skills SHALL guide the next agent without becoming a runtime dependency of Passdown. A missing or renamed suggested skill SHALL NOT prevent setup, resume, handoff persistence, or access to artifact references.

#### Scenario: Resume without a suggested skill
- **WHEN** a handoff names a skill that is absent in the receiving environment
- **THEN** the receiving agent can still read all state and references and treats the suggestion as unverified

#### Scenario: Use a different compatible skill
- **WHEN** the receiving environment provides a different skill that satisfies the recorded reason
- **THEN** the agent can select that compatible skill without modifying the durable handoff schema

### Requirement: Third-party implementation boundary
The Passdown skills and templates SHALL NOT vendor, fork, or redistribute third-party skill instructions as part of composable routing. The integration documentation SHALL distinguish persistent continuity responsibilities from engineering-method responsibilities.

#### Scenario: Document integration with a third-party skill collection
- **WHEN** the evaluation describes compatibility with an external skill collection
- **THEN** it maps responsibilities and invocation points without embedding the external skill implementation
