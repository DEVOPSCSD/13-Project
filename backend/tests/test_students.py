"""Backend API tests. Each test gets a fresh temporary database."""
import pytest

from app import create_app

VALID = {"student_id": "TEST-001", "full_name": "Test Student",
         "email": "test.student@example.com", "course": "Computer Science",
         "year_of_study": 2, "phone": "9876543210"}


@pytest.fixture
def client(tmp_path):
    app = create_app({"TESTING": True, "DATABASE_PATH": str(tmp_path / "test.db"),
                      "SEED_DEMO_DATA": False, "FRONTEND_DIR": str(tmp_path)})
    return app.test_client()


def add(client, **overrides):
    return client.post("/api/students", json={**VALID, **overrides})


def test_health(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.get_json()["data"]["status"] == "ok"


def test_list_empty(client):
    body = client.get("/api/students").get_json()
    assert body["data"] == [] and body["total"] == 0


def test_create_student(client):
    res = add(client)
    assert res.status_code == 201
    data = res.get_json()["data"]
    assert data["student_id"] == "TEST-001" and data["id"] >= 1


def test_year_as_string_is_accepted(client):
    assert add(client, year_of_study="3").status_code == 201


def test_missing_fields(client):
    res = client.post("/api/students", json={})
    assert res.status_code == 400
    details = res.get_json()["error"]["details"]
    assert {"student_id", "full_name", "email", "course", "year_of_study"} <= set(details)


def test_invalid_email(client):
    res = add(client, email="not-an-email")
    assert res.status_code == 400
    assert "email" in res.get_json()["error"]["details"]


def test_invalid_year(client):
    assert add(client, year_of_study=9).status_code == 400


def test_invalid_json_body(client):
    res = client.post("/api/students", data="oops", content_type="application/json")
    assert res.status_code == 400
    assert res.get_json()["error"]["code"] == "INVALID_JSON"


def test_duplicate_email_and_id(client):
    add(client)
    res = add(client)
    assert res.status_code == 409
    details = res.get_json()["error"]["details"]
    assert "email" in details and "student_id" in details


def test_get_by_id_and_404(client):
    new_id = add(client).get_json()["data"]["id"]
    assert client.get(f"/api/students/{new_id}").status_code == 200
    assert client.get("/api/students/9999").status_code == 404


def test_update_student(client):
    new_id = add(client).get_json()["data"]["id"]
    res = client.put(f"/api/students/{new_id}", json={**VALID, "full_name": "Changed Name"})
    assert res.status_code == 200
    assert res.get_json()["data"]["full_name"] == "Changed Name"


def test_update_missing_student(client):
    assert client.put("/api/students/9999", json=VALID).status_code == 404


def test_update_to_duplicate_email_rejected(client):
    add(client)
    other = add(client, student_id="TEST-002", email="other@example.com").get_json()["data"]["id"]
    res = client.put(f"/api/students/{other}", json={**VALID, "student_id": "TEST-002"})
    assert res.status_code == 409


def test_delete_student(client):
    new_id = add(client).get_json()["data"]["id"]
    assert client.delete(f"/api/students/{new_id}").status_code == 200
    assert client.delete(f"/api/students/{new_id}").status_code == 404


def test_search_by_name_email_course(client):
    add(client, full_name="Alice Wonder")
    add(client, student_id="TEST-002", email="bob@example.com",
        full_name="Bob Builder", course="Mechanical")
    assert client.get("/api/students?search=alice").get_json()["count"] == 1
    assert client.get("/api/students?search=bob@example").get_json()["count"] == 1
    assert client.get("/api/students?search=mechanical").get_json()["count"] == 1
    body = client.get("/api/students?search=zzz").get_json()
    assert body["count"] == 0 and body["total"] == 2


def test_search_wildcard_is_literal(client):
    add(client)
    assert client.get("/api/students?search=%25").get_json()["count"] == 0


def test_unknown_api_route_returns_json_404(client):
    res = client.get("/api/nothing")
    assert res.status_code == 404
    assert res.get_json()["success"] is False
