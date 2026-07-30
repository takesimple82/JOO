# Portfolio Impact Interpretation Policy

This package defines an immutable policy that constrains a caller-supplied
Portfolio Impact interpretation. It does not perform the interpretation.

`PortfolioImpactDirection` contains exactly:

- `BENEFICIAL`
- `NEUTRAL`
- `ADVERSE`

`PortfolioImpactInterpretationPolicy` is a frozen, hashable dataclass with:

1. `policy_id: str`
2. `policy_version: str`
3. `allowed_directions: tuple[PortfolioImpactDirection, ...]`
4. `allowed_horizon_ids: tuple[str, ...]`
5. `rationale_required: bool`

The ID and version are separate opaque exact nonblank strings. Versions are
not parsed, ordered, or treated as globally unique.

`validate_portfolio_impact_interpretation_policy()` requires the exact policy
type and validates fields in declared order. Both allowed collections must be
exact nonempty built-in tuples. Directions must be exact enum members and
horizon IDs exact nonblank built-in strings. Duplicates are rejected
immediately in caller order. `rationale_required` must be an exact built-in
bool.

Validation preserves the supplied policy, tuple, and string objects and tuple
order. It does not reconstruct, sort, deduplicate, trim, normalize, convert,
parse durations, or infer semantics.

`classify_portfolio_impact_interpretation_policy_applicability()` validates the
policy exactly once, then requires an exact direction, an exact nonblank
horizon string, and an exact rationale string. It returns:

- `DIRECTION_NOT_ALLOWED`
- `HORIZON_NOT_ALLOWED`
- `RATIONALE_REQUIRED`
- `APPLICABLE`

That order is mismatch precedence. Blank rationale is accepted only when the
policy does not require rationale. Rationale content is otherwise preserved
and not evaluated.

## Non-responsibilities

The policy does not inspect a Thesis or Portfolio Subject, parse statement
text, infer direction, execute semantic production, create an Impact, evaluate
evidence, calculate Expected Value, inspect holdings, allocate capital, or
perform lookup, registry, persistence, runtime, or orchestration.
