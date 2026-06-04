import CloudUploadIcon from "@mui/icons-material/CloudUpload";
import PlayCircleOutlineIcon from "@mui/icons-material/PlayCircleOutline";
import RefreshIcon from "@mui/icons-material/Refresh";
import SourceOutlinedIcon from "@mui/icons-material/SourceOutlined";
import {
  Alert,
  Box,
  Button,
  Checkbox,
  Chip,
  Divider,
  FormControlLabel,
  LinearProgress,
  MenuItem,
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
import { KpiCard, WorkPanel, WorkspaceLayout } from "../../components/Workspace.jsx";
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
  const indexedCount = documents.filter((doc) => doc.status === "completed").length;
  const cachedCount = documents.filter((doc) => doc.summary_cache_key).length;
  const chunkCount = documents.reduce((total, doc) => total + Number(doc.chunk_count || 0), 0);

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
        eyebrow="Source Pipeline"
        title="Sources"
        description="Keep course files, vector indexing, and cached structured summaries visible in one place."
        actions={
          <Button startIcon={<RefreshIcon />} onClick={refresh}>
            Refresh
          </Button>
        }
      />

      {message && (
        <Alert severity={message.severity} sx={{ mb: 2 }}>
          {message.text}
        </Alert>
      )}

      <Box sx={{ display: "grid", gridTemplateColumns: { xs: "1fr", md: "repeat(4, 1fr)" }, gap: 2, mb: 2 }}>
        <KpiCard label="Documents" value={documents.length} />
        <KpiCard label="Indexed" value={indexedCount} tone="success" />
        <KpiCard label="Cached summaries" value={cachedCount} tone="secondary" />
        <KpiCard label="Chunks" value={chunkCount} tone="warning" />
      </Box>

      <WorkspaceLayout inspector={<SourceInspector documents={documents} selectedDocumentId={selectedDocumentId} />}>
        <Stack gap={2}>
          <WorkPanel>
            <Stack direction="row" alignItems="center" gap={1} sx={{ mb: 2 }}>
              <SourceOutlinedIcon color="primary" />
              <Typography variant="h6">Add Source</Typography>
            </Stack>
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
                  <MenuItem value="" disabled>
                    Choose existing subject
                  </MenuItem>
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
              <Stack direction={{ xs: "column", sm: "row" }} gap={1.5}>
                <Button component="label" variant="outlined" startIcon={<CloudUploadIcon />} sx={{ flex: 1 }}>
                  {file ? file.name : "Choose PDF or DOCX"}
                  <input hidden type="file" accept=".pdf,.doc,.docx" onChange={(event) => setFile(event.target.files?.[0] || null)} />
                </Button>
                <Button type="submit" variant="contained" disabled={loading}>
                  Upload
                </Button>
              </Stack>
            </Stack>

            <Divider sx={{ my: 2.5 }} />

            <Stack gap={2}>
              <Typography variant="h6">Index and Summarize</Typography>
              <Box sx={{ display: "grid", gridTemplateColumns: { xs: "1fr", md: "1fr 1fr" }, gap: 2 }}>
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
                  <MenuItem value="" disabled>
                    Select document
                  </MenuItem>
                  {documents.map((doc) => (
                    <MenuItem key={doc.id} value={doc.id}>
                      {doc.filename}
                    </MenuItem>
                  ))}
                </TextField>
              </Box>
              <Stack direction={{ xs: "column", sm: "row" }} justifyContent="space-between" alignItems={{ xs: "stretch", sm: "center" }} gap={1.5}>
                <FormControlLabel
                  control={<Checkbox checked={forceRefresh} onChange={(event) => setForceRefresh(event.target.checked)} />}
                  label="Regenerate cached summary"
                />
                <Button variant="contained" color="success" startIcon={<PlayCircleOutlineIcon />} disabled={loading} onClick={() => ingest()}>
                  Ingest
                </Button>
              </Stack>
            </Stack>
            {loading && <LinearProgress sx={{ mt: 2 }} />}
          </WorkPanel>

          <WorkPanel>
            <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 1.5 }}>
              <Typography variant="h6">Library</Typography>
              <Chip size="small" label={`${documents.length} files`} />
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
                    <TableRow key={doc.id} hover selected={doc.id === selectedDocumentId}>
                      <TableCell>
                        <Typography fontWeight={750}>{doc.filename}</Typography>
                        {doc.description && (
                          <Typography variant="caption" color="text.secondary">
                            {doc.description}
                          </Typography>
                        )}
                      </TableCell>
                      <TableCell>{doc.subject}</TableCell>
                      <TableCell>
                        <StatusChip status={doc.status} />
                      </TableCell>
                      <TableCell align="right">{doc.chunk_count}</TableCell>
                      <TableCell>
                        <Chip size="small" label={doc.summary_cache_key ? "cached" : "missing"} color={doc.summary_cache_key ? "success" : "default"} variant={doc.summary_cache_key ? "filled" : "outlined"} />
                      </TableCell>
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
          </WorkPanel>
        </Stack>
      </WorkspaceLayout>
    </>
  );
}

function SourceInspector({ documents, selectedDocumentId }) {
  const selected = documents.find((doc) => doc.id === selectedDocumentId);
  const bySubject = documents.reduce((counts, doc) => {
    counts[doc.subject] = (counts[doc.subject] || 0) + 1;
    return counts;
  }, {});

  return (
    <Stack gap={2}>
      <WorkPanel>
        <Typography variant="h6" sx={{ mb: 1.5 }}>
          Selected Source
        </Typography>
        {selected ? (
          <Stack gap={1}>
            <Trace label="File" value={selected.filename} />
            <Trace label="Subject" value={selected.subject} />
            <Trace label="Status" value={selected.status} />
            <Trace label="Chunks" value={selected.chunk_count} />
            <Trace label="Summary" value={selected.summary_cache_key ? "cached" : "missing"} />
          </Stack>
        ) : (
          <Typography color="text.secondary">Choose a document to inspect its ingestion state.</Typography>
        )}
      </WorkPanel>

      <WorkPanel>
        <Typography variant="h6" sx={{ mb: 1.5 }}>
          Subject Spread
        </Typography>
        <Stack gap={1}>
          {Object.entries(bySubject).map(([name, count]) => (
            <Stack key={name} direction="row" justifyContent="space-between" gap={1}>
              <Typography variant="body2">{name}</Typography>
              <Chip size="small" label={count} />
            </Stack>
          ))}
          {Object.keys(bySubject).length === 0 && <Typography color="text.secondary">No subjects yet.</Typography>}
        </Stack>
      </WorkPanel>
    </Stack>
  );
}

function Trace({ label, value }) {
  return (
    <Stack direction="row" justifyContent="space-between" gap={1.5}>
      <Typography variant="body2" color="text.secondary">
        {label}
      </Typography>
      <Typography variant="body2" fontWeight={750} sx={{ textAlign: "right" }}>
        {value || "-"}
      </Typography>
    </Stack>
  );
}
