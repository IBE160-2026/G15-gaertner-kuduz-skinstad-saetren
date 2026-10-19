from fastapi.testclient import TestClient

from adaptere.api.main import app


def test_helsesjekk_svarer_ok() -> None:
    respons = TestClient(app).get("/api/helse")

    assert respons.status_code == 200
    assert respons.json() == {"status": "ok"}
