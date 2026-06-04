import DownloadIcon from "@mui/icons-material/Download";
import { jsPDF } from "jspdf";
import {
  Alert,
  Box,
  Button,
  Checkbox,
  FormControlLabel,
  LinearProgress,
  MenuItem,
  Paper,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import { Fragment, useMemo, useState } from "react";

import { api } from "../../api/client.js";
import { ModelSelect } from "../../components/ModelSelect.jsx";
import { PageHeader } from "../../components/PageHeader.jsx";
import { SubjectSelect } from "../../components/SubjectSelect.jsx";

const questionTypes = ["one_liner", "true_false", "fill_blank", "multiple_choice", "descriptive"];

export function QuestionPaperPage({ models, subjects, documents }) {
  const defaultModel = useMemo(() => models.find((model) => model.default)?.id || models[0]?.id || "", [models]);
  const [subject, setSubject] = useState("");
  const [selectedDocuments, setSelectedDocuments] = useState([]);
  const [modelId, setModelId] = useState("");
  const [difficulty, setDifficulty] = useState("medium");
  const [totalQuestions, setTotalQuestions] = useState(10);
  const [distribution, setDistribution] = useState({});
  const [extraContext, setExtraContext] = useState("");
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);

  const eligibleDocs = documents.filter((doc) => doc.subject === subject && doc.summary_cache_key);

  const toggleDocument = (documentId) => {
    setSelectedDocuments((current) =>
      current.includes(documentId) ? current.filter((item) => item !== documentId) : [...current, documentId]
    );
  };

  const setTypeCount = (type, value) => {
    setDistribution((current) => ({ ...current, [type]: Math.max(0, Number(value) || 0) }));
  };

  const generate = async (event) => {
    event.preventDefault();
    setLoading(true);
    setMessage(null);
    setResponse(null);
    try {
      const result = await api.questionPaper({
        subject,
        document_ids: selectedDocuments,
        model_id: modelId || defaultModel,
        total_questions: Number(totalQuestions),
        difficulty,
        distribution,
        extra_context: extraContext,
      });
      setResponse(result);
    } catch (err) {
      setMessage({ severity: "error", text: err.message });
    } finally {
      setLoading(false);
    }
  };

  const download = () => {
    if (!response?.question_paper?.questions?.length) return;
    const doc = new jsPDF();
    let y = 18;
    doc.setFont("helvetica", "bold");
    doc.setFontSize(18);
    doc.text(`${subject} Question Paper`, 14, y);
    y += 12;
    doc.setFontSize(11);
    doc.setFont("helvetica", "normal");
    response.question_paper.questions.forEach((question, index) => {
      const lines = doc.splitTextToSize(`${index + 1}. ${question.question}`, 180);
      if (y + lines.length * 6 > 275) {
        doc.addPage();
        y = 18;
      }
      doc.text(lines, 14, y);
      y += lines.length * 6;
      if (question.options?.length) {
        question.options.forEach((option, optionIndex) => {
          doc.text(`   ${String.fromCharCode(97 + optionIndex)}) ${option}`, 18, y);
          y += 6;
        });
      }
      y += 4;
    });
    doc.addPage();
    y = 18;
    doc.setFont("helvetica", "bold");
    doc.text("Answer Key", 14, y);
    y += 10;
    doc.setFont("helvetica", "normal");
    response.question_paper.questions.forEach((question, index) => {
      const lines = doc.splitTextToSize(`${index + 1}. ${question.answer}`, 180);
      if (y + lines.length * 6 > 275) {
        doc.addPage();
        y = 18;
      }
      doc.text(lines, 14, y);
      y += lines.length * 6 + 3;
    });
    doc.save(`${subject.replace(/\s+/g, "_")}_Question_Paper.pdf`);
  };

  return (
    <>
      <PageHeader
        title="Question Paper"
        description="Generate assessments from cached structured summaries instead of repeatedly summarizing full documents."
      />

      {message && (
        <Alert severity={message.severity} sx={{ mb: 2 }}>
          {message.text}
        </Alert>
      )}

      <Paper className="panel" sx={{ p: 2.5 }}>
        <Stack component="form" onSubmit={generate} gap={2}>
          <Box sx={{ display: "grid", gridTemplateColumns: { xs: "1fr", md: "1fr 1fr 1fr" }, gap: 2 }}>
            <SubjectSelect subjects={subjects} value={subject} onChange={(value) => { setSubject(value); setSelectedDocuments([]); }} />
            <ModelSelect models={models} value={modelId || defaultModel} onChange={setModelId} />
            <TextField select size="small" label="Difficulty" value={difficulty} onChange={(event) => setDifficulty(event.target.value)}>
              {["easy", "medium", "hard"].map((item) => (
                <MenuItem key={item} value={item}>{item}</MenuItem>
              ))}
            </TextField>
          </Box>

          <TextField
            type="number"
            size="small"
            label="Total questions"
            value={totalQuestions}
            onChange={(event) => setTotalQuestions(event.target.value)}
            inputProps={{ min: 1, max: 50 }}
            sx={{ maxWidth: 220 }}
          />

          <Box sx={{ display: "grid", gridTemplateColumns: { xs: "1fr", md: "1fr 1fr" }, gap: 2 }}>
            <Paper variant="outlined" sx={{ p: 2 }}>
              <Typography fontWeight={750} sx={{ mb: 1 }}>Cached source summaries</Typography>
              <Stack gap={0.5}>
                {eligibleDocs.map((doc) => (
                  <FormControlLabel
                    key={doc.id}
                    control={<Checkbox checked={selectedDocuments.includes(doc.id)} onChange={() => toggleDocument(doc.id)} />}
                    label={doc.filename}
                  />
                ))}
                {subject && eligibleDocs.length === 0 && (
                  <Typography color="text.secondary">No completed cached summaries for this subject yet.</Typography>
                )}
              </Stack>
            </Paper>

            <Paper variant="outlined" sx={{ p: 2 }}>
              <Typography fontWeight={750} sx={{ mb: 1 }}>Question distribution</Typography>
              <Box sx={{ display: "grid", gridTemplateColumns: "1fr 96px", gap: 1 }}>
                {questionTypes.map((type) => (
                  <Fragment key={type}>
                    <Typography sx={{ alignSelf: "center" }}>{type}</Typography>
                    <TextField
                      size="small"
                      type="number"
                      value={distribution[type] || ""}
                      onChange={(event) => setTypeCount(type, event.target.value)}
                      inputProps={{ min: 0 }}
                    />
                  </Fragment>
                ))}
              </Box>
            </Paper>
          </Box>

          <TextField
            label="Additional instructions"
            value={extraContext}
            onChange={(event) => setExtraContext(event.target.value)}
            multiline
            minRows={2}
          />

          <Button type="submit" variant="contained" disabled={loading || !subject || selectedDocuments.length === 0}>
            Generate
          </Button>
        </Stack>
        {loading && <LinearProgress sx={{ mt: 2 }} />}
      </Paper>

      {response && (
        <Paper className="panel" sx={{ mt: 2, p: 2.5 }}>
          <Stack direction="row" alignItems="center" justifyContent="space-between" sx={{ mb: 2 }}>
            <Typography variant="h6">Generated Questions</Typography>
            <Button variant="outlined" startIcon={<DownloadIcon />} onClick={download}>
              PDF
            </Button>
          </Stack>
          <Stack gap={1.5}>
            {response.question_paper.questions.map((question, index) => (
              <Paper key={`${question.type}-${index}`} variant="outlined" sx={{ p: 1.5 }}>
                <Typography fontWeight={750}>{index + 1}. {question.question}</Typography>
                {question.options?.map((option, optionIndex) => (
                  <Typography key={option} variant="body2" sx={{ ml: 2 }}>
                    {String.fromCharCode(97 + optionIndex)}) {option}
                  </Typography>
                ))}
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                  Answer: {question.answer}
                </Typography>
              </Paper>
            ))}
          </Stack>
        </Paper>
      )}
    </>
  );
}
