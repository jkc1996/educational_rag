import React, { useState } from "react";
import {
  Box, Button, Typography, TextField,
  MenuItem, Select, InputLabel, FormControl, CircularProgress, Snackbar, Alert, Paper
} from "@mui/material";
import PsychologyAltIcon from "@mui/icons-material/PsychologyAlt";
import axios from "axios";

const SUBJECTS = [
  "Machine Learning",
  "Natural Language Processing"
];

const LLMS = [
  { value: "gemini", label: "Gemini (Google)" },
  { value: "groq", label: "Groq (Llama3)" },
  { value: "ollama", label: "Ollama (Local)" }
];

function QAPage() {
  const [subject, setSubject] = useState("");
  const [question, setQuestion] = useState("");
  const [llmChoice, setLlmChoice] = useState("gemini");
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);
  const [snackbar, setSnackbar] = useState({ open: false, type: "info", message: "" });

  const handleSnackbarClose = () => setSnackbar({ ...snackbar, open: false });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setAnswer("");
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

    try {
      const res = await axios.post("http://localhost:8000/ask-question/", formData);
      setAnswer(res.data.answer);
      setSnackbar({ open: true, type: "success", message: "Answer retrieved successfully!" });
    } catch (err) {
      setSnackbar({ open: true, type: "error", message: "Error getting answer from server." });
    }
    setLoading(false);
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
      <Box
        width="100%"
        maxWidth={560}
        sx={{
          px: { xs: 2, md: 0 },
          py: 4,
        }}
      >
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
          <Button
            type="submit"
            variant="contained"
            color="primary"
            fullWidth
            size="large"
            sx={{ mt: 2, fontWeight: 700, fontSize: 18, height: 48 }}
            disabled={loading}
            startIcon={loading ? <CircularProgress color="inherit" size={22} /> : null}
          >
            {loading ? "Getting Answer..." : "Ask"}
          </Button>
        </form>
        {answer && (
          <Paper elevation={0} sx={{ mt: 4, p: 3, bgcolor: "#f5f8ff", borderRadius: 2 }}>
            <Typography variant="subtitle1" fontWeight={700} color="primary" mb={1}>
              Answer:
            </Typography>
            <Typography variant="body1" sx={{ whiteSpace: "pre-line" }}>
              {answer}
            </Typography>
          </Paper>
        )}
      </Box>
      <Snackbar
        open={snackbar.open}
        autoHideDuration={snackbar.type === "error" ? 4000 : 2500}
        onClose={handleSnackbarClose}
        anchorOrigin={{ vertical: "top", horizontal: "center" }}
      >
        <Alert
          onClose={handleSnackbarClose}
          severity={snackbar.type}
          variant="filled"
          sx={{ width: "100%" }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
}

export default QAPage;
