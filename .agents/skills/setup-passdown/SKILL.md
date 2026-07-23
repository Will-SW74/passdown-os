---
name: setup-passdown
description: Safely initialize or validate a pure-Markdown Passdown state directory for durable cross-session and cross-agent project continuity. Use when a user asks to add, install, initialize, bootstrap, or verify Passdown in a project, especially before work will move between agents or machines.
---

# Setup Passdown

Create a project-controlled `passdown-os/` without overwriting existing state. Use this skill's `assets/passdown-os/` directory as the only template source.

## Workflow

1. Resolve the project root from the user's explicit path; otherwise use the current workspace root.
2. Resolve the target as `<project-root>/passdown-os` and the source relative to this SKILL.md as `assets/passdown-os`.
3. Inspect before writing:
   - Target absent: continue with initialization.
   - Target present and compatible: validate it, report `already initialized`, and do not change any file.
   - Target present but incomplete or incompatible: list missing or conflicting required files and stop without writing.
4. Determine `agent_id` from the active agent or tool name. Use `unknown` only when the environment exposes no identity, and report that fallback.
5. Determine one concrete next step from the user's request and project context. It must name one action and an observable completion condition. If no honest next step can be derived, ask the user before writing.
6. Copy the complete asset tree to the absent target.
7. Rewrite only the copied `handoff/CURRENT.md`:
   - Generate `updated_at` as the current ISO 8601 UTC time.
   - Generate `handoff_id` as `YYYYMMDDTHHMMSSZ-agent_id-three-to-five-word-slug`.
   - Replace every example field with actual initialization facts.
   - Remove `template_example`.
   - Keep `context_anchors`, `blockers`, and `suggested_skills` as empty lists unless verified values exist.
8. Read every required file back and run the validation checklist.

## Required files

- `CONSTITUTION.md`
- `handoff/CURRENT.md`
- `handoff/_template.md`
- `sessions/_template.md`
- `memory/decisions.md`
- `memory/known-issues.md`

Treat an existing target as compatible only when all required files exist, CURRENT has the required front-matter fields, its local anchors resolve, and it has no unresolved template token. Custom prose and additional files are compatible and MUST NOT be overwritten.

## Validation checklist

Verify all of the following before reporting success:

- Every required file exists and is readable.
- CURRENT contains `schema_version`, `handoff_id`, `updated_at`, `agent_id`, `active_work`, `where_we_left_off`, `next_concrete_step`, `context_anchors`, `blockers`, and `suggested_skills`.
- `handoff_id` contains UTC time, agent identity, and a three-to-five-word lowercase English slug.
- `next_concrete_step` is neither empty nor generic continuation text.
- `template_example` and template tokens are absent from CURRENT.
- Every local context-anchor path exists relative to the project root; HTTP(S) URLs are accepted without copying their content.
- Every context anchor contains only `ref` and `purpose`.
- Every suggested skill contains only `name`, `reason`, and `availability`; availability is `available` or `unverified`.

## Failure handling

- Never merge or overwrite an existing incompatible target.
- If copying or rewriting fails, report each file that exists and each required file that is missing. State that setup is incomplete; do not claim rollback or success.
- Never import tool-private memory, credentials, transcripts, third-party skill bodies, tracker data, or hooks during setup.

## Result

Return the target path, `handoff_id`, `agent_id`, concrete next step, file validation count, and either `initialized`, `already initialized`, or `incomplete`.
