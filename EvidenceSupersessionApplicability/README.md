# EvidenceSupersessionApplicability

EvidenceSupersessionApplicability classifies whether one validated explicit
supersession relation exactly references two accepted
`ExactObservedNumericProposition` objects that form a contradiction candidate.
Its three inputs are the left proposition, right proposition, and directed
supersession relation.

The frozen supersession validator owns relation validation. The frozen
contradiction classifier owns proposition validation and contradiction
candidacy; this package has no direct EvidenceComparison dependency. A pair
must be a contradiction candidate before endpoint IDs are inspected.

Applicability requires the relation's two endpoints to equal the two
proposition IDs exactly. Either argument ordering may match, while the
relation continues to own its superseded-versus-superseding direction.
Classification is therefore argument-order independent for valid inputs.
Identifier comparison is case-, whitespace-, and Unicode-representation
sensitive. No normalization, alias resolution, or endpoint lookup occurs.

Malformed inputs raise their upstream exceptions. A noncandidate pair and an
endpoint mismatch are normal inapplicability results. `APPLICABLE` means only
that the supplied relation references the supplied contradiction candidate.
It does not validate trust, authority, truth, sources, chronology, policy
sufficiency, or operational disposition.

EvidenceProposition, EvidenceComparison, EvidenceContradiction,
EvidenceSupersession, and earlier evidence packages remain frozen and must not
depend on this package. A future policy may consume applicability, but
EvidenceResolution remains absent and deferred.
