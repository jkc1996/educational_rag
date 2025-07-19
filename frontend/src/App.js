import React from "react";
import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import UploadPage from "./pages/UploadPage";
import QAPage from "./pages/QAPage";

function App() {
  return (
    <Router>
      <div style={{ padding: 24 }}>
        <h1>edu-rag Academic QA System</h1>
        <nav>
          <Link to="/" style={{ marginRight: 16 }}>Upload PDF</Link>
          <Link to="/qa">Ask Question</Link>
        </nav>
        <hr />
        <Routes>
          <Route path="/" element={<UploadPage />} />
          <Route path="/qa" element={<QAPage />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
