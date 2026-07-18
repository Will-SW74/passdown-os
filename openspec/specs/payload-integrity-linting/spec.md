# payload-integrity-linting Specification

## Purpose

TBD - created by archiving change 'fix-claude-review-findings'. Update Purpose after archive.

## Requirements

### Requirement: Managed payload text is UTF-8 without BOM

The Passdown lint tool SHALL inspect the raw bytes of managed payload text before semantic checks. Markdown, hook JSON, shell, and Python payload files inside the lint root MUST NOT begin with the UTF-8 BOM byte sequence `EF BB BF`. A violation SHALL produce the stable error code `UTF8_BOM` and the path relative to the lint root. The scan MUST preserve the lint tool's existing exclusions for archives, imports, transcripts, version-control metadata, and generated caches.

#### Scenario: Shell hook contains UTF-8 BOM

- **WHEN** a managed `.sh` hook begins with bytes `EF BB BF`
- **THEN** lint reports `UTF8_BOM` for that shell hook and exits nonzero

#### Scenario: Markdown payload contains UTF-8 BOM

- **WHEN** a managed `.md` payload file begins with bytes `EF BB BF`
- **THEN** lint reports `UTF8_BOM` for that Markdown file and exits nonzero

#### Scenario: Excluded transcript contains arbitrary bytes

- **WHEN** a file under `transcripts/` contains a BOM or non-text bytes
- **THEN** payload text validation ignores the file and does not report an encoding error for it

#### Scenario: Managed text has UTF-8 without BOM

- **WHEN** every managed text file decodes as UTF-8 and none begins with `EF BB BF`
- **THEN** the encoding check adds no lint error

---
### Requirement: Literal inline code does not trigger placeholder errors

The placeholder check SHALL remove HTML comments and single-line Markdown inline code spans before matching angle-bracket placeholders in `handoff/CURRENT.md` and `PROJECT_MANIFEST.md`. Angle-bracket text outside those excluded regions MUST continue to produce `PLACEHOLDER_REMAINS`.

#### Scenario: Inline path example contains angle brackets

- **WHEN** `handoff/CURRENT.md` contains the inline code span `` `<repo>/.codex/hooks.json` `` and no angle-bracket placeholder outside inline code
- **THEN** lint does not report `PLACEHOLDER_REMAINS`

#### Scenario: Unfilled placeholder remains in normal text

- **WHEN** `handoff/CURRENT.md` contains `<next-step>` outside HTML comments and inline code
- **THEN** lint reports `PLACEHOLDER_REMAINS` and exits nonzero

---
### Requirement: Windows writing guidance produces UTF-8 without BOM

The installation guide SHALL distinguish PowerShell 7 from Windows PowerShell 5.1. PowerShell 7 guidance MUST use an explicit no-BOM encoding. Windows PowerShell 5.1 guidance MUST use a .NET UTF-8 encoder configured without BOM and MUST NOT claim that `-Encoding utf8` satisfies the no-BOM rule.

#### Scenario: Agent follows PowerShell 5.1 guidance

- **WHEN** an installation agent writes a payload text file using the documented Windows PowerShell 5.1 method
- **THEN** the resulting file is UTF-8 and does not begin with `EF BB BF`
