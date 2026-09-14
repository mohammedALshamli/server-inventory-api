"""Inventory logic for server-inventory-api.

Everything here is a plain function. No Flask, no network, no files opened
except in load_inventory. That is what makes it easy to unit test.
"""

import json

VALID_STATUS = {"online", "offline", "maintenance"}


class InventoryError(Exception):
    """Raised when the inventory file is missing or malformed."""


def load_inventory(path):
    """Read servers.json and return a list of server dicts.

    Raises InventoryError if the file is missing, is not valid JSON,
    or does not contain a top-level "servers" list.
    """
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except FileNotFoundError as exc:
        raise InventoryError(f"inventory file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise InventoryError(f"inventory file is not valid JSON: {exc}") from exc

    servers = data.get("servers")
    if not isinstance(servers, list):
        raise InventoryError("inventory file must contain a 'servers' list")
    return servers


def filter_servers(servers, env=None, status=None):
    """Return the servers matching env and/or status.

    Both filters are optional. Matching is case-insensitive.
    """
    result = servers
    if env:
        result = [s for s in result if s.get("env", "").lower() == env.lower()]
    if status:
        result = [s for s in result if s.get("status", "").lower() == status.lower()]
    return result


def find_server(servers, name):
    """Return one server by name, or None if there is no match."""
    for server in servers:
        if server.get("name", "").lower() == name.lower():
            return server
    return None


def summarize(servers):
    """Build a summary of the inventory.

    Returns a dict with the total count, a count per environment,
    a count per status, and the total CPU cores across all servers.
    """
    by_env = {}
    by_status = {}
    total_cpu = 0

    for server in servers:
        env = server.get("env", "unknown")
        status = server.get("status", "unknown")
        by_env[env] = by_env.get(env, 0) + 1
        by_status[status] = by_status.get(status, 0) + 1
        total_cpu += server.get("cpu_cores", 0)

    return {
        "total": len(servers),
        "by_env": by_env,
        "by_status": by_status,
        "total_cpu_cores": total_cpu,
    }


def unhealthy(servers):
    """Return the names of servers that are not online.

    The list is sorted so the output is stable and easy to assert on.
    """
    names = [s.get("name", "") for s in servers if s.get("status") != "online"]
    return sorted(names)


def validate_server(server):
    """Check one server dict and return a list of problems.

    An empty list means the server record is fine.
    """
    problems = []

    name = server.get("name")
    if not name:
        problems.append("missing name")

    if not server.get("env"):
        problems.append("missing env")

    status = server.get("status")
    if status not in VALID_STATUS:
        problems.append(f"invalid status: {status}")

    cores = server.get("cpu_cores")
    if not isinstance(cores, int) or cores <= 0:
        problems.append("cpu_cores must be a positive integer")

    return problems
