import os, tempfile, unittest
from src.record.airlines import service as airlines
from src.record.airlines import repo as airlines_repo
from src.record.flights import repo as flights_repo
from src.record.clients import service as clients

class AirlinesServiceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        os.environ["DATA_DIR"] = self.tmp.name
        airlines_repo._reset_singleton_for_tests()
        flights_repo._reset_singleton_for_tests()

        # create a client used by flights
        from src.record.clients import repo as clients_repo
        clients_repo._reset_singleton_for_tests()
        clients.create_client({
            "id": 700, "type": "leisure", "name": "Bob",
            "address_line1":"a","city":"c","state":"s","zip_code":"100","country":"X","phone_number":"+1"
        })

    def tearDown(self):
        airlines_repo._reset_singleton_for_tests()
        flights_repo._reset_singleton_for_tests()
        from src.record.clients import repo as clients_repo
        clients_repo._reset_singleton_for_tests()
        self.tmp.cleanup()

    def test_create_get_update_delete_with_guard(self):
        a = airlines.create_airline({"id": 301, "type": "national", "company_name": "Air X"})
        self.assertEqual(a["type"], "National")
        got = airlines.get_airline(301)
        self.assertEqual(got["company_name"], "Air X")

        upd = airlines.update_airline(301, {"company_name": "Air X Up"})
        self.assertEqual(upd["company_name"], "Air X Up")

        # add a future flight -> deletion should be blocked
        from src.record.flights import service as flights
        flights.create_flight({
            "client_id": 700, "airline_id": 301, "date": "2999-01-01",
            "start_city": "A", "end_city": "B"
        })
        with self.assertRaises(Exception):
            airlines.delete_airline(301)

    def test_search_no_pagination(self):
        airlines.create_airline({"id": 310, "type": "regional", "company_name": "Air A"})
        airlines.create_airline({"id": 311, "type": "charter",  "company_name": "Air B"})
        res = airlines.search_airlines(q="Air", sort="company_name")
        self.assertGreaterEqual(res["count"], 2)

if __name__ == "__main__":
    unittest.main()
