import pytest

from app import create_app
from app.models.task import TaskManager


@pytest.fixture(autouse=True)
def clear_tasks():
    manager = TaskManager()
    with manager._task_lock:
        manager._tasks.clear()
    yield
    with manager._task_lock:
        manager._tasks.clear()


def test_list_tasks_serializes_tasks_once_in_newest_first_order():
    manager = TaskManager()
    first_task_id = manager.create_task("graph_build")
    second_task_id = manager.create_task("report_generation")

    app = create_app()
    response = app.test_client().get("/api/graph/tasks")

    assert response.status_code == 200
    assert response.get_json() == {
        "success": True,
        "data": [
            manager.get_task(second_task_id).to_dict(),
            manager.get_task(first_task_id).to_dict(),
        ],
        "count": 2,
    }
