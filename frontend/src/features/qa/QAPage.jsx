import ArticleOutlinedIcon from "@mui/icons-material/ArticleOutlined";
import AutoAwesomeOutlinedIcon from "@mui/icons-material/AutoAwesomeOutlined";
import ChecklistRtlOutlinedIcon from "@mui/icons-material/ChecklistRtlOutlined";
import SendIcon from "@mui/icons-material/Send";
import SourceOutlinedIcon from "@mui/icons-material/SourceOutlined";
import ThumbDownOutlinedIcon from "@mui/icons-material/ThumbDownOutlined";
import ThumbUpOutlinedIcon from "@mui/icons-material/ThumbUpOutlined";
import TuneOutlinedIcon from "@mui/icons-material/TuneOutlined";
import {
  Alert,
  Box,
  Button,
  Checkbox,
  Chip,
  FormControlLabel,
  IconButton,
  LinearProgress,
  Stack,
  TextField,
  Tooltip,
  Typography,
} from "@mui/material";
import { useMemo, useState } from "react";

import { api } from "../../api/client.js";
import { EmptyState, WorkPanel, WorkspaceLayout } from "../../components/Workspace.jsx";
import { MarkdownText } from "../../components/MarkdownText.jsx";
import { ModelSelect } from "../../components/ModelSelect.jsx";
import { PageHeader } from "../../components/PageHeader.jsx";
import { SubjectSelect } from "../../components/SubjectSelect.jsx";

export function QAPage({ models, subjects }) {
  const defaultModel = useMemo(() => models.find((model) => model.default)?.id || models[0]?.id || "", [models]);
  const [subject, setSubject] = useState("");
  const [modelId, setModelId] = useState("");
  const [question, setQuestion] = useState("");
  const [includeContext, setIncludeContext] = useState(true);
  const [answer, setAnswer] = useState(null);
  const [feedbackComment, setFeedbackComment] = useState("");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);

  const selectedModel = modelId || defaultModel;
  const sources = answer?.sources || [];

  const ask = async (event) => {
    event.preventDefault();
    setAnswer(null);
    setMessage(null);
    setLoading(true);
    try {
      const response = await api.ask({
        subject,
        question,
        model_id: selectedModel,
        include_context: includeContext,
      });
      setAnswer(response);
    } catch (err) {
      setMessage({ severity: "error", text: err.message });
    } finally {
      setLoading(false);
    }
  };

  const sendFeedback = async (helpful) => {
    if (!answer?.qa_session_id) return;
    try {
      await api.feedback({
        qa_session_id: answer.qa_session_id,
        helpful,
        comment: helpful ? null : feedbackComment || null,
        model_id: answer.model_id,
      });
      setMessage({ severity: "success", text: "Feedback saved." });
    } catch (err) {
      setMessage({ severity: "error", text: err.message });
    }
  };

  return (
    <>
      <PageHeader
        eyebrow="Study Workbench"
        title="Ask"
        description="A focused space for grounded answers, source traceability, and quick feedback on the response quality."
      />

      {message && (
        <Alert severity={message.severity} sx={{ mb: 2 }}>
          {message.text}
        </Alert>
      )}

      <WorkspaceLayout inspector={<EvidenceInspector subject={subject} modelId={answer?.model_id || selectedModel} includeContext={includeContext} answer={answer} sources={sources} />}>
        <Stack gap={2}>
          <WorkPanel>
            <Stack component="form" onSubmit={ask} gap={2}>
              <Stack direction="row" alignItems="center" gap={1}>
                <TuneOutlinedIcon color="primary" />
                <Typography variant="h6">Question Setup</Typography>
              </Stack>

              <Box sx={{ display: "grid", gridTemplateColumns: { xs: "1fr", md: "1fr 1fr" }, gap: 2 }}>
                <SubjectSelect subjects={subjects} value={subject} onChange={setSubject} />
                <ModelSelect models={models} value={selectedModel} onChange={setModelId} />
              </Box>

              <TextField
                label="Question"
                value={question}
                onChange={(event) => setQuestion(event.target.value)}
                multiline
                minRows={5}
                required
                placeholder="Ask from the indexed material..."
              />

              <Stack direction={{ xs: "column", sm: "row" }} alignItems={{ xs: "stretch", sm: "center" }} justifyContent="space-between" gap={2}>
                <FormControlLabel
                  control={<Checkbox checked={includeContext} onChange={(event) => setIncludeContext(event.target.checked)} />}
                  label="Return retrieved context"
                />
                <Button type="submit" variant="contained" startIcon={<SendIcon />} disabled={loading || !subject || !question}>
                  Ask
                </Button>
              </Stack>
            </Stack>
            {loading && <LinearProgress sx={{ mt: 2 }} />}
          </WorkPanel>

          <WorkPanel sx={{ minHeight: 340 }}>
            <Stack direction="row" alignItems="center" gap={1} sx={{ mb: 1.5 }}>
              <ArticleOutlinedIcon color="primary" />
              <Typography variant="h6">Answer</Typography>
              {answer?.model_id && <Chip size="small" label={answer.model_id} />}
            </Stack>

            {answer ? (
              <>
                <MarkdownText>{answer.answer}</MarkdownText>

                <Box className="inline-section" sx={{ mt: 2 }}>
                  <Stack direction={{ xs: "column", sm: "row" }} alignItems={{ xs: "stretch", sm: "center" }} gap={1.25}>
                    <Typography variant="body2" color="text.secondary">
                      Response quality
                    </Typography>
                    <Tooltip title="Helpful">
                      <IconButton size="small" color="success" onClick={() => sendFeedback(true)}>
                        <ThumbUpOutlinedIcon />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Needs work">
                      <IconButton size="small" color="error" onClick={() => sendFeedback(false)}>
                        <ThumbDownOutlinedIcon />
                      </IconButton>
                    </Tooltip>
                    <TextField
                      size="small"
                      placeholder="Optional feedback"
                      value={feedbackComment}
                      onChange={(event) => setFeedbackComment(event.target.value)}
                      sx={{ minWidth: { sm: 260 }, flex: 1 }}
                    />
                  </Stack>
                </Box>
              </>
            ) : (
              <EmptyState
                icon={<AutoAwesomeOutlinedIcon color="primary" sx={{ fontSize: 38 }} />}
                title="Ready for a grounded answer"
                description="Choose a subject, ask from your indexed course material, and the evidence trace will stay alongside the answer."
              />
            )}
          </WorkPanel>
        </Stack>
      </WorkspaceLayout>
    </>
  );
}

