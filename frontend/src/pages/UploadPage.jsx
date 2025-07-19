import React, { useState } from "react";
import {
  Box, Button, Dialog, DialogActions, DialogContent, DialogContentText,
  DialogTitle, MenuItem, TextField, Typography, LinearProgress, Backdrop, CircularProgress
} from "@mui/material";
import CloudUploadIcon from "@mui/icons-material/CloudUpload";
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
      const res = await ingestPdf({ subject, filename: uploadedFilename });
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
      sx={{ bgcolor: "#f7f8fa" }}
    >
      <Box
        width="100%"
        maxWidth={500}
        sx={{
          px: { xs: 2, md: 0 },
          py: 4,
        }}
      >
        <Typography variant="h4" fontWeight={700} mb={3} color="primary.main">
          Upload Academic PDF
        </Typography>
        <form onSubmit={handleSubmit}>
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
          <Button
            component="label"
            variant="outlined"
            fullWidth
            startIcon={<CloudUploadIcon />}
            sx={{ my: 2 }}
            disabled={uploadInProgress || !!uploadedFilename || ingestInProgress}
          >
            {file ? file.name : "Select PDF File"}
            <input
              type="file"
              hidden
              accept=".pdf"
              onChange={e => setFile(e.target.files[0])}
              disabled={uploadInProgress || !!uploadedFilename || ingestInProgress}
            />
          </Button>
          {uploadInProgress && <LinearProgress sx={{ mb: 2 }} />}
          <Button
            variant="contained"
            color="primary"
            type="submit"
            fullWidth
            disabled={uploadInProgress || !!uploadedFilename || ingestInProgress}
            sx={{ fontWeight: 700, fontSize: 18, height: 48 }}
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
              sx={{ fontWeight: 700, fontSize: 18, height: 48 }}
            >
              {ingestInProgress ? "Processing..." : "Process/Ingest"}
            </Button>
          </Box>
        )}
      </Box>
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
