from fastapi.testclient import TestClient

from todo_dashboard import api


def test_health_endpoint(app):
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_api_todos_filters(app):
    client = TestClient(app)
    response = client.get("/api/todos", params={"status": "OPEN"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 1
    assert payload["items"][0]["status"] == "OPEN"


def test_dashboard_renders(app):
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert "Workspace Todo Dashboard" in response.text
    assert "<th>Title</th>" in response.text
    assert "id=\"preview-panel\"" in response.text
    assert "data-stat-key=\"closed\"" in response.text
    assert "id=\"status-stats-data\"" in response.text


def test_invalid_sort_rejected(app):
    client = TestClient(app)
    response = client.get("/api/todos", params={"sort": "bad"})
    assert response.status_code == 400


def test_markdown_preview_falls_back_without_dependency(monkeypatch):
    monkeypatch.setattr(api, "markdown", None)

    rendered = api.markdown_preview("Hello\n<script>alert('x')</script>")

    assert rendered == "<p>Hello<br />\n&lt;script&gt;alert(&#x27;x&#x27;)&lt;/script&gt;</p>"
