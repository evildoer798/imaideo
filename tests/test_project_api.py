import pytest
pytest.importorskip("fastapi")
from fastapi.testclient import TestClient
from app.main import app
def test_health():
 r=TestClient(app).get("/health"); assert r.status_code==200 and r.json()["status"] in ("ok","degraded")
