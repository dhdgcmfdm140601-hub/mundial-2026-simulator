from fastapi.testclient import TestClient


def test_create_team(client: TestClient):
    res = client.post("/teams/", json={"name": "Argentina", "code": "ARG"})
    assert res.status_code == 201
    data = res.json()
    assert data["name"] == "Argentina"
    assert data["code"] == "ARG"


def test_create_team_duplicate_code(client: TestClient):
    client.post("/teams/", json={"name": "Argentina", "code": "ARG"})
    res = client.post("/teams/", json={"name": "Brasil", "code": "ARG"})
    assert res.status_code == 409


def test_list_teams(client: TestClient):
    client.post("/teams/", json={"name": "Argentina", "code": "ARG"})
    client.post("/teams/", json={"name": "Brasil", "code": "BRA"})
    res = client.get("/teams/")
    assert res.status_code == 200
    assert len(res.json()) == 2


def test_get_team(client: TestClient):
    res = client.post("/teams/", json={"name": "Argentina", "code": "ARG"})
    team_id = res.json()["id"]
    res = client.get(f"/teams/{team_id}")
    assert res.status_code == 200
    assert res.json()["name"] == "Argentina"


def test_get_team_not_found(client: TestClient):
    res = client.get("/teams/999")
    assert res.status_code == 404


def test_update_team(client: TestClient):
    res = client.post("/teams/", json={"name": "Argentina", "code": "ARG"})
    team_id = res.json()["id"]
    res = client.put(f"/teams/{team_id}", json={"name": "Argentina Actualizado"})
    assert res.status_code == 200
    assert res.json()["name"] == "Argentina Actualizado"


def test_delete_team(client: TestClient):
    res = client.post("/teams/", json={"name": "Argentina", "code": "ARG"})
    team_id = res.json()["id"]
    res = client.delete(f"/teams/{team_id}")
    assert res.status_code == 204
    res = client.get(f"/teams/{team_id}")
    assert res.status_code == 404


def test_create_team_duplicate_name(client: TestClient):
    client.post("/teams/", json={"name": "Argentina", "code": "ARG"})
    res = client.post("/teams/", json={"name": "Argentina", "code": "BRA"})
    assert res.status_code == 409
    assert "name" in res.json()["detail"].lower()


def test_update_team_duplicate_name(client: TestClient):
    client.post("/teams/", json={"name": "Argentina", "code": "ARG"})
    res = client.post("/teams/", json={"name": "Brasil", "code": "BRA"})
    team2_id = res.json()["id"]
    res = client.put(f"/teams/{team2_id}", json={"name": "Argentina"})
    assert res.status_code == 409
    assert "name" in res.json()["detail"].lower()


def test_update_team_duplicate_code_different_team(client: TestClient):
    client.post("/teams/", json={"name": "Argentina", "code": "ARG"})
    res = client.post("/teams/", json={"name": "Brasil", "code": "BRA"})
    team2_id = res.json()["id"]
    res = client.put(f"/teams/{team2_id}", json={"code": "ARG"})
    assert res.status_code == 409
    assert "code" in res.json()["detail"].lower()


def test_create_team_code_too_short(client: TestClient):
    res = client.post("/teams/", json={"name": "Argentina", "code": "AR"})
    assert res.status_code == 400


def test_create_team_code_too_long(client: TestClient):
    res = client.post("/teams/", json={"name": "Argentina", "code": "ARGD"})
    assert res.status_code == 400


def test_create_team_code_with_numbers(client: TestClient):
    res = client.post("/teams/", json={"name": "Argentina", "code": "AR1"})
    assert res.status_code == 400


def test_create_team_empty_name(client: TestClient):
    res = client.post("/teams/", json={"name": "", "code": "ARG"})
    assert res.status_code == 400