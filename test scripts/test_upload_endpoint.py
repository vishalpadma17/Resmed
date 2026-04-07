import io
import unittest

import test_helpers as helper


class TestUploadEndpoint(unittest.TestCase):
    ENDPOINT = "/upload"
    CASE_TITLES = {
        "test_upload_accepts_supported_files_from_test_data": "Upload valid files from test_data",
        "test_upload_rejects_file_larger_than_20mb": "Reject upload above 20MB limit",
    }

    def setUp(self):
        self.temp_root = helper.configure_isolated_environment()
        self.client = helper.create_client()

    def tearDown(self):
        helper.cleanup_environment(self.temp_root)

    def test_upload_accepts_supported_files_from_test_data(self):
        contract_file = helper.TEST_DATA_DIR / "Sample_word_contract.docx"
        self.assertTrue(contract_file.exists(), "Sample_word_contract.docx not found in test_data")

        if contract_file.stat().st_size <= helper.backend_app.MAX_UPLOAD_SIZE_BYTES:
            with open(contract_file, "rb") as file_obj:
                response = self.client.post(
                    "/upload",
                    files={"document": (contract_file.name, file_obj)},
                )

            self.assertEqual(response.status_code, 200)
            payload = response.json()
            self.assertIn("file_id", payload)
            self.assertEqual(payload["filename"], contract_file.name)
            return

        # If the contract sample is oversized in a local environment, keep positive coverage
        # by using a within-limit payload derived from the same file content.
        contract_bytes = contract_file.read_bytes()
        in_limit_payload = contract_bytes[:4096] if contract_bytes else b"small test content"

        response = self.client.post(
            "/upload",
            files={
                "document": (
                    "Sample_word_contract_within_limit.docx",
                    io.BytesIO(in_limit_payload),
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
            },
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("file_id", payload)
        self.assertEqual(payload["filename"], "Sample_word_contract_within_limit.docx")

    def test_upload_rejects_file_larger_than_20mb(self):
        files = helper.available_test_files()
        oversized_file = next(
            (p for p in files if p.stat().st_size > helper.backend_app.MAX_UPLOAD_SIZE_BYTES),
            None,
        )

        if oversized_file:
            with open(oversized_file, "rb") as file_obj:
                response = self.client.post(
                    "/upload",
                    files={"document": (oversized_file.name, file_obj)},
                )
        else:
            oversized_payload = helper.build_oversized_payload_from_test_data(
                helper.backend_app.MAX_UPLOAD_SIZE_BYTES + 1024
            )

            response = self.client.post(
                "/upload",
                files={
                    "document": (
                        "oversized_from_test_data.txt",
                        io.BytesIO(oversized_payload),
                        "text/plain",
                    )
                },
            )

        self.assertEqual(response.status_code, 400)
        self.assertIn("20MB", response.json()["detail"])


if __name__ == "__main__":
    unittest.main()
