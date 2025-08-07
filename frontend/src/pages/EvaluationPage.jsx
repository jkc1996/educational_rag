import React, { useState } from "react";
import {
  Box, Paper, Typography, Button, Tooltip, ToggleButtonGroup, ToggleButton,
  Menu, FormControl, InputLabel,
  Select, MenuItem, Checkbox, ListItemText // <--- add these!
} from "@mui/material";
import { METRIC_CATEGORIES, STATIC_COLS, getMetricAverages, METRIC_LABELS } from "../utils/metricUtils";
import MetricTable from "./MetricTable";
import ModelSelector from "./ModelSelector";
import MetricChart from "./MetricChart";
import ViewColumnIcon from "@mui/icons-material/ViewColumn";
import CategoryIcon from "@mui/icons-material/Category";
import { DEFAULT_METRICS } from "../constants/defaults";
import { evaluateModels } from "../utils/api";

export default function EvaluationPage() {
  const [evalMode, setEvalMode] = useState("single");
  const [model, setModel] = useState("groq");
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState("");
  const [categoryKey, setCategoryKey] = useState(METRIC_CATEGORIES[0].key);
  const [chartOpen, setChartOpen] = useState(false);
  const [expandedCell, setExpandedCell] = useState(null);
  const [shownMetrics, setShownMetrics] = useState({
    retrieval: DEFAULT_METRICS.retrieval,
    nvidia: DEFAULT_METRICS.nvidia,
    nlp: DEFAULT_METRICS.nlp,
  });
  const [anchorEl, setAnchorEl] = useState(null);
  const [showContexts, setShowContexts] = useState(false);

  const category = METRIC_CATEGORIES.find(cat => cat.key === categoryKey);
  const categoryMetrics = category.metrics;
  const metricsToShow = shownMetrics[categoryKey] || [];
  const averages = results ? getMetricAverages(results, metricsToShow) : {};

  const handleEvaluate = async () => {
    setLoading(true);
    setResults(null);
    setError("");
    try {
      const data = await evaluateModels({ modelNames: model, category: categoryKey });
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
    <Box sx={{
      width: "100%",
      minHeight: "100vh",
      background: "#f7fafc",
      p: 0,
      m: 0,
      overflow: "auto"
    }}>
      {/* --- Top Card --- */}
      <Box sx={{
        width: "100%",
        maxWidth: 1380,
        mx: "auto",
        mt: 3,
        mb: 1,
        px: { xs: 1, sm: 2, md: 3 },
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
            onChange={(_, val) => val && setEvalMode(val)}
            sx={{ mr: 3 }}
            size="small"
          >
            <ToggleButton value="single" sx={{ px: 2 }}>Single LLM</ToggleButton>
            <ToggleButton value="compare" sx={{ px: 2 }} disabled>
              Compare LLMs (Coming Soon)
            </ToggleButton>
          </ToggleButtonGroup>
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
        </Paper>
      </Box>

      {/* --- Main Content --- */}
      <Box sx={{
        width: "100%",
        maxWidth: 1380,
        mx: "auto",
        px: { xs: 1, sm: 2, md: 3 },
        pt: 2,
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
            {/* --- Controls Above Table --- */}
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
                    minWidth: 140
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
                {STATIC_COLS.map(col => (
                  <MenuItem key={col.key} dense disabled>
                    <Checkbox checked disabled />
                    <ListItemText primary={col.label} />
                  </MenuItem>
                ))}
                <MenuItem
                  dense
                  onClick={() => setShowContexts(val => !val)}
                  sx={{ ml: 0 }}
                >
                  <Checkbox checked={showContexts} />
                  <ListItemText primary="Contexts" />
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
        )}
      </Box>
    </Box>
  );
}
