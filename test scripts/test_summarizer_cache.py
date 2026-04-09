import sys
import unittest
import importlib.util
from pathlib import Path
from unittest.mock import patch

ROOT_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT_DIR / "backend"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

spec = importlib.util.spec_from_file_location(
    "extract_and_summarize",
    str(BACKEND_DIR / "extract_and_summarize.py"),
)
if spec is None or spec.loader is None:
    raise RuntimeError("Failed to load extract_and_summarize module for tests.")

eas = importlib.util.module_from_spec(spec)
spec.loader.exec_module(eas)


class FakeSummarizer:
    def __call__(self, text, **kwargs):
        return [{"summary_text": f"summary:{text[:20]}"}]


class TestSummarizerCache(unittest.TestCase):
    def setUp(self):
        eas.reset_summarizer_cache()

    def tearDown(self):
        eas.reset_summarizer_cache()

    def test_same_model_loaded_once(self):
        with patch.object(eas, "pipeline", return_value=FakeSummarizer()) as mocked_pipeline:
            eas.summarize_text("This is some readable content for a first call.", model_name="m1")
            eas.summarize_text("This is some readable content for a second call.", model_name="m1")

            self.assertEqual(mocked_pipeline.call_count, 1)

    def test_different_models_cached_independently(self):
        with patch.object(eas, "pipeline", return_value=FakeSummarizer()) as mocked_pipeline:
            eas.summarize_text("Text for model one.", model_name="m1")
            eas.summarize_text("Text for model two.", model_name="m2")

            self.assertEqual(mocked_pipeline.call_count, 2)

    def test_reset_cache_forces_reload(self):
        with patch.object(eas, "pipeline", return_value=FakeSummarizer()) as mocked_pipeline:
            eas.summarize_text("First load.", model_name="m1")
            eas.reset_summarizer_cache()
            eas.summarize_text("Second load after reset.", model_name="m1")

            self.assertEqual(mocked_pipeline.call_count, 2)


if __name__ == "__main__":
    unittest.main()
