from app.workflows.core import workflow_ready


def test_workflow_ready() -> None:
    assert workflow_ready()

