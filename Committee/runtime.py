from AIAdapter.models import AIRequest
from Committee.models import (
    CommitteeExecution,
    CommitteeExecutionResult,
)
from ExecutionEngine.base import ExecutionEngine


class CommitteeRuntime:
    def __init__(self, execution_engine: ExecutionEngine) -> None:
        if not isinstance(execution_engine, ExecutionEngine):
            raise TypeError("execution_engine must be ExecutionEngine")
        self._execution_engine = execution_engine

    def run(
        self,
        committee: CommitteeExecution,
    ) -> CommitteeExecutionResult:
        self._validate_committee(committee)

        responses = [
            self._execution_engine.execute(request)
            for request in committee.requests
        ]
        return CommitteeExecutionResult(
            committee_id=committee.committee_id,
            responses=responses,
        )

    @staticmethod
    def _validate_committee(
        committee: CommitteeExecution,
    ) -> None:
        if not isinstance(committee, CommitteeExecution):
            raise TypeError("committee must be CommitteeExecution")

        identity_fields = (
            ("committee_id", committee.committee_id),
            ("name", committee.name),
        )
        for name, value in identity_fields:
            if not isinstance(value, str):
                raise TypeError(f"{name} must be str")
            if not value.strip():
                raise ValueError(f"{name} must not be blank")

        if not isinstance(committee.requests, list):
            raise TypeError("requests must be list[AIRequest]")
        if not all(
            isinstance(request, AIRequest)
            for request in committee.requests
        ):
            raise TypeError("requests must contain only AIRequest")
