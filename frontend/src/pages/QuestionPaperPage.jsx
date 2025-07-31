import React, { useState, useEffect } from "react";
import {
  Box, Button, Typography, MenuItem, Select, InputLabel, FormControl,
  TextField, CircularProgress, Snackbar, Alert, Paper, Grid, Checkbox, ListItemText, OutlinedInput, FormControlLabel
} from "@mui/material";
import DescriptionIcon from "@mui/icons-material/Description";
import axios from "axios";

// Dummy data for subjects and PDFs (replace with real backend calls for production)
const SUBJECTS = [
  "Machine Learning",
  "Natural Language Processing"
];
const PDFS = {
  "Machine Learning": [
    "Machine_Learning_ML_course_content_1.pdf",
    "Machine_Learning_ML_course_content_2.pdf",
    "Machine_Learning_ML_course_content_3.pdf"
  ],
  "Natural Language Processing": [
    "NLP_Unit1.pdf", "NLP_Unit2.pdf"
  ]
};
const LLMS = [
  { value: "gemini", label: "Gemini (Google)" },
  { value: "groq", label: "Groq (Llama3)" },
  { value: "ollama", label: "Ollama (Local)" }
];
const DIFFICULTIES = ["easy", "medium", "hard"];
const ALL_QUESTION_TYPES = [
  { key: "one_liner", label: "One Liner" },
  { key: "true_false", label: "True/False" },
  { key: "fill_blank", label: "Fill Blank" },
  { key: "multiple_choice", label: "Multiple Choice" },
  { key: "descriptive", label: "Descriptive" }
];

