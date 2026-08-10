from __future__ import annotations

import hashlib
import re

from InvestmentResearchOrchestrator.models.prompt import (
    PromptFreezeArtifact,
    PromptTemplate,
)
from InvestmentResearchOrchestrator.validation.prompt import (
    validate_prompt_freeze_artifact,
    validate_prompt_template,
)

_BINDING_PATTERN = re.compile(r"\{([^{}]+)\}")


class PromptFreeze:
    """Materialize immutable prompt instance bytes + content hash."""

    def freeze(
        self,
        *,
        research_id: str,
        committee_id: str,
        template: PromptTemplate,
        bindings: dict[str, str],
        attempt_index: int = 0,
    ) -> PromptFreezeArtifact:
        if type(research_id) is not str or research_id.strip() == "":
            raise ValueError("research_id must be nonblank str")
        if (
            type(committee_id) is not str
            or committee_id.strip() == ""
        ):
            raise ValueError("committee_id must be nonblank str")
        validate_prompt_template(template)
        if type(bindings) is not dict:
            raise TypeError("bindings must be dict")
        for key, value in bindings.items():
            if type(key) is not str or key.strip() == "":
                raise ValueError(
                    "bindings keys must be nonblank str"
                )
            if type(value) is not str:
                raise TypeError(
                    "bindings values must be str"
                )
        if type(attempt_index) is not int:
            raise TypeError("attempt_index must be int")
        if attempt_index != 0:
            raise ValueError(
                "attempt_index must be 0 for IRO-M1"
            )

        try:
            template_text = template.template_bytes.decode(
                "utf-8"
            )
        except UnicodeDecodeError as exc:
            raise ValueError(
                "template_bytes must be valid UTF-8"
            ) from exc

        required_names = set(
            _BINDING_PATTERN.findall(template_text)
        )
        missing = sorted(required_names - set(bindings))
        if missing:
            raise ValueError(
                "missing required binding: "
                + ", ".join(missing)
            )

        def replace(match: re.Match) -> str:
            name = match.group(1)
            return bindings[name]

        frozen_text = _BINDING_PATTERN.sub(
            replace,
            template_text,
        )
        frozen_bytes = frozen_text.encode("utf-8")
        prompt_hash = hashlib.sha256(frozen_bytes).hexdigest()
        artifact = PromptFreezeArtifact(
            research_id=research_id,
            committee_id=committee_id,
            prompt_id=template.prompt_id,
            prompt_version=template.prompt_version,
            frozen_prompt_bytes=frozen_bytes,
            prompt_hash=prompt_hash,
            attempt_index=0,
        )
        validate_prompt_freeze_artifact(artifact)
        return artifact

    def verify_hash(
        self,
        artifact: PromptFreezeArtifact,
    ) -> None:
        validate_prompt_freeze_artifact(artifact)
        expected = hashlib.sha256(
            artifact.frozen_prompt_bytes
        ).hexdigest()
        if expected != artifact.prompt_hash:
            raise ValueError("prompt hash mismatch")
