from dataclasses import dataclass, field
from enum import StrEnum
from uuid import UUID, uuid4


class StepType(StrEnum):
    HTTP_REQUEST = "http_request"
    DELAY = "delay"
    CONDITION = "condition"


@dataclass(frozen=True, kw_only=True)
class WorkflowStep:
    id: UUID = field(default_factory=uuid4)
    name: str
    type: StepType

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Step name cannot be empty")

        object.__setattr__(
            self,
            "name",
            self.name.strip(),
        )
