from dataclasses import dataclass


@dataclass(frozen=True)
class PromptTemplate:
    prompt_id: str
    prompt_version: str
    template_bytes: bytes


@dataclass(frozen=True)
class PromptFreezeArtifact:
    research_id: str
    committee_id: str
    prompt_id: str
    prompt_version: str
    frozen_prompt_bytes: bytes
    prompt_hash: str
    attempt_index: int
