"""健康检查接口测试。"""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_ok() -> None:
    response = client.get("/api/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "ok"
    assert data["app_name"] == "enterprise-rag-knowledge"
    assert "version" in data


def test_openapi_available() -> None:
    response = client.get("/openapi.json")
    assert response.status_code == 200
    assert "paths" in response.json()
