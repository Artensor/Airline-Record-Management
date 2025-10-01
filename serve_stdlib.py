# ------------------------------------------------------------
# serve_stdlib.py — HTTP JSON server
# Exposes Clients, Airlines, Flights APIs (v1).
# ------------------------------------------------------------
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs
import json

from src.conf.errors import InvalidInput, InvalidID, DuplicateID, NotFound, ImmutableID
from src.record.clients import service as clients_svc
from src.record.airlines import service as airlines_svc
from src.record.flights import service as flights_svc

HOST = "127.0.0.1"
PORT = 5000
API_PREFIX = "/api/v1"

def read_json(h):
    n = int(h.headers.get("Content-Length") or 0)
    if n <= 0: return {}
    try:
        return json.loads(h.rfile.read(n))
    except Exception:
        raise InvalidInput("Request body must be JSON")

def write_json(h, status, payload=None, headers=None):
    h.send_response(status)
    h.send_header("Content-Type", "application/json")
    if headers:
        for k,v in headers.items():
            h.send_header(k, v)
    h.end_headers()
    if payload is not None:
        h.wfile.write(json.dumps(payload).encode("utf-8"))

def map_error(e):
    if isinstance(e, (InvalidID, ImmutableID)): return 400
    if isinstance(e, NotFound): return 404
    if isinstance(e, DuplicateID): return 409
    if isinstance(e, InvalidInput): return 422
    return 500

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args, **kwargs):  # keep console quiet
        pass

    def _parts_qs(self):
        p = urlparse(self.path)
        return [s for s in p.path.split("/") if s], parse_qs(p.query)

    # ------- GET -------
    def do_GET(self):
        try:
            parts, qs = self._parts_qs()
            if parts == ["health"]:
                return write_json(self, 200, {"status": "ok"})
            if len(parts) < 2 or ("/" + parts[0] + "/" + parts[1]) != API_PREFIX:
                return write_json(self, 404, {"error": "Not Found"})
            tail = parts[2:]

            # clients collection
            if tail == ["clients"]:
                q = (qs.get("q", [""])[0]).strip()
                sort = (qs.get("sort", ["id"])[0]).strip()
                return write_json(self, 200, clients_svc.search_clients(q=q, sort=sort))

            # clients/{id}
            if len(tail) == 2 and tail[0] == "clients":
                return write_json(self, 200, clients_svc.get_client(int(tail[1])))

            # airlines collection
            if tail == ["airlines"]:
                q = (qs.get("q", [""])[0]).strip()
                sort = (qs.get("sort", ["company_name"])[0]).strip()
                return write_json(self, 200, airlines_svc.search_airlines(q=q, sort=sort))

            # airlines/{id}
            if len(tail) == 2 and tail[0] == "airlines":
                return write_json(self, 200, airlines_svc.get_airline(int(tail[1])))

            # flights collection (today & future only, sorted by date)
            if tail == ["flights"]:
                q = (qs.get("q", [""])[0]).strip()
                cid = qs.get("client_id", [None])[0]
                aid = qs.get("airline_id", [None])[0]
                cid = int(cid) if cid not in (None, "",) else None
                aid = int(aid) if aid not in (None, "",) else None
                return write_json(self, 200, flights_svc.list_flights(q=q, client_id=cid, airline_id=aid))

            # flights/{client_id}/{airline_id}/{date}
            if len(tail) == 4 and tail[0] == "flights":
                return write_json(self, 200, flights_svc.get_flight(int(tail[1]), int(tail[2]), tail[3]))

            return write_json(self, 404, {"error": "Not Found"})
        except Exception as e:
            return write_json(self, map_error(e), {"error": str(e)})

    # ------- POST -------
    def do_POST(self):
        try:
            parts, _ = self._parts_qs()
            if len(parts) < 2 or ("/" + parts[0] + "/" + parts[1]) != API_PREFIX:
                return write_json(self, 404, {"error": "Not Found"})
            tail = parts[2:]
            body = read_json(self)

            if tail == ["clients"]:
                created = clients_svc.create_client(body)
                return write_json(self, 201, created, {"Location": f"{API_PREFIX}/clients/{created['id']}"})

            if tail == ["airlines"]:
                created = airlines_svc.create_airline(body)
                return write_json(self, 201, created, {"Location": f"{API_PREFIX}/airlines/{created['id']}"})

            if tail == ["flights"]:
                created = flights_svc.create_flight(body)
                loc = f"{API_PREFIX}/flights/{created['client_id']}/{created['airline_id']}/{created['date']}"
                return write_json(self, 201, created, {"Location": loc})

            return write_json(self, 404, {"error": "Not Found"})
        except Exception as e:
            return write_json(self, map_error(e), {"error": str(e)})

    # ------- PUT -------
    def do_PUT(self):
        try:
            parts, _ = self._parts_qs()
            if len(parts) < 2 or ("/" + parts[0] + "/" + parts[1]) != API_PREFIX:
                return write_json(self, 404, {"error": "Not Found"})
            tail = parts[2:]
            body = read_json(self)

            if len(tail) == 2 and tail[0] == "clients":
                return write_json(self, 200, clients_svc.update_client(int(tail[1]), body))

            if len(tail) == 2 and tail[0] == "airlines":
                return write_json(self, 200, airlines_svc.update_airline(int(tail[1]), body))

            if len(tail) == 4 and tail[0] == "flights":
                return write_json(self, 200, flights_svc.update_flight(int(tail[1]), int(tail[2]), tail[3], body))

            return write_json(self, 404, {"error": "Not Found"})
        except Exception as e:
            return write_json(self, map_error(e), {"error": str(e)})

    # ------- DELETE -------
    def do_DELETE(self):
        try:
            parts, _ = self._parts_qs()
            if len(parts) < 2 or ("/" + parts[0] + "/" + parts[1]) != API_PREFIX:
                return write_json(self, 404, {"error": "Not Found"})
            tail = parts[2:]

            if len(tail) == 2 and tail[0] == "clients":
                clients_svc.delete_client(int(tail[1]))
                return write_json(self, 204, None)

            if len(tail) == 2 and tail[0] == "airlines":
                airlines_svc.delete_airline(int(tail[1]))
                return write_json(self, 204, None)

            if len(tail) == 4 and tail[0] == "flights":
                flights_svc.delete_flight(int(tail[1]), int(tail[2]), tail[3])
                return write_json(self, 204, None)

            return write_json(self, 404, {"error": "Not Found"})
        except Exception as e:
            return write_json(self, map_error(e), {"error": str(e)})

class QuietServer(ThreadingHTTPServer):
    # let worker threads be daemons so shutdown is immediate
    daemon_threads = True
    # helps when restarting quickly on the same port
    allow_reuse_address = True

#Main entry point
if __name__ == "__main__":
    server = QuietServer((HOST, PORT), Handler)
    print(f"Serving on http://{HOST}:{PORT}  (Ctrl+C to stop)")
    try:
        # small poll interval reacts faster to shutdown
        server.serve_forever(poll_interval=0.5)
    except KeyboardInterrupt:
        # don't print a traceback on Ctrl+C
        print("\nShutting down...")
    finally:
        # ensure sockets/threads are cleaned up
        try:
            server.shutdown()
        except Exception:
            pass
        server.server_close()
        print("Server stopped.")
