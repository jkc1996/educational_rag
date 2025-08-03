// src/components/MetricChart.jsx

import React from "react";
import { Dialog, DialogTitle, DialogContent, IconButton } from "@mui/material";
import CloseIcon from "@mui/icons-material/Close";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from "recharts";

function MetricChart({ open, onClose, averages, metrics }) {
  // Prepare chart data
  const data = metrics.map(metric => ({
    metric,
    value: averages[metric] ?? 0,
  }));

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        Average Metrics
        <IconButton onClick={onClose} sx={{ position: "absolute", right: 12, top: 8 }}>
          <CloseIcon />
        </IconButton>
      </DialogTitle>
      <DialogContent>
        <BarChart width={600} height={280} data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="metric" />
          <YAxis domain={[0, 1]} />
          <Tooltip />
          <Legend />
          <Bar dataKey="value" fill="#1976d2" />
        </BarChart>
      </DialogContent>
    </Dialog>
  );
}

export default MetricChart;
