from fastapi.testclient import TestClient

from mcp.gateway.server import app


client = TestClient(app)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200


def test_tools():
    response = client.get("/tools")

    assert response.status_code == 200

    tools = response.json()["tools"]

    tool_names = {
        f"{tool['server']}.{tool['name']}"
        for tool in tools
    }

    assert "system.ping" in tool_names
    assert "system.status" in tool_names


def test_system_ping():
    response = client.post(
        "/execute",
        json={
            "server": "system",
            "tool": "ping",
            "arguments": {},
            "user_id": "test",
            "role": "admin",
            "work_id": "WO-1042",
            "task_id": "TASK-001",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["server"] == "system"
    assert data["tool"] == "ping"
    assert data["result"]["status"] == "pong"


def test_viewer_cannot_access_system():
    response = client.post(
        "/execute",
        json={
            "server": "system",
            "tool": "status",
            "arguments": {},
            "user_id": "test",
            "role": "viewer",
            "work_id": "WO-1042",
            "task_id": "TASK-001",
        },
    )

    assert response.status_code == 403