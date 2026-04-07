import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';

function DocumentDetailPage() {
  const { fileId } = useParams();
  const navigate = useNavigate();
  const [meta, setMeta] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [summary, setSummary] = useState('');
  const [summarizing, setSummarizing] = useState(false);
  const [summaryError, setSummaryError] = useState('');

  useEffect(() => {
    let cancelled = false;

    async function fetchFile() {
      try {
        const res = await fetch('/api/files');
        if (!res.ok) {
          const err = await res.json().catch(() => ({}));
          throw new Error(err.detail || `Failed to load file (${res.status})`);
        }
        const data = await res.json();
        const file = (data.files || []).find((f) => f.file_id === fileId);
        if (!file) throw new Error('File not found.');
        if (!cancelled) setMeta(file);
      } catch (err) {
        if (!cancelled) setError(err.message);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    fetchFile();
    return () => { cancelled = true; };
  }, [fileId]);

  async function handleDownload() {
    const link = document.createElement('a');
    link.href = `/api/files/${fileId}/download`;
    link.download = meta?.filename || 'file';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }

  async function handleSummarize() {
    setSummarizing(true);
    setSummaryError('');
    setSummary('');
    try {
      const res = await fetch(`/api/files/${fileId}/summary`);
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || `Summary failed (${res.status})`);
      }
      const data = await res.json();
      setSummary(data.summary || 'No summary returned.');
    } catch (err) {
      setSummaryError(err.message);
    } finally {
      setSummarizing(false);
    }
  }

  return (
    <main className="page-shell">
      <section className="study-panel detail-panel" aria-label="Document detail">
        <header className="panel-title-wrap">
          <h1 className="panel-title">Study Hive</h1>
        </header>

        <div className="detail-content">
          {loading && <p className="docs-status">Loading…</p>}
          {error && <p className="docs-status docs-error">{error}</p>}

          {!loading && !error && meta && (
            <>
              <div className="detail-card">
                <h2 className="detail-doc-name">{meta.filename}</h2>

                <div className="detail-row">
                  <span className="detail-label">Unique ID</span>
                  <span className="detail-value detail-id">{meta.file_id}</span>
                </div>
                <div className="detail-row">
                  <span className="detail-label">Size</span>
                  <span className="detail-value">{meta.size.toLocaleString()} bytes</span>
                </div>
                <div className="detail-row">
                  <span className="detail-label">Upload Timestamp</span>
                  <span className="detail-value">{new Date(meta.uploaded_at).toLocaleString()}</span>
                </div>
              </div>

              <div className="detail-actions">
                <button
                  className="small-ghost-button"
                  type="button"
                  onClick={handleDownload}
                >
                  Download
                </button>
                <button
                  className="small-solid-button"
                  type="button"
                  onClick={handleSummarize}
                  disabled={summarizing}
                >
                  {summarizing ? 'Summarizing…' : 'Summarize'}
                </button>
              </div>

              {summaryError && (
                <p className="docs-status docs-error">{summaryError}</p>
              )}

              {summary && (
                <div className="detail-summary">
                  <h3 className="detail-summary-heading">Summary</h3>
                  <p className="detail-summary-text">{summary}</p>
                </div>
              )}
            </>
          )}

          <div className="upload-actions">
            <button className="small-ghost-button" type="button" onClick={() => navigate('/documents')}>
              Back
            </button>
          </div>
        </div>
      </section>
    </main>
  );
}

export default DocumentDetailPage;
