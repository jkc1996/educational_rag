// src/services/uploadService.js
import axios from "axios";

export async function uploadPdf({ subject, description, file }) {
  const formData = new FormData();
  formData.append("subject", subject);
  formData.append("description", description);
  formData.append("file", file);

  return axios.post("http://localhost:8000/upload-pdf/", formData, {
    headers: { "Content-Type": "multipart/form-data" }
  });
}

export async function ingestPdf({ subject, filename }) {
  const params = new URLSearchParams({ subject, filename });
  return axios.post("http://localhost:8000/ingest/", params);
}
