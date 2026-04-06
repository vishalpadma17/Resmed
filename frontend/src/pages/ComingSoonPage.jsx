import { useNavigate } from 'react-router-dom';

function ComingSoonPage() {
  const navigate = useNavigate();

  return (
    <main className="page-shell">
      <section className="study-panel placeholder-panel" aria-label="Feature coming soon">
        <header className="panel-title-wrap">
          <h1 className="panel-title">Study Hive</h1>
        </header>

        <div className="placeholder-content">
          <h2>Documents Page Coming Soon</h2>
          <p>This area will show all processed files, downloads, and summaries.</p>
          <button className="small-solid-button" type="button" onClick={() => navigate('/')}>
            Back to Home
          </button>
        </div>
      </section>
    </main>
  );
}

export default ComingSoonPage;
