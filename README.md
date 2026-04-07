# Study Hive

Study Hive is a full-stack document workflow app where users upload files, browse uploaded documents, download them, and generate AI summaries.
It uses a React frontend and a FastAPI backend with SQLite metadata storage and server-side summarization.

## API Endpoints

The backend exposes each endpoint in two forms: base route and `/api`-prefixed route.

### 1) Upload File
- `POST /api/upload`
- Purpose: Upload one document (`multipart/form-data`, field name: `document`).
- Response: Returns `file_id` and `filename`.

### 2) List Files
- `GET /api/files`
- Purpose: Return metadata for all uploaded files.
- Response: `files` array with `file_id`, `filename`, `size`, and `uploaded_at`.

### 3) Download File
- `GET /api/files/{file_id}/download`
- Purpose: Download a file by its ID.

### 4) Generate/Get Summary
- `GET /api/files/{file_id}/summary`
- Purpose: Generate and return an LLM summary for the selected document.
- Notes: If a summary already exists in DB, the cached summary is returned.

## Prerequisites

Install the following before running the project:

- Python 3.12+ (recommended 3.11)
- Node.js 18+ and npm
- pip (comes with Python)
- Git (optional, for cloning/version control)
- Internet access for first-time model downloads used by `transformers`/`torch`

Python backend dependencies (from `backend/requirements.txt`):
- `fastapi`
- `uvicorn`
- `python-multipart`
- `PyPDF2`
- `python-docx`
- `transformers`
- `torch`

Note: Make a virtual environment with all the above packages. This way the env can be controlled.

Frontend dependencies (from `frontend/package.json`):
- `react`
- `react-dom`
- `react-router-dom`
- `vite`
- `@vitejs/plugin-react`

## Running Frontend and Backend

There are two common ways to run this repo.

### Option A: Full Dev Mode (recommended while developing)

Run backend:

```bash
cd backend
python -m venv .venv
# Windows
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Run frontend in another terminal:

```bash
cd frontend
npm install
npm run dev
```

Open:
- Frontend: `http://localhost:5173`
- Backend: `http://127.0.0.1:8000/`

### Option B: Build Frontend and Serve from Backend (single app process)

Build frontend into backend static folder:

```bash
cd frontend
npm install
npm run build
```

Start backend:

```bash
cd backend
python -m venv .venv
# Windows
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Open:
- App: `http://localhost:8000`

## How to Use the App

1. Open the landing page.
2. Go to Upload and choose one file (PDF, DOCX, or TXT).
3. Submit the upload and wait for success confirmation.
4. Navigate to Documents to view all uploaded files and metadata.
5. Click a document to open its detail page.
6. Use Download to retrieve the original file.
7. Use Summarize to generate and view an AI summary.

## Troubleshooting

### 1) Frontend build not found
- Error: `Frontend build not found. Run npm run build in the frontend folder.`
- Fix: Run `npm run build` inside `frontend`, then restart backend.

### 2) Upload fails with file size error
- Error: `File size should be 20MB or less`
- Fix: Upload a file under 20 MB.

### 3) CORS or failed API calls in frontend dev mode
- Symptom: Requests from Vite UI fail.
- Fix: Ensure backend is running on port 8000 and frontend on 5173.

### 4) Summary generation fails
- Symptom: Summary endpoint returns 500.
- Fix: Check backend logs, verify dependencies installed, and ensure model download/network access works.

### 5) Missing Python/Node packages
- Symptom: `ModuleNotFoundError` or `command not found` errors.
- Fix: Reinstall dependencies:
	- Backend: `pip install -r backend/requirements.txt`
	- Frontend: `npm install` in `frontend`

### 6) File not found on download or summary
- Symptom: 404 for a valid `file_id`.
- Fix: Confirm upload completed successfully and uploaded files still exist in `backend/uploads`.
