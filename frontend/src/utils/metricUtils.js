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
    key: "nlp",
    label: "Language Metrics",
    metrics: [
      "factual_correctness(mode=f1)",
      "semantic_similarity",
      "non_llm_string_similarity",
      "bleu_score",
      "rouge_score(mode=fmeasure)",
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
  "factual_correctness(mode=f1)": "Factual Correctness (F1)",
  "semantic_similarity": "Semantic Similarity",
  "non_llm_string_similarity": "Non-LLM String Similarity",
  "bleu_score": "BLEU Score",
  "rouge_score(mode=fmeasure)": "ROUGE Score (F-measure)",
  "string_present": "String Presence",
  "exact_match": "Exact Match",
};

// Which columns to always show
export const STATIC_COLS = [
  { key: "id", label: "Q#" },
  { key: "question", label: "Question" },
  { key: "answer", label: "Answer" },
  { key: "ground_truth", label: "Ground Truth" },
  { key: "contexts", label: "Contexts" },
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

// Average values per metric across results
export function getMetricAverages(results, metrics) {
  if (!results || !metrics) return {};
  const avg = {};
  metrics.forEach(metric => {
    let values = results.map(row => {
      const v = row[metric];
      return typeof v === "number"
        ? v
        : (typeof v === "object" && v !== null && typeof v.score === "number")
        ? v.score
        : null;
    }).filter(x => typeof x === "number");
    avg[metric] = values.length
      ? values.reduce((a, b) => a + b, 0) / values.length
      : 0;
  });
  return avg;
}
