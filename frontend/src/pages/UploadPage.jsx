import { useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';

function formatBytes(bytes) {
  if (bytes < 1024) {
    return `${bytes} B`;
  }

  const units = ['KB', 'MB', 'GB'];
  let value = bytes / 1024;
  let index = 0;

  while (value >= 1024 && index < units.length - 1) {
    value /= 1024;
    index += 1;
  }

  return `${value.toFixed(value >= 10 ? 0 : 1)} ${units[index]}`;
}

function UploadPage() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [statusMessage, setStatusMessage] = useState('');
  const [isError, setIsError] = useState(false);
  const navigate = useNavigate();

  const fileDetails = useMemo(() => {
    if (!selectedFile) {
      return null;
    }

    return `${selectedFile.name} (${formatBytes(selectedFile.size)})`;
  }, [selectedFile]);

  const handleFileChange = (event) => {
    const file = event.target.files?.[0];
    setStatusMessage('');
    setIsError(false);

    if (!file) {
      setSelectedFile(null);
      return;
    }

    setSelectedFile(file);
  };

  const [isUploading, setIsUploading] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();

    if (!selectedFile) {
      setIsError(true);
      setStatusMessage('Please choose one file before submitting.');
      return;
    }

    const formData = new FormData();
    formData.append('document', selectedFile);

    setIsUploading(true);
    setIsError(false);
    setStatusMessage('');

    try {
      const res = await fetch('/upload', {
        method: 'POST',
        body: formData,
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || `Upload failed (${res.status})`);
      }

      const data = await res.json();
      setIsError(false);
      setStatusMessage(`Uploaded successfully: ${data.filename}`);
      setSelectedFile(null);
    } catch (err) {
      setIsError(true);
      setStatusMessage(err.message || 'Upload failed. Please try again.');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <main className="page-shell">
      <section className="study-panel upload-panel" aria-label="Upload document form">
        <header className="panel-title-wrap">
          <h1 className="panel-title">Study Hive</h1>
        </header>

        <form className="upload-form" onSubmit={handleSubmit} encType="multipart/form-data">
          <label className="upload-drop-zone" htmlFor="document-upload">
            <input
              id="document-upload"
              name="document"
              type="file"
              className="upload-input"
              onChange={handleFileChange}
            />
            <span className="upload-headline">Upload a Document</span>
            <span className="upload-help-text">One file at a time. Accepted formats: PDF, DOCX, TXT.</span>
            {fileDetails ? <span className="upload-file-meta">{fileDetails}</span> : null}
          </label>

          {statusMessage ? (
            <p className={`upload-status ${isError ? 'upload-status-error' : 'upload-status-success'}`}>{statusMessage}</p>
          ) : null}

          <div className="upload-actions">
            <button className="small-ghost-button" type="button" onClick={() => navigate('/')}>
              Back
            </button>
            <button className="small-solid-button" type="submit" disabled={isUploading}>
              {isUploading ? 'Uploading…' : 'Enter'}
            </button>
          </div>
        </form>
      </section>
    </main>
  );
}

export default UploadPage;
