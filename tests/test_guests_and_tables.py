"""Unit tests for guest-management table lifecycle and guest point endpoints."""

from fastapi.testclient import TestClient

from guest_management.main import create_app


def _client() -> TestClient:
    return TestClient(create_app())


def test_health_check() -> None:
    client = _client()
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "guest-management"}


def test_create_list_and_get_table() -> None:
    client = _client()
    create_resp = client.post("/tables", json={"table_number": "A-01", "capacity": 4})
    assert create_resp.status_code == 201
    table = create_resp.json()
    assert table["table_number"] == "A-01"
    assert table["capacity"] == 4
    assert table["status"] == "available"
    assert table["current_session_id"] is None
    assert table["qr_token"] is None

    list_resp = client.get("/tables")
    assert list_resp.status_code == 200
    assert [item["id"] for item in list_resp.json()] == [table["id"]]

    get_resp = client.get(f"/tables/{table['id']}")
    assert get_resp.status_code == 200
    assert get_resp.json() == table

    missing_resp = client.get("/tables/nonexistent-id")
    assert missing_resp.status_code == 404


def test_table_full_lifecycle_and_reuse() -> None:
    client = _client()
    table_id = client.post("/tables", json={"table_number": "B-02", "capacity": 2}).json()["id"]

    occupy_resp = client.post(f"/tables/{table_id}/occupy", json={"party_size": 2})
    assert occupy_resp.status_code == 200
    occupied = occupy_resp.json()
    assert occupied["status"] == "occupied"
    assert occupied["current_session_id"]
    assert occupied["qr_token"]

    clean_resp = client.post(f"/tables/{table_id}/request-cleaning")
    assert clean_resp.status_code == 200
    cleaning = clean_resp.json()
    assert cleaning["status"] == "cleaning"
    assert cleaning["current_session_id"] is None
    assert cleaning["qr_token"] is None

    release_resp = client.post(f"/tables/{table_id}/release")
    assert release_resp.status_code == 200
    released = release_resp.json()
    assert released["status"] == "available"

    reoccupy_resp = client.post(f"/tables/{table_id}/occupy", json={"party_size": 1})
    assert reoccupy_resp.status_code == 200
    reoccupied = reoccupy_resp.json()
    assert reoccupied["status"] == "occupied"
    assert reoccupied["current_session_id"] != occupied["current_session_id"]
    assert reoccupied["qr_token"] != occupied["qr_token"]


def test_table_invalid_state_transitions_return_409() -> None:
    client = _client()
    table_id = client.post("/tables", json={"table_number": "C-03", "capacity": 4}).json()["id"]

    # From available
    assert client.post(f"/tables/{table_id}/request-cleaning").status_code == 409
    assert client.post(f"/tables/{table_id}/release").status_code == 409

    # From occupied
    assert client.post(f"/tables/{table_id}/occupy", json={"party_size": 2}).status_code == 200
    assert client.post(f"/tables/{table_id}/occupy", json={"party_size": 1}).status_code == 409
    assert client.post(f"/tables/{table_id}/release").status_code == 409

    # From cleaning
    assert client.post(f"/tables/{table_id}/request-cleaning").status_code == 200
    assert client.post(f"/tables/{table_id}/occupy", json={"party_size": 1}).status_code == 409
    assert client.post(f"/tables/{table_id}/request-cleaning").status_code == 409

    # Non-existent table
    assert client.post("/tables/missing/occupy", json={"party_size": 1}).status_code == 404
    assert client.post("/tables/missing/request-cleaning").status_code == 404
    assert client.post("/tables/missing/release").status_code == 404


def test_table_capacity_exceeded_returns_422() -> None:
    client = _client()
    table_id = client.post("/tables", json={"table_number": "D-04", "capacity": 2}).json()["id"]

    resp = client.post(f"/tables/{table_id}/occupy", json={"party_size": 3})
    assert resp.status_code == 422

    # Ensure table remains available after failed occupy
    table = client.get(f"/tables/{table_id}").json()
    assert table["status"] == "available"

    # Invalid non-positive values
    assert client.post("/tables", json={"table_number": "X", "capacity": 0}).status_code == 422
    assert client.post(f"/tables/{table_id}/occupy", json={"party_size": 0}).status_code == 422


def test_guest_registration_and_points_adjustment() -> None:
    client = _client()
    guest_resp = client.post("/guests", json={"name": "Taro", "email": "taro@example.com"})
    assert guest_resp.status_code == 201
    guest = guest_resp.json()
    assert guest["name"] == "Taro"
    assert guest["email"] == "taro@example.com"
    assert guest["points"] == 0

    guest_no_email = client.post("/guests", json={"name": "Hanako"})
    assert guest_no_email.status_code == 201
    assert guest_no_email.json()["email"] is None

    guest_id = guest["id"]

    add_resp = client.post(f"/guests/{guest_id}/points", json={"delta": 100})
    assert add_resp.status_code == 200
    assert add_resp.json()["points"] == 100

    sub_resp = client.post(f"/guests/{guest_id}/points", json={"delta": -40})
    assert sub_resp.status_code == 200
    assert sub_resp.json()["points"] == 60

    insufficient_resp = client.post(f"/guests/{guest_id}/points", json={"delta": -61})
    assert insufficient_resp.status_code == 422

    exact_resp = client.post(f"/guests/{guest_id}/points", json={"delta": -60})
    assert exact_resp.status_code == 200
    assert exact_resp.json()["points"] == 0

    missing_resp = client.post("/guests/nonexistent/points", json={"delta": 10})
    assert missing_resp.status_code == 404
