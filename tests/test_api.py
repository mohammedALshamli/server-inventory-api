"""Tests for the HTTP endpoints, using the Flask test client."""

import pytest

from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_healthz_returns_200(client):
    resp = client.get("/healthz")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok"


def test_readyz_reports_ready(client):
    resp = client.get("/readyz")
    assert resp.status_code == 200
    assert resp.get_json()["servers_loaded"] == 9


def test_version_endpoint(client):
    resp = client.get("/version")
    assert resp.status_code == 200
    assert "version" in resp.get_json()


def test_list_all_servers(client):
    body = client.get("/servers").get_json()
    assert body["count"] == 9


def test_list_servers_filtered_by_env(client):
    body = client.get("/servers?env=prod").get_json()
    assert body["count"] == 5


def test_get_one_server(client):
    body = client.get("/servers/db-01").get_json()
    assert body["cpu_cores"] == 16


def test_get_unknown_server_returns_404(client):
    resp = client.get("/servers/ghost-99")
    assert resp.status_code == 404


def test_stats_endpoint(client):
    body = client.get("/stats").get_json()
    assert body["total"] == 9
    assert body["by_env"]["prod"] == 5
    assert "cache-01" in body["unhealthy"]
