# Airline Record Management — Flask Backend

Small backend for a travel agent. It manages:
- **Clients** (done)
- **Airlines** and **Flights** (to be added later)

Data is stored as JSON files on disk (lists of dicts). **IDs are user-provided**, must be **unique**, and **cannot change** after creation.

---

## Requirements
- Python **3.10–3.12**
- No database needed

---

## Setup

```bash
# from the project root
python3 -m venv .venv
# macOS/Linux:
source .venv/bin/activate
# Windows (PowerShell):
# .\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

## Run the app

### Easiest (recommended)
```bash
python run.py
```
Open: http://127.0.0.1:5000/health  
You should see: `{"status":"ok","version":"v1"}`

### Alternate (Flask CLI)
```bash
python -m flask --app src.main:create_app run
```

**Where data is stored**  
JSON files are created under `src/data/`.  
To use a different folder for a run:

```bash
# macOS/Linux
export DATA_DIR=./mydata
# Windows PowerShell
# $env:DATA_DIR = ".\mydata"
```

---

## API (v1)

Base: `/api/v1`

### Clients

#### Create
`POST /api/v1/clients`

Body:
```json
{
  "id": 1,
  "type": "business",
  "name": "Alice",
  "address_line1": "123 Ave",
  "address_line2": null,
  "address_line3": null,
  "city": "San José",
  "state": "SJ",
  "zip_code": "10101",
  "country": "CR",
  "phone_number": "+506 8888-8888"
}
```

Example:
```bash
curl -s -X POST http://127.0.0.1:5000/api/v1/clients \
  -H "Content-Type: application/json" \
  -d '{
    "id": 1,
    "type": "business",
    "name": "Alice",
    "address_line1": "123 Ave",
    "city": "San José",
    "state": "SJ",
    "zip_code": "10101",
    "country": "CR",
    "phone_number": "+506 8888-8888"
  }'
```

#### Get one
`GET /api/v1/clients/1`

#### List
`GET /api/v1/clients?limit=50&offset=0&sort=id`

Returns:
```json
{ "data": [ ... ], "count": 3, "limit": 50, "offset": 0, "sort": "id" }
```

#### Search
`GET /api/v1/clients?q=alice&type=business&city=Heredia&state=SJ&country=CR`

- `q` searches: `id`, `name`, `city`, `country`, `phone_number`
- `type`, `city`, `state`, `country` are exact (case-insensitive)

#### Update
`PUT /api/v1/clients/1`  
Body: partial or full record. If `id` is present in the body, it **must** equal the path ID.

#### Delete
`DELETE /api/v1/clients/1` → `204 No Content`

#### Error format (all endpoints)
```json
{ "error": { "code": "DUPLICATE_ID", "message": "ID already exists" } }
```
Common codes: `INVALID_ID`, `DUPLICATE_ID`, `ID_IMMUTABLE`, `INVALID_INPUT`, `NOT_FOUND`

---

## Tests

```bash
pytest -q
```

The tests use a temporary data folder, so they won’t touch `src/data/`.

---

## Notes for VS Code users
- Running **`run.py`** with the ▶ button works out of the box (recommended).
- If you run `src/main.py` directly, use a debug config or ensure the repo root is on `PYTHONPATH`.