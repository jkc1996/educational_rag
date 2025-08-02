import React, { useState } from "react";
import { Box, Button, Typography, Select, MenuItem, TextField, Paper } from "@mui/material";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from "recharts";

const MODELS = [
  { value: "groq", label: "Groq" },
  { value: "gemini", label: "Gemini" },
  { value: "ollama", label: "Ollama" },
];

function EvaluationPage() {
  const [subject, setSubject] = useState("Machine Learning");
  const [model, setModel] = useState("groq");
  const [loading, setLoading] = useState(false);
  const [metrics, setMetrics] = useState(null);
  const [error, setError] = useState("");

  const handleEvaluate = async () => {
    setLoading(true);
    setMetrics(null);
    setError("");
    try {
      const response = await fetch("http://localhost:8000/evaluate-ragas/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ subject, model_name: model }),
      });
      const data = await response.json();
      if (data.status === "success") {
        setMetrics(data.metrics);
      } else {
        setError(data.message || "Error during evaluation.");
      }
    } catch (e) {
      setError(e.message || "Network error");
    }
    setLoading(false);
  };

  // Prepare data for chart (if metrics are available)
  const chartData = metrics
    ? Object.keys(metrics).map(metric => ({
        metric,
        value: typeof metrics[metric] === "object" ? metrics[metric]?.score || 0 : metrics[metric]
      }))
    : [];

  return (
    <Box maxWidth={600} mx="auto" my={4}>
      <Paper elevation={3} sx={{ p: 3 }}>
        <Typography variant="h5" mb={2}>RAGAS Evaluation</Typography>
        <TextField
          label="Subject"
          value={subject}
          onChange={e => setSubject(e.target.value)}
          fullWidth
          margin="normal"
        />
        <Select
          value={model}
          onChange={e => setModel(e.target.value)}
          fullWidth
          margin="normal"
        >
          {MODELS.map(m => (
            <MenuItem value={m.value} key={m.value}>{m.label}</MenuItem>
          ))}
        </Select>
        <Button
          variant="contained"
          onClick={handleEvaluate}
          disabled={loading}
          sx={{ mt: 2, mb: 2, width: "100%" }}
        >
          {loading ? "Evaluating..." : "Run Evaluation"}
        </Button>

        {error && (
          <Typography color="error" mt={2}>{error}</Typography>
        )}

        {metrics && (
          <>
            <Typography variant="h6" mt={2} mb={1}>RAGAS Metrics</Typography>
            <BarChart width={500} height={250} data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="metric" />
              <YAxis domain={[0, 1]} />
              <Tooltip />
              <Legend />
              <Bar dataKey="value" fill="#1976d2" />
            </BarChart>
            <Box mt={3}>
              <Typography variant="subtitle1">Raw Results:</Typography>
              <pre style={{ background: "#f5f5f5", padding: 8 }}>
                {JSON.stringify(metrics, null, 2)}
              </pre>
            </Box>
          </>
        )}
      </Paper>
    </Box>
  );
}

export default EvaluationPage;
