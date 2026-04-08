import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "studyhive.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create the files table if it doesn't already exist."""
    conn = get_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS files (
            file_id   TEXT PRIMARY KEY,
            filename  TEXT NOT NULL,
            size      INTEGER NOT NULL,
            uploaded_at TEXT NOT NULL,
            summary   TEXT DEFAULT '',
            file_content TEXT DEFAULT ''
        )
        """
    )

    columns = [row["name"] for row in conn.execute("PRAGMA table_info(files)").fetchall()]
    if "file_content" not in columns:
        conn.execute("ALTER TABLE files ADD COLUMN file_content TEXT DEFAULT ''")

    conn.commit()
    conn.close()


def insert_file(
    file_id: str,
    filename: str,
    size: int,
    uploaded_at: str,
    summary: str = "",
    file_content: str = "",
):
    conn = get_connection()
    conn.execute(
        """
        INSERT INTO files (file_id, filename, size, uploaded_at, summary, file_content)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (file_id, filename, size, uploaded_at, summary, file_content),
    )
    conn.commit()
    conn.close()


def get_file(file_id: str) -> dict | None:
    conn = get_connection()
    row = conn.execute("SELECT * FROM files WHERE file_id = ?", (file_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_all_files() -> list[dict]:
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT file_id, filename, size, uploaded_at, summary
        FROM files
        ORDER BY uploaded_at DESC
        """
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_summary(file_id: str, summary: str):
    conn = get_connection()
    conn.execute("UPDATE files SET summary = ? WHERE file_id = ?", (summary, file_id))
    conn.commit()
    conn.close()
