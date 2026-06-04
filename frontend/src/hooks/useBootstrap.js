import { useCallback, useEffect, useState } from "react";

import { api } from "../api/client.js";

export function useBootstrap() {
  const [models, setModels] = useState([]);
  const [embeddingModel, setEmbeddingModel] = useState("");
  const [subjects, setSubjects] = useState([]);
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const refresh = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const [modelPayload, subjectsPayload, documentsPayload] = await Promise.all([
        api.models(),
        api.subjects(),
        api.documents(),
      ]);
      setModels(modelPayload.models || []);
      setEmbeddingModel(modelPayload.embedding_model || "");
      setSubjects(subjectsPayload || []);
      setDocuments(documentsPayload || []);
    } catch (err) {
      setError(err.message || "Unable to load backend metadata.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return { models, embeddingModel, subjects, documents, loading, error, refresh };
}

