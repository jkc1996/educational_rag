import React, { useState } from "react";
import {
  Box, Button, Dialog, DialogActions, DialogContent, DialogContentText,
  DialogTitle, MenuItem, TextField, Typography, LinearProgress, Backdrop, CircularProgress, Paper,
  FormControlLabel, Switch, Stack
} from "@mui/material";
import CloudUploadIcon from "@mui/icons-material/CloudUpload";
import FileUploadOutlinedIcon from "@mui/icons-material/FileUploadOutlined";
import { uploadPdf, ingestPdf } from "../services/uploadService";

const SUBJECTS = [
  "Machine Learning",
  "Natural Language Processing"
];

function UploadPage() {
  const [subject, setSubject] = useState("");
  const [description, setDescription] = useState("");
  const [file, setFile] = useState(null);
  const [uploadedFilename, setUploadedFilename] = useState(null);
  const [uploadInProgress, setUploadInProgress] = useState(false);
  const [ingestInProgress, setIngestInProgress] = useState(false);
  const [useLlamaParse, setUseLlamaParse] = useState(false);
  const [dialog, setDialog] = useState({ open: false, type: "", title: "", message: "" });

  const handleDialogClose = () => setDialog({ ...dialog, open: false });

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!subject || !file) {
      setDialog({
        open: true, type: "error", title: "Missing Information",
        message: "Please select subject and file."
      });
      return;
    }
    setUploadInProgress(true);

    try {
      const response = await uploadPdf({ subject, description, file });
      setUploadedFilename(response.data.filename);
      setDialog({
        open: true, type: "success", title: "Upload Successful",
        message: response.data.message || "File uploaded! Click 'Process/Ingest' to continue."
      });
    } catch (err) {
      setDialog({
        open: true, type: "error", title: "Upload Failed",
        message: err.response?.data?.message || "Error uploading file. Please try again."
      });
    }
    setUploadInProgress(false);
  };

  const handleIngest = async () => {
    setIngestInProgress(true);
    setDialog({ open: false });
    try {
      const res = await ingestPdf({ subject, filename: uploadedFilename, useLlamaParse });
      if (res.data.status === "success") {
        setDialog({
          open: true, type: "success", title: "Ingestion Successful",
          message: res.data.message
        });
        setSubject("");
        setDescription("");
        setFile(null);
        setUploadedFilename(null);
      } else {
        setDialog({
          open: true, type: "error", title: "Ingestion Failed",
          message: res.data.message || "Ingest failed."
        });
      }
    } catch (err) {
      setDialog({
        open: true, type: "error", title: "Ingestion Failed",
        message: err.response?.data?.message || "Failed to ingest file."
      });
    }
    setIngestInProgress(false);
  };

  return (
    <Box
      display="flex"
      flexDirection="column"
      alignItems="center"
      justifyContent="center"
      minHeight="80vh"
      width="100%"
      sx={{ bgcolor: "#f6f8fb" }}
    >
      <Paper
        elevation={3}
        sx={{
          width: "100%",
          maxWidth: 540,
          px: { xs: 2, md: 5 },
          py: 5,
          borderRadius: 4,
          boxShadow: "0 4px 32px #a9b4cc1a",
          mt: { xs: 1, sm: 3, md: 5 }  // <-- ADD THIS LINE
        }}
      >
        <Box display="flex" alignItems="center" mb={3} gap={1}>
          <FileUploadOutlinedIcon sx={{ fontSize: 38, color: "#2e3c5d" }} />
          <Typography variant="h4" fontWeight={800} color="#2e3c5d">
            Upload Academic Document
          </Typography>
        </Box>
        <form onSubmit={handleSubmit} autoComplete="off">
          <TextField
            select
            label="Subject"
            value={subject}
            onChange={e => setSubject(e.target.value)}
            required
            fullWidth
            margin="normal"
            disabled={uploadInProgress || !!uploadedFilename || ingestInProgress}
          >
            <MenuItem value="">Select Subject</MenuItem>
            {SUBJECTS.map((s) => (
              <MenuItem value={s} key={s}>{s}</MenuItem>
            ))}
          </TextField>
          <TextField
            label="Description"
            value={description}
            onChange={e => setDescription(e.target.value)}
            placeholder="(optional)"
            fullWidth
            margin="normal"
            disabled={uploadInProgress || !!uploadedFilename || ingestInProgress}
          />

          <FormControlLabel
            control={
              <Switch
                checked={useLlamaParse}
                onChange={e => setUseLlamaParse(e.target.checked)}
                disabled={uploadInProgress || !!uploadedFilename || ingestInProgress}
                color="primary"
              />
            }
            label="Advanced PDF Parsing (LlamaParse)"
            sx={{
              mt: 1.5,
              mb: 1.5,
              fontWeight: 600
            }}
          />

          {/* File upload block */}
          <Paper
            variant="outlined"
            sx={{
              borderStyle: "dashed",
              bgcolor: "#fafdff",
              py: 3,
              mb: 2,
              borderRadius: 3,
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
              position: "relative",
              transition: "border-color 0.3s"
            }}
          >
            <CloudUploadIcon sx={{ fontSize: 40, color: "#1A2A53", mb: 1 }} />
            <Typography fontWeight={600} mb={1}>
              {file ? file.name : "Select PDF or DOCX file to Upload"}
            </Typography>
            <Button
              component="label"
              variant="outlined"
              sx={{ fontWeight: 700 }}
              disabled={uploadInProgress || !!uploadedFilename || ingestInProgress}
            >
              Choose File
              <input
                type="file"
                hidden
                accept=".pdf,.docx"
                onChange={e => setFile(e.target.files[0])}
                disabled={uploadInProgress || !!uploadedFilename || ingestInProgress}
              />
            </Button>
          </Paper>
          {uploadInProgress && <LinearProgress sx={{ mb: 2, borderRadius: 1 }} />}
          <Button
            variant="contained"
            color="primary"
            type="submit"
            fullWidth
            disabled={uploadInProgress || !!uploadedFilename || ingestInProgress}
            sx={{ fontWeight: 800, fontSize: 18, height: 48, borderRadius: 2, my: 1.5 }}
          >
            {uploadInProgress ? "Uploading..." : "Upload"}
          </Button>
        </form>
        {uploadedFilename && (
          <Box mt={3}>
            <Button
              variant="contained"
              color="success"
              fullWidth
              onClick={handleIngest}
              disabled={ingestInProgress}
              sx={{ fontWeight: 800, fontSize: 18, height: 48, borderRadius: 2 }}
            >
              {ingestInProgress ? "Processing..." : "Process/Ingest"}
            </Button>
          </Box>
        )}
      </Paper>
      <Dialog open={dialog.open} onClose={handleDialogClose}>
        <DialogTitle
          sx={{ color: dialog.type === "success" ? "green" : dialog.type === "error" ? "red" : "inherit" }}
        >
          {dialog.title}
        </DialogTitle>
        <DialogContent>
          <DialogContentText>
            {dialog.message}
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleDialogClose} autoFocus>OK</Button>
        </DialogActions>
      </Dialog>
      <Backdrop
        sx={{ color: '#fff', zIndex: (theme) => theme.zIndex.drawer + 1 }}
        open={ingestInProgress}
      >
        <CircularProgress color="inherit" />
        <Typography sx={{ ml: 2 }} variant="h6">
          Processing & indexing your document...<br />
          This may take a minute. Please do not close the page.
        </Typography>
      </Backdrop>
    </Box>
  );
}

export default UploadPage;
