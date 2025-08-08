import React, { useState, useEffect } from "react";
import {
  Box, Button, Typography, MenuItem, Select, InputLabel, FormControl,
  TextField, CircularProgress, Snackbar, Alert, Paper, Grid, Checkbox, ListItemText, OutlinedInput, FormControlLabel,
  Accordion, AccordionSummary, AccordionDetails, Chip, Stack
} from "@mui/material";
import DescriptionIcon from "@mui/icons-material/Description";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import jsPDF from "jspdf";
import axios from "axios";
import ShortTextIcon from "@mui/icons-material/ShortText";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import EditNoteIcon from "@mui/icons-material/EditNote";
import ListAltIcon from "@mui/icons-material/ListAlt";
import SubjectIcon from "@mui/icons-material/Subject";

// Dummy data (replace with real backend data if needed)
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
  { value: "groq", label: "Groq (Llama3)" }
];
const DIFFICULTIES = ["easy", "medium", "hard"];
const ALL_QUESTION_TYPES = [
  { key: "one_liner", label: "One Liner" },
  { key: "true_false", label: "True/False" },
  { key: "fill_blank", label: "Fill Blank" },
  { key: "multiple_choice", label: "Multiple Choice" },
  { key: "descriptive", label: "Descriptive" }
];

const QUESTION_TYPE_ICONS = {
  one_liner: <ShortTextIcon fontSize="large" sx={{ color: "#466bdb" }} />,
  true_false: <CheckCircleIcon fontSize="large" sx={{ color: "#1baf5c" }} />,
  fill_blank: <EditNoteIcon fontSize="large" sx={{ color: "#e79c26" }} />,
  multiple_choice: <ListAltIcon fontSize="large" sx={{ color: "#aa49ee" }} />,
  descriptive: <SubjectIcon fontSize="large" sx={{ color: "#db5050" }} />
};

// SAFELY parse the new {questions: [...]}
function safeParseQuestions(raw) {
  if (!raw) return [];
  try {
    if (Array.isArray(raw)) return raw;
    if (typeof raw === "object" && Array.isArray(raw.questions)) return raw.questions;
    let data = typeof raw === "string" ? JSON.parse(raw) : raw;
    if (data && Array.isArray(data.questions)) return data.questions;
    if (Array.isArray(data)) return data;
    return [];
  } catch (e) {
    console.error("Failed to parse questions JSON:", e);
    return [];
  }
}

// For preview
function formatQuestion(q, idx) {
  return (
    <Box key={idx} mb={2} pb={2} borderBottom={idx === 6 ? 0 : "1px solid #eef2f6"}>
      <Typography fontWeight={600} sx={{ mb: 0.3 }}>
        {`Q${idx + 1}.`}
      </Typography>
      <Typography sx={{ whiteSpace: "pre-line" }}>{q.question}</Typography>
      {q.options && Array.isArray(q.options) && q.options.length > 0 && (
        <Box pl={2} mt={0.7}>
          {q.options.map((opt, i) => (
            <Typography key={i} variant="body2">{String.fromCharCode(97 + i) + ". " + opt}</Typography>
          ))}
        </Box>
      )}
    </Box>
  );
}

