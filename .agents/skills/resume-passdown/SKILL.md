---
name: resume-passdown
description: Resume a project from its durable Passdown state, validate handoff integrity, and deterministically repair CURRENT from a newer complete session log. Use when starting or resuming work in a project containing passdown-os, switching agents or machines, or investigating an interrupted or inconsistent handoff.
---

# Resume Passdown

Load only the state required to continue safely. Treat `passdown-os/` as authoritative over tool-private memory.

## Workflow

1. Resolve the project root from the user's explicit path; otherwise use the current workspace root.
2. Require `passdown-os/CONSTITUTION.md` and `passdown-os/handoff/CURRENT.md`. If either is missing, report `recovery-required` and stop.
3. Read CONSTITUTION, then CURRENT. Do not scan all historical logs or referenced artifacts first.
4. Validate CURRENT against the durable state contract:
   - Require `schema_version`, `handoff_id`, `updated_at`, `agent_id`, `active_work`, `where_we_left_off`, `next_concrete_step`, `context_anchors`, `blockers`, and `suggested_skills`.
   - Reject an empty, template-like, or generic continuation next step.
   - Require each local anchor to exist relative to the project root. Accept HTTP(S) URLs without fetching or copying them.
   - Require every anchor to contain only `ref` and `purpose`, and every suggested skill to contain only `name`, `reason`, and `availability`.
   - Require suggestion availability to be `available` or `unverified`; a reason must name its relationship to the next step or a blocker.
5. Inspect `passdown-os/sessions/*.md`, excluding `_template.md`. Classify each log as complete or incomplete; a complete log has every required current-state field plus `work_performed`, `verification`, and `unfinished_reason`.
6. Track incomplete logs as possible partial writes. Select the complete log with the latest parseable `updated_at`. Use timestamps inside front matter, not filename order or filesystem modification time.
7. Apply the recovery table.
8. After a successful state decision, load only the anchors required for the concrete next step.
9. Return the resume summary in the required format.

## Recovery table

- No session logs and complete CURRENT: treat as a valid initialized state and summarize CURRENT.
- CURRENT and newest complete log share `handoff_id`: summarize CURRENT.
- Newest complete log has a later `updated_at`: reconstruct CURRENT from that log, preserving the CURRENT document shape; read the result back and require matching fields and identifier.
- An incomplete log is newer than CURRENT, has an invalid timestamp, or shares CURRENT's timestamp with another identifier: report `recovery-required` and list its missing or conflicting fields.
- CURRENT has a later `updated_at` than every log: report `recovery-required` because the corresponding log might be a partial write.
- Equal timestamps with different identifiers, an invalid timestamp, missing required fields, conflicting newest logs, or an invalid local anchor: report `recovery-required` with each conflicting field and do not write.

Never merge two sources by intuition. Deterministic reconstruction uses one newer complete log as the sole source.

## Suggested skills

Keep every suggestion available to the receiving agent without making it a dependency:

- Preserve `name` and task-specific `reason`.
- Set `availability` to `available` only when the current environment exposes that skill by name.
- Otherwise report it as `unverified`; do not remove it and do not block resume.
- A compatible skill with another name can satisfy the reason without changing durable state.

## Resume summary

Return exactly these sections:

- `Status`: `ready`, `recovered`, or `recovery-required`.
- `Active work`
- `Where we left off`
- `Next concrete step`
- `Context anchors`: each reference plus its purpose.
- `Blockers`
- `Suggested skills`: name, reason, and current availability.
- `Verification`: source identifier, source timestamp, and read-back result.

For `recovery-required`, replace normal continuation advice with the missing or conflicting fields and the smallest user action needed to establish one authoritative source.

## Write boundary

Only deterministic recovery from one newer complete log authorizes a write. Ordinary resume is read-only. Never install skills, fetch external artifacts, modify logs, or copy third-party instructions.
