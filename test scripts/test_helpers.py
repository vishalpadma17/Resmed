import shutil
import sys
import tempfile
from datetime import datetime
from pathlib import Path

from fastapi.testclient import TestClient

ROOT_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT_DIR / "backend"
TEST_DATA_DIR = ROOT_DIR / "test_data"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import app as backend_app  # noqa: E402
import database as db_module  # noqa: E402


def configure_isolated_environment() -> Path:
    """Point backend storage and DB to temporary test-only locations."""
    temp_root = Path(tempfile.mkdtemp(prefix="studyhive_tests_"))
    uploads_dir = temp_root / "uploads"
    uploads_dir.mkdir(parents=True, exist_ok=True)

    db_module.DB_PATH = temp_root / "studyhive_test.db"
    db_module.init_db()

    backend_app.UPLOAD_DIR = uploads_dir
    backend_app.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    return temp_root


def cleanup_environment(temp_root: Path) -> None:
    shutil.rmtree(temp_root, ignore_errors=True)


def create_client() -> TestClient:
    return TestClient(backend_app.app)


def insert_metadata(file_id: str, filename: str, size: int, summary: str = "") -> None:
    db_module.insert_file(
        file_id=file_id,
        filename=filename,
        size=size,
        uploaded_at=datetime.utcnow().isoformat(),
        summary=summary,
    )


def create_storage_file(file_id: str, filename: str, content: bytes) -> Path:
    path = backend_app.UPLOAD_DIR / f"{file_id}_{filename}"
    path.write_bytes(content)
    return path


def available_test_files() -> list[Path]:
    candidates = sorted(TEST_DATA_DIR.glob("*"))
    return [p for p in candidates if p.is_file()]


def build_oversized_payload_from_test_data(min_size_bytes: int) -> bytes:
    seed_file = TEST_DATA_DIR / "Sample_Text_25.txt"
    seed = seed_file.read_bytes()
    if not seed:
        seed = b"X"

    repeats = (min_size_bytes // len(seed)) + 2
    return seed * repeats
