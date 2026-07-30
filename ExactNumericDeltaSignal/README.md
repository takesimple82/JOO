# Exact Numeric Delta Signal

This package classifies one deterministic numeric Signal from an actual exact
cross-context numeric delta and an actual caller-supplied materiality policy.

## Public contract

`ExactNumericDeltaSignalStatus` has:

- `UNIT_MISMATCH`
- `NO_CHANGE`
- `IMMATERIAL_INCREASE`
- `IMMATERIAL_DECREASE`
- `MATERIAL_INCREASE`
- `MATERIAL_DECREASE`

`ExactNumericDeltaSignalClassification` is a frozen, hashable structural
result containing the original delta, original policy, classified direction,
classified materiality, and final Signal status. It has no separate identity.

`classify_exact_numeric_delta_signal(delta, policy)` validates the delta
exactly once and policy exactly once. It then delegates to private unchecked
direction and materiality helpers using those original inputs. Caller-supplied
status enums are not accepted.

## Mapping

`UNIT_MISMATCH` materiality maps to `UNIT_MISMATCH` Signal for every
mathematical direction, while preserving that direction in the result.
Otherwise:

- `ZERO + IMMATERIAL` → `NO_CHANGE`
- `POSITIVE + IMMATERIAL` → `IMMATERIAL_INCREASE`
- `NEGATIVE + IMMATERIAL` → `IMMATERIAL_DECREASE`
- `POSITIVE + MATERIAL` → `MATERIAL_INCREASE`
- `NEGATIVE + MATERIAL` → `MATERIAL_DECREASE`

`ZERO + MATERIAL` is unsupported because it is impossible under the accepted
non-negative strict-threshold materiality contract.

## Boundaries

This Signal describes numeric change only. It does not interpret predicate
meaning, decide whether change is beneficial or harmful, select endpoints,
subtract values, convert units, modify decimal context, recheck applicability,
or implement semantic hypothesis production, Thesis, Expected Value,
Portfolio impact, CIO decisions, allocation, runtime, persistence, registry,
lookup, or orchestration.
