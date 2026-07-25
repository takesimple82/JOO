from dataclasses import dataclass


@dataclass
class AIRequest:
    provider: str
    prompt: str
    prompt_id: str
    prompt_version: str
    task_id: str


@dataclass
class AIResponse:
    provider: str
    task_id: str
    prompt_id: str
    prompt_version: str
    content: str
    status: str
    error: str
