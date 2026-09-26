"""Version-1 closed journal codec. No dynamic types from persisted data/pickle."""
from dataclasses import fields, is_dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from enum import Enum
from importlib import import_module

# Fixed trusted model modules, NOT names read from a journal or an AI response.
_MODULES = (
    "OperationalCioCycle.models", "InvestmentDecisionVerticalSlice.models",
    "PortfolioDomain.models", "PortfolioSnapshot.models", "PortfolioHoldingSnapshot.models",
    "PortfolioHoldingObservation.models", "PortfolioPosition.models", "PortfolioMembership.models",
    "PortfolioObservationContext.models", "PortfolioWatchlistEntry.models",
    "PortfolioImpactInterpretationPolicy.models", "ExactNumericDeltaSignal.models",
    "ExactCrossContextNumericDelta.models", "ExactNumericDeltaMateriality.models",
    "ExactCrossContextNumericDeltaDirection.models", "ExactCrossContextNumericDeltaApplicability.models",
    "ExplicitHypothesis.models", "ExplicitThesis.models", "ExplicitPortfolioImpact.models",
    "SemanticHypothesisProduction.models", "SemanticThesisProduction.models",
    "SemanticPortfolioImpactProduction.models", "ThesisPortfolioSubjectLink.models",
    "ExpectedValueAssumptionSet.models", "ExpectedValueAssumptionSetApplicability.models",
    "SemanticExpectedValueAssumptionSetProduction.models", "ExactExpectedValue.models",
    "KbPortfolioVerticalSlice.models", "PortfolioSnapshotProducer.models.types",
    "InvestmentResearchOrchestrator.run_coordinator", "InvestmentResearchOrchestrator.models.run",
    "InvestmentResearchOrchestrator.models.enums", "InvestmentResearchOrchestrator.models.scan",
    "InvestmentResearchOrchestrator.models.plan", "InvestmentResearchOrchestrator.models.prompt",
    "InvestmentResearchOrchestrator.models.memory", "InvestmentResearchOrchestrator.models.store",
    "InvestmentResearchOrchestrator.models.contradiction", "InvestmentResearchOrchestrator.models.re_research",
    "EvidenceContradiction.models", "FactStore.models.types",
    "CapitalAllocationCycle.models", "KbCapitalFactAuthority.models",
    "BrokerExecutionCycle.models",
)
_TYPES = {}
for _name in _MODULES:
    for _type in vars(import_module(_name)).values():
        if isinstance(_type, type) and _type.__module__ == _name and (is_dataclass(_type) or issubclass(_type, Enum)):
            _TYPES[_name + "." + _type.__name__] = _type


def encode(value):
    if value is None or type(value) in (str, bool, int):
        return value
    if type(value) is Decimal:
        if not value.is_finite():
            raise ValueError("non-finite Decimal")
        return {"decimal": str(value)}
    if type(value) is datetime:
        if value.tzinfo is not timezone.utc:
            raise ValueError("UTC required")
        return {"datetime": value.isoformat()}
    if type(value) is timedelta:
        return {"microseconds": (value.days * 86400 + value.seconds) * 1000000 + value.microseconds}
    if type(value) is bytes:
        return {"bytes": value.hex()}
    if type(value) is tuple:
        return {"tuple": [encode(x) for x in value]}
    if type(value) is list:
        return {"list": [encode(x) for x in value]}
    if type(value) is dict and all(type(k) is str for k in value):
        return {"dict": {k: encode(v) for k, v in value.items()}}
    name = type(value).__module__ + "." + type(value).__name__
    if _TYPES.get(name) is not type(value):
        raise TypeError("type not admitted by cycle journal codec")
    if isinstance(value, Enum):
        return {"enum": name, "value": value.value}
    return {"type": name, "fields": {f.name: encode(getattr(value, f.name)) for f in fields(value)}}


def decode(value):
    if value is None or type(value) in (str, bool, int):
        return value
    if type(value) is not dict:
        raise ValueError("invalid cycle encoded value")
    keys = set(value)
    if keys == {"decimal"} and type(value["decimal"]) is str:
        result = Decimal(value["decimal"])
        if not result.is_finite():
            raise ValueError("non-finite Decimal")
        return result
    if keys == {"datetime"}:
        result = datetime.fromisoformat(value["datetime"])
        if result.tzinfo is not timezone.utc:
            raise ValueError("UTC required")
        return result
    if keys == {"microseconds"} and type(value["microseconds"]) is int:
        return timedelta(microseconds=value["microseconds"])
    if keys == {"bytes"}:
        return bytes.fromhex(value["bytes"])
    for tag in ("tuple", "list"):
        if keys == {tag} and type(value[tag]) is list:
            items = [decode(x) for x in value[tag]]
            return tuple(items) if tag == "tuple" else items
    if keys == {"dict"} and type(value["dict"]) is dict:
        return {k: decode(v) for k, v in value["dict"].items()}
    if keys == {"enum", "value"} and value["enum"] in _TYPES:
        cls = _TYPES[value["enum"]]
        if issubclass(cls, Enum):
            return cls(value["value"])
    if keys == {"type", "fields"} and value["type"] in _TYPES:
        cls = _TYPES[value["type"]]
        if is_dataclass(cls) and type(value["fields"]) is dict and set(value["fields"]) == {f.name for f in fields(cls)}:
            return cls(**{k: decode(v) for k, v in value["fields"].items()})
    raise ValueError("unknown/malformed cycle codec schema")
