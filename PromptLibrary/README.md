# Prompt Library

## Purpose

The Prompt Library provides a structured foundation for storing reusable prompt templates, their metadata, and their version history. It makes prompt identity, ownership, inputs, revisions, and integrity explicit without changing the repository's existing prompts.

## Directory Structure

```text
PromptLibrary/
├── README.md
├── templates/
│   ├── committee.md
│   ├── daily.md
│   └── research.md
├── metadata/
│   ├── committee.yaml
│   ├── daily.yaml
│   └── research.yaml
└── versions/
    └── manifest.json
```

- `templates/` contains prompt template content.
- `metadata/` contains one metadata record for each managed template.
- `versions/` contains the manifest used to register prompt versions.
- Existing prompts at the root of `PromptLibrary/` remain unchanged.

## Prompt Lifecycle

1. Define the prompt's purpose, variables, owner, and stage.
2. Create the template and its matching metadata record.
3. Validate the template and required metadata.
4. Assign a prompt ID and version.
5. Generate a deterministic hash from the exact stored template content.
6. Register the approved revision in the version manifest.
7. Reference the registered revision during research execution.
8. Create a new version for any approved content change.

## Prompt Versioning Rules

- A Prompt ID identifies one logical prompt across revisions.
- A Prompt Version identifies one immutable revision of that prompt.
- Every registered version must reference its matching metadata and template.
- Published prompt content must not be overwritten.
- Content changes require a new Prompt Version and Prompt Hash.
- Research runs must record the Prompt ID, Prompt Version, and Prompt Hash they use.

## Prompt Hash Purpose

The Prompt Hash verifies the exact template content used during execution. A deterministic hash makes prompt integrity checkable, detects unrecorded content changes, and allows replay to resolve and verify the precise prompt revision used by a research run.