function QuestionPaperPage() {
  const [subject, setSubject] = useState("");
  const [pdfs, setPdfs] = useState([]);
  const [selectedPdfs, setSelectedPdfs] = useState([]);
  const [llmChoice, setLlmChoice] = useState("groq");
  const [difficulty, setDifficulty] = useState("medium");
  const [questionTypes, setQuestionTypes] = useState([]);
  const [distribution, setDistribution] = useState({});
  const [extraContext, setExtraContext] = useState("");
  const [loading, setLoading] = useState(false);
  const [summary, setSummary] = useState("");
  const [questions, setQuestions] = useState([]);
  const [snackbar, setSnackbar] = useState({ open: false, type: "info", message: "" });

  // Calculate total questions on the fly
  const totalQuestions = Object.values(distribution).reduce((a, b) => a + (parseInt(b) || 0), 0);

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
    setQuestions([]); setSummary("");
    setSnackbar({ open: false });

    if (!subject || selectedPdfs.length === 0) {
      setSnackbar({ open: true, type: "error", message: "Select subject and PDF(s)." }); return;
    }
    if (questionTypes.length === 0) {
      setSnackbar({ open: true, type: "error", message: "Select at least one question type." }); return;
    }
    if (totalQuestions === 0) {
      setSnackbar({ open: true, type: "error", message: "Total questions must be > 0." }); return;
    }

    setLoading(true);

    const payload = {
      subject,
      filenames: selectedPdfs,
      llm_choice: llmChoice,
      question_config: {
        total_questions: totalQuestions, // Dynamic!
        difficulty,
        distribution
      },
      extra_context: extraContext
    };

    try {
      const res = await axios.post("http://localhost:8000/generate-question-paper/", payload);
      setSummary(res.data.summary);
      const arr = safeParseQuestions(res.data.questions);
      setQuestions(arr);
      setSnackbar({ open: true, type: "success", message: "Question paper generated!" });
    } catch {
      setSnackbar({ open: true, type: "error", message: "Error generating question paper." });
    }
    setLoading(false);
  };

  // PDF download handler (nicely formatted, multipage)
  const handleDownloadPDF = () => {
    const arr = questions;
    if (arr.length === 0) {
      setSnackbar({ open: true, type: "error", message: "Could not parse questions to generate PDF." });
      return;
    }

    const doc = new jsPDF();
    let y = 20;
    const pageMargin = 14;
    const contentWidth = doc.internal.pageSize.getWidth() - pageMargin * 2;
    const pageHeight = doc.internal.pageSize.getHeight();

    // --- Page Header ---
    doc.setFont("helvetica", "bold");
    doc.setFontSize(20);
    doc.text("Question Paper", doc.internal.pageSize.getWidth() / 2, y, { align: "center" });
    y += 12;
    doc.setFontSize(14);
    doc.setFont("helvetica", "normal");
    doc.text(`Subject: ${subject}`, pageMargin, y);
    y += 15;

    // --- Questions Section ---
    doc.setFont("helvetica", "bold");
    doc.setFontSize(16);
    doc.text("Questions", pageMargin, y);
    y += 10;
    doc.setFontSize(12);

    let qNo = 1;
    let answerArr = [];

    const checkPageBreak = (requiredHeight) => {
      if (y + requiredHeight > pageHeight - pageMargin) {
        doc.addPage();
        y = 20;
      }
    };

    arr.forEach(q => {
      answerArr.push({ num: qNo, answer: q.answer });

      doc.setFont("helvetica", "bold");
      const questionText = `Q${qNo}. ${q.question}`;
      const questionLines = doc.splitTextToSize(questionText, contentWidth);

      checkPageBreak(questionLines.length * 7);
      doc.text(questionLines, pageMargin, y);
      y += questionLines.length * 6 + 4;

      doc.setFont("helvetica", "normal");

      if (q.type === "multiple_choice" && Array.isArray(q.options)) {
        checkPageBreak(q.options.length * 6 + 4);
        q.options.forEach((opt, i) => {
          const optionText = `  ${String.fromCharCode(97 + i)}) ${opt}`;
          const optionLines = doc.splitTextToSize(optionText, contentWidth - 5);
          checkPageBreak(optionLines.length * 6);
          doc.text(optionLines, pageMargin + 2, y);
          y += optionLines.length * 6;
        });
      }
      y += 8;
      qNo++;
    });

    // --- Answer Key Section (new page) ---
    doc.addPage();
    y = 20;
    doc.setFont("helvetica", "bold");
    doc.setFontSize(16);
    doc.text("Answer Key", pageMargin, y);
    y += 12;
    doc.setFontSize(12);
    doc.setFont("helvetica", "normal");

    answerArr.forEach(ans => {
      let ansText = `Q${ans.num}: ${ans.answer ? String(ans.answer).replace(/\n\n/g, '\n') : "N/A"}`;
      const ansLines = doc.splitTextToSize(ansText, contentWidth);
      checkPageBreak(ansLines.length * 6 + 6);
      doc.text(ansLines, pageMargin, y);
      y += ansLines.length * 6 + 6;
    });

    doc.save(`Question_Paper_${subject.replace(/\s+/g, "_")}.pdf`);
  };

  return (
    <Box display="flex" flexDirection="column" alignItems="center" minHeight="80vh" width="100%" sx={{ bgcolor: "#f6f8fb" }}>
      <Box width="100%" maxWidth={950} sx={{ px: { xs: 2, md: 0 }, py: 5 }}>
        <Box display="flex" alignItems="center" mb={4}>
          <DescriptionIcon sx={{ fontSize: 38, color: "#1A2A53", mr: 1 }} />
          <Typography variant="h4" fontWeight={800}>
            Generate Question Paper
          </Typography>
        </Box>
        <form onSubmit={handleGenerate} autoComplete="off">
          {/* SECTION 1 */}
          <Paper sx={{ p: 3, mb: 3, borderRadius: 3, boxShadow: 2, background: "#fafdff" }}>
            <Typography variant="h6" fontWeight={800} color="primary" gutterBottom>
              1. Data Source
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} md={4}>
                <FormControl fullWidth sx={{ minWidth: 200 }}>
                  <InputLabel>Subject</InputLabel>
                  <Select value={subject} onChange={e => setSubject(e.target.value)} label="Subject" disabled={loading} required>
                    <MenuItem value="">Select Subject</MenuItem>
                    {SUBJECTS.map(s => <MenuItem key={s} value={s}>{s}</MenuItem>)}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} md={4}>
                <FormControl fullWidth sx={{ minWidth: 200 }}>
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
          {/* SECTION 2 */}
          <Paper sx={{ p: 3, mb: 3, borderRadius: 3, boxShadow: 2, background: "#fcfdff" }}>
            <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
              <Typography variant="h6" fontWeight={800} color="primary">
                2. Question Setup
              </Typography>
              <Box
                sx={{
                  bgcolor: "#1A2A53",
                  color: "#ffffff",
                  borderRadius: "22px",
                  px: 1.5,
                  py: 1,
                  fontWeight: 700,
                  fontSize: 17,
                  minWidth: 165,
                  textAlign: "center",
                  letterSpacing: 0.2,
                  boxShadow: "0 1px 5px #bdd2f980"
                }}
              >
                Total Questions: {totalQuestions}
              </Box>
            </Box>
            <Box maxWidth={260} mb={3}>
              <FormControl fullWidth>
                <InputLabel>Difficulty</InputLabel>
                <Select
                  value={difficulty}
                  onChange={e => setDifficulty(e.target.value)}
                  label="Difficulty"
                  disabled={loading}
                >
                  {DIFFICULTIES.map(d => (
                    <MenuItem key={d} value={d}>{d.charAt(0).toUpperCase() + d.slice(1)}</MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Box>
            <Box>
              {ALL_QUESTION_TYPES.map((type, idx) => (
                <React.Fragment key={type.key}>
                  <Box
                    sx={{
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "space-between",
                      py: 2,
                      px: 1,
                    }}
                  >
                    <Box display="flex" alignItems="center">
                      {QUESTION_TYPE_ICONS[type.key]}
                      <Typography fontWeight={600} fontSize={16} ml={1.5}>
                        {type.label}
                      </Typography>
                    </Box>
                    <Box display="flex" alignItems="center">
                      <Checkbox
                        checked={questionTypes.includes(type.key)}
                        onChange={() => handleTypeChange(type.key)}
                        disabled={loading}
                        sx={{
                          mx: 1.2
                        }}
                      />
                      <TextField
                        type="number"
                        size="small"
                        disabled={!questionTypes.includes(type.key) || loading}
                        sx={{
                          width: 56,
                          "& .MuiInputBase-input": { textAlign: "center", fontWeight: 700 }
                        }}
                        value={distribution[type.key] || ""}
                        onChange={e => handleDistributionChange(type.key, e.target.value)}
                        inputProps={{ min: 0, step: 1 }}
                        placeholder="#"
                      />
                    </Box>
                  </Box>
                  {idx !== ALL_QUESTION_TYPES.length - 1 && (
                    <Box sx={{ height: 1, bgcolor: "#e3e6ed", width: "100%" }} />
                  )}
                </React.Fragment>
              ))}
            </Box>
          </Paper>
          {/* SECTION 3: Extra Context */}
          <Paper sx={{ p: 3, mb: 2, borderRadius: 3, boxShadow: 2, background: "#fcfdff" }}>
            <Typography variant="h6" fontWeight={800} color="primary" gutterBottom>
              3. Additional Context or Instructions
            </Typography>
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
              sx={{
                fontWeight: 800,
                fontSize: 18,
                minWidth: 340,
                height: 52,
                width: "100%",
                borderRadius: 2,
                boxShadow: "0 4px 16px #183e8140",
                textTransform: "uppercase"
              }}
              disabled={loading}
              startIcon={loading ? <CircularProgress color="inherit" size={22} /> : null}
            >
              {loading ? "Generating..." : "Generate Question Paper"}
            </Button>
          </Box>
        </form>
        {/* Results below */}
        {summary && (
          <Accordion sx={{
            mt: 4, mb: 1, borderRadius: 2,
            bgcolor: "#e7f6ef",
            '& .MuiAccordionSummary-root': { minHeight: 54 },
            '& .MuiAccordionDetails-root': { bgcolor: "#eafaf6" }
          }}>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="subtitle1" fontWeight={700} color="primary">
                Deep Summary
              </Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Typography variant="body2" sx={{ whiteSpace: "pre-line" }}>
                {summary}
              </Typography>
            </AccordionDetails>
          </Accordion>
        )}
        {(questions.length > 0) && (
          <Paper elevation={0} sx={{
            mt: 3, p: 3, bgcolor: "#fff", borderRadius: 2, boxShadow: 2,
            border: "1.5px solid #dde6ee"
          }}>
            <Typography variant="subtitle1" fontWeight={800} color="primary" mb={1} sx={{ fontSize: 21 }}>
              Generated Questions:
            </Typography>
            {/* Preview */}
            <Box>
              {questions.map((q, idx) => formatQuestion(q, idx))}
            </Box>
            {/* Download PDF Button */}
            <Box display="flex" justifyContent="flex-end" mt={2}>
              <Button
                variant="contained"
                color="success"
                sx={{
                  fontWeight: 700,
                  borderRadius: 2,
                  fontSize: 16,
                  px: 3,
                  boxShadow: "0 2px 10px #26b75e20"
                }}
                onClick={handleDownloadPDF}
              >
                Download as PDF
              </Button>
            </Box>
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
