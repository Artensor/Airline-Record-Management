# ------------------------------------------------------------
# test_health_endpoint.py — lightweight integration check
# Requires the server to be running on HOST:PORT.
# ------------------------------------------------------------
import json, http.client, unittest

HOST, PORT = "127.0.0.1", 5000

class TestHealthEndpoint(unittest.TestCase):
    def test_health_ok(self):
        conn = http.client.HTTPConnection(HOST, PORT, timeout=2)
        conn.request("GET", "/api/v1/health")
        resp = conn.getresponse()
        body = resp.read().decode("utf-8")
        conn.close()
        self.assertEqual(resp.status, 200)
        self.assertEqual(json.loads(body).get("status"), "ok")

if __name__ == "__main__":
    unittest.main()
