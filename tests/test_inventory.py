"""Unit tests for the inventory logic. No Flask involved."""

import json

import pytest

from inventory import (
    InventoryError,
    filter_servers,
    find_server,
    load_inventory,
    summarize,
    unhealthy,
    validate_server,
)

SAMPLE = [
    {"name": "web-01", "env": "prod", "status": "online", "cpu_cores": 8},
    {"name": "db-01", "env": "prod", "status": "maintenance", "cpu_cores": 16},
    {"name": "web-s1", "env": "staging", "status": "online", "cpu_cores": 4},
    {"name": "test-01", "env": "dev", "status": "offline", "cpu_cores": 2},
]


def test_load_inventory_reads_the_real_file():
    servers = load_inventory("servers.json")
    assert len(servers) == 9
    assert servers[0]["name"] == "web-01"


def test_load_inventory_missing_file_raises():
    with pytest.raises(InventoryError):
        load_inventory("does-not-exist.json")


def test_load_inventory_bad_json_raises(tmp_path):
    bad = tmp_path / "broken.json"
    bad.write_text("{ this is not json", encoding="utf-8")
    with pytest.raises(InventoryError):
        load_inventory(str(bad))


def test_load_inventory_wrong_shape_raises(tmp_path):
    wrong = tmp_path / "wrong.json"
    wrong.write_text(json.dumps({"hosts": []}), encoding="utf-8")
    with pytest.raises(InventoryError):
        load_inventory(str(wrong))


def test_filter_by_env():
    assert len(filter_servers(SAMPLE, env="prod")) == 2


def test_filter_is_case_insensitive():
    assert len(filter_servers(SAMPLE, env="PROD")) == 2


def test_filter_by_env_and_status():
    result = filter_servers(SAMPLE, env="prod", status="online")
    assert len(result) == 1
    assert result[0]["name"] == "web-01"


def test_filter_with_no_arguments_returns_everything():
    assert len(filter_servers(SAMPLE)) == 4


def test_find_server_hit_and_miss():
    assert find_server(SAMPLE, "db-01")["cpu_cores"] == 16
    assert find_server(SAMPLE, "nope") is None


def test_summarize_counts():
    result = summarize(SAMPLE)
    assert result["total"] == 4
    assert result["by_env"]["prod"] == 2
    assert result["by_status"]["online"] == 2
    assert result["total_cpu_cores"] == 30


def test_summarize_empty_list():
    result = summarize([])
    assert result["total"] == 0
    assert result["total_cpu_cores"] == 0
    assert result["by_env"] == {}


def test_unhealthy_is_sorted():
    assert unhealthy(SAMPLE) == ["db-01", "test-01"]


def test_validate_server_accepts_a_good_record():
    good = {"name": "web-01", "env": "prod", "status": "online", "cpu_cores": 8}
    assert validate_server(good) == []


def test_validate_server_reports_every_problem():
    bad = {"name": "", "env": "", "status": "banana", "cpu_cores": 0}
    problems = validate_server(bad)
    assert len(problems) == 4
