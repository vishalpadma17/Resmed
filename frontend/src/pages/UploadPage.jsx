import { useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';

const MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024;

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

    if (file.size > MAX_FILE_SIZE_BYTES) {
      setSelectedFile(null);
      event.target.value = '';
      setIsError(true);
      setStatusMessage('File is too large. Please select a file up to 20 MB.');
      return;
    }

    setSelectedFile(file);
  };

  const handleSubmit = (event) => {
    event.preventDefault();

    if (!selectedFile) {
      setIsError(true);
      setStatusMessage('Please choose one file before submitting.');
      return;
    }

    if (selectedFile.size > MAX_FILE_SIZE_BYTES) {
      setIsError(true);
      setStatusMessage('File is too large. Please select a file up to 20 MB.');
      return;
    }

    const formData = new FormData();
    formData.append('document', selectedFile);

    // Placeholder success flow until backend upload endpoint is connected.
    setIsError(false);
    setStatusMessage('File is ready and validated with multipart/form-data payload.');
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
            <span className="upload-help-text">One file at a time, max size 20 MB.</span>
            {fileDetails ? <span className="upload-file-meta">{fileDetails}</span> : null}
          </label>

          {statusMessage ? (
            <p className={`upload-status ${isError ? 'upload-status-error' : 'upload-status-success'}`}>{statusMessage}</p>
          ) : null}

          <div className="upload-actions">
            <button className="small-ghost-button" type="button" onClick={() => navigate('/')}>
              Back
            </button>
            <button className="small-solid-button" type="submit">
              Enter
            </button>
          </div>
        </form>
      </section>
    </main>
  );
}

export default UploadPage;
