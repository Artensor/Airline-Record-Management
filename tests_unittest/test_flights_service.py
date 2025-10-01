import os, tempfile, unittest
from src.record.flights import service as flights
from src.record.flights import repo as flights_repo
from src.record.clients import service as clients
from src.record.airlines import service as airlines

class FlightsServiceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        os.environ["DATA_DIR"] = self.tmp.name
        flights_repo._reset_singleton_for_tests()

        # seed a client and an airline
        from src.record.clients import repo as clients_repo
        from src.record.airlines import repo as airlines_repo
        clients_repo._reset_singleton_for_tests()
        airlines_repo._reset_singleton_for_tests()

        clients.create_client({
            "id": 900, "type": "corporate", "name": "Corp",
            "address_line1":"x","city":"c","state":"s","zip_code":"100","country":"X","phone_number":"+1"
        })
        airlines.create_airline({"id": 800, "type": "low_cost", "company_name": "LC"})

    def tearDown(self):
        flights_repo._reset_singleton_for_tests()
        from src.record.clients import repo as clients_repo
        from src.record.airlines import repo as airlines_repo
        clients_repo._reset_singleton_for_tests()
        airlines_repo._reset_singleton_for_tests()
        self.tmp.cleanup()

    def test_create_list_future_only_get_update_delete(self):
        # create future and past flights
        flights.create_flight({"client_id":900,"airline_id":800,"date":"1999-01-01","start_city":"X","end_city":"Y"})
        flights.create_flight({"client_id":900,"airline_id":800,"date":"2999-01-01","start_city":"A","end_city":"B"})

        # list should include only future
        res = flights.list_flights()
        self.assertGreaterEqual(res["count"], 1)
        for f in res["data"]:
            self.assertTrue(f["date"] >= "2025-")  # weak check; existence of future row matters

        # get/update/delete using composite key
        got = flights.get_flight(900, 800, "2999-01-01")
        self.assertEqual(got["start_city"], "A")

        upd = flights.update_flight(900, 800, "2999-01-01", {"start_city": "A2"})
        self.assertEqual(upd["start_city"], "A2")

        flights.delete_flight(900, 800, "2999-01-01")

        # confirm deletion
        from src.conf.errors import NotFound
        with self.assertRaises(NotFound):
            flights.get_flight(900, 800, "2999-01-01")

if __name__ == "__main__":
    unittest.main()
