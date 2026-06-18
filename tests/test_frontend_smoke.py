import os
import uuid

import pytest


pytestmark = pytest.mark.frontend

APP_URL = os.getenv("APP_URL", "http://127.0.0.1:8000")


def _unique(name: str) -> str:
    return f"{name}_{uuid.uuid4().hex[:8]}"


def test_frontend_main_simulation_flow(page):
    page.goto(APP_URL)
    page.wait_for_load_state("networkidle")

    button = page.locator("#btnSimular")
    assert button.is_visible()
    assert button.is_enabled()

    with page.expect_response(
        lambda response: "/simulator/run" in response.url
        and response.request.method == "POST",
        timeout=30000,
    ) as simulation_response:
        button.click()

    response = simulation_response.value
    assert response.ok

    page.wait_for_selector("#resultsSection", state="visible", timeout=30000)
    page.wait_for_function(
        "document.getElementById('championResult').innerText.trim().length > 0",
        timeout=30000,
    )
    page.wait_for_function(
        "document.getElementById('dashboardResult').innerText.trim().length > 10",
        timeout=30000,
    )
    page.wait_for_function(
        "document.getElementById('bracketResult').innerText.trim().length > 10",
        timeout=30000,
    )

    assert page.locator("#championResult").is_visible()
    assert page.locator("#dashboardResult").is_visible()
    assert page.locator("#bracketResult").is_visible()

    page.set_viewport_size({"width": 375, "height": 667})
    page.wait_for_timeout(500)

    scroll_width = page.evaluate("document.body.scrollWidth")
    viewport_width = page.evaluate("window.innerWidth")
    assert scroll_width <= viewport_width


def test_api_duplicate_team_code_via_browser(page):
    request = page.request
    tag = uuid.uuid4().hex[:6]
    name_a = f"Argentina_{tag}"
    name_b = f"Brasil_{tag}"
    code_a = f"AR{tag[:2]}"
    request.post(f"{APP_URL}/teams/", data={"name": name_a, "code": code_a})
    res = request.post(f"{APP_URL}/teams/", data={"name": name_b, "code": code_a})
    assert res.status == 409
    body = res.json()
    assert "code" in body["detail"].lower()


def test_api_duplicate_team_name_via_browser(page):
    request = page.request
    tag = uuid.uuid4().hex[:6]
    name = f"Argentina_{tag}"
    code_a = f"AR{tag[:2]}1"
    code_b = f"AR{tag[:2]}2"
    request.post(f"{APP_URL}/teams/", data={"name": name, "code": code_a})
    res = request.post(f"{APP_URL}/teams/", data={"name": name, "code": code_b})
    assert res.status == 409
    body = res.json()
    assert "name" in body["detail"].lower()


def test_api_duplicate_player_in_team_via_browser(page):
    request = page.request
    tag = uuid.uuid4().hex[:6]
    team_name = f"Argentina_{tag}"
    code = f"AR{tag[:3]}"
    team_res = request.post(f"{APP_URL}/teams/", data={"name": team_name, "code": code})
    team = team_res.json()
    player_name = f"Messi_{tag}"
    request.post(f"{APP_URL}/players/", data={"name": player_name, "position": "FW", "team_id": team["id"]})
    res = request.post(f"{APP_URL}/players/", data={"name": player_name, "position": "FW", "team_id": team["id"]})
    assert res.status == 409
    body = res.json()
    assert "player" in body["detail"].lower()


def test_api_player_same_name_different_team_via_browser(page):
    request = page.request
    tag = uuid.uuid4().hex[:6]
    t1_name = f"Argentina_{tag}"
    t2_name = f"Brasil_{tag}"
    code_1 = f"AR{tag[:3]}"
    code_2 = f"BR{tag[:3]}"
    t1 = request.post(f"{APP_URL}/teams/", data={"name": t1_name, "code": code_1}).json()
    t2 = request.post(f"{APP_URL}/teams/", data={"name": t2_name, "code": code_2}).json()
    player_name = f"Messi_{tag}"
    res1 = request.post(f"{APP_URL}/players/", data={"name": player_name, "position": "FW", "team_id": t1["id"]})
    assert res1.status == 201
    res2 = request.post(f"{APP_URL}/players/", data={"name": player_name, "position": "FW", "team_id": t2["id"]})
    assert res2.status == 201
