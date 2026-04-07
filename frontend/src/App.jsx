import { Navigate, Route, Routes } from 'react-router-dom';
import LandingPage from './pages/LandingPage.jsx';
import UploadPage from './pages/UploadPage.jsx';
import DocumentsPage from './pages/DocumentsPage.jsx';
import DocumentDetailPage from './pages/DocumentDetailPage.jsx';

function App() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/upload" element={<UploadPage />} />
      <Route path="/documents" element={<DocumentsPage />} />
      <Route path="/documents/:fileId" element={<DocumentDetailPage />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default App;
