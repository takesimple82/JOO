from typing import Protocol
from InvestmentDecisionVerticalSlice.models import SemanticProductionOutput, SemanticProductionRequest


class SemanticDecisionProducer(Protocol):
    def produce(self, request: SemanticProductionRequest) -> SemanticProductionOutput:
        ...
