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

export async function ingestPdf({ subject, filename, useLlamaParse }) {
  return axios.post("http://localhost:8000/ingest/", {
    subject,
    filename,
    use_llamaparse: useLlamaParse, // <-- backend expects this key
  });
}
