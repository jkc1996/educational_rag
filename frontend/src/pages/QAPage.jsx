import React, { useState } from "react";
import {
  Box, Button, Typography, TextField,
  MenuItem, Select, InputLabel, FormControl, CircularProgress, Snackbar, Alert, Paper, Chip, Divider, Grid,
  Tooltip, IconButton
} from "@mui/material";
import PsychologyAltIcon from "@mui/icons-material/PsychologyAlt";
import ArticleIcon from "@mui/icons-material/Article";
import PageviewIcon from "@mui/icons-material/Pageview";
import ThumbUpAltOutlinedIcon from "@mui/icons-material/ThumbUpAltOutlined";
import ThumbDownAltOutlinedIcon from "@mui/icons-material/ThumbDownAltOutlined";
import SendIcon from "@mui/icons-material/Send";
import axios from "axios";

const SUBJECTS = ["Machine Learning", "Natural Language Processing"];

const LLMS = [
  { value: "gemini", label: "Gemini (Google)" },
  { value: "groq", label: "Groq (Llama3)" },
  { value: "ollama", label: "Ollama (Local)" }
];

function QAPage() {
  const [subject, setSubject] = useState("");
  const [question, setQuestion] = useState("");
  const [llmChoice, setLlmChoice] = useState("gemini");
  const [addContext, setAddContext] = useState(false);

  const [answer, setAnswer] = useState("");
  const [contexts, setContexts] = useState([]);

  const [qaSessionId, setQaSessionId] = useState(null);            // <-- NEW
  const [feedbackChoice, setFeedbackChoice] = useState(null);      // 'up' | 'down' | null
  const [feedbackComment, setFeedbackComment] = useState("");      // for 👎
  const [feedbackLoading, setFeedbackLoading] = useState(false);   // spinner for feedback post
  const [feedbackSubmitted, setFeedbackSubmitted] = useState(false);

  const [loading, setLoading] = useState(false);
  const [snackbar, setSnackbar] = useState({ open: false });
  const handleSnackbarClose = () => setSnackbar({ ...snackbar, open: false });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setAnswer("");
    setContexts([]);
    setQaSessionId(null);
    setFeedbackChoice(null);
    setFeedbackComment("");
    setFeedbackSubmitted(false);
    setSnackbar({ open: false });

    if (!subject || !question) {
      setSnackbar({ open: true, type: "error", message: "Please select subject and enter your question." });
      return;
    }

    setLoading(true);

    const formData = new FormData();
    formData.append("subject", subject);
    formData.append("question", question);
    formData.append("llm_choice", llmChoice);
    formData.append("add_context", addContext ? "true" : "false");

    try {
      const res = await axios.post("http://localhost:8000/ask-question/", formData);
      setAnswer(res.data?.answer ?? "");
      setQaSessionId(res.data?.qa_session_id ?? null);                 // <-- NEW
      const ctx = Array.isArray(res.data?.context) ? res.data.context.slice(0, 3) : [];
      setContexts(ctx);
      setSnackbar({ open: true, type: "success", message: "Answer retrieved successfully!" });
    } catch (err) {
      setSnackbar({ open: true, type: "error", message: "Error getting answer from server." });
    } finally {
      setLoading(false);
    }
  };

  const submitFeedback = async (helpful) => {
    if (!qaSessionId) {
      setSnackbar({ open: true, type: "error", message: "Unable to send feedback (missing session id)." });
      return;
    }
    setFeedbackLoading(true);
    try {
      await axios.post("http://localhost:8000/api/feedback", {
        qa_session_id: qaSessionId,
        helpful,
        comment: helpful ? null : (feedbackComment?.trim() || null),
        llm_backend: llmChoice
      });
      setFeedbackSubmitted(true);
      setSnackbar({ open: true, type: "success", message: "Thanks for the feedback!" });
    } catch (e) {
      setSnackbar({ open: true, type: "error", message: "Couldn't send feedback. Please try again." });
    } finally {
      setFeedbackLoading(false);
    }
  };

  return (
    <Box
      display="flex"
      flexDirection="column"
      alignItems="center"
      justifyContent="center"
      minHeight="80vh"
      width="100%"
      sx={{ bgcolor: "#f7f8fa" }}
    >
      <Box width="100%" maxWidth={720} sx={{ px: { xs: 2, md: 0 }, py: 4 }}>
        <Box display="flex" alignItems="center" mb={2}>
          <PsychologyAltIcon sx={{ fontSize: 38, color: "primary.main", mr: 1 }} />
          <Typography variant="h4" fontWeight={700}>
            Ask a Question
          </Typography>
        </Box>

        <form onSubmit={handleSubmit} autoComplete="off">
          <FormControl fullWidth margin="normal">
            <InputLabel>Subject</InputLabel>
            <Select
              value={subject}
              onChange={e => setSubject(e.target.value)}
              label="Subject"
              disabled={loading}
              required
              size="medium"
            >
              <MenuItem value="">Select Subject</MenuItem>
              {SUBJECTS.map(s => (
                <MenuItem key={s} value={s}>{s}</MenuItem>
              ))}
            </Select>
          </FormControl>

          <FormControl fullWidth margin="normal">
            <InputLabel>LLM</InputLabel>
            <Select
              value={llmChoice}
              onChange={e => setLlmChoice(e.target.value)}
              label="LLM"
              disabled={loading}
            >
              {LLMS.map(llm => (
                <MenuItem key={llm.value} value={llm.value}>{llm.label}</MenuItem>
              ))}
            </Select>
          </FormControl>

          <TextField
            label="Question"
            value={question}
            onChange={e => setQuestion(e.target.value)}
            placeholder="Type your question"
            required
            fullWidth
            margin="normal"
            disabled={loading}
            multiline
            minRows={2}
          />

          <Box my={2}>
            <label style={{ fontWeight: 500, display: "inline-flex", alignItems: "center", cursor: "pointer" }}>
              <input
                type="checkbox"
                checked={addContext}
                onChange={e => setAddContext(e.target.checked)}
                disabled={loading}
                style={{ marginRight: 8 }}
              />
              Also show retrieved context (Top 3)
            </label>
          </Box>

          <Button
            type="submit"
            variant="contained"
            color="primary"
            fullWidth
            size="large"
            sx={{ mt: 1, fontWeight: 700, fontSize: 18, height: 48 }}
            disabled={loading}
            startIcon={loading ? <CircularProgress color="inherit" size={22} /> : null}
          >
            {loading ? "Getting Answer..." : "Ask"}
          </Button>
        </form>

        {/* Answer */}
        {answer && (
          <Paper elevation={0} sx={{ mt: 4, p: 3, bgcolor: "#f5f8ff", borderRadius: 2 }}>
            <Typography variant="subtitle1" fontWeight={700} color="primary" mb={1} display="flex" alignItems="center" gap={1}>
              <ArticleIcon /> Answer
            </Typography>
            <Typography variant="body1" sx={{ whiteSpace: "pre-line" }}>
              {answer}
            </Typography>

            {/* --- Feedback row (binary) --- */}
            <Box mt={2} display="flex" alignItems="center" gap={1} flexWrap="wrap">
              <Typography variant="body2" color="text.secondary" sx={{ mr: 1 }}>
                Was this helpful?
              </Typography>

              <Tooltip title="Yes">
                <span>
                  <IconButton
                    size="small"
                    color={feedbackChoice === "up" ? "success" : "default"}
                    onClick={() => {
                      if (feedbackSubmitted) return;
                      setFeedbackChoice("up");
                      submitFeedback(true);
                    }}
                    disabled={!qaSessionId || feedbackSubmitted || feedbackLoading}
                  >
                    <ThumbUpAltOutlinedIcon fontSize="small" />
                  </IconButton>
                </span>
              </Tooltip>

              <Tooltip title="No">
                <span>
                  <IconButton
                    size="small"
                    color={feedbackChoice === "down" ? "error" : "default"}
                    onClick={() => {
                      if (feedbackSubmitted) return;
                      setFeedbackChoice("down");
                    }}
                    disabled={!qaSessionId || feedbackSubmitted || feedbackLoading}
                  >
                    <ThumbDownAltOutlinedIcon fontSize="small" />
                  </IconButton>
                </span>
              </Tooltip>

              {feedbackSubmitted && (
                <Chip size="small" label="Thanks for the feedback!" color="success" sx={{ ml: 1 }} />
              )}
            </Box>

            {/* Comment box visible only when 👎 selected and not yet submitted */}
            {feedbackChoice === "down" && !feedbackSubmitted && (
              <Box mt={1} display="flex" gap={1} alignItems="flex-start">
                <TextField
                  size="small"
                  fullWidth
                  placeholder="What could be improved? (optional)"
                  value={feedbackComment}
                  onChange={e => setFeedbackComment(e.target.value)}
                  disabled={feedbackLoading}
                />
                <Button
                  variant="outlined"
                  size="small"
                  endIcon={feedbackLoading ? <CircularProgress size={16} /> : <SendIcon />}
                  onClick={() => submitFeedback(false)}
                  disabled={feedbackLoading}
                >
                  Submit
                </Button>
              </Box>
            )}
          </Paper>
        )}

        {/* Context (Top 3) */}
        {addContext && (
          <Paper elevation={0} sx={{ mt: 3, p: 3, bgcolor: "#fff", borderRadius: 2, border: "1px solid #e7eaf3" }}>
            <Typography variant="subtitle1" fontWeight={700} color="text.primary" mb={1} display="flex" alignItems="center" gap={1}>
              <PageviewIcon /> Retrieved Context (Top 3)
            </Typography>
            <Divider sx={{ mb: 2 }} />
            {contexts.length === 0 ? (
              <Typography variant="body2" color="text.secondary">
                {answer ? "No context returned." : "Context will appear here after you ask a question."}
              </Typography>
            ) : (
              <Grid container spacing={2}>
                {contexts.map((c, idx) => (
                  <Grid item xs={12} key={`${c.source_pdf}-${c.page}-${idx}`}>
                    <Paper variant="outlined" sx={{ p: 2, borderRadius: 2 }}>
                      <Box display="flex" alignItems="center" gap={1} mb={1} flexWrap="wrap">
                        <Chip size="small" label={`#${idx + 1}`} />
                        {c.source_pdf && <Chip size="small" label={c.source_pdf} />}
                        {typeof c.page === "number" && <Chip size="small" label={`Page ${c.page}`} />}
                      </Box>
                      <Typography variant="body2" sx={{ whiteSpace: "pre-line" }}>
                        {c.preview || "—"}
                      </Typography>
                    </Paper>
                  </Grid>
                ))}
              </Grid>
            )}
          </Paper>
        )}
      </Box>

      <Snackbar
        open={snackbar.open}
        autoHideDuration={snackbar.type === "error" ? 4000 : 2500}
        onClose={handleSnackbarClose}
        anchorOrigin={{ vertical: "top", horizontal: "center" }}
      >
        <Alert onClose={handleSnackbarClose} severity={snackbar.type} variant="filled" sx={{ width: "100%" }}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
}

export default QAPage;
