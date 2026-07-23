---
schema_version: 1
handoff_id: "20260101T010203Z-example-finish-parser-regression-fix"
updated_at: "2026-01-01T01:02:03Z"
agent_id: "example"
template_example: true
active_work: "Fix the parser regression described by the active specification"
where_we_left_off: "The failing input is reproduced and the implementation has not been changed."
next_concrete_step: "Add the regression assertion for empty input and confirm that it fails for the documented parser behavior."
context_anchors:
  - ref: "specs/parser/spec.md"
    purpose: "Defines the expected empty-input behavior."
blockers: []
suggested_skills:
  - name: "tdd"
    reason: "The next step is an explicit failing regression assertion."
    availability: "unverified"
work_performed:
  - "Reproduced the empty-input failure without modifying production code."
verification:
  - "Recorded the exact failing input and observed output in the active specification notes."
unfinished_reason: "Implementation begins in the next session so the failing assertion remains the first code change."
---

# Durable Session Log Template

Use the same `handoff_id` and current-state fields written to `handoff/CURRENT.md`. Replace every example value with session facts and remove `template_example` before completion.

## Work performed

- Reproduced the empty-input failure without modifying production code.

## Verification

- Recorded the exact failing input and observed output in the active specification notes.

## Unfinished reason

Implementation begins in the next session so the failing assertion remains the first code change.

## Next step

Add the regression assertion for empty input and confirm that it fails for the documented parser behavior.

## Context anchors

- `specs/parser/spec.md` — Defines the expected empty-input behavior.

## Blockers

None.

## Suggested skills

- `tdd` — The next step is an explicit failing regression assertion. Availability: `unverified`.
