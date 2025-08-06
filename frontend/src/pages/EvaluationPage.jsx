import React, { useRef, useEffect, useState } from "react";

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
import Chip from "@mui/material/Chip";

const MODELS = [
  { value: "groq", label: "Groq" },
  { value: "gemini", label: "Gemini" },
  { value: "ollama", label: "Ollama" },
];

const DEFAULT_METRICS = {
  retrieval: ["context_precision", "context_recall"],
  nvidia: ["nv_accuracy", "nv_context_relevance"],
  nlp: ["factual_correctness(mode=f1)", "semantic_similarity"],
};

function TruncatedCell({ value, isExpanded, onToggle, maxLines = 3 }) {
  const boxRef = useRef(null);
  const [isOverflowing, setIsOverflowing] = useState(false);

  useEffect(() => {
    if (boxRef.current && !isExpanded) {
      // Only check for overflow when NOT expanded
      setIsOverflowing(boxRef.current.scrollHeight > boxRef.current.clientHeight + 2);
    }
    // When expanded, force overflow "true" so the icon always shows
  }, [value, isExpanded, maxLines]);

  const shouldShowExpand =
    (isOverflowing && !isExpanded) || isExpanded;

  return (
    <Box
      ref={boxRef}
      sx={{
        position: "relative",
        overflow: isExpanded ? "visible" : "hidden",
        display: "-webkit-box",
        WebkitLineClamp: isExpanded ? "unset" : maxLines,
        WebkitBoxOrient: "vertical",
        whiteSpace: isExpanded ? "pre-line" : "normal",
        textOverflow: "ellipsis",
        cursor: shouldShowExpand ? "pointer" : "default",
        pr: shouldShowExpand ? 3 : 0,
        background: isExpanded ? "#f9fafb" : "inherit",
        transition: "all 0.2s",
        minHeight: "1em",
      }}
      onClick={shouldShowExpand ? onToggle : undefined}
    >
      {value}
      {/* Always show expand/collapse icon if possible */}
      {shouldShowExpand && (
        <IconButton
          size="small"
          onClick={e => { e.stopPropagation(); onToggle(); }}
          sx={{
            position: "absolute",
            right: 0,
            top: 2,
            bgcolor: "#fff",
            p: "2px",
            zIndex: 2,
          }}
          aria-label={isExpanded ? "Collapse" : "Expand"}
        >
          <ExpandMoreIcon
            sx={{
              fontSize: 18,
              transform: isExpanded ? "rotate(180deg)" : "rotate(0deg)",
              transition: "0.2s"
            }}
          />
        </IconButton>
      )}
      {/* Only show shadow if truncated and not expanded */}
      {isOverflowing && !isExpanded && (
        <Box
          sx={{
            position: "absolute",
            left: 0,
            right: 0,
            bottom: 0,
            height: "1em",
            background: "linear-gradient(180deg,transparent, #fff 100%)",
            pointerEvents: "none"
          }}
        />
      )}
    </Box>
  );
}

