import ArticleOutlinedIcon from "@mui/icons-material/ArticleOutlined";
import SendIcon from "@mui/icons-material/Send";
import ThumbDownOutlinedIcon from "@mui/icons-material/ThumbDownOutlined";
import ThumbUpOutlinedIcon from "@mui/icons-material/ThumbUpOutlined";
import {
  Alert,
  Box,
  Button,
  Checkbox,
  Chip,
  FormControlLabel,
  IconButton,
  LinearProgress,
  Paper,
  Stack,
  TextField,
  Tooltip,
  Typography,
} from "@mui/material";
import { useMemo, useState } from "react";

import { api } from "../../api/client.js";
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

  const ask = async (event) => {
    event.preventDefault();
    setAnswer(null);
    setMessage(null);
    setLoading(true);
    try {
      const response = await api.ask({
        subject,
        question,
        model_id: modelId || defaultModel,
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
      <PageHeader title="Ask Questions" description="Ask grounded questions against indexed course material and inspect retrieved context when needed." />

      {message && (
        <Alert severity={message.severity} sx={{ mb: 2 }}>
          {message.text}
        </Alert>
      )}

      <Paper className="panel" sx={{ p: 2.5 }}>
        <Stack component="form" onSubmit={ask} gap={2}>
          <Box sx={{ display: "grid", gridTemplateColumns: { xs: "1fr", md: "1fr 1fr" }, gap: 2 }}>
            <SubjectSelect subjects={subjects} value={subject} onChange={setSubject} />
            <ModelSelect models={models} value={modelId || defaultModel} onChange={setModelId} />
          </Box>
          <TextField
            label="Question"
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            multiline
            minRows={3}
            required
          />
          <Stack direction="row" alignItems="center" justifyContent="space-between" gap={2} flexWrap="wrap">
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
      </Paper>

      {answer && (
        <Paper className="panel" sx={{ mt: 2, p: 2.5 }}>
          <Stack direction="row" alignItems="center" gap={1} sx={{ mb: 1 }}>
            <ArticleOutlinedIcon color="primary" />
            <Typography variant="h6">Answer</Typography>
            <Chip size="small" label={answer.model_id} />
          </Stack>
          <MarkdownText>{answer.answer}</MarkdownText>

          <Stack direction="row" alignItems="center" gap={1} sx={{ mt: 2 }}>
            <Typography variant="body2" color="text.secondary">
              Was this helpful?
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
              sx={{ minWidth: 240 }}
            />
          </Stack>

          {answer.sources?.length > 0 && (
            <Box sx={{ mt: 2, display: "grid", gap: 1 }}>
              {answer.sources.map((source) => (
                <Paper key={`${source.rank}-${source.chunk_uid}`} variant="outlined" sx={{ p: 1.5 }}>
                  <Stack direction="row" gap={1} alignItems="center" flexWrap="wrap" sx={{ mb: source.preview ? 1 : 0 }}>
                    <Chip size="small" label={`#${source.rank}`} />
                    {source.source_file && <Chip size="small" label={source.source_file} />}
                    {source.page && <Chip size="small" label={`Page ${source.page}`} />}
                  </Stack>
                  {source.preview && <Typography variant="body2">{source.preview}</Typography>}
                </Paper>
              ))}
            </Box>
          )}
        </Paper>
      )}
    </>
  );
}
