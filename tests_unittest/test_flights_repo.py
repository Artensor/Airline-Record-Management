import os, tempfile, unittest
from src.record.flights.repo import FlightsRepo, _reset_singleton_for_tests
from src.conf.errors import NotFound

def _sample(client_id=1, airline_id=10, date="2999-01-01T09:00:00", start="CityA", end="CityB"):
    return {"client_id": client_id,"airline_id": airline_id,"date": date,"start_city": start,"end_city": end}

class FlightsRepoTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        os.environ["DATA_DIR"] = self.tmp.name
        _reset_singleton_for_tests()

    def tearDown(self):
        _reset_singleton_for_tests()
        self.tmp.cleanup()

    def test_insert_list_get_update_delete(self):
        r = FlightsRepo(data_dir=self.tmp.name, autosave=True)
        r.insert(_sample(1, 10, "2999-01-01T09:00:00", "A", "B"))
        r.insert(_sample(1, 10, "2999-01-02T09:00:00", "C", "D"))
        self.assertEqual(len(r.list_all()), 2)

        one = r.get_one(1, 10, "2999-01-02T09:00:00")
        self.assertEqual(one["start_city"], "C")

        upd = r.update(1, 10, "2999-01-02T09:00:00", {"start_city": "C2"})
        self.assertEqual(upd["start_city"], "C2")

        self.assertTrue(r.delete(1, 10, "2999-01-02T09:00:00"))
        with self.assertRaises(NotFound):
            r.get_one(1, 10, "2999-01-02T09:00:00")

if __name__ == "__main__":
    unittest.main()
