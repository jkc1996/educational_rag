import { Alert, LinearProgress } from "@mui/material";
import { Navigate, Route, Routes } from "react-router-dom";

import { api } from "./api/client.js";
import { AppShell } from "./components/AppShell.jsx";
import { useBootstrap } from "./hooks/useBootstrap.js";
import { DocumentManager } from "./features/documents/DocumentManager.jsx";
import { EvaluationPage } from "./features/evaluation/EvaluationPage.jsx";
import { MonitorPage } from "./features/monitor/MonitorPage.jsx";
import { QAPage } from "./features/qa/QAPage.jsx";
import { QuestionPaperPage } from "./features/questionPapers/QuestionPaperPage.jsx";

export default function App() {
  const bootstrap = useBootstrap();

  return (
    <Routes>
      <Route element={<AppShell apiBaseUrl={api.baseUrl} />}>
        <Route
          path="/"
          element={
            <BootstrapGate bootstrap={bootstrap}>
              <QAPage models={bootstrap.models} subjects={bootstrap.subjects} />
            </BootstrapGate>
          }
        />
        <Route
          path="/sources"
          element={
            <BootstrapGate bootstrap={bootstrap}>
              <DocumentManager {...bootstrap} />
            </BootstrapGate>
          }
        />
        <Route
          path="/assessment"
          element={
            <BootstrapGate bootstrap={bootstrap}>
              <QuestionPaperPage models={bootstrap.models} subjects={bootstrap.subjects} documents={bootstrap.documents} />
            </BootstrapGate>
          }
        />
        <Route
          path="/evaluate"
          element={
            <BootstrapGate bootstrap={bootstrap}>
              <EvaluationPage models={bootstrap.models} subjects={bootstrap.subjects} />
            </BootstrapGate>
          }
        />
        <Route path="/monitor" element={<MonitorPage />} />
        <Route path="/qa" element={<Navigate to="/" replace />} />
        <Route path="/documents" element={<Navigate to="/sources" replace />} />
        <Route path="/question-paper" element={<Navigate to="/assessment" replace />} />
        <Route path="/evaluation" element={<Navigate to="/evaluate" replace />} />
        <Route path="/usage" element={<Navigate to="/monitor" replace />} />
        <Route path="/logs" element={<Navigate to="/monitor" replace />} />
        <Route
          path="*"
          element={<Navigate to="/" replace />}
        />
      </Route>
    </Routes>
  );
}

function BootstrapGate({ bootstrap, children }) {
  if (bootstrap.loading) return <LinearProgress />;
  if (bootstrap.error) return <Alert severity="error">{bootstrap.error}</Alert>;
  return children;
}
