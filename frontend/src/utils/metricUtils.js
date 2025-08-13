// src/utils/metricUtils.js

export const METRIC_CATEGORIES = [
  {
    key: "retrieval",
    label: "Retrieval Metrics",
    metrics: [
      "context_precision",
      "context_recall",
      "faithfulness"
    ],
  },
  {
    key: "nvidia",
    label: "Nvidia Metrics",
    metrics: [
      "nv_accuracy",
      "nv_context_relevance",
      "nv_response_groundedness",
    ],
  },
  {
    key: "language",
    label: "Language Metrics",
    metrics: [
      "factual_correctness",
      "semantic_similarity",
      "bleu_score",
      "rouge_score",
      "string_present",
      "exact_match",
    ],
  },
];

export const METRIC_LABELS = {
  "context_precision": "Context Precision",
  "context_recall": "Context Recall",
  "faithfulness": "Faithfulness",
  "nv_accuracy": "NV Answer Accuracy",
  "nv_context_relevance": "NV Context Relevance",
  "nv_response_groundedness": "NV Response Groundedness",
  "factual_correctness": "Factual Correctness (F1)",
  "semantic_similarity": "Semantic Similarity",
  "bleu_score": "BLEU Score",
  "rouge_score": "ROUGE Score (F-measure)",
  "string_present": "String Presence",
  "exact_match": "Exact Match",
};

// Which columns to always show
export const STATIC_COLS = [
  { key: "id", label: "Q#" },
  { key: "question", label: "Question" },
  { key: "answer", label: "Answer" },
  { key: "ground_truth", label: "Ground Truth" },
  // { key: "contexts", label: "Contexts" },
];

// Color by value (0-1)
export function getMetricColor(value) {
  if (typeof value !== "number") return "";
  if (value > 0.7) return "#d0f5e0";      // Green-ish
  if (value >= 0.4) return "#fff9c4";     // Yellow
  return "#ffcdd2";                       // Red
}

// Get metric keys for a given category key
export function getMetricsForCategory(categoryKey) {
  const cat = METRIC_CATEGORIES.find(c => c.key === categoryKey);
  return cat ? cat.metrics : [];
}

// src/utils/metricUtils.js

// NEW: robust resolver for "metric" OR "metric(...)" keys and {score}/{value} shapes
export function resolveMetricValue(row, metricKey) {
  if (!row || !metricKey) return null;

  // exact match first
  let v = row[metricKey];
  if (v === undefined) {
    // fallback: find keys like "metricKey(...)" or "metricKey_score" etc.
    const re = new RegExp(`^${metricKey}(\\(|_|$)`, "i");
    const hit = Object.keys(row).find(k => re.test(k));
    if (hit) v = row[hit];
  }

  if (v && typeof v === "object") {
    if (typeof v.score === "number") return v.score;
    if (typeof v.value === "number") return v.value;
    if (typeof v.score === "string" && !isNaN(+v.score)) return +v.score;
    if (typeof v.value === "string" && !isNaN(+v.value)) return +v.value;
  }

  return (typeof v === "number") ? v
       : (typeof v === "string" && !isNaN(+v)) ? +v
       : null;
}

// ⬇️ update existing function to use the resolver
export function getMetricAverages(results, metrics) {
  if (!results || !metrics) return {};
  const avg = {};
  metrics.forEach(metric => {
    const values = (results || [])
      .map(row => resolveMetricValue(row, metric))
      .filter(x => typeof x === "number");
    avg[metric] = values.length
      ? values.reduce((a, b) => a + b, 0) / values.length
      : 0;
  });
  return avg;
}

