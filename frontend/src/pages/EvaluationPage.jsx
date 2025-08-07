import React, { useState } from "react";
import {
  Box, Paper, Typography, Button, Tooltip, ToggleButtonGroup, ToggleButton,
  Menu, FormControl, InputLabel, Select, MenuItem, Checkbox, ListItemText
} from "@mui/material";
import { METRIC_CATEGORIES, STATIC_COLS, getMetricAverages, METRIC_LABELS } from "../utils/metricUtils";
import MetricTable from "./MetricTable";
import CompareTable from "./CompareTable";
import AggregatedCompareTable from "./AggregatedCompareTable";
import ModelSelector from "./ModelSelector";
import ModelMultiSelector from "./ModelMultiSelector";
import MetricChart from "./MetricChart";
import ViewColumnIcon from "@mui/icons-material/ViewColumn";
import CategoryIcon from "@mui/icons-material/Category";
import { DEFAULT_METRICS } from "../constants/defaults";
import { MODELS } from "../constants/models";
import { evaluateModels } from "../utils/api";
import { alignCompareResults } from "../utils/compareUtils";

export default function EvaluationPage() {
  // Top-level state
  const [evalMode, setEvalMode] = useState("single");
  const [model, setModel] = useState("groq");
  const [multiModels, setMultiModels] = useState(["groq", "gemini"]);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [compareResults, setCompareResults] = useState(null);
  const [error, setError] = useState("");
  const [categoryKey, setCategoryKey] = useState(METRIC_CATEGORIES[0].key);
  const [chartOpen, setChartOpen] = useState(false);
  const [expandedCell, setExpandedCell] = useState(null);

  // For multi LLM mode: "per-question" vs "aggregate"
  const [compareTableMode, setCompareTableMode] = useState("per-question");

  // Show columns logic
  const [shownMetrics, setShownMetrics] = useState({
    retrieval: [...DEFAULT_METRICS.retrieval],
    nvidia: [...DEFAULT_METRICS.nvidia],
    nlp: [...DEFAULT_METRICS.nlp],
  });
  const [anchorEl, setAnchorEl] = useState(null);
  const [showContexts, setShowContexts] = useState(false);

  // Derived variables
  const category = METRIC_CATEGORIES.find(cat => cat.key === categoryKey);
  const categoryMetrics = category.metrics;
  const metricsToShow = shownMetrics[categoryKey] || [];
  const averages = results ? getMetricAverages(results, metricsToShow) : {};
  const alignedRows = compareResults ? alignCompareResults(compareResults) : [];

  // ---- Single LLM handlers ----
  const handleEvaluate = async () => {
    setLoading(true); setResults(null); setError("");
    try {
      const data = await evaluateModels({ modelNames: model, category: categoryKey });
      if (data.status === "success") setResults(data.results);
      else setError(data.message || "Error during evaluation.");
    } catch (e) { setError(e.message || "Network error"); }
    setLoading(false);
  };

  // ---- Compare LLM handlers ----
  const handleRunCompare = async () => {
    setLoading(true); setCompareResults(null); setError("");
    try {
      const data = await evaluateModels({ modelNames: multiModels, category: categoryKey });
      if (data.status === "success") setCompareResults(data.results);
      else setError(data.message || "Error during comparison.");
    } catch (e) { setError(e.message || "Network error"); }
    setLoading(false);
  };

  // Shared handlers
  const handleCategoryChange = (e) => {
    const newCat = e.target.value;
    setCategoryKey(newCat);
    setShownMetrics(prev => ({
      ...prev,
      [newCat]: prev[newCat]?.length ? prev[newCat] : DEFAULT_METRICS[newCat]
    }));
  };
  const handleColMenuOpen = (e) => setAnchorEl(e.currentTarget);
  const handleColMenuClose = () => setAnchorEl(null);
  const handleMetricToggle = (metric) => {
    setShownMetrics(prev => {
      let old = prev[categoryKey] || [];
      if (old.includes(metric)) {
        if (old.length === 1) return prev;
        return { ...prev, [categoryKey]: old.filter(m => m !== metric) };
      } else {
        return { ...prev, [categoryKey]: [...old, metric] };
      }
    });
  };

  return (
    <Box sx={{ width: "100%", minHeight: "100vh", background: "#f7fafc", p: 0, m: 0, overflow: "auto" }}>
      {/* --- TOP BAR (always) --- */}
      <Box sx={{
        width: "100%", maxWidth: 1380, mx: "auto", mt: 3, mb: 1, px: { xs: 1, sm: 2, md: 3 },
      }}>
        <Paper
          elevation={2}
          sx={{
            background: "#fff",
            borderRadius: 3,
            boxShadow: 1,
            display: "flex",
            alignItems: "center",
            gap: 2,
            px: { xs: 1, sm: 2, md: 3 },
            pt: 3,
            pb: 2,
            minWidth: 320,
            zIndex: 3
          }}
        >
          <Typography variant="h5" fontWeight={700} color="primary" sx={{ mr: 2 }}>
            RAGAS Evaluation
          </Typography>
          <ToggleButtonGroup
            value={evalMode}
            exclusive
            onChange={(_, val) => {
              setEvalMode(val);
              setCompareTableMode("per-question");
              setResults(null);
              setCompareResults(null);
              setError("");
            }}
            sx={{ mr: 3 }}
            size="small"
          >
            <ToggleButton value="single" sx={{ px: 2 }}>Single LLM</ToggleButton>
            <ToggleButton value="compare" sx={{ px: 2 }}>Multi LLM</ToggleButton>
          </ToggleButtonGroup>
          {/* --- SINGLE LLM CONTROLS --- */}
          {evalMode === "single" ? (
            <>
              <ModelSelector
                multiple={false}
                value={model}
                onChange={e => setModel(e.target.value)}
                disabled={evalMode === "compare"}
              />
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
            </>
          ) : (
            /* --- MULTI LLM CONTROLS --- */
            <>
              <ModelMultiSelector
                selected={multiModels}
                onChange={setMultiModels}
                options={MODELS}
                sx={{ minWidth: 220 }}
              />
              <Button
                variant="contained"
                onClick={handleRunCompare}
                disabled={loading || multiModels.length < 2}
                sx={{ ml: 2, minWidth: 160 }}
              >
                {loading ? "Comparing..." : "Run Comparison"}
              </Button>
              <Button
                variant="outlined"
                size="medium"
                onClick={() => setChartOpen(true)}
                sx={{ ml: 2 }}
                disabled={!compareResults}
              >
                Show Chart
              </Button>
            </>
          )}
        </Paper>
      </Box>

      {/* --- MAIN CONTENT --- */}
      <Box sx={{ width: "100%", maxWidth: 1380, mx: "auto", px: { xs: 1, sm: 2, md: 3 }, pt: 2 }}>
        {/* --- ERROR --- */}
        {error && <Typography color="error" mt={2}>{error}</Typography>}

        {/* --- SINGLE LLM MODE --- */}
        {evalMode === "single" ? (
          !results ? (
            // Empty state (before Run Evaluation)
            <Box mt={8} display="flex" flexDirection="column" alignItems="center">
              <Typography variant="h5" color="text.secondary">
                Click <b>Run Evaluation</b> to see your RAGAS results!
              </Typography>
            </Box>
          ) : (
            <>
              {/* --- Category & Show Columns --- */}
              <Box sx={{
                display: "flex", alignItems: "center", gap: 2, mb: 2,
                justifyContent: { xs: "flex-start", sm: "space-between" }
              }}>
                <FormControl sx={{ minWidth: 180 }}>
                  <InputLabel id="cat-dd-label">
                    <CategoryIcon sx={{ fontSize: 18, mr: 1, verticalAlign: "middle" }} />Category
                  </InputLabel>
                  <Select
                    labelId="cat-dd-label"
                    value={categoryKey}
                    label="Category"
                    onChange={handleCategoryChange}
                    size="small"
                    sx={{ fontWeight: 600, background: "#fff" }}
                  >
                    {METRIC_CATEGORIES.map(cat => (
                      <MenuItem key={cat.key} value={cat.key}>{cat.label}</MenuItem>
                    ))}
                  </Select>
                </FormControl>
                <Box sx={{ flex: 1 }} />
                <Tooltip title="Choose metrics to show">
                  <Button
                    variant="outlined"
                    startIcon={<ViewColumnIcon />}
                    onClick={handleColMenuOpen}
                    sx={{ background: "#fff", fontWeight: 600, borderRadius: 2, minWidth: 140 }}
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
                  {/* Always-on base columns */}
                  <MenuItem dense disabled><Checkbox checked disabled /><ListItemText primary="Q#" /></MenuItem>
                  <MenuItem dense disabled><Checkbox checked disabled /><ListItemText primary="Question" /></MenuItem>
                  <MenuItem dense disabled><Checkbox checked disabled /><ListItemText primary="Ground Truth" /></MenuItem>
                  <MenuItem dense onClick={() => setShowContexts(val => !val)} sx={{ ml: 0 }}>
                    <Checkbox checked={showContexts} /><ListItemText primary="Contexts" />
                  </MenuItem>
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
              {/* --- Table/Chart --- */}
              <MetricChart
                open={chartOpen}
                onClose={() => setChartOpen(false)}
                averages={averages}
                metrics={metricsToShow}
              />
              <Paper elevation={2}
                sx={{
                  width: "100%",
                  overflow: "hidden",
                  borderRadius: "10px",
                  background: "#fff",
                  boxShadow: "0 2px 4px rgba(0,0,0,0.07)",
                  my: 1,
                  pb: 2,
                  border: "1.5px solid #e0e0e0"
                }}
              >
                <Box sx={{
                  width: "100%",
                  overflowX: "auto",
                  borderRadius: "inherit"
                }}>
                  <MetricTable
                    results={results}
                    metricsToShow={metricsToShow}
                    expandedCell={expandedCell}
                    setExpandedCell={setExpandedCell}
                    showContexts={showContexts}
                  />
                </Box>
              </Paper>
            </>
          )
        ) : (
          // --- MULTI LLM MODE ---
          !compareResults ? (
            // Empty state
            <Typography sx={{ mt: 10, textAlign: "center" }}>
              Select 2 or more models and click <b>Run Comparison</b>
            </Typography>
          ) : (
            <>
              {/* --- Table Mode Toggle (radio) --- */}
              <Box sx={{ width: "100%", mb: 2 }}>
                {/* Radio buttons as a row */}
                <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
                  <ToggleButtonGroup
                    exclusive
                    value={compareTableMode}
                    onChange={(_, val) => val && setCompareTableMode(val)}
                    size="small"
                  >
                    <ToggleButton value="per-question" sx={{ px: 3 }}>
                      <span style={{ color: compareTableMode === "per-question" ? "#d32f2f" : undefined, fontWeight: 600 }}>
                        PER QUESTION COMPARE
                      </span>
                    </ToggleButton>
                    <ToggleButton value="aggregated" sx={{ px: 3 }}>
                      <span style={{ color: compareTableMode === "aggregated" ? "#d32f2f" : undefined, fontWeight: 600 }}>
                        AGGREGATE COMPARISION
                      </span>
                    </ToggleButton>
                  </ToggleButtonGroup>
                </Box>
                {/* Category and Show Columns row (only if per-question) */}
                {compareTableMode === "per-question" && (
                  <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
                    <FormControl sx={{ minWidth: 180 }}>
                      <InputLabel id="multi-cat-dd">
                        <CategoryIcon sx={{ fontSize: 18, mr: 1, verticalAlign: "middle" }} />Category
                      </InputLabel>
                      <Select
                        labelId="multi-cat-dd"
                        value={categoryKey}
                        label="Category"
                        onChange={handleCategoryChange}
                        size="small"
                        sx={{ fontWeight: 600, background: "#fff" }}
                      >
                        {METRIC_CATEGORIES.map(cat => (
                          <MenuItem key={cat.key} value={cat.key}>{cat.label}</MenuItem>
                        ))}
                      </Select>
                    </FormControl>
                    <Box sx={{ flex: 1 }} />
                    <Tooltip title="Choose metrics to show">
                      <Button
                        variant="outlined"
                        startIcon={<ViewColumnIcon />}
                        onClick={handleColMenuOpen}
                        sx={{ background: "#fff", fontWeight: 600, borderRadius: 2, minWidth: 140 }}
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
                      <MenuItem dense onClick={() => setShowContexts(v => !v)}>
                        <Checkbox checked={showContexts} />
                        <ListItemText primary="Contexts" />
                      </MenuItem>
                      <Box sx={{ borderTop: "1px solid #eee", my: 0.5 }} />
                      {(METRIC_CATEGORIES.find(cat => cat.key === categoryKey)?.metrics || []).map(metric => (
                        <MenuItem
                          key={metric}
                          dense
                          onClick={() => handleMetricToggle(metric)}
                          disabled={metricsToShow.length === 1 && metricsToShow.includes(metric)}
                        >
                          <Checkbox checked={metricsToShow.includes(metric)} />
                          <ListItemText primary={METRIC_LABELS[metric] || metric} />
                        </MenuItem>
                      ))}
                    </Menu>
                  </Box>
                )}
              </Box>
              {/* --- Table --- */}
              {compareTableMode === "per-question" ? (
                <CompareTable
                  alignedRows={alignedRows}
                  selectedModels={multiModels}
                  metricsToShow={metricsToShow}
                  showContexts={showContexts}
                  metricLabels={METRIC_LABELS}
                />
              ) : (
                <AggregatedCompareTable
                  compareResults={compareResults}
                  selectedModels={multiModels}
                  metricCategories={METRIC_CATEGORIES}
                  metricLabels={METRIC_LABELS}
                />
              )}
            </>
          )
        )}
      </Box>
    </Box>
  );
}
