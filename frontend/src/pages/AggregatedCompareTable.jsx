import React from "react";
import { Table, TableHead, TableRow, TableCell, TableBody, Box, Chip, Typography } from "@mui/material";

export default function AggregatedCompareTable({
  compareResults,
  selectedModels,
  metricCategories,
  metricLabels
}) {
  if (!compareResults || selectedModels.length < 2) return null;

  // Build a { [model]: { [metric]: avg } } map for all metrics
  const averagesByModel = {};
  selectedModels.forEach(model => {
    averagesByModel[model] = {};
    const rows = compareResults[model] || [];
    metricCategories.forEach(category => {
      category.metrics.forEach(metric => {
        const vals = rows.map(row =>
          typeof row[metric] === "number"
            ? row[metric]
            : (typeof row[metric] === "object" && row[metric]?.score)
        ).filter(v => typeof v === "number");
        averagesByModel[model][metric] =
          vals.length ? vals.reduce((a, b) => a + b, 0) / vals.length : null;
      });
    });
  });

  return (
    <Box sx={{ width: "100%", overflowX: "auto" }}>
      <Table size="small">
        <TableHead>
          <TableRow>
            <TableCell sx={{ fontWeight: 700, minWidth: 150 }}>Metric Category</TableCell>
            <TableCell sx={{ fontWeight: 700, minWidth: 180 }}>Metric Name</TableCell>
            {selectedModels.map(model => (
              <TableCell key={model} align="center" sx={{ fontWeight: 700, minWidth: 90 }}>
                {model.toUpperCase()}
                <Typography variant="caption" component="div">
                  (Average Score)
                </Typography>
              </TableCell>
            ))}
          </TableRow>
        </TableHead>
        <TableBody>
          {metricCategories.map(category => (
            <React.Fragment key={category.key}>
              <TableRow>
                <TableCell colSpan={2 + selectedModels.length}
                  sx={{ fontWeight: 900, fontSize: 16, bgcolor: "#fafbfc" }}>
                  {category.label}
                </TableCell>
              </TableRow>
              {category.metrics.map(metric => (
                <TableRow key={metric}>
                  <TableCell sx={{ border: 0 }} />
                  <TableCell>
                    <Chip
                      size="small"
                      label={metric}
                      sx={{
                        bgcolor: "#edf2fa",
                        color: "#1a237e",
                        fontFamily: "monospace",
                        fontSize: 13
                      }}
                    />{" "}
                    {metricLabels[metric] && (
                      <Typography component="span" variant="body2" sx={{ color: "#333", ml: 1 }}>
                        {metricLabels[metric]}
                      </Typography>
                    )}
                  </TableCell>
                  {selectedModels.map(model => (
                    <TableCell key={model + "_" + metric} align="center">
                      <Chip
                        label={
                          typeof averagesByModel[model][metric] === "number"
                            ? averagesByModel[model][metric].toFixed(3)
                            : "-"
                        }
                        size="small"
                        sx={{
                          bgcolor: "#f6f8ff",
                          color: "#222",
                          fontWeight: 600,
                          fontSize: 14,
                          px: 0.8,
                          minWidth: 40,
                          borderRadius: 1.3,
                          border: "1px solid #e0e0e0"
                        }}
                      />
                    </TableCell>
                  ))}
                </TableRow>
              ))}
              {/* Spacing Row */}
              <TableRow><TableCell colSpan={2 + selectedModels.length} sx={{ py: 0.4, border: 0 }}/></TableRow>
            </React.Fragment>
          ))}
        </TableBody>
      </Table>
    </Box>
  );
}
