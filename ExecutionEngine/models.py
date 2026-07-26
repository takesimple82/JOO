from dataclasses import dataclass


@dataclass
class ExecutionRequest:
    task_id: str
    committee: str
    provider: str
    prompt_id: str
    prompt_version: str


@dataclass
class ExecutionResult:
    task_id: str
    committee: str
    provider: str
    prompt_id: str
    prompt_version: str
    status: str
    output: str
    error: str


@dataclass(frozen=True)
class ExecutionLog:
    task_id: str
    provider: str
    prompt_id: str
    prompt_version: str
    event_type: str
    occurred_at: str
    error: str

    def __post_init__(self) -> None:
        values = (
            ("task_id", self.task_id),
            ("provider", self.provider),
            ("prompt_id", self.prompt_id),
            ("prompt_version", self.prompt_version),
            ("event_type", self.event_type),
            ("occurred_at", self.occurred_at),
            ("error", self.error),
        )
        for name, value in values:
            if not isinstance(value, str):
                raise TypeError(f"{name} must be str")

        if self.event_type not in {"start", "success", "failure"}:
            raise ValueError(
                "event_type must be start, success, or failure"
            )
