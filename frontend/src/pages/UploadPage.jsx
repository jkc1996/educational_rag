import React, { useState } from "react";
import axios from "axios";

const SUBJECTS = [
  "Machine Learning",
  "Natural Language Processing"
];

function UploadPage() {
  const [subject, setSubject] = useState("");
  const [description, setDescription] = useState("");
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState({ type: "", text: "" });
  const [uploadedFilename, setUploadedFilename] = useState(null);
  const [ingestStatus, setIngestStatus] = useState({ type: "", text: "" });
  const [uploadInProgress, setUploadInProgress] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!subject || !file) {
      setMessage({ type: "error", text: "Please select subject and file." });
      return;
    }

    setUploadInProgress(true);
    setMessage({ type: "", text: "" });
    setIngestStatus({ type: "", text: "" });
    // Don't clear uploadedFilename here

    const formData = new FormData();
    formData.append("subject", subject);
    formData.append("description", description);
    formData.append("file", file);

    try {
      const response = await axios.post("http://localhost:8000/upload-pdf/", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setMessage({
        type: "success",
        text: response.data.message || "File uploaded! Now click 'Process/Ingest' to prepare it for QA."
      });
      setUploadedFilename(response.data.filename);
      // Don't clear the form yet: let user process/ingest!
      // setSubject("");
      // setDescription("");
      // setFile(null);
    } catch (err) {
      setMessage({
        type: "error",
        text: err.response?.data?.message || "Error uploading file. Please try again."
      });
    }
    setUploadInProgress(false);
  };

  const handleIngest = async () => {
    setIngestStatus({ type: "", text: "Processing..." });
    try {
      const params = new URLSearchParams({
        subject,
        filename: uploadedFilename
      });
      const res = await axios.post("http://localhost:8000/ingest/", params);
      if (res.data.status === "success") {
        setIngestStatus({ type: "success", text: res.data.message });
        // Now clear form after ingest
        setTimeout(() => {
          setSubject("");
          setDescription("");
          setFile(null);
          setUploadedFilename(null);
          setMessage({ type: "", text: "" });
          setIngestStatus({ type: "", text: "" });
        }, 2000); // Delay so user can see the green message
      } else {
        setIngestStatus({ type: "error", text: res.data.message || "Ingest failed." });
      }
    } catch (err) {
      setIngestStatus({
        type: "error",
        text: err.response?.data?.message || "Failed to ingest file."
      });
    }
  };

  return (
    <div>
      <h2>Upload Academic PDF</h2>
      <form onSubmit={handleSubmit} style={{ maxWidth: 400 }}>
        <div>
          <label>Subject:</label>
          <select
            value={subject}
            onChange={(e) => setSubject(e.target.value)}
            required
            style={{ width: "100%", marginBottom: 8 }}
            disabled={uploadInProgress || !!uploadedFilename}
          >
            <option value="">Select Subject</option>
            {SUBJECTS.map((s) => (
              <option value={s} key={s}>{s}</option>
            ))}
          </select>
        </div>
        <div>
          <label>Description:</label>
          <input
            type="text"
            value={description}
            onChange={e => setDescription(e.target.value)}
            placeholder="(optional)"
            style={{ width: "100%", marginBottom: 8 }}
            disabled={uploadInProgress || !!uploadedFilename}
          />
        </div>
        <div>
          <label>PDF File:</label>
          <input
            type="file"
            accept=".pdf"
            onChange={e => setFile(e.target.files[0])}
            required
            style={{ width: "100%", marginBottom: 8 }}
            disabled={uploadInProgress || !!uploadedFilename}
          />
        </div>
        <button type="submit" disabled={uploadInProgress || !!uploadedFilename}>
          {uploadInProgress ? "Uploading..." : "Upload"}
        </button>
      </form>

      {/* Upload feedback */}
      {message.text && (
        <p style={{
          color: message.type === "success" ? "green" : "red",
          marginTop: 8
        }}>
          {message.text}
        </p>
      )}

      {/* Process/Ingest button and feedback */}
      {uploadedFilename && (
        <div style={{ marginTop: 16 }}>
          <button onClick={handleIngest} disabled={ingestStatus.text === "Processing..."}>
            {ingestStatus.text === "Processing..." ? "Processing..." : "Process/Ingest"}
          </button>
          {ingestStatus.text && (
            <p style={{
              color: ingestStatus.type === "success" ? "green"
                : ingestStatus.type === "error" ? "red"
                : "black",
              marginTop: 8
            }}>
              {ingestStatus.text}
            </p>
          )}
        </div>
      )}
    </div>
  );
}

export default UploadPage;
