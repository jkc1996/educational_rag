import React, { useMemo, useState, useEffect } from "react";
import {
  Dialog, DialogTitle, DialogContent, IconButton, Box, Tabs, Tab,
  Typography, ToggleButtonGroup, ToggleButton, Chip, Divider,
  FormControl, InputLabel, Select, MenuItem, Stack, Checkbox, ListItemText
} from "@mui/material";
import CloseIcon from "@mui/icons-material/Close";
import {
  ResponsiveContainer,
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar,
  BarChart, Bar, LabelList, XAxis, YAxis, CartesianGrid, Tooltip, Legend
} from "recharts";
import { METRIC_CATEGORIES as BASE_METRIC_CATEGORIES } from "../utils/metricUtils";

// feature flag: hide/show correlation heatmap tab & panel
const ENABLE_CORR_HEATMAP = false; // <- set true to show, false to hide
/* ===================== constants ===================== */
// changed ollama color away from green
const MODEL_COLORS = { groq: "#1976d2", gemini: "#9c27b0", ollama: "#ef6c00" };

// Base categories (we’ll auto-append “Other” for extra metrics in metricLabels)
// const BASE_METRIC_CATEGORIES = [
//   { key: "retrieval", label: "Retrieval", metrics: ["context_precision", "context_recall", "faithfulness"] },
//   { key: "nvidia",    label: "Nvidia",    metrics: ["nv_accuracy", "nv_context_relevance", "nv_response_groundedness"] },
//   { key: "language",  label: "Language",  metrics: ["factual_correctness", "semantic_similarity", "bleu_score", "rouge_score", "string_present",
//   "exact_match"] },
// ];

/* ===================== robust readers ===================== */
const toNum = (v) =>
  typeof v === "number" ? v :
  (typeof v === "string" && v.trim() !== "" && !isNaN(+v)) ? +v : NaN;

const norm = (s) =>
  String(s).toLowerCase().replace(/\(.*?\)/g, "").replace(/[^a-z0-9]+/g, "_").replace(/^_+|_+$/g, "");

const keyMatches = (candidate, targets) => {
  const nk = norm(candidate);
  return targets.some(t => nk === t || nk.includes(t) || t.includes(nk));
};

const aliasesFor = (metric) => {
  const base = norm(metric);
  const extras = new Set([
    base,
    base.replace(/_score$/, ""),
    base.replace(/_mode_.+$/, ""),
    base.replace(/_mode_.+$/, "").replace(/_score$/, ""),
    base.replace(/_f1$/, ""),
  ]);
  // safety for common misspelling
  if (base.includes("groundedness")) extras.add(base.replace("groundedness", "groundness"));
  if (base.includes("groundness")) extras.add(base.replace("groundness", "groundedness"));
  return [...extras];
};

// ⬇️ FIXED: now reads {score} or {value} objects too
const valueFromObject = (obj, metricKey) => {
  if (!obj || typeof obj !== "object") return 0;
  const targets = aliasesFor(metricKey);
  const sources = [obj, obj.metrics || {}, obj.scores || {}];
  for (const src of sources) {
    for (const [k, v] of Object.entries(src)) {
      if (!keyMatches(k, targets)) continue;

      if (typeof v === "object" && v !== null) {
        // common shapes: { score }, { value }
        if (typeof v.score === "number") return v.score;
        if (typeof v.value === "number") return v.value;
        if (typeof v.score === "string" && !isNaN(+v.score)) return +v.score;
        if (typeof v.value === "string" && !isNaN(+v.value)) return +v.value;
      }

      const n = toNum(v);
      if (!Number.isNaN(n)) return n;
    }
  }
  return 0;
};

/* ===================== helpers ===================== */
function averageByMetric(rows, metrics) {
  const sums = {}, counts = {};
  metrics.forEach(m => (sums[m] = 0, counts[m] = 0));
  (rows || []).forEach(r => {
    metrics.forEach(m => {
      const v = valueFromObject(r, m);
      // treat only real numbers; skip truly-missing values (we return 0 only when it's a real 0)
      if (typeof v === "number" && !Number.isNaN(v)) {
        sums[m] += v;
        counts[m] += 1;
      }
    });
  });
  const out = {};
  metrics.forEach(m => out[m] = counts[m] ? sums[m] / counts[m] : 0);
  return out;
}

