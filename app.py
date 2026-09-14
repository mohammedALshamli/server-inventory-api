"""server-inventory-api

A small Flask API over a JSON server inventory.
The endpoints are chosen so they map onto the CI/CD pipeline you will build:

  /healthz   liveness  - is the process up?
  /readyz    readiness - is the inventory loaded and usable?
  /version   which build is running (set by the pipeline)
  /servers   the data itself
"""

import os

from flask import Flask, jsonify, request

from inventory import (
    InventoryError,
    filter_servers,
    find_server,
    load_inventory,
    summarize,
    unhealthy,
)

APP_VERSION = os.getenv("APP_VERSION", "0.1.0")
INVENTORY_PATH = os.getenv("INVENTORY_PATH", "servers.json")

app = Flask(__name__)

# Loaded once at startup. If it fails, the app still starts but /readyz
# reports not-ready. That is what a readiness probe is for.
try:
    SERVERS = load_inventory(INVENTORY_PATH)
    LOAD_ERROR = None
except InventoryError as exc:
    SERVERS = []
    LOAD_ERROR = str(exc)


@app.get("/healthz")
def healthz():
    """Liveness. Always 200 while the process is running."""
    return jsonify(status="ok"), 200


@app.get("/readyz")
def readyz():
    """Readiness. 200 only when the inventory loaded correctly."""
    if LOAD_ERROR:
        return jsonify(status="not ready", reason=LOAD_ERROR), 503
    return jsonify(status="ready", servers_loaded=len(SERVERS)), 200


@app.get("/version")
def version():
    return jsonify(version=APP_VERSION), 200


@app.get("/servers")
def list_servers():
    """List servers. Optional filters: ?env=prod&status=online"""
    env = request.args.get("env")
    status = request.args.get("status")
    matches = filter_servers(SERVERS, env=env, status=status)
    return jsonify(count=len(matches), servers=matches), 200


@app.get("/servers/<name>")
def get_server(name):
    server = find_server(SERVERS, name)
    if server is None:
        return jsonify(error="server not found", name=name), 404
    return jsonify(server), 200


@app.get("/stats")
def stats():
    data = summarize(SERVERS)
    data["unhealthy"] = unhealthy(SERVERS)
    return jsonify(data), 200


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port)
