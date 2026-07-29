# EvidenceSupersession

EvidenceSupersession owns one explicit, directed proposition-level
supersession relation. `ExplicitPropositionSupersession` contains exactly
the ID of the superseded proposition and the ID of the superseding
proposition; the direction is from the former to the latter.

The package performs structural validation only. Identifiers must be exact
nonblank built-in strings, and a proposition cannot directly supersede
itself. Identifiers are preserved without trimming, case folding, Unicode
normalization, conversion, or alias resolution.

The relation does not validate endpoint existence or certify a proposition
family. It is an explicit caller-supplied declaration, not an inference,
truth judgment, deletion requirement, source-authority decision, or
chronology inference. It does not establish that the declaration is trusted
or applicable.

Duplicate handling, multi-edge graph behavior, chains, branching, merging,
cycle detection beyond a direct self-edge, and transitive inference are
deferred. This package has no dependency on evidence comparison or
contradiction and produces no resolution output. A future
EvidenceResolution policy may consume this relation together with its
independent proposition and contradiction inputs.
