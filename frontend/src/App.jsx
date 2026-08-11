import styles from "./App.module.css";
import { Routes, Route, Navigate } from 'react-router-dom';
import Header from "./components/header/Header";
import UploadPage from "./pages/Upload/UploadPage";
import RegistryPage from "./pages/Registry/RegistryPage";
import Footer from "./components/footer/Footer";

function App() {
  return (
    <div className={styles.globalGridContainer}>
      <Header />

      <main>
        <Routes>
          <Route path="/" element={<Navigate to="/upload" replace />} />

          <Route path="/upload" element={<UploadPage />} />
          <Route path="/registry" element={<RegistryPage />} />

          <Route path="*" element={<div>Страница не найдена</div>} />
        </Routes>
      </main>

      <Footer />
    </div>
  );
}

export default App;
