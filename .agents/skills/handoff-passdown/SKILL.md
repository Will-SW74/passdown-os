---
name: handoff-passdown
description: Persist a durable Passdown handoff for the next agent or session, including current state, one append-only session log, grounded skill suggestions, artifact references, decisions, known issues, and read-back verification. Use when ending work, switching agents or work items, preparing context compression, or explicitly asked to hand off a project.
---

# Handoff Passdown

Persist only project state that another agent needs. Treat `passdown-os/` as the shared source of truth and avoid copying existing artifact bodies.

## Workflow

1. Resolve the project root and require a compatible `passdown-os/` with CONSTITUTION, CURRENT, both templates, decisions memory, and known-issues memory.
2. Read CONSTITUTION, CURRENT, and the two templates. Read only anchors needed to establish current facts.
3. Compare the session with durable state and classify changes.
4. If no durable category changed, return `no durable state change`; do not modify CURRENT, sessions, decisions, or known issues.
5. Determine the active agent's free-form `agent_id`, current ISO 8601 UTC time, and a three-to-five-word lowercase English slug. Do not restrict identity to a vendor or model list; use `unknown` only when no identity is exposed.
6. Generate one `handoff_id` as `YYYYMMDDTHHMMSSZ-agent_id-slug` and use it in both outputs.
7. Build a complete state using the template contract. Reject missing fields, invalid anchors, an unusable next step, or ungrounded skill suggestions before writing.
8. Write the new session log first, then overwrite CURRENT. This order lets resume reconstruct CURRENT if interruption occurs between the pair.
9. Append a decision or known issue only when the session established one that affects later work. Reference existing specs, plans, ADRs, issues, commits, and diffs rather than duplicating them.
10. Read all written files back and verify the handoff before reporting completion.

## Durable change categories

A session log is required when at least one of these changed:

- Code or configuration
- Project artifacts such as specs, plans, tests, or documentation
- A durable decision or rejected alternative
- A blocker, failure mode, or verified workaround
- The concrete next step or its acceptance condition
- Project scope, direction, or active work

Switching agents, switching work items, preparing context compression, or an explicit handoff request triggers this evaluation but does not create an empty log by itself.

## State contract

CURRENT and the session log MUST share `schema_version`, `handoff_id`, `updated_at`, `agent_id`, `active_work`, `where_we_left_off`, `next_concrete_step`, `context_anchors`, `blockers`, and `suggested_skills`.

The session log MUST additionally contain:

- `work_performed`: concrete durable changes made.
- `verification`: commands or manual assertions actually completed.
- `unfinished_reason`: why work remains, or `none` when the work item is complete.

Write one executable and verifiable `next_concrete_step`; reject empty text, unresolved template values, and generic continuation wording.

## References and suggested skills

- Store each context anchor as `ref` plus `purpose`.
- Use project-root-relative paths or HTTP(S) URLs. Verify local paths; do not fetch URLs merely to complete handoff.
- Do not copy artifact or third-party skill bodies.
- Store each suggested skill as `name`, task-specific `reason`, and `availability`.
- Use `available` only when the current environment exposes that exact skill name; otherwise use `unverified`.
- Keep the list empty when no skill directly supports the next step or a blocker.
- Missing or renamed skills never block handoff.

## Verification

Read back the new log, CURRENT, and any appended memory entry. Confirm:

- The paired files exist and share identifier, timestamp, and current-state fields.
- Every required field is present and no template marker remains.
- The next step is executable and verifiable.
- Every local anchor resolves from the project root.
- Suggested skills contain only name, reason, and allowed availability.
- Exactly one new session log exists for this handoff.

If only one paired file exists, report `partial write`, name the present and missing side, and state that the next resume requires recovery. Never report success based only on attempted writes.

Require an independent second review for destructive changes, security-sensitive work, and architecture decisions. Ordinary Markdown handoffs require read-back only.

## Result

Return `completed`, `no durable state change`, or `partial write`, followed by `handoff_id`, files written, verification evidence, next step, blockers, and suggested skills.
