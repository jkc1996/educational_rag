import React from "react";
import { Table, TableHead, TableRow, TableCell, TableBody, Box, Chip, Typography } from "@mui/material";

export default function AggregatedCompareTable({
  compareResults,
  selectedModels,
  metricCategories,
  metricLabels
}) {
  if (!compareResults || selectedModels.length < 2) return null;

  // Calculate averages by model+metric
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

  // --- Table Render ---
  return (
    <Box sx={{
      width: "100%",
      overflowX: "auto",
      border: "2px solid #e0e6f3",    // <---- OUTSIDE BORDER!
      borderRadius: "10px",           // Optional, for a nice look
      background: "#fff"
    }}>
      <Table size="small">
        <TableHead>
          <TableRow>
            <TableCell sx={{ fontWeight: 700, minWidth: 160, borderBottom: "2px solid #e0e6f3" }}>
              Metric Category
            </TableCell>
            <TableCell sx={{ fontWeight: 700, minWidth: 180, borderBottom: "2px solid #e0e6f3" }}>
              Metric Name
            </TableCell>
            {selectedModels.map(model => (
              <TableCell key={model} align="center" sx={{ fontWeight: 700, minWidth: 90, borderBottom: "2px solid #e0e6f3" }}>
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
            category.metrics.map((metric, mIdx) => {
              const isFirst = mIdx === 0;
              const isLast = mIdx === category.metrics.length - 1;
              return (
                <TableRow key={category.key + "_" + metric}>
                  {isFirst && (
                    <TableCell
                      rowSpan={category.metrics.length}
                      sx={{
                        fontWeight: 900,
                        fontSize: 17,
                        color: "#23396f",
                        borderRight: "2px solid #e0e6f3",
                        bgcolor: "#f9fafd",
                        verticalAlign: "middle",
                        textAlign: "left",
                        minWidth: 140,
                        borderTop: "2px solid #e0e6f3",
                        borderBottom: isLast ? "2px solid #e0e6f3" : "none"
                      }}
                    >
                      {category.label}
                    </TableCell>
                  )}
                  {!isFirst && <></>}
                  <TableCell
                    sx={{
                      bgcolor: "#fff",
                      borderTop: isFirst ? "2px solid #e0e6f3" : "none",
                      borderBottom: isLast ? "2px solid #e0e6f3" : "1px solid #f0f0f0",
                    }}
                  >
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
                    <TableCell
                      key={model + "_" + metric}
                      align="center"
                      sx={{
                        borderTop: isFirst ? "2px solid #e0e6f3" : "none",
                        borderBottom: isLast ? "2px solid #e0e6f3" : "1px solid #f0f0f0",
                      }}
                    >
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
              );
            })
          ))}
        </TableBody>
      </Table>
    </Box>
  );
}
