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
    status: str
    output: str
