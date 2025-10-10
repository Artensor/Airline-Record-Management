# Airline Record Management System

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)

---

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Requirements](#requirements)
4. [Quick Start](#quick-start)
5. [Project Structure](#project-structure)
6. [Data Models](#data-models)
7. [API Reference](#api-reference-v1)
8. [Status Codes](#status-codes)
9. [Testing](#testing)
10. [Frontend Details](#frontend-details)

---

## Overview

Solution to manage **Clients**, **Airlines**, and **Flights** with both a **Backend API (Python stdlib)** and a **Frontend GUI (HTML/JS)**.

---

## Features

**Backend (API)**
 - ✅ Pure Python 3 (stdlib only — no third-party libraries)
 - ✅ JSON file storage (one per entity, auto-save/load)
 - ✅ CRUD for Clients, Airlines, Flights
 - ✅ Business rules enforced:
      - IDs are user-provided and must be unique
      - Cannot delete Client/Airline if it has today/future flights
      - Flights list shows only today & future, sorted by date

**Frontend (GUI)**
- ✅ Implemented with vanilla HTML/CSS/JS (no frameworks)
- ✅ Separate forms for Create/Update/Delete/Search per entity
- ✅ Integrated with backend APIs via fetch calls
- ✅ Design guided by Figma prototype: https://www.figma.com/design/bY4HncvPWx1Rem6Bu2JHI9/Record-Management-System?node-id=65-201 

---

## Requirements

  - **Python 3.10+**
  - No `pip install` needed (stdlib only).
  - Browser (tested in Chrome/Edge/Safari).

- `requirements.txt` is intentionally empty.

---

## Quick Start

1. Run the Backend API

Run from repo root (the folder with `serve_stdlib.py`):

- **macOS/Linux**

```bash
export DATA_DIR=./data-stdlib
python serve_stdlib.py
```


- **Windows (PowerShell)**

```powershell
$env:DATA_DIR = ".\data-stdlib"
python serve_stdlib.py
```
You should see:

```text
Serving on http://127.0.0.1:5000  (Ctrl+C to stop)
```

Stop with Ctrl+C.

- **Run from VS Code**

  1. Open repo root in VS Code
  2. Select Python 3.x interpreter
  3. Add .vscode/launch.json:
  ```json
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
---

2. Run the Frontend (GUI)

  With the server running, open the GUI in a browser:

  👉 http://127.0.0.1:5000/dashboard.html

  The dashboard allows navigation across Clients, Airlines, and Flights, with options to add, update, delete, and search records.

---

## Project Structure

```text
serve_stdlib.py             # stdlib HTTP server (entrypoint)
run_tests.py                # stdlib unittest runner
requirements.txt            # empty (no external deps)

src/
  conf/                     # configuration (enums, errors, settings)
  record/                   # backend services and repos
    clients/                # clients repo + service
    airlines/               # airlines repo + service
    flights/                # flights repo + service
    common/                 # JSON load/save + validation helpers
  frontend/                 # GUI (HTML/CSS/JS)
    dashboard.html           # main dashboard
    add_new_clients_form.html
    add_new_airlines_form.html
    add_new_flights_form.html
    update_clients_form.html
    update_airlines_form.html
    update_flights_form.html
    js/                     # all JS handlers (fetch + events)
      dashboard.js
      add_new_clients_form.js
      add_new_airlines_form.js
      add_new_flights_form.js
      update_clients_form.js
      update_airlines_form.js
      update_flights_form.js
    style.css                # frontend stylesheet
    tests/                   # frontend test harness
      tests.html
      tests.js
  search/                   # search helpers
tests_unittest/             # backend unit tests
data-stdlib/                # JSON storage (auto-created if missing)
```

---

## Data Models

- **Client**

```json
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

```
Allowed type: Business, Corporate, Leisure, VIP (case-insensitive on input).

- **Airline**

```json
 {
  "id": 301,
  "type": "National",          // ENUM (case-insensitive input; stored canonical)
  "company_name": "Air Demo"
}
```
Allowed type: Charter, Low Cost, National, Regional (case-insensitive on input).

- **Flight**

```json
 {
  "client_id": 101,
  "airline_id": 301,
  "date": "2999-01-01",        // ISO 8601: "YYYY-MM-DD" or "YYYY-MM-DDTHH:MM[:SS]" (optional 'Z')
  "start_city": "NYC",
  "end_city": "SFO"
}
```

Identity is (client_id, airline_id, date).
Flights are only listed if date >= today.

**Date Format Tips**

Accepted formats:
  - YYYY-MM-DD
  - YYYY-MM-DDTHH:MM or YYYY-MM-DDTHH:MM:SS
  - Optional Z suffix (treated as UTC for parsing)

---

## API Reference (v1)

Base URL: http://127.0.0.1:5000

**Health**

```bash
GET /health → {"status":"ok"}
```

**Clients**

```bash
POST /api/v1/clients — create

GET /api/v1/clients/{id} — read

PUT /api/v1/clients/{id} — update

DELETE /api/v1/clients/{id} — delete

GET /api/v1/clients?q=&sort= — search/list
```

**Example**
```bash
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

# Search
curl -s "http://127.0.0.1:5000/api/v1/clients?q=alice&sort=id"

# Delete
curl -i -X DELETE http://127.0.0.1:5000/api/v1/clients/101
```


**Airlines**
```bash

POST /api/v1/airlines — create

GET /api/v1/airlines/{id} — read

PUT /api/v1/airlines/{id} — update

DELETE /api/v1/airlines/{id} — delete

GET /api/v1/airlines?q=&sort= — search/list
```

**Examples** 
```bash
# Create
curl -i -X POST http://127.0.0.1:5000/api/v1/airlines \
  -H "Content-Type: application/json" \
  -d '{"id":301,"type":"national","company_name":"Air Demo"}'

# Get
curl -s http://127.0.0.1:5000/api/v1/airlines/301

# Update
curl -i -X PUT http://127.0.0.1:5000/api/v1/airlines/301 \
  -H "Content-Type: application/json" \
  -d '{"company_name":"Air Demo Updated"}'

# Search
curl -s "http://127.0.0.1:5000/api/v1/airlines?q=air&sort=company_name"

# Delete
curl -i -X DELETE http://127.0.0.1:5000/api/v1/airlines/301
```


**Flights**

```bash
POST /api/v1/flights — create

GET /api/v1/flights?... — list today+future

GET /api/v1/flights/{client_id}/{airline_id}/{date} — read

PUT /api/v1/flights/{client_id}/{airline_id}/{date} — update

DELETE /api/v1/flights/{client_id}/{airline_id}/{date} — delete
```

**Examples** 
```bash
# Create future flight
curl -i -X POST http://127.0.0.1:5000/api/v1/flights \
-H "Content-Type: application/json" \
-d '{"client_id":101,"airline_id":301,"date":"2999-01-01","start_city":"NYC","end_city":"SFO"}'

# List
curl -s http://127.0.0.1:5000/api/v1/flights

# Get one
curl -s http://127.0.0.1:5000/api/v1/flights/101/301/2999-01-01

# Update
curl -i -X PUT http://127.0.0.1:5000/api/v1/flights/101/301/2999-01-01 \
-H "Content-Type: application/json" \
-d '{"start_city":"NYC-Updated"}'

# Delete
curl -i -X DELETE http://127.0.0.1:5000/api/v1/flights/101/301/2999-01-01
```


---

## Status Codes

- 201 Created — POST success

- 200 OK — GET/PUT success

- 204 No Content — DELETE success

- 400 Bad Request — invalid ID / identity change

- 404 Not Found — resource missing

-  409 Conflict — duplicate ID

- 422 Unprocessable Entity — validation errors (missing fields, bad enum, delete guard, etc.)

---

## Testing

- **Backend unit tests**
```bash
export DATA_DIR=./data-test 
python run_tests.py
```
```powershell
$env:DATA_DIR = ".\data-test"
python run_tests.py
```

The runner discovers tests under `tests_unittest/`.

Tests use temp folders and reset repo singletons, so they won’t affect your live data.


- **Frontend testing**

Manual UAT: open `dashboard.html` → run Create/Update/Delete/Search flows.
Lightweight test harness under frontend/tests/ (`tests.html`, `tests.js`).

Ensure IDs entered are integers, as backend requires numeric IDs.

---

## Frontend details

The GUI is built with vanilla HTML, CSS, and JavaScript and connects to the backend API using fetch.

**Structure**

- `dashboard.html`→ entry point (tabs for Clients, Airlines, Flights)

**Entity Forms**

Add forms:
- `add_new_clients_form.html` → `js/add_new_clients_form.js`
- `add_new_airlines_form.html` → `js/add_new_airlines_form.js`
- `add_new_flights_form.html` → `js/add_new_flights_form.js`

Update forms:
- `update_clients_form.html` → `js/update_clients_form.js`
- `update_airlines_form.html` → `js/update_airlines_form.js`
- `update_flights_form.html` → `js/update_flights_form.js`

- Each form maps fields to JSON payloads and calls the relevant backend API endpoint.

**Style**

- Shared `style.css` ensures consistent layout and simple responsive design.

**Design**

- Figma prototype: https://www.figma.com/design/bY4HncvPWx1Rem6Bu2JHI9/Record-Management-System?node-id=65-201 