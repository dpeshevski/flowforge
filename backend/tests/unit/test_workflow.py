import pytest

from flowforge.domain.exceptions import InvalidWorkflowDefinition, InvalidWorkflowTransition
from flowforge.domain.workflow import (
    Workflow,
    WorkflowStatus,
)


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
