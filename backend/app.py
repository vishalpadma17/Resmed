import os
import uuid
import shutil
import logging
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

from extract_and_summarize import extract_and_summarize
from database import init_db, insert_file, get_file, get_all_files, update_summary

app = FastAPI(title="Study Hive API")

# Initialise the SQLite database (creates table if needed)
init_db()

# CORS – allow the Vite dev server and common local origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directory where uploaded files are stored
UPLOAD_DIR = Path(__file__).resolve().parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)


# ---------------------------------------------------------------------------
# API 1 – Upload a file
# ---------------------------------------------------------------------------
@app.post("/upload")
async def upload_file(document: UploadFile = File(...)):
    """Accept a file upload (multipart/form-data) and return a unique file ID."""
    try:
        file_id = uuid.uuid4().hex
        safe_name = document.filename or "unnamed"
        dest = UPLOAD_DIR / f"{file_id}_{safe_name}"

        with open(dest, "wb") as buf:
            shutil.copyfileobj(document.file, buf)

        file_size = os.path.getsize(dest)
        uploaded_at = datetime.utcnow().isoformat()

        insert_file(
            file_id=file_id,
            filename=safe_name,
            size=file_size,
            uploaded_at=uploaded_at,
        )

        return {"file_id": file_id, "filename": safe_name}

    except Exception as e:
        logger.exception("Upload failed for file_id=%s with error: %s", file_id, str(e))
        raise HTTPException(status_code=500, detail="The file could not be uploaded at this time. Please try again or contact the admin.")


# ---------------------------------------------------------------------------
# API 2 – Download a file by ID
# ---------------------------------------------------------------------------
@app.get("/files/{file_id}/download")
async def download_file(file_id: str):
    """Download the file associated with the given ID."""
    try:
        meta = get_file(file_id)
        if not meta:
            raise HTTPException(status_code=404, detail="The requested document could not be found. Please check the file and try again.")

        # Locate the file on disk using the stored file_id + filename
        matches = list(UPLOAD_DIR.glob(f"{file_id}_*"))
        if not matches or not matches[0].exists():
            raise HTTPException(status_code=404, detail="The requested document could not be found in storage. Please contact the admin.")

        return FileResponse(
            path=str(matches[0]),
            filename=meta["filename"],
            media_type="application/octet-stream",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Download failed for file_id=%s with error: %s", file_id, str(e))
        raise HTTPException(status_code=500, detail="The file could not be downloaded at this time. Please try again or contact the admin.")


# ---------------------------------------------------------------------------
# API 3 – List all uploaded files (metadata only)
# ---------------------------------------------------------------------------
@app.get("/files")
async def list_files():
    """Return metadata for every uploaded file (no content)."""
    try:
        return {"files": get_all_files()}

    except Exception as e:
        logger.exception("Failed to list files due to error %s", str(e))
        raise HTTPException(status_code=500, detail="Unable to retrieve the document list. Please try again or contact the admin.")


# ---------------------------------------------------------------------------
# API 4 – Get an LLM-generated summary of a file
# ---------------------------------------------------------------------------
@app.get("/files/{file_id}/summary")
async def get_file_summary(file_id: str):
    """Return an LLM-generated summary for the file with the given ID."""
    try:
        meta = get_file(file_id)
        if not meta:
            raise HTTPException(status_code=404, detail="The requested document could not be found. Please check the file and try again.")

        # Return cached summary if available
        if meta.get("summary"):
            return {
                "file_id": file_id,
                "filename": meta["filename"],
                "summary": meta["summary"],
            }

        matches = list(UPLOAD_DIR.glob(f"{file_id}_*"))
        if not matches or not matches[0].exists():
            raise HTTPException(status_code=404, detail="The requested document could not be found in storage. Please contact the admin.")

        summary = extract_and_summarize(str(matches[0]))

        if summary.startswith("Error:"):
            logger.error("Summarization returned an error for file_id=%s: %s", file_id, summary)
            raise HTTPException(status_code=500, detail="The summarization of the current document is not possible. Please contact the admin.")

        # Persist the summary in the database
        update_summary(file_id, summary)

        return {
            "file_id": file_id,
            "filename": meta["filename"],
            "summary": summary,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Summary generation failed for file_id=%s with error: %s", file_id, str(e))
        raise HTTPException(status_code=500, detail="The summarization of the current document is not possible. Please contact the admin.")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
