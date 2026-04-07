import unittest

import test_helpers as helper


class TestListFilesEndpoint(unittest.TestCase):
    ENDPOINT = "/files"
    CASE_TITLES = {
        "test_list_files_returns_uploaded_metadata": "List files returns metadata",
        "test_list_files_returns_500_when_data_access_fails": "List files handles internal data error",
    }

    def setUp(self):
        self.temp_root = helper.configure_isolated_environment()
        self.client = helper.create_client()

    def tearDown(self):
        helper.cleanup_environment(self.temp_root)

    def test_list_files_returns_uploaded_metadata(self):
        helper.insert_metadata("id_1", "Sample_Text_25.txt", 123)
        helper.insert_metadata("id_2", "Sample_pdf_25.pdf", 456)

        response = self.client.get("/files")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("files", payload)
        ids = {item["file_id"] for item in payload["files"]}
        self.assertTrue({"id_1", "id_2"}.issubset(ids))

    def test_list_files_returns_500_when_data_access_fails(self):
        original = helper.backend_app.get_all_files
        helper.backend_app.get_all_files = lambda: (_ for _ in ()).throw(Exception("db failure"))

        try:
            response = self.client.get("/files")
        finally:
            helper.backend_app.get_all_files = original

        self.assertEqual(response.status_code, 500)
        self.assertIn("Unable to retrieve", response.json()["detail"])


if __name__ == "__main__":
    unittest.main()
