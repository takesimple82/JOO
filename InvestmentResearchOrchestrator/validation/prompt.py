from __future__ import annotations

from InvestmentResearchOrchestrator.models.prompt import (
    PromptFreezeArtifact,
    PromptTemplate,
)
from InvestmentResearchOrchestrator.validation.common import (
    require_bytes,
    require_int,
    require_nonblank_string,
)


def validate_prompt_template(template: PromptTemplate) -> None:
    if type(template) is not PromptTemplate:
        raise TypeError("template must be PromptTemplate")
    require_nonblank_string("prompt_id", template.prompt_id)
    require_nonblank_string(
        "prompt_version",
        template.prompt_version,
    )
    require_bytes("template_bytes", template.template_bytes)
    if len(template.template_bytes) == 0:
        raise ValueError("template_bytes must not be empty")


def validate_prompt_freeze_artifact(
    artifact: PromptFreezeArtifact,
) -> None:
    if type(artifact) is not PromptFreezeArtifact:
        raise TypeError(
            "artifact must be PromptFreezeArtifact"
        )
    require_nonblank_string(
        "research_id",
        artifact.research_id,
    )
    require_nonblank_string(
        "committee_id",
        artifact.committee_id,
    )
    require_nonblank_string("prompt_id", artifact.prompt_id)
    require_nonblank_string(
        "prompt_version",
        artifact.prompt_version,
    )
    require_bytes(
        "frozen_prompt_bytes",
        artifact.frozen_prompt_bytes,
    )
    if len(artifact.frozen_prompt_bytes) == 0:
        raise ValueError(
            "frozen_prompt_bytes must not be empty"
        )
    require_nonblank_string(
        "prompt_hash",
        artifact.prompt_hash,
    )
    require_int("attempt_index", artifact.attempt_index)
    if artifact.attempt_index < 0:
        raise ValueError(
            "attempt_index must be >= 0"
        )
