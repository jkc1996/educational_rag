import {
  Alert,
  Box,
  Button,
  Checkbox,
  FormControl,
  FormControlLabel,
  InputLabel,
  LinearProgress,
  MenuItem,
  Paper,
  Select,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from "@mui/material";
import { useEffect, useMemo, useState } from "react";

import { api } from "../../api/client.js";
import { PageHeader } from "../../components/PageHeader.jsx";
import { SubjectSelect } from "../../components/SubjectSelect.jsx";

const ragasMetrics = ["context_precision", "context_recall", "faithfulness", "answer_relevancy"];

export function EvaluationPage({ models, subjects }) {
  const defaultModel = useMemo(() => models.find((model) => model.default)?.id || models[0]?.id || "", [models]);
  const [subject, setSubject] = useState("");
  const [selectedModels, setSelectedModels] = useState([]);
  const [evalSet, setEvalSet] = useState("default");
  const [evalSets, setEvalSets] = useState([]);
  const [limit, setLimit] = useState(10);
  const [metrics, setMetrics] = useState(ragasMetrics);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);

  const activeModels = selectedModels.length ? selectedModels : [defaultModel].filter(Boolean);

  useEffect(() => {
    api
      .evaluationSets()
      .then((response) => {
        const items = response.items || [];
        setEvalSets(items);
        if (items.length && !items.some((item) => item.name === evalSet)) {
          setEvalSet(items[0].name);
        }
      })
      .catch((err) => setMessage({ severity: "error", text: err.message }));
  }, []);

  const toggleModel = (modelId) => {
    setSelectedModels((current) => (current.includes(modelId) ? current.filter((item) => item !== modelId) : [...current, modelId]));
  };

  const toggleMetric = (metric) => {
    setMetrics((current) => (current.includes(metric) ? current.filter((item) => item !== metric) : [...current, metric]));
  };

  const run = async () => {
    setLoading(true);
    setMessage(null);
    setResults(null);
    try {
      const response = await api.evaluateRagas({
        subject,
        model_ids: activeModels,
        eval_set: evalSet,
        metrics,
        limit: Number(limit),
      });
      setResults(response.results);
    } catch (err) {
      setMessage({ severity: "error", text: err.message });
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <PageHeader title="RAGAS Evaluation" description="Run RAGAS-only evaluations and compare approved OpenAI models." />

      {message && <Alert severity={message.severity} sx={{ mb: 2 }}>{message.text}</Alert>}

      <Paper className="panel" sx={{ p: 2.5 }}>
        {evalSets.length === 0 && (
          <Alert severity="info" sx={{ mb: 2 }}>
            No evaluation sets found. The backend will seed a default set when storage is writable.
          </Alert>
        )}

        <Box sx={{ display: "grid", gridTemplateColumns: { xs: "1fr", md: "1fr 220px 140px" }, gap: 2 }}>
          <SubjectSelect subjects={subjects} value={subject} onChange={setSubject} />
          <FormControl size="small">
            <InputLabel>Eval set</InputLabel>
            <Select label="Eval set" value={evalSet} onChange={(event) => setEvalSet(event.target.value)}>
              {evalSets.length === 0 && (
                <MenuItem value={evalSet} disabled>
                  Loading eval sets...
                </MenuItem>
              )}
              {evalSets.map((item) => (
                <MenuItem key={item.name} value={item.name}>
                  {item.name} ({item.row_count})
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          <TextField size="small" type="number" label="Limit" value={limit} onChange={(event) => setLimit(event.target.value)} />
        </Box>

        {evalSets.find((item) => item.name === evalSet)?.sample_questions?.length > 0 && (
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            Sample: {evalSets.find((item) => item.name === evalSet).sample_questions[0]}
          </Typography>
        )}

        <Box sx={{ display: "grid", gridTemplateColumns: { xs: "1fr", md: "1fr 1fr" }, gap: 2, mt: 2 }}>
          <Paper variant="outlined" sx={{ p: 2 }}>
            <Typography fontWeight={750} sx={{ mb: 1 }}>Models</Typography>
            {models.map((model) => (
              <FormControlLabel
                key={model.id}
                control={<Checkbox checked={activeModels.includes(model.id)} onChange={() => toggleModel(model.id)} />}
                label={`${model.label} (${model.role})`}
              />
            ))}
          </Paper>
          <Paper variant="outlined" sx={{ p: 2 }}>
            <Typography fontWeight={750} sx={{ mb: 1 }}>Metrics</Typography>
            {ragasMetrics.map((metric) => (
              <FormControlLabel
                key={metric}
                control={<Checkbox checked={metrics.includes(metric)} onChange={() => toggleMetric(metric)} />}
                label={metric}
              />
            ))}
          </Paper>
        </Box>

        <Button variant="contained" sx={{ mt: 2 }} disabled={loading || !subject || !evalSet || !metrics.length || !activeModels.length} onClick={run}>
          Run Evaluation
        </Button>
        {loading && <LinearProgress sx={{ mt: 2 }} />}
      </Paper>

      {results && (
        <Paper className="panel" sx={{ mt: 2, p: 2.5, overflow: "hidden" }}>
          <Typography variant="h6" sx={{ mb: 1.5 }}>Results</Typography>
          <Box sx={{ overflowX: "auto" }}>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Model</TableCell>
                  <TableCell>Q#</TableCell>
                  <TableCell>Question</TableCell>
                  <TableCell>Answer</TableCell>
                  {metrics.map((metric) => <TableCell key={metric}>{metric}</TableCell>)}
                </TableRow>
              </TableHead>
              <TableBody>
                {Object.entries(results).flatMap(([model, rows]) =>
                  rows.map((row) => (
                    <TableRow key={`${model}-${row.id}`} hover>
                      <TableCell>{model}</TableCell>
                      <TableCell>{row.id}</TableCell>
                      <TableCell>{row.question}</TableCell>
                      <TableCell>{row.answer}</TableCell>
                      {metrics.map((metric) => (
                        <TableCell key={metric}>{formatMetric(row[metric])}</TableCell>
                      ))}
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </Box>
        </Paper>
      )}
    </>
  );
}

function formatMetric(value) {
  if (typeof value === "number") return value.toFixed(3);
  if (value && typeof value === "object" && typeof value.score === "number") return value.score.toFixed(3);
  return value ?? "";
}