function pearson(xs, ys) {
  const n = Math.min(xs.length, ys.length);
  if (n < 2) return 0;
  let sx = 0, sy = 0, sxx = 0, syy = 0, sxy = 0;
  for (let i = 0; i < n; i++) {
    const x = xs[i], y = ys[i];
    sx += x; sy += y; sxx += x * x; syy += y * y; sxy += x * y;
  }
  const cov = sxy / n - (sx / n) * (sy / n);
  const vx = sxx / n - (sx / n) ** 2;
  const vy = syy / n - (sy / n) ** 2;
  const denom = Math.sqrt(Math.max(vx, 0)) * Math.sqrt(Math.max(vy, 0));
  return denom === 0 ? 0 : cov / denom;
}

// max across selected models & metrics (for ABS scaling)
function computeMax(rowsByModel, models, metrics) {
  let max = 0;
  (models || []).forEach(m => {
    (rowsByModel[m] || []).forEach(r => {
      (metrics || []).forEach(k => {
        const v = valueFromObject(r, k);
        if (typeof v === "number" && !Number.isNaN(v)) {
          if (v > max) max = v;
        }
      });
    });
  });
  return max || 1; // avoid zero domain
}

/* ===================== main component ===================== */
export default function MetricsInsightDialog({
  open,
  onClose,
  mode,                 // 'single' | 'compare'
  metricLabels,         // map key->nice label (may include extra metrics; we'll include them)
  singleData,           // array (single)
  rawCompare,           // { modelName: rows[] } (compare)
  selectedModels,       // string[]
  onQuestionClick,
}) {
  /* -------- tabs -------- */
  const BASE_TABS = [
  { value: 0, label: "AVERAGES (GROUPED BARS)" },
  { value: 1, label: mode === "single" ? "INDIVIDUAL PERFORMANCE" : "COMPARE PERFORMANCE" },
  // NOTE: correlation tab (value: 2) is conditionally added below
  { value: 3, label: "PER-QUESTION DRILLDOWN" },
  ];

  const TABS = ENABLE_CORR_HEATMAP
    ? [
        { value: 0, label: "AVERAGES (GROUPED BARS)" },
        { value: 1, label: mode === "single" ? "INDIVIDUAL PERFORMANCE" : "COMPARE PERFORMANCE" },
        { value: 2, label: "METRIC CORRELATION" },
        { value: 3, label: "PER-QUESTION DRILLDOWN" },
      ]
    : BASE_TABS;
  const [tab, setTab] = useState(0);

  // global scale toggle (% vs ABS) — applies to bars, radar, and drilldown
  const [scaleMode, setScaleMode] = useState("pct");
  const isPct = scaleMode === "pct";
  const fmtAxis = (v) => isPct ? `${Math.round(v * 100)}%` : (typeof v === "number" ? v.toFixed(2) : v);
  const fmtLabel = (v) => isPct ? `${(v * 100).toFixed(1)}%` : (typeof v === "number" ? v.toFixed(3) : v);

  /* dynamic categories (auto-add “Other” for metrics not in base) */
  const categories = useMemo(() => {
    const known = new Set(BASE_METRIC_CATEGORIES.flatMap(c => c.metrics));
    const extra = Object.keys(metricLabels || {}).filter(k => !known.has(k));
    const out = BASE_METRIC_CATEGORIES.map(c => ({ ...c, metrics: [...c.metrics] }));
    if (extra.length) out.push({ key: "other", label: "Other", metrics: extra });
    return out;
  }, [metricLabels]);

  const ALL_METRICS = useMemo(
    () => categories.flatMap(c => c.metrics),
    [categories]
  );

  /* metric selection for averages bar chart */
  const getDefaultSelection = () => categories.map(c => c.metrics[0]).filter(Boolean);
  const [selectedMetrics, setSelectedMetrics] = useState([]);

  useEffect(() => {
    if (selectedMetrics.length === 0 && categories.length) {
      setSelectedMetrics(getDefaultSelection());
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [categories]);

  const allSelected = selectedMetrics.length === ALL_METRICS.length;

  const toggleAllMetrics = () => {
    if (allSelected) setSelectedMetrics(getDefaultSelection());
    else setSelectedMetrics([...ALL_METRICS]);
  };
  const toggleCategory = (cat) => {
    const setSel = new Set(selectedMetrics);
    const allInCatSelected = cat.metrics.every(m => setSel.has(m));
    if (allInCatSelected) cat.metrics.forEach(m => setSel.delete(m));
    else cat.metrics.forEach(m => setSel.add(m));
    setSelectedMetrics(Array.from(setSel));
  };
  const toggleMetric = (m) => {
    const setSel = new Set(selectedMetrics);
    if (setSel.has(m)) setSel.delete(m); else setSel.add(m);
    setSelectedMetrics(Array.from(setSel));
  };

  /* ---- separate metric selection for DRILLDOWN (same UX) ---- */
  const [selectedDrillMetrics, setSelectedDrillMetrics] = useState([]);
  useEffect(() => {
    if (selectedDrillMetrics.length === 0 && categories.length) {
      setSelectedDrillMetrics(getDefaultSelection());
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [categories]);
  const allDrillSelected = selectedDrillMetrics.length === ALL_METRICS.length;
  const toggleAllDrill = () => {
    if (allDrillSelected) setSelectedDrillMetrics(getDefaultSelection());
    else setSelectedDrillMetrics([...ALL_METRICS]);
  };
  const toggleDrillCategory = (cat) => {
    const setSel = new Set(selectedDrillMetrics);
    const allInCatSelected = cat.metrics.every(m => setSel.has(m));
    if (allInCatSelected) cat.metrics.forEach(m => setSel.delete(m));
    else cat.metrics.forEach(m => setSel.add(m));
    setSelectedDrillMetrics(Array.from(setSel));
  };
  const toggleDrillMetric = (m) => {
    const setSel = new Set(selectedDrillMetrics);
    if (setSel.has(m)) setSel.delete(m); else setSel.add(m);
    setSelectedDrillMetrics(Array.from(setSel));
  };

  /* state for correlation heatmap model picker */
  const [activeModel, setActiveModel] = useState(selectedModels?.[0] || "");
  // if correlation is disabled and current tab is 2, bump back to 0
  useEffect(() => {
    if (!ENABLE_CORR_HEATMAP && tab === 2) setTab(0);
  }, [tab]);
  useEffect(() => {
    if (selectedModels?.length && !selectedModels.includes(activeModel)) {
      setActiveModel(selectedModels[0]);
    }
  }, [selectedModels, activeModel]);

  /* unify access to rows by model */
  const rowsByModel = useMemo(() => {
    if (mode === "single") {
      const m = selectedModels?.[0];
      return { [m]: singleData || [] };
    }
    return rawCompare || {};
  }, [mode, singleData, rawCompare, selectedModels]);

  /* ---------- grouped bar data (single + compare) ---------- */
  const groupedBarData = useMemo(() => {
    if (!selectedModels?.length) return [];
    const metrics = selectedMetrics;

    if (mode === "single") {
      const m = selectedModels[0];
      const avg = averageByMetric(rowsByModel[m] || [], metrics);
      return metrics.map(k => ({
        metric: metricLabels?.[k] || k,
        value: +(avg[k] ?? 0).toFixed(3),
      }));
    }

    return metrics.map(k => {
      const rec = { metric: metricLabels?.[k] || k };
      selectedModels.forEach(m => {
        const avg = averageByMetric(rowsByModel[m] || [], [k]);
        rec[m] = +((avg[k] ?? 0)).toFixed(3);
      });
      return rec;
    });
  }, [mode, rowsByModel, selectedModels, metricLabels, selectedMetrics]);

  // max for ABS scaling on bars
  const barsAbsMax = useMemo(
    () => computeMax(rowsByModel, selectedModels, selectedMetrics),
    [rowsByModel, selectedModels, selectedMetrics]
  );

  /* ---- dynamic bar width by number of groups ---- */
  const groupCount = groupedBarData.length || 1;
  const barSize = useMemo(() => {
    if (groupCount <= 2) return 60; // wider for 1–2 metrics
    if (groupCount <= 4) return 60; // medium for 3–4 metrics
    return 50;                      // smaller when many metrics
  }, [groupCount]);

  /* ---------- RADAR: category dropdown + one radar per model (side-by-side) ---------- */
  const [radarCategoryKey, setRadarCategoryKey] = useState(
    () => (categories[0]?.key ?? "")
  );
  useEffect(() => {
    if (!radarCategoryKey && categories[0]?.key) setRadarCategoryKey(categories[0].key);
  }, [categories, radarCategoryKey]);

  const activeCategory = useMemo(() => {
    return categories.find(c => c.key === radarCategoryKey) || categories[0] || { metrics: [], label: "" };
  }, [categories, radarCategoryKey]);

  // Per-model radar data: { modelName: [{subject, value}, ...] }
  const radarPerModelData = useMemo(() => {
    const out = {};
    if (!activeCategory?.metrics?.length) return out;
    (selectedModels || []).forEach((m) => {
      out[m] = activeCategory.metrics.map((k) => {
        const avg = averageByMetric(rowsByModel[m] || [], [k]);
        return {
          subject: metricLabels?.[k] || k,
          value: +((avg[k] ?? 0)).toFixed(3),
        };
      });
    });
    return out;
  }, [activeCategory, metricLabels, rowsByModel, selectedModels]);

  // ABS max for the selected category only
  const radarCatAbsMax = useMemo(
    () => computeMax(rowsByModel, selectedModels, activeCategory.metrics),
    [rowsByModel, selectedModels, activeCategory]
  );

  /* ---------- correlation matrix for active model (ALL metrics) ---------- */
  const corrMatrix = useMemo(() => {
    const rows = rowsByModel[activeModel] || [];
    const vectors = {};
    ALL_METRICS.forEach(k => vectors[k] = rows.map(r => valueFromObject(r, k)));
    const mat = ALL_METRICS.map((rKey) =>
      ALL_METRICS.map((cKey) => +pearson(vectors[rKey], vectors[cKey]).toFixed(3))
    );
    return mat; // square matrix
  }, [rowsByModel, activeModel, ALL_METRICS]);

  /* ---------- per-question matrix (rows = models, cols = selected metrics) ---------- */
  const perQuestionMatrix = useMemo(() => {
    const qMap = new Map(); // id -> { id, question, cells: { [metric]: { [model]: score } } }
    (selectedModels || []).forEach((model) => {
      const rows = rowsByModel[model] || [];
      rows.forEach((r, idx) => {
        const qid = r.id ?? idx + 1;
        if (!qMap.has(qid)) {
          qMap.set(qid, {
            id: qid,
            question: r.question || r.user_input || `Q${qid}`,
            cells: {}, // metric -> model -> value
          });
        }
        const qEntry = qMap.get(qid);
        selectedDrillMetrics.forEach((mk) => {
          if (!qEntry.cells[mk]) qEntry.cells[mk] = {};
          qEntry.cells[mk][model] = +valueFromObject(r, mk).toFixed(3);
        });
      });
    });

    const arr = Array.from(qMap.values());
    arr.sort((a, b) => {
      const na = Number(a.id), nb = Number(b.id);
      if (!Number.isNaN(na) && !Number.isNaN(nb)) return na - nb;
      return String(a.id).localeCompare(String(b.id));
    });
    return arr;
  }, [rowsByModel, selectedModels, selectedDrillMetrics]);

  const drillAbsMax = useMemo(
    () => computeMax(rowsByModel, selectedModels, selectedDrillMetrics),
    [rowsByModel, selectedModels, selectedDrillMetrics]
  );

  /* ===== cell renderer for the per-question table ===== */
  const ValueCell = ({ value = 0, color }) => {
    const denom = isPct ? 1 : drillAbsMax || 1;
    const pct = Math.max(0, Math.min(1, value / denom));
    return (
      <Box sx={{ position: "relative", height: 22, minWidth: 72 }}>
        <Box sx={{ position: "absolute", inset: 3, background: "#eceff1", borderRadius: 8 }} />
        <Box sx={{
          position: "absolute", left: 3, top: 3, bottom: 3,
          width: `${pct * 100}%`, background: color, borderRadius: 8,
          transition: "width 240ms ease"
        }} />
        <Box sx={{
          position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center",
          fontSize: 12, fontWeight: 600, color: pct > 0.6 ? "#fff" : "#455a64"
        }}>
          {fmtLabel(value)}
        </Box>
      </Box>
    );
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="xl" fullWidth>
      <DialogTitle sx={{ pr: 7 }}>
        Metrics Insight
        <IconButton onClick={onClose} sx={{ position: "absolute", right: 12, top: 8 }}>
          <CloseIcon />
        </IconButton>
      </DialogTitle>

      <DialogContent dividers>
        {/* Tabs */}
        <Box sx={{ borderBottom: 1, borderColor: "divider", mb: 1 }}>
          <Tabs value={tab} onChange={(_, v) => setTab(v)} variant="scrollable" allowScrollButtonsMobile>
            {TABS.map(t => <Tab key={t.value} label={t.label} value={t.value} />)}
          </Tabs>
        </Box>

        {/* top-right global scale toggle */}
        {tab !== 2 && (
          <Box sx={{ display: "flex", justifyContent: "flex-end", mb: 1 }}>
            <Stack direction="row" spacing={1} alignItems="center">
              <Typography variant="caption" color="text.secondary">Scale</Typography>
              <ToggleButtonGroup
                exclusive size="small" value={scaleMode}
                onChange={(_, v) => v && setScaleMode(v)}
              >
                <ToggleButton value="pct">%</ToggleButton>
                <ToggleButton value="abs">ABS</ToggleButton>
              </ToggleButtonGroup>
            </Stack>
          </Box>
        )}

        {/* ===== Tab 0: Averages (Grouped Bars) ===== */}
        {tab === 0 && (
          <Box sx={{ p: 1 }}>
            <Stack direction="row" spacing={2} sx={{ mb: 1, alignItems: "center" }}>
              <FormControl size="small" sx={{ minWidth: 320 }}>
                <InputLabel>Metrics</InputLabel>
                <Select
                  multiple
                  value={selectedMetrics}
                  label="Metrics"
                  onChange={() => {}}
                  renderValue={(sel) => {
                    if (sel.length === 0) return "None selected";
                    if (sel.length === ALL_METRICS.length) return "All metrics";
                    return `${sel.length} selected`;
                  }}
                  MenuProps={{ PaperProps: { style: { maxHeight: 420 } } }}
                >
                  <MenuItem onClick={(e) => { e.stopPropagation(); toggleAllMetrics(); }}>
                    <Checkbox checked={allSelected} />
                    <ListItemText primary="All metrics" />
                  </MenuItem>
                  {categories.map(cat => {
                    const selCount = cat.metrics.filter(m => selectedMetrics.includes(m)).length;
                    const allCat = selCount === cat.metrics.length && cat.metrics.length > 0;
                    const someCat = selCount > 0 && !allCat;
                    return (
                      <Box key={`cat-${cat.key}`}>
                        <MenuItem
                          onClick={(e) => { e.stopPropagation(); toggleCategory(cat); }}
                          sx={{ fontWeight: 700, pt: 1, pb: 0.5 }}
                        >
                          <Checkbox checked={allCat} indeterminate={someCat} />
                          <ListItemText primary={cat.label} />
                        </MenuItem>
                        {cat.metrics.map(m => (
                          <MenuItem
                            key={m}
                            sx={{ pl: 6 }}
                            onClick={(e) => { e.stopPropagation(); toggleMetric(m); }}
                          >
                            <Checkbox checked={selectedMetrics.includes(m)} />
                            <ListItemText primary={metricLabels?.[m] || m} />
                          </MenuItem>
                        ))}
                      </Box>
                    );
                  })}
                </Select>
              </FormControl>

              <Typography variant="body2" color="text.secondary">
                Average of each selected metric across all questions.
              </Typography>
            </Stack>

            <Box sx={{ height: 560, border: "1px solid #e0e0e0", borderRadius: 2, p: 1.5, background: "#fff" }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={groupedBarData}
                  barCategoryGap="30%"
                  barGap={10}
                  margin={{ top: 56, right: 32, left: 16, bottom: 96 }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis
                    dataKey="metric"
                    angle={-24}
                    textAnchor="end"
                    interval={0}
                    tick={{ fontSize: 14, fontWeight: 600 }}
                    tickMargin={18}
                  />
                  <YAxis
                    domain={isPct ? [0, 1] : [0, barsAbsMax]}
                    tickFormatter={fmtAxis}
                    tick={{ fontSize: 14, fontWeight: 600 }}
                  />
                  <Tooltip
                    formatter={(v) => fmtLabel(v)}
                    labelStyle={{ fontWeight: 700, fontSize: 14 }}
                    itemStyle={{ fontSize: 14, fontWeight: 600 }}
                  />
                  <Legend
                    verticalAlign="top"
                    align="right"
                    iconSize={16}
                    wrapperStyle={{ fontSize: 14, fontWeight: 600, paddingBottom: 10, lineHeight: "22px" }}
                    formatter={(value) => String(value).toUpperCase()}
                  />

                  {mode === "single" ? (
                    <Bar
                      dataKey="value"
                      fill={MODEL_COLORS[selectedModels?.[0]] || "#1976d2"}
                      radius={[6, 6, 0, 0]}
                      barSize={barSize}
                    >
                      <LabelList
                        dataKey="value"
                        position="top"
                        formatter={(v) => fmtLabel(v)}
                        style={{ fontSize: 14, fontWeight: 700 }}
                      />
                    </Bar>
                  ) : (
                    (selectedModels || []).map((m) => (
                      <Bar
                        key={m}
                        dataKey={m}
                        fill={MODEL_COLORS[m]}
                        radius={[6, 6, 0, 0]}
                        barSize={barSize}
                      >
                        <LabelList
                          dataKey={m}
                          position="top"
                          formatter={(v) => fmtLabel(v)}
                          style={{ fontSize: 14, fontWeight: 700 }}
                        />
                      </Bar>
                    ))
                  )}
                </BarChart>
              </ResponsiveContainer>
            </Box>
          </Box>
        )}

        {/* ===== Tab 1: Individual performance (radar, category dropdown; one radar per model) ===== */}
        {tab === 1 && (
          <Box>
            <Stack direction="row" spacing={2} sx={{ mb: 2, alignItems: "center", flexWrap: "wrap" }}>
              <FormControl size="small" sx={{ minWidth: 220 }}>
                <InputLabel>Category</InputLabel>
                <Select
                  value={radarCategoryKey}
                  label="Category"
                  onChange={(e) => setRadarCategoryKey(e.target.value)}
                >
                  {categories.map((c) => (
                    <MenuItem key={c.key} value={c.key}>{c.label}</MenuItem>
                  ))}
                </Select>
              </FormControl>

              <Typography variant="caption" color="text.secondary">
                Showing one radar per model for <strong>{activeCategory?.label}</strong>.
              </Typography>
            </Stack>

            <Box sx={{ display: "flex", flexWrap: "wrap", gap: 2, justifyContent: "center" }}>
              {(selectedModels || []).map((m) => (
                <Box key={m} sx={{ width: 360, height: 360, p: 1 }}>
                  <Stack direction="row" justifyContent="center" sx={{ mb: 1 }}>
                    <Chip
                      size="small"
                      label={m.toUpperCase()}
                      sx={{ background: MODEL_COLORS[m], color: "#fff", fontWeight: 700 }}
                    />
                  </Stack>
                  <ResponsiveContainer>
                    <RadarChart
                      cx="50%"
                      cy="50%"
                      outerRadius="78%"
                      data={radarPerModelData[m] || []}
                      margin={{ top: 10, right: 18, bottom: 10, left: 18 }}
                    >
                      <PolarGrid />
                      <PolarAngleAxis dataKey="subject" tick={{ fontSize: 12 }} />
                      <PolarRadiusAxis
                        angle={30}
                        domain={isPct ? [0, 1] : [0, radarCatAbsMax || 1]}
                        tickFormatter={fmtAxis}
                      />
                      <Radar
                        name={m.toUpperCase()}
                        dataKey="value"
                        stroke={MODEL_COLORS[m]}
                        fill={MODEL_COLORS[m]}
                        fillOpacity={0.36}
                      />
                      <Tooltip formatter={(v) => fmtLabel(v)} />
                    </RadarChart>
                  </ResponsiveContainer>
                </Box>
              ))}
            </Box>
          </Box>
        )}

        {/* ===== Tab 2: correlation heatmap (ALL metrics) ===== */}
        {ENABLE_CORR_HEATMAP && tab === 2 && (
          <Box>
            <ToggleButtonGroup
              exclusive size="small" value={activeModel}
              onChange={(_, v) => v && setActiveModel(v)} sx={{ mb: 2 }}
            >
              {(selectedModels || []).map(m => (
                <ToggleButton key={m} value={m} sx={{ fontWeight: 700 }}>
                  <span style={{ color: MODEL_COLORS[m] }}>{m.toUpperCase()}</span>
                </ToggleButton>
              ))}
            </ToggleButtonGroup>

            <Typography variant="body2" sx={{ mb: 1 }}>
              Correlation across questions for <Chip size="small" label={activeModel.toUpperCase()} sx={{ ml: 0.5, background: MODEL_COLORS[activeModel], color: "#fff" }} />
            </Typography>

            <Box sx={{ overflow: "auto", border: "1px solid #eee", borderRadius: 2, p: 1 }}>
              <table style={{ borderCollapse: "collapse" }}>
                <thead>
                  <tr>
                    <th style={{ width: 160 }}></th>
                    {ALL_METRICS.map((m) => (
                      <th key={m} style={{ padding: "6px 8px", fontSize: 12, textAlign: "center" }}>
                        {metricLabels?.[m] || m}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {ALL_METRICS.map((rowKey, r) => (
                    <tr key={rowKey}>
                      <td style={{ padding: "6px 8px", fontSize: 12, position: "sticky", left: 0, background: "#fff" }}>
                        {metricLabels?.[rowKey] || rowKey}
                      </td>
                      {ALL_METRICS.map((colKey, c) => {
                        const v = corrMatrix[r][c] || 0;
                        const hue = v >= 0 ? 120 : 0;
                        const sat = Math.round(Math.abs(v) * 70);
                        const light = 90 - Math.round(Math.abs(v) * 40);
                        return (
                          <td key={colKey}
                            title={`${(metricLabels?.[rowKey]||rowKey)} vs ${(metricLabels?.[colKey]||colKey)}: ${v.toFixed(3)}`}
                            style={{
                              width: 44, height: 28, textAlign: "center",
                              background: `hsl(${hue} ${sat}% ${light}%)`,
                              border: "1px solid #eee", fontSize: 12
                            }}
                          >
                            {v.toFixed(2)}
                          </td>
                        );
                      })}
                    </tr>
                  ))}
                </tbody>
              </table>
            </Box>
          </Box>
        )}

        {/* ===== Tab 3: per-question drilldown (question-first matrix) ===== */}
        {tab === 3 && (
          <Box>
            <Stack direction="row" spacing={2} sx={{ mb: 2, alignItems: "center", flexWrap: "wrap" }}>
              {/* Hierarchical metric selector (shared UX) */}
              <FormControl size="small" sx={{ minWidth: 320 }}>
                <InputLabel>Metrics</InputLabel>
                <Select
                  multiple
                  value={selectedDrillMetrics}
                  label="Metrics"
                  onChange={() => {}}
                  renderValue={(sel) => {
                    if (sel.length === 0) return "None selected";
                    if (sel.length === ALL_METRICS.length) return "All metrics";
                    return `${sel.length} selected`;
                  }}
                  MenuProps={{ PaperProps: { style: { maxHeight: 420 } } }}
                >
                  <MenuItem onClick={(e) => { e.stopPropagation(); toggleAllDrill(); }}>
                    <Checkbox checked={allDrillSelected} />
                    <ListItemText primary="All metrics" />
                  </MenuItem>

                  {categories.map(cat => {
                    const selCount = cat.metrics.filter(m => selectedDrillMetrics.includes(m)).length;
                    const allCat = selCount === cat.metrics.length && cat.metrics.length > 0;
                    const someCat = selCount > 0 && !allCat;
                    return (
                      <Box key={`drill-cat-${cat.key}`}>
                        <MenuItem
                          onClick={(e) => { e.stopPropagation(); toggleDrillCategory(cat); }}
                          sx={{ fontWeight: 700, pt: 1, pb: 0.5 }}
                        >
                          <Checkbox checked={allCat} indeterminate={someCat} />
                          <ListItemText primary={cat.label} />
                        </MenuItem>
                        {cat.metrics.map(m => (
                          <MenuItem
                            key={m}
                            sx={{ pl: 6 }}
                            onClick={(e) => { e.stopPropagation(); toggleDrillMetric(m); }}
                          >
                            <Checkbox checked={selectedDrillMetrics.includes(m)} />
                            <ListItemText primary={metricLabels?.[m] || m} />
                          </MenuItem>
                        ))}
                      </Box>
                    );
                  })}
                </Select>
              </FormControl>

              {/* Legend */}
              <Stack direction="row" spacing={1}>
                {(selectedModels || []).map(m => (
                  <Chip key={m} size="small" label={m.toUpperCase()} sx={{ background: MODEL_COLORS[m], color: "#fff" }} />
                ))}
              </Stack>
            </Stack>

            <Divider sx={{ mb: 2 }} />

            {selectedDrillMetrics.length === 0 ? (
              <Typography variant="body2" color="text.secondary">
                Select one or more metrics to see the per-question drilldown.
              </Typography>
            ) : (
              <Box sx={{ display: "flex", flexDirection: "column", gap: 2, maxHeight: 520, overflow: "auto", pr: 1 }}>
                {perQuestionMatrix.map(q => (
                  <Box key={q.id} sx={{ border: '1px solid #eee', borderRadius: 2, p: 1.25 }}>
                    <Typography
                      variant="body2"
                      sx={{ mb: 1, fontWeight: 600 }}
                      noWrap
                      title={q.question}
                      onClick={() => onQuestionClick && onQuestionClick(q.id)}
                    >
                      Q{q.id}: {q.question}
                    </Typography>

                    <Box sx={{ overflowX: "auto" }}>
                      <table style={{ borderCollapse: "collapse", width: "100%" }}>
                        <thead>
                          <tr>
                            <th style={{ width: 100, textAlign: "left", padding: "6px 8px", fontSize: 12 }}></th>
                            {selectedDrillMetrics.map(mk => (
                              <th key={mk} style={{ minWidth: 140, textAlign: "center", padding: "6px 8px", fontSize: 12 }}>
                                {metricLabels?.[mk] || mk}
                              </th>
                            ))}
                          </tr>
                        </thead>
                        <tbody>
                          {(selectedModels || []).map(model => (
                            <tr key={model}>
                              <td style={{ padding: "6px 8px", fontSize: 12, fontWeight: 700, color: MODEL_COLORS[model], whiteSpace: "nowrap" }}>
                                {model.toUpperCase()}
                              </td>
                              {selectedDrillMetrics.map(mk => {
                                const val = q.cells?.[mk]?.[model] ?? 0;
                                return (
                                  <td key={mk} style={{ padding: "4px 6px" }}>
                                    <ValueCell value={val} color={ MODEL_COLORS[model] } />
                                  </td>
                                );
                              })}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </Box>
                  </Box>
                ))}
              </Box>
            )}
          </Box>
        )}
      </DialogContent>
    </Dialog>
  );
}
