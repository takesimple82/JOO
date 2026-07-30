# Exact Cross-Context Numeric Delta

This package calculates one exact, traceable numeric delta for supplied
baseline/current semantic propositions when the accepted applicability
classifier determines that the actual inputs are calculable.

## Public models

`ExactCrossContextNumericDelta` is a frozen dataclass with:

1. `baseline_proposition_id: str`
2. `current_proposition_id: str`
3. `unit_id: str`
4. `value: Decimal`

`ExactCrossContextNumericDeltaCalculation` is a frozen dataclass with:

1. `applicability_status:
   ExactCrossContextNumericDeltaApplicabilityStatus`
2. `delta: Optional[ExactCrossContextNumericDelta]`

For `CALCULABLE`, `delta` must contain an exact delta. For every other status,
`delta` must be `None`. Public validators enforce these structural invariants,
exact built-in field types, nonblank identifiers, and a finite exact Decimal.

## Calculation

`calculate_exact_cross_context_numeric_delta()` accepts the same five actual
inputs as the applicability classifier. It calls that public classifier
exactly once. A non-calculable status is returned unchanged with `delta=None`.

For `CALCULABLE`, the calculator calls:

```python
subtract_exact_decimal(
    current.proposition.value,
    baseline.proposition.value,
)
```

It stores the arithmetic result object directly. Proposition IDs come from
the explicit pair, and the unit object comes from the compatible baseline
proposition. No input or field is copied, normalized, or converted.

## Boundaries

This package does not reimplement pair applicability or compatibility. It does
not classify direction, determine materiality, generate Signal, convert units,
use float or Fraction, select endpoints, or implement runtime, persistence,
orchestration, Hypothesis, Thesis, Portfolio impact, or CIO decisions.
