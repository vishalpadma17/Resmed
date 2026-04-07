import unittest

import test_helpers as helper


class TestDownloadEndpoint(unittest.TestCase):
    ENDPOINT = "/files/{file_id}/download"
    CASE_TITLES = {
        "test_download_returns_existing_file": "Download existing file by id",
        "test_download_returns_404_for_unknown_file_id": "Download returns 404 for unknown id",
    }

    def setUp(self):
        self.temp_root = helper.configure_isolated_environment()
        self.client = helper.create_client()

    def tearDown(self):
        helper.cleanup_environment(self.temp_root)

    def test_download_returns_existing_file(self):
        file_id = "download_ok_1"
        filename = "Sample_Text_25.txt"
        content = b"download endpoint content"

        helper.insert_metadata(file_id, filename, len(content))
        helper.create_storage_file(file_id, filename, content)

        response = self.client.get(f"/files/{file_id}/download")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, content)
        self.assertIn(filename, response.headers.get("content-disposition", ""))

    def test_download_returns_404_for_unknown_file_id(self):
        response = self.client.get("/files/missing-id/download")
        self.assertEqual(response.status_code, 404)
        self.assertIn("could not be found", response.json()["detail"])


if __name__ == "__main__":
    unittest.main()
