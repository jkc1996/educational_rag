import React, { useEffect, useState } from "react";
import { Box, Typography, Paper, Select, MenuItem, TextField } from "@mui/material";
import { DataGrid } from "@mui/x-data-grid";
import axios from "axios";

function LogViewer() {
  const [logs, setLogs] = useState([]);
  const [level, setLevel] = useState("ALL");
  const [search, setSearch] = useState("");

  useEffect(() => {
    const fetchLogs = () => {
      axios.get("http://localhost:8000/logs?limit=500")
        .then(res => setLogs(res.data))
        .catch(() => {});
    };
    fetchLogs();
    const interval = setInterval(fetchLogs, 2000);
    return () => clearInterval(interval);
  }, []);

  // Prepare columns for DataGrid
  const columns = [
    { field: "timestamp", headerName: "Timestamp", width: 160 },
    { field: "level", headerName: "Level", width: 90 },
    { field: "event", headerName: "Event", width: 160 },
    { field: "subject", headerName: "Subject", width: 130 },
    { field: "question", headerName: "Question", width: 260, flex: 1 },
    {
      field: "msg",
      headerName: "Details",
      width: 280,
      flex: 2,
      valueGetter: (params) => {
        const log = params?.row || {};
        return Object.entries(log)
          .filter(([k]) => !["timestamp", "level", "event", "subject", "question", "id"].includes(k))
          .map(([k, v]) => `${k}: ${typeof v === "object" ? JSON.stringify(v) : v}`)
          .join(" | ");
      }
    }
  ];

  // Filter logs: only valid objects, with id, matching search/level
  const filteredLogs = logs
    .filter(l => typeof l === "object" && l !== null) // Only objects, not undefined/null
    .map((l, idx) => ({ ...l, id: idx }))
    .filter(l =>
      (level === "ALL" || l.level === level) &&
      (search === "" ||
        Object.values(l).join(" ").toLowerCase().includes(search.toLowerCase()))
    );

  return (
    <Box maxWidth={1200} mx="auto" mt={4}>
      <Typography variant="h5" mb={2}>System & User Logs</Typography>
      <Box display="flex" gap={2} mb={2}>
        <Select value={level} onChange={e => setLevel(e.target.value)}>
          <MenuItem value="ALL">All Levels</MenuItem>
          <MenuItem value="INFO">INFO</MenuItem>
          <MenuItem value="DEBUG">DEBUG</MenuItem>
          <MenuItem value="ERROR">ERROR</MenuItem>
        </Select>
        <TextField
          label="Search"
          size="small"
          value={search}
          onChange={e => setSearch(e.target.value)}
        />
      </Box>
      <Paper elevation={3} sx={{ height: 650, width: "100%" }}>
        <DataGrid
          rows={filteredLogs}
          columns={columns}
          pageSize={25}
          rowsPerPageOptions={[25, 50, 100]}
          getRowClassName={(params) =>
            params.row.level === "ERROR"
              ? "log-row-error"
              : params.row.level === "DEBUG"
              ? "log-row-debug"
              : ""
          }
        />
      </Paper>
      {/* Optional: Some quick styles */}
      <style>
        {`
          .log-row-error {
            background: #fff5f5;
            color: #c62828;
          }
          .log-row-debug {
            background: #f0f6ff;
            color: #1565c0;
          }
        `}
      </style>
    </Box>
  );
}

export default LogViewer;
