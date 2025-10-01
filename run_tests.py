# ------------------------------------------------------------
# run_tests.py — Run all stdlib unittest tests
# ------------------------------------------------------------
import sys, unittest

if __name__ == "__main__":
    suite = unittest.defaultTestLoader.discover("tests_unittest")
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
