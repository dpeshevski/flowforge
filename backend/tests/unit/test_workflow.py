import pytest

from flowforge.domain.exceptions import InvalidWorkflowDefinition, InvalidWorkflowTransition
from flowforge.domain.workflow import (
    Workflow,
    WorkflowStatus,
)
from flowforge.domain.workflow_step import StepType, WorkflowStep


def test_new_workflow_status_in_draft() -> None:
    workflow = Workflow(name="Order Processing")

    assert workflow.status == WorkflowStatus.DRAFT
    assert workflow.name == "Order Processing"


def test_workflow_can_be_activated() -> None:
    workflow = Workflow(name="Order Processing")

    workflow.activate()

    assert workflow.status == WorkflowStatus.ACTIVE


def test_active_workflow_can_be_archived() -> None:
    workflow = Workflow(name="Order Processing")

    workflow.activate()
    workflow.archive()

    assert workflow.status == WorkflowStatus.ARCHIVED


def test_archived_workflow_cannot_be_activated() -> None:
    workflow = Workflow(name="Order Processing")

    workflow.activate()
    workflow.archive()

    with pytest.raises(InvalidWorkflowTransition):
        workflow.activate()


def test_draft_workflow_cannot_be_archived() -> None:
    workflow = Workflow(name="Order Processing")

    with pytest.raises(InvalidWorkflowTransition):
        workflow.archive()


@pytest.mark.parametrize(
    "name",
    ["", " ", "   "],
)
def test_workflow_requires_nonempty_name(name: str) -> None:
    with pytest.raises(InvalidWorkflowDefinition):
        Workflow(name=name)


def test_workflow_name_is_trimmed() -> None:
    workflow = Workflow(name="   Order Processing   ")

    assert workflow.name == "Order Processing"


def test_can_add_step_to_draft_workflow() -> None:
    workflow = Workflow(name="Order Processing")

    step = WorkflowStep(name="Validate Order", type=StepType.HTTP_REQUEST)

    workflow.add_step(step)

    assert len(workflow.steps) == 1
    assert workflow.steps[0] == step


def test_cannot_add_step_to_active_workflow() -> None:
    workflow = Workflow(name="Order Processing")
    workflow.activate()

    step = WorkflowStep(name="Validate Order", type=StepType.HTTP_REQUEST)

    with pytest.raises(InvalidWorkflowTransition):
        workflow.add_step(step)


def test_cannot_add_duplicate_step() -> None:
    workflow = Workflow(name="Order Processing")
    step = WorkflowStep(name="Validate Order", type=StepType.HTTP_REQUEST)

    workflow.add_step(step)

    with pytest.raises(InvalidWorkflowDefinition):
        workflow.add_step(step)


def test_steps_collection_is_read_only() -> None:
    workflow = Workflow(name="Order Processing")

    assert isinstance(workflow.steps, tuple)
