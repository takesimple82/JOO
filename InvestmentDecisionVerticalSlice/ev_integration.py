from ExactExpectedValue.calculation import calculate_exact_expected_value
from ExactExpectedValue.validation import validate_exact_expected_value_calculation
from SemanticExpectedValueAssumptionSetProduction.models import SemanticallyProducedExpectedValueAssumptionSet
from InvestmentDecisionVerticalSlice.models import ExactEvRecord
from InvestmentDecisionVerticalSlice.validation import nonblank, validate_ev_provenance


def calculate_admitted_ev(record_id, source):
    nonblank("record_id", record_id)
    validate_ev_provenance(source)
    calculation = calculate_exact_expected_value(
        SemanticallyProducedExpectedValueAssumptionSet(source.assumption_set)
    )
    validate_exact_expected_value_calculation(calculation)
    return ExactEvRecord(record_id, source, calculation)


def replay_exact_ev(record):
    replayed = calculate_admitted_ev(record.record_id, record.source)
    if replayed != record:
        raise ValueError("deterministic EV replay mismatch")
    return replayed