function QuestionPaperPage() {
  const [subject, setSubject] = useState("");
  const [pdfs, setPdfs] = useState([]);
  const [selectedPdfs, setSelectedPdfs] = useState([]);
  const [llmChoice, setLlmChoice] = useState("groq");
  const [difficulty, setDifficulty] = useState("medium");
  const [totalQuestions, setTotalQuestions] = useState(5);
  const [questionTypes, setQuestionTypes] = useState([]);
  const [distribution, setDistribution] = useState({});
  const [extraContext, setExtraContext] = useState("");
  const [loading, setLoading] = useState(false);
  const [summary, setSummary] = useState("");
  const [questions, setQuestions] = useState("");
  const [snackbar, setSnackbar] = useState({ open: false, type: "info", message: "" });

  useEffect(() => {
    if (subject) {
      setPdfs(PDFS[subject] || []);
      setSelectedPdfs([]);
    }
  }, [subject]);

  const handleSnackbarClose = () => setSnackbar({ ...snackbar, open: false });

  const handleTypeChange = (type) => {
    if (questionTypes.includes(type)) {
      setQuestionTypes(qts => qts.filter(q => q !== type));
      setDistribution(d => {
        const { [type]: _, ...rest } = d;
        return rest;
      });
    } else {
      setQuestionTypes(qts => [...qts, type]);
    }
  };

  const handleDistributionChange = (type, value) => {
    setDistribution(d => ({
      ...d,
      [type]: Math.max(0, parseInt(value) || 0)
    }));
  };

  const handleGenerate = async (e) => {
    e.preventDefault();
    setQuestions(""); setSummary("");
    setSnackbar({ open: false });

    if (!subject || selectedPdfs.length === 0) {
      setSnackbar({ open: true, type: "error", message: "Select subject and PDF(s)." }); return;
    }
    if (questionTypes.length === 0) {
      setSnackbar({ open: true, type: "error", message: "Select at least one question type." }); return;
    }
    const sum = Object.values(distribution).reduce((a, b) => a + b, 0);
    if (sum !== parseInt(totalQuestions)) {
      setSnackbar({ open: true, type: "error", message: "Sum of question types must equal total questions." }); return;
    }

    setLoading(true);

    const payload = {
      subject,
      filenames: selectedPdfs,
      llm_choice: llmChoice,
      question_config: {
        total_questions: parseInt(totalQuestions),
        difficulty,
        distribution
      },
      extra_context: extraContext
    };

    try {
      const res = await axios.post("http://localhost:8000/generate-question-paper/", payload);
      setSummary(res.data.summary);
      setQuestions(res.data.questions);
      setSnackbar({ open: true, type: "success", message: "Question paper generated!" });
    } catch {
      setSnackbar({ open: true, type: "error", message: "Error generating question paper." });
    }
    setLoading(false);
  };

  return (
    <Box display="flex" flexDirection="column" alignItems="center" minHeight="80vh" width="100%">
      <Box width="100%" maxWidth={900} sx={{ px: { xs: 2, md: 0 }, py: 4 }}>
        <Box display="flex" alignItems="center" mb={3}>
          <DescriptionIcon sx={{ fontSize: 38, color: "primary.main", mr: 1 }} />
          <Typography variant="h4" fontWeight={700}>
            Generate Question Paper
          </Typography>
        </Box>
        <form onSubmit={handleGenerate} autoComplete="off">

          {/* SECTION 1: Data Source */}
          <Paper sx={{ p: 3, mb: 3, borderRadius: 3 }}>
            <Typography variant="h6" fontWeight={700} gutterBottom>1. Data Source</Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} md={4}>
                <FormControl fullWidth>
                  <InputLabel>Subject</InputLabel>
                  <Select value={subject} onChange={e => setSubject(e.target.value)} label="Subject" disabled={loading} required>
                    <MenuItem value="">Select Subject</MenuItem>
                    {SUBJECTS.map(s => <MenuItem key={s} value={s}>{s}</MenuItem>)}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} md={4}>
                <FormControl fullWidth>
                  <InputLabel>PDF(s)</InputLabel>
                  <Select
                    multiple
                    value={selectedPdfs}
                    onChange={e => setSelectedPdfs(e.target.value)}
                    input={<OutlinedInput label="PDF(s)" />}
                    renderValue={selected => selected.join(', ')}
                    disabled={loading || !pdfs.length}
                  >
                    {pdfs.map(pdf => (
                      <MenuItem key={pdf} value={pdf}>
                        <Checkbox checked={selectedPdfs.includes(pdf)} />
                        <ListItemText primary={pdf} />
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} md={4}>
                <FormControl fullWidth>
                  <InputLabel>LLM</InputLabel>
                  <Select value={llmChoice} onChange={e => setLlmChoice(e.target.value)} label="LLM" disabled={loading}>
                    {LLMS.map(llm => <MenuItem key={llm.value} value={llm.value}>{llm.label}</MenuItem>)}
                  </Select>
                </FormControl>
              </Grid>
            </Grid>
          </Paper>

          {/* SECTION 2: Question Setup */}
          <Paper sx={{ p: 3, mb: 3, borderRadius: 3 }}>
            <Typography variant="h6" fontWeight={700} gutterBottom>2. Question Setup</Typography>
            <Grid container spacing={2} alignItems="center">
              <Grid item xs={12} md={4}>
                <TextField
                  label="Total Questions"
                  type="number"
                  value={totalQuestions}
                  onChange={e => setTotalQuestions(e.target.value)}
                  fullWidth
                  inputProps={{ min: 1, step: 1 }}
                  disabled={loading}
                />
              </Grid>
              <Grid item xs={12} md={4}>
                <FormControl fullWidth>
                  <InputLabel>Difficulty</InputLabel>
                  <Select
                    value={difficulty}
                    onChange={e => setDifficulty(e.target.value)}
                    label="Difficulty"
                    disabled={loading}
                  >
                    {DIFFICULTIES.map(d => <MenuItem key={d} value={d}>{d.charAt(0).toUpperCase() + d.slice(1)}</MenuItem>)}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12}>
                <Box display="flex" flexWrap="wrap" alignItems="center" gap={2} mt={2}>
                  {ALL_QUESTION_TYPES.map(type =>
                    <Box key={type.key} sx={{ display: "flex", alignItems: "center", mb: 1 }}>
                      <FormControlLabel
                        control={
                          <Checkbox
                            checked={questionTypes.includes(type.key)}
                            onChange={() => handleTypeChange(type.key)}
                            disabled={loading}
                          />
                        }
                        label={type.label}
                      />
                      <TextField
                        type="number"
                        size="small"
                        disabled={!questionTypes.includes(type.key) || loading}
                        sx={{ width: 60, ml: 1 }}
                        value={distribution[type.key] || ""}
                        onChange={e => handleDistributionChange(type.key, e.target.value)}
                        inputProps={{ min: 0, step: 1 }}
                        placeholder="#"
                      />
                    </Box>
                  )}
                </Box>
              </Grid>
            </Grid>
          </Paper>

          {/* SECTION 3: Extra Context */}
          <Paper sx={{ p: 3, mb: 2, borderRadius: 3 }}>
            <Typography variant="h6" fontWeight={700} gutterBottom>3. Additional Context or Instructions</Typography>
            <TextField
              label="Extra Context / Instructions (Optional)"
              value={extraContext}
              onChange={e => setExtraContext(e.target.value)}
              placeholder="E.g. Focus on regression, only use Chapter 2..."
              fullWidth
              margin="normal"
              multiline
              minRows={2}
              disabled={loading}
            />
          </Paper>

          {/* BUTTON */}
          <Box display="flex" justifyContent="center" mt={2}>
            <Button
              type="submit"
              variant="contained"
              color="primary"
              size="large"
              sx={{ fontWeight: 700, fontSize: 18, minWidth: 340, height: 48 }}
              disabled={loading}
              startIcon={loading ? <CircularProgress color="inherit" size={22} /> : null}
            >
              {loading ? "Generating..." : "Generate Question Paper"}
            </Button>
          </Box>
        </form>

        {/* Results below */}
        {summary && (
          <Paper elevation={0} sx={{ mt: 4, p: 3, bgcolor: "#e7f6ef", borderRadius: 2 }}>
            <Typography variant="subtitle1" fontWeight={700} color="primary" mb={1}>
              Deep Summary:
            </Typography>
            <Typography variant="body2" sx={{ whiteSpace: "pre-line" }}>
              {summary}
            </Typography>
          </Paper>
        )}
        {questions && (
          <Paper elevation={0} sx={{ mt: 4, p: 3, bgcolor: "#f8fafc", borderRadius: 2 }}>
            <Typography variant="subtitle1" fontWeight={700} color="primary" mb={1}>
              Generated Questions:
            </Typography>
            <Typography variant="body2" sx={{ whiteSpace: "pre-line" }}>
              {typeof questions === "string" ? questions : JSON.stringify(questions, null, 2)}
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

export default QuestionPaperPage;
