// CompareUtils.js

// Returns array of objects like { id, question, ground_truth, ...model1: {answer, metrics...}, model2: {...} }
export function alignCompareResults(resultsByModel) {
    // resultsByModel: { modelName1: [rows], modelName2: [rows], ... }
    // Assume all results arrays are for same question set, align by 'id'
    const modelNames = Object.keys(resultsByModel);
    if (!modelNames.length) return [];
    const base = resultsByModel[modelNames[0]] || [];
  
    return base.map(row => {
      const res = {
        id: row.id,
        question: row.question,
        ground_truth: row.ground_truth,
        // contexts: row.contexts, // can add if needed
      };
      modelNames.forEach(model => {
        // Find row in that model by id
        const match = (resultsByModel[model] || []).find(r => r.id === row.id);
        res[model] = match ? {
          answer: match.answer,
          ...match // includes metrics like context_precision etc.
        } : {};
      });
      return res;
    });
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
  