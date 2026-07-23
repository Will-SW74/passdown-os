# Passdown Constitution

This directory is the project-controlled source of truth for continuity between agents and sessions. Tool-private memory is supplementary and MUST NOT be the only place where project state or decisions exist.

## Required layout

- `handoff/CURRENT.md`: the only current-state entry point.
- `handoff/_template.md`: the canonical current-state data shape.
- `sessions/_template.md`: the canonical durable session-log data shape.
- `sessions/*.md`: append-only logs for sessions that changed durable state.
- `memory/decisions.md`: decisions that affect later work.
- `memory/known-issues.md`: reproducible problems and verified workarounds.

## Lifecycle

1. Setup creates the required layout only when it can do so without overwriting incompatible content.
2. Resume reads this file and `handoff/CURRENT.md` before following context anchors.
3. Handoff records a durable change and verifies its output before reporting completion.

## Durable state contract

`CURRENT.md` and every session log MUST contain YAML front matter with:

- `schema_version`
- `handoff_id`
- `updated_at`
- `agent_id`
- `active_work`
- `where_we_left_off`
- `next_concrete_step`
- `context_anchors`
- `blockers`
- `suggested_skills`

Session logs MUST additionally contain `work_performed`, `verification`, and `unfinished_reason`.

Each non-initial `handoff_id` MUST combine an ISO 8601 UTC timestamp, the free-form `agent_id`, and a three-to-five-word lowercase English slug. `next_concrete_step` MUST name one executable action and its observable completion condition.

Each context anchor MUST contain only `ref` and `purpose`. `ref` MUST be a project-root-relative path or an HTTP(S) URL. Do not copy artifact bodies into a handoff.

Each suggested skill MUST contain only `name`, `reason`, and `availability`. `availability` MUST be `available` or `unverified`. A missing suggested skill never blocks state access or recovery.

## Event-driven logging

Create a session log when code, artifacts, decisions, blockers, the concrete next step, or project direction changes durably. Evaluate handoff when switching agents, switching work items, preparing context compression, responding to an explicit handoff request, or observing one of those durable changes.

Do not modify CURRENT or create an empty log for explanatory discussion with no durable state change. When uncertain whether a change is durable, prefer recording it.

Context percentages and conversation counts are advisory signals, not portable hard requirements.

## Deterministic recovery

Compare CURRENT with the newest complete session log by `updated_at` and `handoff_id`.

- Matching identifiers: resume from CURRENT.
- Newer complete log: reconstruct CURRENT from that log, then read it back.
- Missing fields, conflicting identifiers at the same time, invalid anchors, or an unknown newest source: report `recovery-required` with the exact conflicts and do not invent a merged state.
- A template example with no session logs is a valid newly initialized state.

## Verification policy

Every write MUST be read back. Verify required files, fields, identifiers, unresolved placeholders, and local anchor existence. Report partial writes explicitly.

Independent second review is required for destructive changes, security-sensitive work, and architecture decisions. Ordinary Markdown state updates require read-back but do not require another agent.

Agent identities are free-form strings. Subagents, model tiers, external trackers, spec systems, hooks, and third-party skills are optional integrations rather than runtime dependencies.
