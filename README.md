# Airline Record Management (Backend, stdlib-only)

Solution to manage **Clients**, **Airlines**, and **Flights**.

**BackEnd**

✅ **No third-party libraries** — only Python’s standard library.

- **Storage:** JSON files (one per entity) in a local data folder  
- **Architecture:** API (stdlib HTTP server) → Service (business rules) → Repo (JSON I/O)  
- **APIs:** CRUD for Clients/Airlines/Flights, plus search/list 
- **Rules:**  
  - **IDs are user-provided** must be **unique**  
  - **Delete guard:** cannot delete a Client or Airline if it has **today/future** flights  
  - **Flights list:** shows **today & future** only, sorted by date (past flights are hidden)

---

## Requirements

- **Python 3.10+**
- No `pip install` needed. `requirements.txt` is intentionally empty.

> Always run commands from the **repo root** (the folder containing `serve_stdlib.py` and `src/`).

---

## Quick Start

### Run from the console

**macOS / Linux**
```bash
# optional: choose where JSON data is stored
export DATA_DIR=./data-stdlib

# start the server
python serve_stdlib.py

Windows (PowerShell)

$env:DATA_DIR = ".\data-stdlib"
python serve_stdlib.py

You should see:
Serving on http://127.0.0.1:5000  (Ctrl+C to stop)
Stop with Ctrl+C. You’ll get a clean shutdown.

Run from VS Code (Run button)
1. Open the repo root in VS Code.
2. Command Palette → Python: Select Interpreter → pick your Python 3.x.
3. Add .vscode/launch.json:

{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Run API (stdlib)",
      "type": "python",
      "request": "launch",
      "program": "${workspaceFolder}/serve_stdlib.py",
      "env": { "DATA_DIR": "${workspaceFolder}/data-stdlib" },
      "console": "integratedTerminal"
    },
    {
      "name": "Run tests (unittest)",
      "type": "python",
      "request": "launch",
      "program": "${workspaceFolder}/run_tests.py",
      "console": "integratedTerminal"
    }
  ]
}

Use the Run and Debug panel to start Run API (stdlib) or Run tests (unittest).

Project Structure
serve_stdlib.py             # stdlib HTTP server (entrypoint)
run_tests.py                # stdlib unittest runner (optional)
requirements.txt            # empty (no external deps)

src/
  conf/
    errors.py               # small custom exceptions
    settings.py             # DATA_DIR, AUTOSAVE
    enums.py                # allowed types (Clients / Airlines)
  record/
    common/
      storage.py            # JSON load / save
      validation.py         # small validators + date helpers

    clients/
      repo.py               # JSON CRUD (no business logic)
      service.py            # validation + rules for Clients
    airlines/
      repo.py               # JSON CRUD
      service.py            # validation + rules for Airlines
    flights/
      repo.py               # JSON CRUD (composite identity)
      service.py            # validation + rules for Flights

tests_unittest/             # stdlib tests (if included)

Data Model
{
  "id": 101,
  "type": "Business",          // ENUM (case-insensitive input; stored canonical)
  "name": "Alice",
  "address_line1": "123 Main",
  "address_line2": "optional",
  "address_line3": "optional",
  "city": "Springfield",
  "state": "IL",
  "zip_code": "62701",
  "country": "USA",
  "phone_number": "+1-555-1111"
}
Allowed type: Business, Corporate, Leisure, VIP (case-insensitive on input).

Airline
{
  "id": 301,
  "type": "National",          // ENUM (case-insensitive input; stored canonical)
  "company_name": "Air Demo"
}
Allowed type: Charter, Low Cost, National, Regional (case-insensitive on input).

Flight
{
  "client_id": 101,
  "airline_id": 301,
  "date": "2999-01-01",        // ISO 8601: "YYYY-MM-DD" or "YYYY-MM-DDTHH:MM[:SS]" (optional 'Z')
  "start_city": "NYC",
  "end_city": "SFO"
}
Identity is (client_id, airline_id, date).
Flights are only listed if date >= today.

API Reference (v1)

Base URL: http://127.0.0.1:5000

Health
GET /health → {"status":"ok"}

Clients
- POST /api/v1/clients — create (user supplies unique id)
- GET /api/v1/clients/{id} — read one
- PUT /api/v1/clients/{id} — update (cannot change id)
- DELETE /api/v1/clients/{id} — delete
- GET /api/v1/clients?q=&sort= — search/list (no pagination) 
  - q matches name or city (case-insensitive)

Examples
# Create
curl -i -X POST http://127.0.0.1:5000/api/v1/clients \
  -H "Content-Type: application/json" \
  -d '{"id":101,"type":"business","name":"Alice","address_line1":"123 Main","city":"Springfield","state":"IL","zip_code":"62701","country":"USA","phone_number":"+1-555-1111"}'

# Get
curl -s http://127.0.0.1:5000/api/v1/clients/101

# Update
curl -i -X PUT http://127.0.0.1:5000/api/v1/clients/101 \
  -H "Content-Type: application/json" \
  -d '{"city":"New City"}'

# Search (no pagination)
curl -s "http://127.0.0.1:5000/api/v1/clients?q=alice&sort=id"

# Delete (422 if client has future/today flights)
curl -i -X DELETE http://127.0.0.1:5000/api/v1/clients/101

Airlines

- POST /api/v1/airlines — create
- GET /api/v1/airlines/{id} — read one
- PUT /api/v1/airlines/{id} — update (cannot change id)
- DELETE /api/v1/airlines/{id} — delete
- GET /api/v1/airlines?q=&sort= — search/list (no pagination) 
  - q matches company_name (case-insensitive)

Examples
curl -i -X POST http://127.0.0.1:5000/api/v1/airlines \
  -H "Content-Type: application/json" \
  -d '{"id":301,"type":"national","company_name":"Air Demo"}'

curl -s http://127.0.0.1:5000/api/v1/airlines/301

curl -i -X PUT http://127.0.0.1:5000/api/v1/airlines/301 \
  -H "Content-Type: application/json" \
  -d '{"company_name":"Air Demo Updated"}'

curl -s "http://127.0.0.1:5000/api/v1/airlines?q=air&sort=company_name"

curl -i -X DELETE http://127.0.0.1:5000/api/v1/airlines/301

Flights

- POST /api/v1/flights — create (composite identity). Client + Airline must already exist.
- GET /api/v1/flights?client_id=&airline_id=&q= — list today & future only, sorted by date asc 
  - client_id (optional)
  - airline_id (optional)
  - q matches start_city or end_city (case-insensitive)

- GET /api/v1/flights/{client_id}/{airline_id}/{date} — read one
- PUT /api/v1/flights/{client_id}/{airline_id}/{date} — update (cannot change identity)
- DELETE /api/v1/flights/{client_id}/{airline_id}/{date} — delete

Examples
# Create a *future* flight
curl -i -X POST http://127.0.0.1:5000/api/v1/flights \
  -H "Content-Type: application/json" \
  -d '{"client_id":101,"airline_id":301,"date":"2999-01-01","start_city":"NYC","end_city":"SFO"}'

# List flights (today+future)
curl -s http://127.0.0.1:5000/api/v1/flights

# Get one by composite key
curl -s http://127.0.0.1:5000/api/v1/flights/101/301/2999-01-01

# Update
curl -i -X PUT http://127.0.0.1:5000/api/v1/flights/101/301/2999-01-01 \
  -H "Content-Type: application/json" \
  -d '{"start_city":"NYC-Updated"}'

# Delete
curl -i -X DELETE http://127.0.0.1:5000/api/v1/flights/101/301/2999-01-01
```
## Details
Status Codes
- 201 Created — POST success
- 200 OK — GET/PUT success (returns JSON)
- 204 No Content — DELETE success
- 400 Bad Request — bad ID format, attempted identity change
- 404 Not Found — resource not found
- 409 Conflict — duplicate ID on create
- 422 Unprocessable Entity — validation errors (missing fields, bad enum, FK missing, delete guard, etc.)

Date Format Tips
Accepted:
"YYYY-MM-DD"
"YYYY-MM-DDTHH:MM" or "YYYY-MM-DDTHH:MM:SS"
Optional 'Z' suffix (treated as UTC for parsing)

Tests (stdlib unittest)
Optional in case you want to test:
export DATA_DIR=./data-test   # PowerShell: $env:DATA_DIR = ".\data-test"
python run_tests.py

The runner discovers tests under tests_unittest/.
Tests use temp folders and reset repo singletons, so they won’t affect your live data.