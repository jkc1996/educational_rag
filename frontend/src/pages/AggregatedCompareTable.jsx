import React from "react";
import { Table, TableHead, TableRow, TableCell, TableBody, Box, Chip, Typography } from "@mui/material";

/**
 * @param {Object} props
 * @param {Object} props.compareResults  // { model: [{ metric: value, ...}, ...] }
 * @param {string[]} props.selectedModels
 * @param {Object[]} props.metricCategories // [{key, label, metrics:[metric1,...]}, ...]
 * @param {Object} props.metricLabels // { metric: label, ... }
 */
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

  // Common cell border style for vertical lines
  const borderStyle = "1.5px solid #e0e6f3";

  return (
    <Box sx={{
      width: "100%",
      overflowX: "auto",
      border: borderStyle,
      borderRadius: "9px",
      background: "#fff",
      boxShadow: "0 2px 6px rgba(110,125,170,0.04)"
    }}>
      <Table
        size="small"
        sx={{
          minWidth: 900,
          borderCollapse: "separate",
          borderSpacing: 0
        }}
      >
        <TableHead>
          <TableRow>
            <TableCell
              sx={{
                fontWeight: 700,
                minWidth: 170,
                borderRight: borderStyle,
                borderBottom: borderStyle,
                background: "#fafbfc"
              }}
            >
              Metric Category
            </TableCell>
            <TableCell
              sx={{
                fontWeight: 700,
                minWidth: 210,
                borderRight: borderStyle,
                borderBottom: borderStyle,
                background: "#fafbfc"
              }}
            >
              Metric Name
            </TableCell>
            {selectedModels.map((model, i) => (
              <TableCell
                key={model}
                align="center"
                sx={{
                  fontWeight: 700,
                  minWidth: 110,
                  borderRight: i === selectedModels.length - 1 ? "none" : borderStyle,
                  borderBottom: borderStyle,
                  background: "#fafbfc"
                }}
              >
                {model.toUpperCase()}
                <Typography variant="caption" component="div">
                  (Average Score)
                </Typography>
              </TableCell>
            ))}
          </TableRow>
        </TableHead>
        <TableBody>
          {metricCategories.map(category =>
            category.metrics.map((metric, mIdx) => {
              const isFirst = mIdx === 0;
              const isLast = mIdx === category.metrics.length - 1;
              return (
                <TableRow key={category.key + "_" + metric}>
                  {/* Only show the category cell for the first metric in each category (with rowspan) */}
                  {isFirst && (
                    <TableCell
                      rowSpan={category.metrics.length}
                      sx={{
                        fontWeight: 900,
                        fontSize: 17,
                        color: "#23396f",
                        borderRight: borderStyle,
                        borderBottom: isLast ? borderStyle : 0,
                        borderTop: borderStyle,
                        bgcolor: "#f9fafd",
                        verticalAlign: "middle",
                        textAlign: "left",
                        minWidth: 140,
                        borderLeft: borderStyle
                      }}
                    >
                      {category.label}
                    </TableCell>
                  )}
                  {/* Hidden empty cell when not first metric in category, to keep columns aligned */}
                  {!isFirst && null}
                  <TableCell
                    sx={{
                      borderRight: borderStyle,
                      borderBottom: isLast ? borderStyle : "1px solid #f0f0f0",
                      borderTop: isFirst ? borderStyle : 0,
                      minWidth: 200,
                      bgcolor: "#fff"
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
                  {selectedModels.map((model, i) => (
                    <TableCell
                      key={model + "_" + metric}
                      align="center"
                      sx={{
                        borderRight: i === selectedModels.length - 1 ? "none" : borderStyle,
                        borderBottom: isLast ? borderStyle : "1px solid #f0f0f0",
                        borderTop: isFirst ? borderStyle : 0,
                        minWidth: 90,
                        bgcolor: "#fff"
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
          )}
        </TableBody>
      </Table>
    </Box>
  );
}
