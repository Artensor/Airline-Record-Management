import os, tempfile, unittest
from src.record.clients import service as clients
from src.record.clients import repo as clients_repo
from src.record.flights import repo as flights_repo
from src.record.airlines import service as airlines
from src.record.airlines import repo as airlines_repo

class ClientsServiceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        os.environ["DATA_DIR"] = self.tmp.name
        clients_repo._reset_singleton_for_tests()
        flights_repo._reset_singleton_for_tests()
        airlines_repo._reset_singleton_for_tests()

    def tearDown(self):
        clients_repo._reset_singleton_for_tests()
        flights_repo._reset_singleton_for_tests()
        airlines_repo._reset_singleton_for_tests()
        self.tmp.cleanup()

    def test_create_get_update_delete_with_guard(self):
        body = {
            "id": 101, "type": "business", "name": "Alice",
            "address_line1": "x","city":"C","state":"S","zip_code":"100","country":"X","phone_number":"+1"
        }
        created = clients.create_client(body)
        self.assertEqual(created["type"], "Business")

        got = clients.get_client(101)
        self.assertEqual(got["name"], "Alice")

        upd = clients.update_client(101, {"city": "New City"})
        self.assertEqual(upd["city"], "New City")
        # Seed an airline so the flight is valid
        airlines.create_airline({
            "id": 999,
            "type": "national",
            "company_name": "Air Demo"
        })
        # add a future flight -> deletion should be blocked
        from src.record.flights import service as flights
        flights.create_flight({
            "client_id": 101, "airline_id": 999, "date": "2999-01-01",
            "start_city": "A", "end_city": "B"
        })
        with self.assertRaises(Exception):
            clients.delete_client(101)        

    def test_search_no_pagination(self):
        for i in range(3):
            clients.create_client({
                "id": 200+i, "type": "vip", "name": f"N{i}",
                "address_line1": "a","city":"CityX","state":"S","zip_code":"100","country":"X","phone_number":"+1"
            })
        res = clients.search_clients(q="n", sort="id")
        self.assertGreaterEqual(res["count"], 3)
        self.assertTrue(isinstance(res["data"], list))

if __name__ == "__main__":
    unittest.main()
