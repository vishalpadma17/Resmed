import unittest

import test_helpers as helper


class TestSummaryEndpoint(unittest.TestCase):
    ENDPOINT = "/files/{file_id}/summary"
    CASE_TITLES = {
        "test_summary_returns_cached_value_when_available": "Summary returns cached value",
        "test_summary_returns_404_for_unknown_file_id": "Summary returns 404 for unknown id",
    }

    def setUp(self):
        self.temp_root = helper.configure_isolated_environment()
        self.client = helper.create_client()

    def tearDown(self):
        helper.cleanup_environment(self.temp_root)

    def test_summary_returns_cached_value_when_available(self):
        file_id = "summary_ok_1"
        filename = "Sample_pdf_25.docx"
        cached_summary = "Cached summary for test verification."

        helper.insert_metadata(file_id, filename, 50, summary=cached_summary)

        response = self.client.get(f"/files/{file_id}/summary")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["file_id"], file_id)
        self.assertEqual(payload["filename"], filename)
        self.assertEqual(payload["summary"], cached_summary)

    def test_summary_returns_404_for_unknown_file_id(self):
        response = self.client.get("/files/missing-id/summary")
        self.assertEqual(response.status_code, 404)
        self.assertIn("could not be found", response.json()["detail"])


if __name__ == "__main__":
    unittest.main()
