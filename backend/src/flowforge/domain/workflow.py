from dataclasses import dataclass, field
from enum import StrEnum
from uuid import UUID, uuid4

from flowforge.domain.exceptions import InvalidWorkflowDefinition, InvalidWorkflowTransition
from flowforge.domain.workflow_step import WorkflowStep

# A workflow can be activated only form DRAFT, and archived only from ACTIVE
# An archived workflow cannot be reactivated


class WorkflowStatus(StrEnum):
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"


@dataclass(kw_only=True)
class Workflow:
    id: UUID = field(default_factory=uuid4)
    name: str
    status: WorkflowStatus = field(default=WorkflowStatus.DRAFT, init=False)
    _steps: list[WorkflowStep] = field(default_factory=list, init=False, repr=False)

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise InvalidWorkflowDefinition("Workflow name cannot be empty.")

        self.name = self.name.strip()

    def activate(self) -> None:
        if self.status != WorkflowStatus.DRAFT:
            raise InvalidWorkflowTransition(f"Cannot activate workflow in {self.status} state")

        self.status = WorkflowStatus.ACTIVE

    def archive(self) -> None:
        if self.status != WorkflowStatus.ACTIVE:
            raise InvalidWorkflowTransition(f"Cannot archive workflow in {self.status} state")

        self.status = WorkflowStatus.ARCHIVED

    @property
    def steps(self) -> tuple[WorkflowStep, ...]:
        return tuple(self._steps)

    def add_step(self, step: WorkflowStep) -> None:
        if self.status != WorkflowStatus.DRAFT:
            raise InvalidWorkflowTransition("Steps can only be added to draft workflows")

        if any(existing.id == step.id for existing in self._steps):
            raise InvalidWorkflowDefinition(f"Step {step.id} already exists")

        self._steps.append(step)
