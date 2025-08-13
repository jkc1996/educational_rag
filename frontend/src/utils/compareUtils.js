// CompareUtils.js

function normalizeMetricKey(key) {
  // strip mode=f1 or (mode=f1)
  return key.replace(/\(.*?\)/g, "").trim().toLowerCase();
}
// Returns array of objects like { id, question, ground_truth, ...model1: {answer, metrics...}, model2: {...} }

export function alignCompareResults(compareResults) {
  const allIds = new Set();
  const allRows = {};

  for (const model in compareResults) {
    for (const row of compareResults[model]) {
      const rowId = row.id;
      allIds.add(rowId);
      if (!allRows[rowId]) {
        allRows[rowId] = { id: rowId, question: row.question, ground_truth: row.ground_truth, contexts: row.contexts };
      }

      const normalizedMetrics = {};
      for (const key in row) {
        const normKey = normalizeMetricKey(key);
        normalizedMetrics[normKey] = row[key];
      }
      console.log("Normalized keys for row:", Object.keys(normalizedMetrics));

      allRows[rowId][model] = {
        answer: row.answer,
        ...normalizedMetrics,
      };
    }
  }

  return Array.from(allIds).map(id => allRows[id]);
}

  
  // Averages per model/metric
  export function getCompareMetricAverages(resultsByModel, metricsToShow) {
    const averages = {};
    for (const model in resultsByModel) {
      const data = resultsByModel[model];
      if (!data) continue;
      averages[model] = {};
      metricsToShow.forEach(metric => {
        const vals = data.map(row =>
          typeof row[metric] === "number"
            ? row[metric]
            : (typeof row[metric] === "object" && row[metric]?.score)
        ).filter(v => typeof v === "number");
        averages[model][metric] =
          vals.length ? vals.reduce((a, b) => a + b, 0) / vals.length : 0;
      });
    }
    return averages;
  }
  