function EvidenceInspector({ subject, modelId, includeContext, answer, sources }) {
  return (
    <Stack gap={2}>
      <WorkPanel>
        <Stack direction="row" alignItems="center" gap={1} sx={{ mb: 1.5 }}>
          <ChecklistRtlOutlinedIcon color="primary" />
          <Typography variant="h6">Run Trace</Typography>
        </Stack>
        <Stack gap={1}>
          <TraceRow label="Subject" value={subject || "Not selected"} />
          <TraceRow label="Model" value={modelId || "Not selected"} />
          <TraceRow label="Context" value={includeContext ? "Returned" : "Hidden"} />
          <TraceRow label="Session" value={answer?.qa_session_id || "Not started"} mono />
        </Stack>
      </WorkPanel>

      <WorkPanel>
        <Stack direction="row" alignItems="center" gap={1} sx={{ mb: 1.5 }}>
          <SourceOutlinedIcon color="primary" />
          <Typography variant="h6">Evidence</Typography>
          <Chip size="small" label={sources.length} />
        </Stack>
        <Stack gap={1.25}>
          {sources.map((source) => (
            <Box key={`${source.rank}-${source.chunk_uid}`} className="inline-section" sx={{ p: 1.25 }}>
              <Stack direction="row" gap={0.75} flexWrap="wrap" sx={{ mb: source.preview ? 1 : 0 }}>
                <Chip size="small" label={`#${source.rank}`} color="primary" variant="outlined" />
                {source.source_file && <Chip size="small" label={source.source_file} />}
                {source.page && <Chip size="small" label={`Page ${source.page}`} />}
              </Stack>
              {source.preview && (
                <Typography variant="body2" color="text.secondary">
                  {source.preview}
                </Typography>
              )}
            </Box>
          ))}
          {sources.length === 0 && (
            <Typography color="text.secondary" variant="body2">
              No retrieved context yet.
            </Typography>
          )}
        </Stack>
      </WorkPanel>
    </Stack>
  );
}

function TraceRow({ label, value, mono = false }) {
  return (
    <Stack direction="row" justifyContent="space-between" gap={1.5}>
      <Typography variant="body2" color="text.secondary">
        {label}
      </Typography>
      <Typography variant="body2" fontWeight={750} className={mono ? "mono-cell" : undefined} sx={{ textAlign: "right" }}>
        {value}
      </Typography>
    </Stack>
  );
}
