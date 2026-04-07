import unittest
from pathlib import Path


class DetailedResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.records = []
        self.passed = []

    def _record(self, test, result, detail=""):
        endpoint = getattr(test.__class__, "ENDPOINT", "unknown")
        case_titles = getattr(test.__class__, "CASE_TITLES", {})
        method_name = getattr(test, "_testMethodName", str(test))
        case_name = case_titles.get(method_name, method_name.replace("_", " "))

        self.records.append(
            {
                "test_case": case_name,
                "endpoint": endpoint,
                "result": result,
                "detail": detail,
            }
        )

    def addSuccess(self, test):
        super().addSuccess(test)
        self.passed.append(test)
        self._record(test, "PASS")

    def addFailure(self, test, err):
        super().addFailure(test, err)
        message = self._exc_info_to_string(err, test).splitlines()[-1]
        self._record(test, "FAIL", message)

    def addError(self, test, err):
        super().addError(test, err)
        message = self._exc_info_to_string(err, test).splitlines()[-1]
        self._record(test, "ERROR", message)


if __name__ == "__main__":
    test_dir = Path(__file__).resolve().parent
    suite = unittest.defaultTestLoader.discover(
        start_dir=str(test_dir),
        pattern="test_*_endpoint.py",
    )

    runner = unittest.TextTestRunner(verbosity=2, resultclass=DetailedResult)
    result = runner.run(suite)

    print("\n=== Endpoint Test Status Report ===")
    print(f"{'Test Case':52} | {'Endpoint':30} | {'Result':8}")
    print("-" * 100)

    for entry in result.records:
        print(
            f"{entry['test_case'][:52]:52} | "
            f"{entry['endpoint'][:30]:30} | "
            f"{entry['result']:8}"
        )
        if entry["detail"]:
            print(f"    Detail: {entry['detail']}")

    print("-" * 100)
    print(
        f"Total: {result.testsRun}, "
        f"Passed: {len(result.passed)}, "
        f"Failed: {len(result.failures)}, "
        f"Errors: {len(result.errors)}"
    )
