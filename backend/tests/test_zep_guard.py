import pytest

from app import create_app
from app.config import Config
from app.models.task import TaskManager


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(Config, "USE_ZEP", False)
    monkeypatch.setattr(Config, "ZEP_API_KEY", "invalid-test-key")
    return create_app().test_client()


@pytest.mark.parametrize(
    ("method", "path", "payload"),
    [
        ("post", "/api/graph/build", {"project_id": "proj_test"}),
        ("get", "/api/graph/data/graph_test", None),
        ("delete", "/api/graph/delete/graph_test", None),
        ("get", "/api/simulation/entities/graph_test", None),
        ("post", "/api/simulation/prepare", {"simulation_id": "sim_test"}),
        ("post", "/api/simulation/generate-profiles", {"graph_id": "graph_test"}),
        (
            "post",
            "/api/simulation/start",
            {"simulation_id": "sim_test", "enable_graph_memory_update": True},
        ),
        ("post", "/api/report/generate", {"simulation_id": "sim_test"}),
        ("post", "/api/report/chat", {"report_id": "report_test"}),
        ("post", "/api/report/tools/search", {"graph_id": "graph_test"}),
        ("post", "/api/report/tools/statistics", {"graph_id": "graph_test"}),
    ],
)
def test_zep_dependent_routes_return_503_when_disabled(client, method, path, payload):
    response = getattr(client, method)(path, json=payload)

    assert response.status_code == 503
    assert response.get_json() == {
        "success": False,
        "error": "Zep integration is disabled",
    }


def test_disabled_graph_build_does_not_create_task(client):
    manager = TaskManager()
    with manager._task_lock:
        manager._tasks.clear()

    response = client.post("/api/graph/build", json={"project_id": "proj_test"})

    assert response.status_code == 503
    assert manager.list_tasks() == []


def test_enabled_zep_without_key_returns_503(monkeypatch):
    monkeypatch.setattr(Config, "USE_ZEP", True)
    monkeypatch.setattr(Config, "ZEP_API_KEY", None)
    client = create_app().test_client()

    response = client.post("/api/graph/build", json={"project_id": "proj_test"})

    assert response.status_code == 503
    assert response.get_json()["error"] == "ZEP_API_KEY is not configured"


def test_config_validation_skips_zep_key_when_disabled(monkeypatch):
    monkeypatch.setattr(Config, "USE_ZEP", False)
    monkeypatch.setattr(Config, "ZEP_API_KEY", None)
    monkeypatch.setattr(Config, "LLM_API_KEY", "configured")

    assert Config.validate() == []
