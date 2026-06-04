import CloudUploadIcon from "@mui/icons-material/CloudUpload";
import PlayCircleOutlineIcon from "@mui/icons-material/PlayCircleOutline";
import RefreshIcon from "@mui/icons-material/Refresh";
import {
  Alert,
  Box,
  Button,
  Checkbox,
  Divider,
  FormControlLabel,
  LinearProgress,
  MenuItem,
  Paper,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from "@mui/material";
import { useMemo, useState } from "react";

import { api } from "../../api/client.js";
import { ModelSelect } from "../../components/ModelSelect.jsx";
import { PageHeader } from "../../components/PageHeader.jsx";
import { StatusChip } from "../../components/StatusChip.jsx";

export function DocumentManager({ models, subjects, documents, refresh }) {
  const [subject, setSubject] = useState("");
  const [description, setDescription] = useState("");
  const [file, setFile] = useState(null);
  const [summaryModel, setSummaryModel] = useState("");
  const [forceRefresh, setForceRefresh] = useState(false);
  const [selectedDocumentId, setSelectedDocumentId] = useState("");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);

  const summaryDefault = useMemo(
    () => models.find((model) => model.role === "summarization")?.id || models.find((model) => model.default)?.id || "",
    [models]
  );

  const upload = async (event) => {
    event.preventDefault();
    if (!subject || !file) {
      setMessage({ severity: "error", text: "Choose a subject and a document first." });
      return;
    }
    setLoading(true);
    setMessage(null);
    try {
      const response = await api.uploadDocument({ subject, description, file });
      setSelectedDocumentId(response.document.id);
      setFile(null);
      setDescription("");
      setMessage({ severity: "success", text: "Uploaded. Run ingestion to index and summarize it." });
      await refresh();
    } catch (err) {
      setMessage({ severity: "error", text: err.message });
    } finally {
      setLoading(false);
    }
  };

  const ingest = async (documentId = selectedDocumentId) => {
    if (!documentId) {
      setMessage({ severity: "error", text: "Select a document to ingest." });
      return;
    }
    setLoading(true);
    setMessage({ severity: "info", text: "Ingestion started. This will embed chunks and cache structured summaries." });
    try {
      const response = await api.ingestDocument({
        documentId,
        modelId: summaryModel || summaryDefault,
        forceSummaryRefresh: forceRefresh,
      });
      setMessage({
        severity: response.status === "failed" ? "error" : "success",
        text:
          response.status === "failed"
            ? response.error || "Ingestion failed."
            : `Ingested ${response.chunk_count} chunks and cached the summary.`,
      });
      await refresh();
    } catch (err) {
      setMessage({ severity: "error", text: err.message });
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <PageHeader
        title="Documents"
        description="Upload academic material, index it into Chroma, and generate cached structured summaries for later question-paper generation."
      />

      {message && (
        <Alert severity={message.severity} sx={{ mb: 2 }}>
          {message.text}
        </Alert>
      )}

      <Box sx={{ display: "grid", gridTemplateColumns: { xs: "1fr", md: "380px 1fr" }, gap: 2 }}>
        <Paper className="panel" sx={{ p: 2.5 }}>
          <Typography variant="h6" sx={{ mb: 2 }}>
            Upload and Ingest
          </Typography>
          <Stack component="form" onSubmit={upload} gap={2}>
            <TextField
              size="small"
              label="Subject"
              value={subject}
              onChange={(event) => setSubject(event.target.value)}
              placeholder={subjects[0] || "Machine Learning"}
            />
            {subjects.length > 0 && (
              <TextField
                select
                size="small"
                label="Existing subjects"
                value=""
                onChange={(event) => setSubject(event.target.value)}
              >
                {subjects.map((item) => (
                  <MenuItem key={item} value={item}>
                    {item}
                  </MenuItem>
                ))}
              </TextField>
            )}
            <TextField
              size="small"
              label="Description"
              value={description}
              onChange={(event) => setDescription(event.target.value)}
            />
            <Button component="label" variant="outlined" startIcon={<CloudUploadIcon />}>
              {file ? file.name : "Choose PDF or DOCX"}
              <input hidden type="file" accept=".pdf,.doc,.docx" onChange={(event) => setFile(event.target.files?.[0] || null)} />
            </Button>
            <Button type="submit" variant="contained" disabled={loading}>
              Upload
            </Button>
          </Stack>

          <Divider sx={{ my: 2.5 }} />

          <Stack gap={2}>
            <ModelSelect
              models={models}
              value={summaryModel || summaryDefault}
              onChange={setSummaryModel}
              label="Summary model"
              disabled={loading}
            />
            <TextField
              select
              size="small"
              label="Document"
              value={selectedDocumentId}
              onChange={(event) => setSelectedDocumentId(event.target.value)}
            >
              {documents.map((doc) => (
                <MenuItem key={doc.id} value={doc.id}>
                  {doc.filename}
                </MenuItem>
              ))}
            </TextField>
            <FormControlLabel
              control={<Checkbox checked={forceRefresh} onChange={(event) => setForceRefresh(event.target.checked)} />}
              label="Regenerate cached summary"
            />
            <Button variant="contained" color="success" startIcon={<PlayCircleOutlineIcon />} disabled={loading} onClick={() => ingest()}>
              Ingest and Summarize
            </Button>
          </Stack>
          {loading && <LinearProgress sx={{ mt: 2 }} />}
        </Paper>

        <Paper className="panel" sx={{ p: 2.5, overflow: "hidden" }}>
          <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 1.5 }}>
            <Typography variant="h6">Document Registry</Typography>
            <Button size="small" startIcon={<RefreshIcon />} onClick={refresh}>
              Refresh
            </Button>
          </Stack>
          <Box sx={{ overflowX: "auto" }}>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>File</TableCell>
                  <TableCell>Subject</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell align="right">Chunks</TableCell>
                  <TableCell>Summary</TableCell>
                  <TableCell />
                </TableRow>
              </TableHead>
              <TableBody>
                {documents.map((doc) => (
                  <TableRow key={doc.id} hover>
                    <TableCell>{doc.filename}</TableCell>
                    <TableCell>{doc.subject}</TableCell>
                    <TableCell>
                      <StatusChip status={doc.status} />
                    </TableCell>
                    <TableCell align="right">{doc.chunk_count}</TableCell>
                    <TableCell>{doc.summary_cache_key ? "cached" : "missing"}</TableCell>
                    <TableCell align="right">
                      <Button size="small" onClick={() => ingest(doc.id)} disabled={loading}>
                        Reingest
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
                {documents.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={6}>
                      <Typography color="text.secondary">No documents uploaded yet.</Typography>
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </Box>
        </Paper>
      </Box>
    </>
  );
}

