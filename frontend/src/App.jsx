import { Alert, LinearProgress } from "@mui/material";
import { Route, Routes } from "react-router-dom";

import { api } from "./api/client.js";
import { AppShell } from "./components/AppShell.jsx";
import { useBootstrap } from "./hooks/useBootstrap.js";
import { DocumentManager } from "./features/documents/DocumentManager.jsx";
import { EvaluationPage } from "./features/evaluation/EvaluationPage.jsx";
import { LogsPage } from "./features/logs/LogsPage.jsx";
import { QAPage } from "./features/qa/QAPage.jsx";
import { QuestionPaperPage } from "./features/questionPapers/QuestionPaperPage.jsx";
import { UsagePage } from "./features/usage/UsagePage.jsx";

export default function App() {
  const bootstrap = useBootstrap();

  return (
    <Routes>
      <Route element={<AppShell apiBaseUrl={api.baseUrl} />}>
        <Route
          path="/"
          element={
            <BootstrapGate bootstrap={bootstrap}>
              <DocumentManager {...bootstrap} />
            </BootstrapGate>
          }
        />
        <Route
          path="/qa"
          element={
            <BootstrapGate bootstrap={bootstrap}>
              <QAPage models={bootstrap.models} subjects={bootstrap.subjects} />
            </BootstrapGate>
          }
        />
        <Route
          path="/question-paper"
          element={
            <BootstrapGate bootstrap={bootstrap}>
              <QuestionPaperPage models={bootstrap.models} subjects={bootstrap.subjects} documents={bootstrap.documents} />
            </BootstrapGate>
          }
        />
        <Route
          path="/evaluation"
          element={
            <BootstrapGate bootstrap={bootstrap}>
              <EvaluationPage models={bootstrap.models} subjects={bootstrap.subjects} />
            </BootstrapGate>
          }
        />
        <Route path="/usage" element={<UsagePage />} />
        <Route path="/logs" element={<LogsPage />} />
      </Route>
    </Routes>
  );
}

function BootstrapGate({ bootstrap, children }) {
  if (bootstrap.loading) return <LinearProgress />;
  if (bootstrap.error) return <Alert severity="error">{bootstrap.error}</Alert>;
  return children;
}

