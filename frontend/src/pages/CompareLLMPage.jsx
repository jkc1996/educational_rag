import React, { useState } from "react";
import {
  Box, Typography, Button, Paper, Menu, Tooltip, FormControl, InputLabel,
  Select, MenuItem, Checkbox, ListItemText, ToggleButton, ToggleButtonGroup
} from "@mui/material";
import { MODELS } from "../constants/models";
import { evaluateModels } from "../utils/api";
import { DEFAULT_METRICS } from "../constants/defaults";
import { METRIC_CATEGORIES, METRIC_LABELS, STATIC_COLS } from "../utils/metricUtils";
import { alignCompareResults, getCompareMetricAverages } from "../utils/compareUtils";
import ModelMultiSelector from "./ModelMultiSelector";
import CompareTable from "./CompareTable";
import AggregatedCompareTable from "./AggregatedCompareTable";
import ViewColumnIcon from "@mui/icons-material/ViewColumn";
import CategoryIcon from "@mui/icons-material/Category";

export default function CompareLLMPage() {
  const [selectedModels, setSelectedModels] = useState([]);
  const [loading, setLoading] = useState(false);
  const [compareResults, setCompareResults] = useState(null);
  const [error, setError] = useState("");
  const [categoryKey, setCategoryKey] = useState(METRIC_CATEGORIES[0].key);

  // Table display mode
  const [tableMode, setTableMode] = useState("per-question"); // or "aggregated"

  // Show columns state
  const [shownMetrics, setShownMetrics] = useState({
    retrieval: [...DEFAULT_METRICS.retrieval],
    nvidia: [...DEFAULT_METRICS.nvidia],
    nlp: [...DEFAULT_METRICS.nlp],
  });
  const [showContexts, setShowContexts] = useState(false);
  const [colMenuAnchor, setColMenuAnchor] = useState(null);

  const handleRunCompare = async () => {
    setLoading(true);
    setError("");
    setCompareResults(null);
    try {
      const res = await evaluateModels({
        modelNames: selectedModels,
        category: categoryKey,
      });
      if (res.status === "success") {
        setCompareResults(res.results);
      } else {
        setError(res.message || "Comparison failed.");
      }
    } catch (err) {
      setError(err.message || "Network error");
    }
    setLoading(false);
  };

  // Prepare aligned table data
  const alignedRows = compareResults
    ? alignCompareResults(compareResults)
    : [];

  // Metrics & Averages
  const metricsToShow = shownMetrics[categoryKey] || [];
  const metricAverages = compareResults
    ? getCompareMetricAverages(compareResults, metricsToShow)
    : {};

  // Category change resets metrics shown if needed
  const handleCategoryChange = (e) => {
    const newCat = e.target.value;
    setCategoryKey(newCat);
    setShownMetrics(prev => ({
      ...prev,
      [newCat]: prev[newCat]?.length ? prev[newCat] : DEFAULT_METRICS[newCat]
    }));
  };

  // "Show Columns" menu
  const handleMetricToggle = (metric) => {
    setShownMetrics(prev => {
      let old = prev[categoryKey] || [];
      if (old.includes(metric)) {
        // Prevent 0 metrics
        if (old.length === 1) return prev;
        return { ...prev, [categoryKey]: old.filter(m => m !== metric) };
      } else {
        return { ...prev, [categoryKey]: [...old, metric] };
      }
    });
  };

  return (
    <Box sx={{ width: "100%", maxWidth: 1380, mx: "auto", pt: 3, px: { xs: 1, sm: 2, md: 3 } }}>
      {/* Model selection bar */}
      <Paper sx={{ p: 3, borderRadius: 3, mb: 2, display: "flex", alignItems: "center", gap: 2 }}>
        <Typography variant="h5" fontWeight={700} sx={{ mr: 2 }}>
          Compare LLMs
        </Typography>
        <ModelMultiSelector
          selected={selectedModels}
          onChange={setSelectedModels}
          options={MODELS}
          sx={{ minWidth: 220 }}
        />
        <Button
          variant="contained"
          onClick={handleRunCompare}
          disabled={loading || selectedModels.length < 2}
          sx={{ ml: 2, minWidth: 160 }}
        >
          {loading ? "Comparing..." : "Run Comparison"}
        </Button>
      </Paper>

      {/* Table mode toggle (radio) */}
      <Box sx={{ display: "flex", alignItems: "center", mb: 2, gap: 2 }}>
        <ToggleButtonGroup
          exclusive
          value={tableMode}
          onChange={(_, val) => val && setTableMode(val)}
          size="small"
        >
          <ToggleButton value="per-question">Per-Question Table</ToggleButton>
          <ToggleButton value="aggregated">Aggregated Metric Table</ToggleButton>
        </ToggleButtonGroup>

        {/* Only show these controls in per-question mode */}
        {tableMode === "per-question" && (
          <>
            <FormControl sx={{ minWidth: 170, ml: 2 }}>
              <InputLabel id="metric-cat-dd">
                <CategoryIcon sx={{ fontSize: 18, mr: 1, verticalAlign: "middle" }} />Category
              </InputLabel>
              <Select
                labelId="metric-cat-dd"
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
            <Tooltip title="Choose columns to show">
              <Button
                variant="outlined"
                startIcon={<ViewColumnIcon />}
                onClick={e => setColMenuAnchor(e.currentTarget)}
                sx={{ background: "#fff", fontWeight: 600, borderRadius: 2, minWidth: 140 }}
              >
                Show Columns
              </Button>
            </Tooltip>
            <Menu
              anchorEl={colMenuAnchor}
              open={!!colMenuAnchor}
              onClose={() => setColMenuAnchor(null)}
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
          </>
        )}
      </Box>

      {error && (
        <Typography color="error" mt={2}>{error}</Typography>
      )}
      {alignedRows.length > 0 && tableMode === "per-question" && (
        <CompareTable
          alignedRows={alignedRows}
          selectedModels={selectedModels}
          metricsToShow={metricsToShow}
          showContexts={showContexts}
          metricLabels={METRIC_LABELS}
        />
      )}
      {alignedRows.length > 0 && tableMode === "aggregated" && (
        <AggregatedCompareTable
          compareResults={compareResults}
          selectedModels={selectedModels}
          categoryKey={categoryKey}
          metricsToShow={metricsToShow}
          metricLabels={METRIC_LABELS}
        />
      )}
      {!alignedRows.length && !loading && (
        <Typography sx={{ mt: 10, textAlign: "center" }}>
          Select 2 or more models to compare!
        </Typography>
      )}
    </Box>
  );
}
