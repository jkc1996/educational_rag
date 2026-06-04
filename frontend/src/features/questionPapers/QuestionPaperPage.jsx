import AssignmentOutlinedIcon from "@mui/icons-material/AssignmentOutlined";
import DownloadIcon from "@mui/icons-material/Download";
import FormatListNumberedOutlinedIcon from "@mui/icons-material/FormatListNumberedOutlined";
import { jsPDF } from "jspdf";
import {
  Alert,
  Box,
  Button,
  Checkbox,
  Chip,
  FormControlLabel,
  LinearProgress,
  MenuItem,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import { Fragment, useMemo, useState } from "react";

import { api } from "../../api/client.js";
import { EmptyState, WorkPanel, WorkspaceLayout } from "../../components/Workspace.jsx";
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
  const requestedDistribution = Object.values(distribution).reduce((total, value) => total + Number(value || 0), 0);

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
        eyebrow="Assessment Studio"
        title="Assessment"
        description="Build question papers from cached document intelligence instead of sending full PDFs through the model again."
        actions={
          response?.question_paper?.questions?.length ? (
            <Button variant="outlined" startIcon={<DownloadIcon />} onClick={download}>
              PDF
            </Button>
          ) : null
        }
      />

      {message && (
        <Alert severity={message.severity} sx={{ mb: 2 }}>
          {message.text}
        </Alert>
      )}

      <WorkspaceLayout
        inspector={
          <AssessmentInspector
            eligibleDocs={eligibleDocs}
            selectedDocuments={selectedDocuments}
            totalQuestions={Number(totalQuestions)}
            requestedDistribution={requestedDistribution}
            difficulty={difficulty}
            modelId={modelId || defaultModel}
          />
        }
      >
        <Stack gap={2}>
          <WorkPanel>
            <Stack component="form" onSubmit={generate} gap={2}>
              <Stack direction="row" alignItems="center" gap={1}>
                <AssignmentOutlinedIcon color="primary" />
                <Typography variant="h6">Paper Blueprint</Typography>
              </Stack>

              <Box sx={{ display: "grid", gridTemplateColumns: { xs: "1fr", md: "1fr 1fr 180px" }, gap: 2 }}>
                <SubjectSelect
                  subjects={subjects}
                  value={subject}
                  onChange={(value) => {
                    setSubject(value);
                    setSelectedDocuments([]);
                  }}
                />
                <ModelSelect models={models} value={modelId || defaultModel} onChange={setModelId} />
                <TextField select size="small" label="Difficulty" value={difficulty} onChange={(event) => setDifficulty(event.target.value)}>
                  {["easy", "medium", "hard"].map((item) => (
                    <MenuItem key={item} value={item}>
                      {item}
                    </MenuItem>
                  ))}
                </TextField>
              </Box>

              <Box sx={{ display: "grid", gridTemplateColumns: { xs: "1fr", md: "220px 1fr" }, gap: 2 }}>
                <TextField
                  type="number"
                  size="small"
                  label="Total questions"
                  value={totalQuestions}
                  onChange={(event) => setTotalQuestions(event.target.value)}
                  inputProps={{ min: 1, max: 50 }}
                />

                <TextField
                  label="Additional instructions"
                  value={extraContext}
                  onChange={(event) => setExtraContext(event.target.value)}
                  multiline
                  minRows={2}
                />
              </Box>

              <Box className="inline-section">
                <Typography fontWeight={800} sx={{ mb: 1 }}>
                  Cached Source Summaries
                </Typography>
                <Stack gap={0.75}>
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
                  {!subject && <Typography color="text.secondary">Select a subject to see summary-backed sources.</Typography>}
                </Stack>
              </Box>

              <Box className="inline-section">
                <Typography fontWeight={800} sx={{ mb: 1 }}>
                  Question Distribution
                </Typography>
                <Box sx={{ display: "grid", gridTemplateColumns: { xs: "1fr 92px", md: "repeat(2, minmax(0, 1fr) 92px)" }, gap: 1 }}>
                  {questionTypes.map((type) => (
                    <Fragment key={type}>
                      <Typography sx={{ alignSelf: "center" }}>{type.replace(/_/g, " ")}</Typography>
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
              </Box>

              <Button type="submit" variant="contained" disabled={loading || !subject || selectedDocuments.length === 0}>
                Generate
              </Button>
            </Stack>
            {loading && <LinearProgress sx={{ mt: 2 }} />}
          </WorkPanel>

          <WorkPanel>
            <Stack direction="row" alignItems="center" gap={1} sx={{ mb: 1.5 }}>
              <FormatListNumberedOutlinedIcon color="primary" />
              <Typography variant="h6">Generated Questions</Typography>
              {response?.question_paper?.questions?.length ? <Chip size="small" label={response.question_paper.questions.length} /> : null}
            </Stack>

            {response?.question_paper?.questions?.length ? (
              <Stack gap={1.5}>
                {response.question_paper.questions.map((question, index) => (
                  <Box key={`${question.type}-${index}`} className="question-card">
                    <Stack direction="row" gap={1} flexWrap="wrap" sx={{ mb: 1 }}>
                      <Chip size="small" label={`Q${index + 1}`} color="primary" />
                      <Chip size="small" label={question.type?.replace(/_/g, " ") || "question"} variant="outlined" />
                    </Stack>
                    <Typography fontWeight={800}>{question.question}</Typography>
                    {question.options?.map((option, optionIndex) => (
                      <Typography key={`${option}-${optionIndex}`} variant="body2" sx={{ ml: 2, mt: 0.5 }}>
                        {String.fromCharCode(97 + optionIndex)}) {option}
                      </Typography>
                    ))}
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                      Answer: {question.answer}
                    </Typography>
                  </Box>
                ))}
              </Stack>
            ) : (
              <EmptyState
                icon={<AssignmentOutlinedIcon color="primary" sx={{ fontSize: 38 }} />}
                title="No paper generated yet"
                description="Select cached summaries and generate a structured paper when the blueprint is ready."
              />
            )}
          </WorkPanel>
        </Stack>
      </WorkspaceLayout>
    </>
  );
}

function AssessmentInspector({ eligibleDocs, selectedDocuments, totalQuestions, requestedDistribution, difficulty, modelId }) {
  const selectedCount = selectedDocuments.length;
  const distributionStatus = requestedDistribution === 0 ? "auto" : `${requestedDistribution}/${totalQuestions}`;

  return (
    <Stack gap={2}>
      <WorkPanel>
        <Typography variant="h6" sx={{ mb: 1.5 }}>
          Blueprint State
        </Typography>
        <Stack gap={1.25}>
          <Trace label="Model" value={modelId || "Not selected"} />
          <Trace label="Difficulty" value={difficulty} />
          <Trace label="Available summaries" value={eligibleDocs.length} />
          <Trace label="Selected summaries" value={selectedCount} />
          <Trace label="Distribution" value={distributionStatus} />
        </Stack>
      </WorkPanel>

      <WorkPanel>
        <Typography variant="h6" sx={{ mb: 1.5 }}>
          Generation Policy
        </Typography>
        <Stack gap={1}>
          <Chip label="Uses cached summaries" color="success" variant="outlined" />
          <Chip label="Final synthesis model only" color="primary" variant="outlined" />
          <Chip label="Schema validated output" color="secondary" variant="outlined" />
        </Stack>
      </WorkPanel>
    </Stack>
  );
}

function Trace({ label, value }) {
  return (
    <Stack direction="row" justifyContent="space-between" gap={1.5}>
      <Typography variant="body2" color="text.secondary">
        {label}
      </Typography>
      <Typography variant="body2" fontWeight={750} sx={{ textAlign: "right" }}>
        {value || "-"}
      </Typography>
    </Stack>
  );
}
