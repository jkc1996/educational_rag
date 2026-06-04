import RefreshIcon from "@mui/icons-material/Refresh";
import {
  Box,
  Button,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Typography,
} from "@mui/material";
import { useEffect, useState } from "react";

import { api } from "../../api/client.js";
import { PageHeader } from "../../components/PageHeader.jsx";
import { KpiCard, WorkPanel } from "../../components/Workspace.jsx";

export function UsagePage({ embedded = false }) {
  const [usage, setUsage] = useState(null);
  const [loading, setLoading] = useState(false);

  const load = async () => {
    setLoading(true);
    try {
      setUsage(await api.usage());
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  return (
    <>
      {!embedded && (
        <PageHeader
          eyebrow="System Monitor"
          title="Usage"
          description="OpenAI token telemetry and pricing-table cost calculations captured by backend features."
        />
      )}
      <Stack direction="row" justifyContent="flex-end" sx={{ mb: 2 }}>
        <Button startIcon={<RefreshIcon />} onClick={load} disabled={loading}>
          Refresh
        </Button>
      </Stack>

      <Box sx={{ display: "grid", gridTemplateColumns: { xs: "1fr", md: "repeat(4, 1fr)" }, gap: 2, mb: 2 }}>
        <KpiCard label="Prompt tokens" value={usage?.total_prompt_tokens || 0} />
        <KpiCard label="Completion tokens" value={usage?.total_completion_tokens || 0} tone="secondary" />
        <KpiCard label="Cached tokens" value={usage?.total_cached_tokens || 0} tone="success" />
        <KpiCard label="Calculated cost" value={`$${(usage?.estimated_cost_usd || 0).toFixed(4)}`} tone="warning" />
      </Box>

      <WorkPanel>
        <Typography variant="h6" sx={{ mb: 1.5 }}>Recent Records</Typography>
        <Box sx={{ overflowX: "auto" }}>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Time</TableCell>
                <TableCell>Feature</TableCell>
                <TableCell>Model</TableCell>
                <TableCell>Token source</TableCell>
                <TableCell align="right">Prompt</TableCell>
                <TableCell align="right">Completion</TableCell>
                <TableCell align="right">Cached</TableCell>
                <TableCell align="right">Total</TableCell>
                <TableCell align="right">Cost</TableCell>
                <TableCell>Cost source</TableCell>
                <TableCell>OpenAI ID</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {(usage?.records || []).map((row, index) => (
                <TableRow key={`${row.timestamp}-${index}`}>
                  <TableCell>{row.timestamp}</TableCell>
                  <TableCell>{row.feature}</TableCell>
                  <TableCell>{row.model_id}</TableCell>
                  <TableCell>{row.token_source || "legacy"}</TableCell>
                  <TableCell align="right">{row.prompt_tokens}</TableCell>
                  <TableCell align="right">{row.completion_tokens}</TableCell>
                  <TableCell align="right">{row.cached_tokens}</TableCell>
                  <TableCell align="right">{row.total_tokens || row.prompt_tokens + row.completion_tokens}</TableCell>
                  <TableCell align="right">${Number(row.estimated_cost_usd || 0).toFixed(5)}</TableCell>
                  <TableCell>{row.pricing_snapshot || row.cost_source || "legacy"}</TableCell>
                  <TableCell>{row.openai_response_id || row.openai_request_id || "-"}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Box>
      </WorkPanel>
    </>
  );
}
