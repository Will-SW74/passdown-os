## MODIFIED Requirements

### Requirement: Portable memory anchors

Code Symbol Anchor instructions SHALL require repository-relative Markdown links together with a symbol name and line range. Absolute paths, including file URIs, SHALL NOT be used. Teaching examples that intentionally name a non-existent path MUST be represented as inline-code literals so Markdown link checkers do not treat them as repository targets. Every actual anchor written to handoff/CURRENT.md or a session log MUST resolve to an existing repository-relative file when the handoff is validated, while the symbol name remains the durable locator after line numbers drift.

#### Scenario: Anchor written during handoff

- **WHEN** an agent records a real Code Symbol Anchor in CURRENT.md or a session log
- **THEN** the anchor uses a repository-relative Markdown link with a symbol name and line range, contains no machine-specific absolute path, and resolves to an existing file

#### Scenario: Template displays a hypothetical anchor

- **WHEN** a template or protocol shows an anchor whose target does not exist in the framework repository
- **THEN** the complete example is wrapped as an inline-code literal and is not parsed as a local Markdown link

#### Scenario: Handoff anchor target is missing

- **WHEN** installation lint or handoff read-back validation encounters an actual memory anchor whose repository-relative target does not exist
- **THEN** validation fails with the anchor path and the handoff cannot be marked complete
