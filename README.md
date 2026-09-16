# server-inventory-api

<!-- Homework task 8: put your workflow status badge on the line below -->

A small Flask API over a JSON server inventory. Used in the DevOps Engineering
Bootcamp, Course 07 (CI/CD).

## Run it locally

PowerShell on Windows 11:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pytest -q
flake8 .
$env:APP_VERSION = "0.1.0"
python app.py
```

If PowerShell blocks the activate script, run this once in the same window:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
```

## Endpoints

| Endpoint | What it returns |
|---|---|
| `GET /healthz` | Always 200 while the process is running |
| `GET /readyz` | 200 with `servers_loaded`, or 503 if the inventory is broken |
| `GET /version` | The value of the `APP_VERSION` environment variable |
| `GET /servers` | All servers. Filter with `?env=prod&status=online` |
| `GET /servers/<name>` | One server, or 404 |
| `GET /stats` | Counts per environment and status, plus unhealthy servers |

Try it:

```powershell
curl http://127.0.0.1:5000/stats
curl "http://127.0.0.1:5000/servers?env=prod&status=online"
```

## Layout

```
app.py                    Flask app, 7 endpoints
inventory.py              The logic. Plain functions, no Flask.
servers.json              9 servers across prod, staging and dev
tests/test_inventory.py   14 tests for the logic
tests/test_api.py         8 tests for the endpoints
requirements.txt          flask, pytest, flake8, requests
setup.cfg                 flake8 settings
pytest.ini                tells pytest where to find the code
.github/                  empty - your homework goes here
```

## Your homework

Create `.github/workflows/ci.yml` so GitHub runs the tests on every push.
Full instructions are in the homework PDF.