function EvaluationPage() {
  const [evalMode, setEvalMode] = useState("single");
  const [model, setModel] = useState("groq");
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState("");
  const [categoryKey, setCategoryKey] = useState(METRIC_CATEGORIES[0].key);
  const [chartOpen, setChartOpen] = useState(false);
  const [expandedCell, setExpandedCell] = useState(null); // { rowId, colKey }
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
        maxWidth: 1680,
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
      </Box>

      {/* --- Main Content --- */}
      <Box sx={{
        width: "100%",
        maxWidth: 1680,
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

            {/* --- Table in a perfectly rounded box, horizontally scrollable --- */}
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
                <Table size="small" stickyHeader sx={{
                  minWidth: 1200 + metricsToShow.length * 135,
                  background: "#fff",
                  borderRadius: "inherit"
                }}>
                  <TableHead>
                    <TableRow>
                      {STATIC_COLS.map(col => (
                        <TableCell key={col.key} sx={{
                          fontWeight: 700,
                          background: "#f3f4f6",
                          minWidth:
                            col.key === "id" ? 15 :
                            col.key === "question" ? 160 :
                            col.key === "answer" ? 180 :
                            col.key === "ground_truth" ? 180 :
                            col.key === "contexts" ? 180 :
                            60,
                          maxWidth:
                            col.key === "id" ? 25 :
                            col.key === "question" ? 180 :
                            col.key === "answer" ? 200 :
                            col.key === "ground_truth" ? 200 :
                            col.key === "contexts" ? 200 :
                            undefined,
                          whiteSpace: "normal",
                          wordBreak: "break-word",
                          fontSize: 14,
                          verticalAlign: "top",
                          position: "relative"
                        }}>
                          {col.label}
                        </TableCell>
                      ))}
                      {showContexts && (
                        <TableCell key="contexts"
                          sx={{
                            fontWeight: 700,
                            background: "#f3f4f6",
                            minWidth: 180,
                            maxWidth: 200,
                            whiteSpace: "normal",
                            wordBreak: "break-word",
                            fontSize: 14,
                            verticalAlign: "top",
                            position: "relative"
                          }}
                        >
                          Contexts
                        </TableCell>
                      )}
                      {metricsToShow.map(metric => (
                        <TableCell key={metric} sx={{
                          textAlign: "center",
                          fontWeight: 700,
                          background: "#f3f4f6",
                          minWidth: 80,
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
                        {STATIC_COLS.map(col => {
                          // Only truncate these columns
                          const shouldTruncate = ["question", "answer", "ground_truth", "contexts"].includes(col.key);
                          const val = Array.isArray(row[col.key])
                            ? row[col.key].join(" || ")
                            : row[col.key];

                          // Identify this cell uniquely
                          const cellId = `${row.id || idx}-${col.key}`;
                          const isExpanded = expandedCell && expandedCell.cellId === cellId;

                          return (
                            <TableCell
                              key={col.key}
                              sx={{
                                minWidth:
                                col.key === "id" ? 15 :
                                col.key === "question" ? 160 :
                                col.key === "answer" ? 180 :
                                col.key === "ground_truth" ? 180 :
                                col.key === "contexts" ? 180 :
                                60,
                              maxWidth:
                                col.key === "id" ? 25 :
                                col.key === "question" ? 180 :
                                col.key === "answer" ? 200 :
                                col.key === "ground_truth" ? 200 :
                                col.key === "contexts" ? 200 :
                                undefined,
                                whiteSpace: "normal",
                                wordBreak: "break-word",
                                fontSize: 14,
                                verticalAlign: "top",
                                position: "relative"
                              }}
                            >
                              {shouldTruncate ? (
                                <TruncatedCell
                                  value={val}
                                  isExpanded={isExpanded}
                                  onToggle={() => setExpandedCell(isExpanded ? null : { cellId })}
                                  maxLines={3}
                                />
                              ) : val}
                            </TableCell>
                          );
                        })}
                        {showContexts && (
                          <TableCell
                            key="contexts"
                            sx={{
                              minWidth: 180,
                              maxWidth: 200,
                              whiteSpace: "normal",
                              wordBreak: "break-word",
                              fontSize: 14,
                              verticalAlign: "top",
                              position: "relative"
                            }}
                          >
                            <TruncatedCell
                              value={Array.isArray(row["contexts"]) ? row["contexts"].join(" || ") : row["contexts"]}
                              isExpanded={expandedCell && expandedCell.cellId === `${row.id || idx}-contexts`}
                              onToggle={() =>
                                setExpandedCell(
                                  expandedCell && expandedCell.cellId === `${row.id || idx}-contexts`
                                    ? null
                                    : { cellId: `${row.id || idx}-contexts` }
                                )
                              }
                              maxLines={3}
                            />
                          </TableCell>
                        )}
                        {metricsToShow.map(metric => {
                          let val = row[metric];
                          if (typeof val === "object" && val !== null && typeof val.score === "number") {
                            val = val.score;
                          }
                          return (
                            <TableCell
                              key={metric}
                              sx={{
                                fontWeight: 600,
                                textAlign: "center"
                              }}
                            >
                              <Chip
                                label={typeof val === "number" ? val.toFixed(3) : "-"}
                                size="small"
                                sx={{
                                  bgcolor: getMetricColor(val),
                                  color: "#111",
                                  fontWeight: 600,
                                  fontSize: 14,
                                  px: 1,
                                  minWidth: 40,
                                  borderRadius: 1.3,
                                  boxShadow: "0 1px 2px rgba(0,0,0,0.07)",
                                  border: "1px solid #e0e0e0",
                                }}
                                />
                            </TableCell>
                          );
                        })}
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </Box>
            </Paper>
          </>
        )}
      </Box>
    </Box>
  );
}

export default EvaluationPage;
