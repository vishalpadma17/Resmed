import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

function formatBytes(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  const units = ['KB', 'MB', 'GB'];
  let value = bytes / 1024;
  let idx = 0;
  while (value >= 1024 && idx < units.length - 1) {
    value /= 1024;
    idx += 1;
  }
  return `${value.toFixed(value >= 10 ? 0 : 1)} ${units[idx]}`;
}

function DocumentsPage() {
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    let cancelled = false;

    async function fetchFiles() {
      try {
        const res = await fetch('/api/files');
        if (!res.ok) {
          const err = await res.json().catch(() => ({}));
          throw new Error(err.detail || `Failed to load files (${res.status})`);
        }
        const data = await res.json();
        if (!cancelled) {
          setFiles(data.files || []);
        }
      } catch (err) {
        if (!cancelled) setError(err.message);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    fetchFiles();
    return () => { cancelled = true; };
  }, []);

  return (
    <main className="page-shell">
      <section className="study-panel docs-panel" aria-label="Uploaded documents">
        <header className="panel-title-wrap">
          <h1 className="panel-title">Study Hive</h1>
        </header>

        <div className="docs-content">
          <h2 className="docs-heading">Your Documents</h2>

          {loading && <p className="docs-status">Loading…</p>}
          {error && <p className="docs-status docs-error">{error}</p>}

          {!loading && !error && files.length === 0 && (
            <p className="docs-status">No documents uploaded yet.</p>
          )}

          {!loading && !error && files.length > 0 && (
            <ul className="docs-list">
              {files.map((f) => (
                <li
                  key={f.file_id}
                  className="docs-item docs-item-detail docs-item-clickable"
                  role="button"
                  tabIndex={0}
                  onClick={() => navigate(`/documents/${f.file_id}`)}
                  onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') navigate(`/documents/${f.file_id}`); }}
                >
                  <div className="docs-detail-row">
                    <span className="docs-label">File Name</span>
                    <span className="docs-value docs-filename">{f.filename}</span>
                  </div>
                  <div className="docs-detail-row">
                    <span className="docs-label">Size</span>
                    <span className="docs-value">{f.size.toLocaleString()} bytes</span>
                  </div>
                  <div className="docs-detail-row">
                    <span className="docs-label">Uploaded</span>
                    <span className="docs-value">{new Date(f.uploaded_at).toLocaleString()}</span>
                  </div>
                  <div className="docs-detail-row">
                    <span className="docs-label">Unique ID</span>
                    <span className="docs-value docs-id">{f.file_id}</span>
                  </div>
                </li>
              ))}
            </ul>
          )}

          <div className="upload-actions">
            <button className="small-ghost-button" type="button" onClick={() => navigate('/')}>
              Back
            </button>
          </div>
        </div>
      </section>
    </main>
  );
}

export default DocumentsPage;
