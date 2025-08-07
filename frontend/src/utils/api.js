export async function evaluateModels({ modelNames, category }) {
  // modelNames can be a single string or an array
  const res = await fetch("http://localhost:8000/evaluate-ragas/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(
      Array.isArray(modelNames)
        ? { model_names: modelNames, category }
        : { model_name: modelNames, category }
    ),
  });
  return await res.json();
}
