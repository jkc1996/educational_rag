import React, { useState } from "react";
import {
  Box, Button, Typography, Select, MenuItem, Table, TableHead, TableRow, TableCell, TableBody,
  IconButton, Tooltip, ToggleButtonGroup, ToggleButton, Paper, Menu, Checkbox, ListItemText, FormControl, InputLabel
} from "@mui/material";
import MetricChart from "./MetricChart";
import {
  METRIC_CATEGORIES, STATIC_COLS, getMetricColor, getMetricAverages, METRIC_LABELS
} from "./../utils/metricUtils";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import ViewColumnIcon from "@mui/icons-material/ViewColumn";
import CategoryIcon from "@mui/icons-material/Category";

const MODELS = [
  { value: "groq", label: "Groq" },
  { value: "gemini", label: "Gemini" },
  { value: "ollama", label: "Ollama" },
];

// Default 2 metrics per category
const DEFAULT_METRICS = {
  retrieval: ["context_precision", "context_recall"],
  nvidia: ["nv_accuracy", "nv_context_relevance"],
  nlp: ["factual_correctness(mode=f1)", "semantic_similarity"],
};

function EvaluationPage() {
  const [evalMode, setEvalMode] = useState("single");
  const [model, setModel] = useState("groq");
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState("");
  // Use category key (not tab idx) for UI
  const [categoryKey, setCategoryKey] = useState(METRIC_CATEGORIES[0].key);
  const [chartOpen, setChartOpen] = useState(false);
  const [expandedRows, setExpandedRows] = useState({});
  const [shownMetrics, setShownMetrics] = useState({
    retrieval: DEFAULT_METRICS.retrieval,
    nvidia: DEFAULT_METRICS.nvidia,
    nlp: DEFAULT_METRICS.nlp,
  });
  const [anchorEl, setAnchorEl] = useState(null); // For column selector

  // Derived
  const category = METRIC_CATEGORIES.find(cat => cat.key === categoryKey);
  const categoryMetrics = category.metrics;
  const metricsToShow = shownMetrics[categoryKey] || [];
  const averages = results ? getMetricAverages(results, metricsToShow) : {};

  // Evaluate button
  const handleEvaluate = async () => {
    setLoading(true);
    setResults(null);
    setError("");
    try {
      const response = await fetch("http://localhost:8000/evaluate-ragas/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ model_name: model }),
      });
      const data = await response.json();
      if (data.status === "success") {
        setResults(data.results);
      } else {
        setError(data.message || "Error during evaluation.");
      }
    } catch (e) {
      setError(e.message || "Network error");
    }
    setLoading(false);
  };

  // Change category (dropdown)
  const handleCategoryChange = (e) => {
    const newCat = e.target.value;
    setCategoryKey(newCat);
    // Ensure at least some metrics selected
    setShownMetrics(prev => ({
      ...prev,
      [newCat]: prev[newCat]?.length ? prev[newCat] : DEFAULT_METRICS[newCat]
    }));
  };

  // Show/Hide column selector menu
  const handleColMenuOpen = (e) => setAnchorEl(e.currentTarget);
  const handleColMenuClose = () => setAnchorEl(null);

  // Metric column toggle
  const handleMetricToggle = (metric) => {
    setShownMetrics(prev => {
      let old = prev[categoryKey] || [];
      // Always at least 1 metric shown!
      if (old.includes(metric)) {
        if (old.length === 1) return prev;
        return { ...prev, [categoryKey]: old.filter(m => m !== metric) };
      } else {
        return { ...prev, [categoryKey]: [...old, metric] };
      }
    });
  };

  // Context expand/collapse
  const handleExpandRow = (id) => {
    setExpandedRows(prev => ({ ...prev, [id]: !prev[id] }));
  };

  return (
    <Box sx={{
      width: "100%",
      minHeight: "100vh",
      background: "#f7fafc",
      p: 0,
      m: 0,
      overflow: "hidden"
    }}>
      {/* Top Card */}
      <Paper
        elevation={2}
        sx={{
          background: "#fff",
          borderRadius: 3,
          boxShadow: 1,
          display: "flex",
          alignItems: "center",
          gap: 2,
          px: 4,
          pt: 4,
          pb: 2,
          mt: 2,
          mx: "auto",
          maxWidth: "98vw",
          minWidth: 320,
          zIndex: 3
        }}
      >
        <Typography variant="h4" fontWeight={700} color="primary" sx={{ mr: 3 }}>
          RAGAS Evaluation
        </Typography>
        <ToggleButtonGroup
          value={evalMode}
          exclusive
          onChange={(_, val) => val && setEvalMode(val)}
          sx={{ mr: 3 }}
        >
          <ToggleButton value="single" sx={{ px: 2 }}>Single LLM</ToggleButton>
          <ToggleButton value="compare" sx={{ px: 2 }} disabled>
            Compare LLMs (Coming Soon)
          </ToggleButton>
        </ToggleButtonGroup>
        <Select
          value={model}
          onChange={e => setModel(e.target.value)}
          sx={{ minWidth: 200, background: "#f3f6fc", fontWeight: 600 }}
          size="medium"
          disabled={evalMode === "compare"}
        >
          {MODELS.map(m => (
            <MenuItem value={m.value} key={m.value}>{m.label}</MenuItem>
          ))}
        </Select>
        <Button
          variant="contained"
          onClick={handleEvaluate}
          disabled={loading || evalMode === "compare"}
          sx={{ minWidth: 160, ml: 2 }}
          size="medium"
        >
          {loading ? "Evaluating..." : "Run Evaluation"}
        </Button>
        <Button
          variant="outlined"
          size="medium"
          onClick={() => setChartOpen(true)}
          sx={{ ml: 2 }}
          disabled={!results}
        >
          Show Chart
        </Button>
      </Paper>

      {/* Main Content */}
      <Box sx={{
        px: 2,
        pt: 3,
        width: "100%",
        maxWidth: "100vw",
        overflow: "visible" // allow scroll only inside the rounded box
      }}>
        {error && (
          <Typography color="error" mt={2}>{error}</Typography>
        )}
        {!results && (
          <Box mt={8} display="flex" flexDirection="column" alignItems="center">
            <Typography variant="h5" color="text.secondary">
              Click <b>Run Evaluation</b> to see your RAGAS results!
            </Typography>
          </Box>
        )}
        {results && (
          <>
            {/* Dropdowns above table */}
            <Box sx={{
              display: "flex", alignItems: "center", gap: 2, mb: 2,
              justifyContent: { xs: "flex-start", sm: "space-between" }
            }}>
              <FormControl sx={{ minWidth: 210 }}>
                <InputLabel id="cat-dd-label"><CategoryIcon sx={{ fontSize: 18, mr: 1, verticalAlign: "middle" }} />Category</InputLabel>
                <Select
                  labelId="cat-dd-label"
                  value={categoryKey}
                  label="Category"
                  onChange={handleCategoryChange}
                  size="small"
                  sx={{ fontWeight: 600, background: "#fff" }}
                >
                  {METRIC_CATEGORIES.map(cat => (
                    <MenuItem key={cat.key} value={cat.key}>
                      {cat.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
              <Box sx={{ flex: 1 }} />
              <Tooltip title="Choose metrics to show">
                <Button
                  variant="outlined"
                  startIcon={<ViewColumnIcon />}
                  onClick={handleColMenuOpen}
                  sx={{
                    background: "#fff",
                    fontWeight: 600,
                    borderRadius: 2,
                    minWidth: 170
                  }}
                >
                  Show Columns
                </Button>
              </Tooltip>
              <Menu
                anchorEl={anchorEl}
                open={!!anchorEl}
                onClose={handleColMenuClose}
                keepMounted
              >
                {/* Qid/question/answer/ground_truth/contexts always checked/disabled */}
                {STATIC_COLS.map(col => (
                  <MenuItem key={col.key} dense disabled>
                    <Checkbox checked disabled />
                    <ListItemText primary={col.label} />
                  </MenuItem>
                ))}
                <Box sx={{ borderTop: "1px solid #eee", mt: 0.5, mb: 0.5 }} />
                {categoryMetrics.map(metric => (
                  <MenuItem key={metric} dense
                    onClick={() => handleMetricToggle(metric)}
                    disabled={metricsToShow.length === 1 && metricsToShow.includes(metric)}
                  >
                    <Checkbox checked={metricsToShow.includes(metric)} />
                    <ListItemText primary={METRIC_LABELS[metric] || metric} />
                  </MenuItem>
                ))}
              </Menu>
            </Box>
            <MetricChart
              open={chartOpen}
              onClose={() => setChartOpen(false)}
              averages={averages}
              metrics={metricsToShow}
            />
            {/* Table inside a perfectly rounded box */}
            <Paper elevation={2}
              sx={{
                width: "100%",
                maxWidth: "100%",
                overflow: "auto",
                borderRadius: "10px",
                background: "#fff",
                boxShadow: "0 2px 4px rgba(0,0,0,0.07)",
                my: 1,
                px: 0,
                pb: 2,
                border: "1.5px solid #e0e0e0",
                minHeight: 350
              }}
            >
              <Table size="small" stickyHeader >
                <TableHead>
                  <TableRow>
                    {STATIC_COLS.map(col => (
                      <TableCell key={col.key} sx={{
                        fontWeight: 700,
                        background: "#f3f4f6",
                        minWidth:
                          col.key === "question" ? 400 :
                          col.key === "answer" ? 400 :
                          col.key === "ground_truth" ? 400 :
                          col.key === "contexts" ? 320 :
                          80,
                        fontSize: 15
                      }}>
                        {col.label}
                      </TableCell>
                    ))}
                    {metricsToShow.map(metric => (
                      <TableCell key={metric} sx={{
                        fontWeight: 700,
                        background: "#f3f4f6",
                        minWidth: 135,
                        fontSize: 15
                      }}>
                        {METRIC_LABELS[metric] || metric}
                      </TableCell>
                    ))}
                  </TableRow>
                </TableHead>
                <TableBody>
                  {results.map((row, idx) => (
                    <TableRow key={row.id || idx}>
                      {STATIC_COLS.map(col => (
                        <TableCell
                          key={col.key}
                          sx={{
                            minWidth:
                              col.key === "question" ? 400 :
                              col.key === "answer" ? 400 :
                              col.key === "ground_truth" ? 400 :
                              col.key === "contexts" ? 320 :
                              80,
                            whiteSpace: "normal",
                            wordBreak: "break-word",
                            fontSize: 14,
                          }}
                        >
                          {col.key === "contexts" ? (
                            <Box>
                              <Tooltip title="Expand/Collapse">
                                <IconButton
                                  size="small"
                                  onClick={() => handleExpandRow(row.id || idx)}
                                >
                                  <ExpandMoreIcon
                                    sx={{
                                      transform: expandedRows[row.id || idx] ? "rotate(180deg)" : "rotate(0deg)",
                                      transition: "0.2s"
                                    }}
                                  />
                                </IconButton>
                              </Tooltip>
                              <Box
                                sx={{
                                  maxHeight: expandedRows[row.id || idx] ? "none" : 48,
                                  overflow: "hidden",
                                  transition: "max-height 0.2s"
                                }}
                              >
                                {Array.isArray(row[col.key])
                                  ? row[col.key].join(" || ")
                                  : row[col.key]}
                              </Box>
                            </Box>
                          ) : (
                            Array.isArray(row[col.key])
                              ? row[col.key].join(" || ")
                              : row[col.key]
                          )}
                        </TableCell>
                      ))}
                      {metricsToShow.map(metric => {
                        let val = row[metric];
                        if (typeof val === "object" && val !== null && typeof val.score === "number") {
                          val = val.score;
                        }
                        return (
                          <TableCell
                            key={metric}
                            sx={{
                              background: getMetricColor(val),
                              fontWeight: 600,
                              textAlign: "center"
                            }}
                          >
                            {typeof val === "number" ? val.toFixed(3) : "-"}
                          </TableCell>
                        );
                      })}
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </Paper>
          </>
        )}
      </Box>
    </Box>
  );
}

export default EvaluationPage;
