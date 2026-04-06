const actions = [
  {
    title: 'Upload a Document',
    subtitle: 'Store resources securely on disk.',
    accentClass: 'accent-upload'
  },
  {
    title: 'View all Documents',
    subtitle: 'Browse, download, and summarize files.',
    accentClass: 'accent-library'
  }
];

function App() {
  return (
    <main className="page-shell">
      <section className="study-panel" aria-label="Study Hive landing actions">
        <header className="panel-title-wrap">
          <h1 className="panel-title">Study Hive</h1>
        </header>

        <div className="action-grid">
          {actions.map((action) => (
            <button key={action.title} className={`action-card ${action.accentClass}`} type="button">
              <span className="action-title">{action.title}</span>
              <span className="action-subtitle">{action.subtitle}</span>
            </button>
          ))}
        </div>
      </section>
    </main>
  );
}

export default App;
