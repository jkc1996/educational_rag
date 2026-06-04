import ExpandLessIcon from "@mui/icons-material/ExpandLess";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import RefreshIcon from "@mui/icons-material/Refresh";
import SearchIcon from "@mui/icons-material/Search";
import {
  Box,
  Button,
  Chip,
  Collapse,
  FormControl,
  IconButton,
  InputAdornment,
  InputLabel,
  MenuItem,
  Paper,
  Select,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from "@mui/material";
import { useEffect, useState } from "react";

import { api } from "../../api/client.js";
import { PageHeader } from "../../components/PageHeader.jsx";

const defaultResponse = {
  items: [],
  summary: { total: 0, errors: 0, warnings: 0, qa_events: 0, llm_events: 0, openai_events: 0, ingestion_events: 0, noisy_events: 0 },
  levels: [],
  categories: [],
};

const categoryLabels = {
  qa: "QA",
  llm: "LLM",
  question_paper: "Question Paper",
  evaluation: "Evaluation",
  feedback: "Feedback",
  ingestion: "Ingestion",
  document_upload: "Upload",
  openai: "OpenAI",
  http: "HTTP",
  retry: "Retry",
  vector_store: "Vector DB",
  error: "Error",
  system: "System",
};

const levelColors = {
  DEBUG: "default",
  INFO: "info",
  WARNING: "warning",
  ERROR: "error",
  CRITICAL: "error",
};

export function LogsPage() {
  const [logs, setLogs] = useState(defaultResponse);
  const [search, setSearch] = useState("");
  const [level, setLevel] = useState("");
  const [category, setCategory] = useState("");
  const [limit, setLimit] = useState(500);
  const [expanded, setExpanded] = useState(null);
  const [loading, setLoading] = useState(false);

  const load = async () => {
    setLoading(true);
    try {
      setLogs(await api.logs({ limit, query: search.trim(), level, category }));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const clearFilters = () => {
    setSearch("");
    setLevel("");
    setCategory("");
    setLoading(true);
    api.logs({ limit }).then(setLogs).finally(() => setLoading(false));
  };

  return (
    <>
      <PageHeader title="Logs" description="Application flow traces for QA, ingestion, question papers, evaluation, OpenAI calls, and retries." />

      <Box sx={{ display: "grid", gridTemplateColumns: { xs: "1fr", sm: "repeat(2, 1fr)", lg: "repeat(6, 1fr)" }, gap: 2, mb: 2 }}>
        <Stat label="Shown" value={logs.summary.total} />
        <Stat label="Errors" value={logs.summary.errors} tone={logs.summary.errors ? "error" : "success"} />
        <Stat label="Warnings" value={logs.summary.warnings} tone={logs.summary.warnings ? "warning" : "success"} />
        <Stat label="QA Events" value={logs.summary.qa_events} />
        <Stat label="LLM Events" value={logs.summary.llm_events || logs.summary.openai_events} />
        <Stat label="Noise" value={logs.summary.noisy_events} tone="muted" />
      </Box>

      <Paper className="panel" sx={{ p: 2.5, overflow: "hidden" }}>
        <Stack direction={{ xs: "column", lg: "row" }} gap={1.5} alignItems={{ xs: "stretch", lg: "center" }} sx={{ mb: 2 }}>
          <TextField
            size="small"
            label="Search logs"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter") load();
            }}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon fontSize="small" />
                </InputAdornment>
              ),
            }}
            sx={{ minWidth: { lg: 320 } }}
          />
          <FormControl size="small" sx={{ minWidth: 150 }}>
            <InputLabel>Level</InputLabel>
            <Select label="Level" value={level} onChange={(event) => setLevel(event.target.value)}>
              <MenuItem value="">All levels</MenuItem>
              {logs.levels.map((item) => (
                <MenuItem key={item} value={item}>
                  {item}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          <FormControl size="small" sx={{ minWidth: 170 }}>
            <InputLabel>Category</InputLabel>
            <Select label="Category" value={category} onChange={(event) => setCategory(event.target.value)}>
              <MenuItem value="">All categories</MenuItem>
              {logs.categories.map((item) => (
                <MenuItem key={item} value={item}>
                  {categoryLabels[item] || item}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Limit</InputLabel>
            <Select label="Limit" value={limit} onChange={(event) => setLimit(Number(event.target.value))}>
              {[100, 250, 500, 1000].map((item) => (
                <MenuItem key={item} value={item}>
                  {item}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          <Stack direction="row" gap={1} sx={{ ml: { lg: "auto" } }}>
            <Button onClick={clearFilters}>Clear</Button>
            <Button variant="contained" startIcon={<RefreshIcon />} onClick={load} disabled={loading}>
              Refresh
            </Button>
          </Stack>
        </Stack>

        <Box sx={{ overflowX: "auto" }}>
          <Table size="small" sx={{ minWidth: 1180 }}>
            <TableHead>
              <TableRow>
                <TableCell width={54} />
                <TableCell>Time</TableCell>
                <TableCell>Severity</TableCell>
                <TableCell>Flow</TableCell>
                <TableCell>Step</TableCell>
                <TableCell>Event</TableCell>
                <TableCell>Key Details</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {logs.items.map((row, index) => {
                const rowKey = `${row.timestamp}-${row.fingerprint}-${index}`;
                const isOpen = expanded === rowKey;
                return (
                  <LogRow
                    key={rowKey}
                    rowKey={rowKey}
                    row={row}
                    isOpen={isOpen}
                    onToggle={() => setExpanded(isOpen ? null : rowKey)}
                  />
                );
              })}
              {logs.items.length === 0 && (
                <TableRow>
                  <TableCell colSpan={7}>
                    <Typography color="text.secondary">No logs match the current filters.</Typography>
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </Box>
      </Paper>
    </>
  );
}

function LogRow({ row, isOpen, onToggle }) {
  return (
    <>
      <TableRow hover sx={{ "& > td": { borderBottom: isOpen ? 0 : undefined } }}>
        <TableCell>
          <IconButton size="small" onClick={onToggle} aria-label={isOpen ? "Collapse log details" : "Expand log details"}>
            {isOpen ? <ExpandLessIcon fontSize="small" /> : <ExpandMoreIcon fontSize="small" />}
          </IconButton>
        </TableCell>
        <TableCell className="mono-cell">{formatTime(row.timestamp)}</TableCell>
        <TableCell>
          <Chip size="small" label={row.level || "INFO"} color={levelColors[row.level] || "default"} variant={row.level === "INFO" ? "outlined" : "filled"} />
        </TableCell>
        <TableCell sx={{ minWidth: 170 }}>
          <Stack gap={0.5}>
            <Chip
              size="small"
              label={categoryLabels[row.flow || row.category] || row.flow || row.category}
              variant={row.is_noise ? "outlined" : "filled"}
              sx={{ width: "fit-content" }}
            />
            {row.flow_id && (
              <Typography variant="caption" color="text.secondary" className="mono-cell">
                {shortFlowId(row.flow_id)}
              </Typography>
            )}
          </Stack>
        </TableCell>
        <TableCell>
          <Chip size="small" label={row.step || "-"} variant="outlined" />
        </TableCell>
        <TableCell>
          <Typography variant="body2" sx={{ fontWeight: 650 }}>
            {row.message}
          </Typography>
          <Typography variant="caption" color="text.secondary">
            {row.event}
          </Typography>
        </TableCell>
        <TableCell>
          {row.details_preview ? (
            <Typography
              variant="body2"
              className="mono-cell"
              sx={{
                display: "-webkit-box",
                WebkitLineClamp: 3,
                WebkitBoxOrient: "vertical",
                overflow: "hidden",
              }}
            >
              {row.details_preview}
            </Typography>
          ) : (
            <Typography variant="body2" color="text.secondary">
              No extra details
            </Typography>
          )}
        </TableCell>
      </TableRow>
      <TableRow>
        <TableCell colSpan={7} sx={{ p: 0, borderBottom: isOpen ? undefined : 0 }}>
          <Collapse in={isOpen} timeout="auto" unmountOnExit>
            <Box sx={{ px: 7, py: 1.5, bgcolor: "grey.50", borderTop: "1px solid", borderColor: "divider" }}>
              <Typography variant="caption" color="text.secondary">
                Raw structured payload
              </Typography>
              <Box
                component="pre"
                className="mono-cell"
                sx={{
                  mt: 1,
                  mb: 0,
                  p: 1.5,
                  overflowX: "auto",
                  bgcolor: "common.white",
                  border: "1px solid",
                  borderColor: "divider",
                  borderRadius: 1,
                  whiteSpace: "pre-wrap",
                }}
              >
                {JSON.stringify(row.details || {}, null, 2)}
              </Box>
            </Box>
          </Collapse>
        </TableCell>
      </TableRow>
    </>
  );
}

function Stat({ label, value, tone = "primary" }) {
  const colorMap = {
    primary: "primary.dark",
    success: "success.main",
    warning: "warning.main",
    error: "error.main",
    muted: "text.secondary",
  };

  return (
    <Paper className="panel" sx={{ p: 2 }}>
      <Typography variant="body2" color="text.secondary">
        {label}
      </Typography>
      <Typography variant="h5" color={colorMap[tone] || colorMap.primary}>
        {value}
      </Typography>
    </Paper>
  );
}

function formatTime(value) {
  if (!value) return "-";
  return value.replace(" ", "\n");
}

function shortFlowId(value) {
  if (!value) return "";
  const [prefix, id] = String(value).split("_");
  return id ? `${prefix}_${id.slice(0, 8)}` : String(value).slice(0, 12);
}
