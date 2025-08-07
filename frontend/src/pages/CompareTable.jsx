import React, { useState } from "react";
import { Table, TableHead, TableRow, TableCell, TableBody, Box, Chip } from "@mui/material";
import { STATIC_COLS, getMetricColor } from "../utils/metricUtils";
import TruncatedCell from "./TruncatedCell";

// Always-on columns
const BASE_COLS = ["id", "question", "ground_truth"];

export default function CompareTable({
  alignedRows,
  selectedModels,
  metricsToShow,
  showContexts,
  metricLabels
}) {
  // State for expanding one cell at a time (rowIdx, colKey, model?)
  const [expandedCell, setExpandedCell] = useState(null);
  const makeExpandHandler = (rowIdx, colKey, model = null) => {
    return () => {
      const key = model ? `${rowIdx}-${colKey}-${model}` : `${rowIdx}-${colKey}`;
      setExpandedCell(expandedCell?.key === key ? null : { key });
    };
  };

  // Build table headers: base columns, (optionally Contexts), then for each top-level: Answer, each metric
  const metricColHeaders = [
    { label: "Answer", key: "answer" },
    ...metricsToShow.map(m => ({ label: metricLabels[m] || m, key: m })),
  ];

  return (
    <Box sx={{ overflowX: "auto", width: "100%" }}>
      <Table size="small" stickyHeader>
        <TableHead>
          <TableRow>
            {/* Static columns (Q#, Question, Ground Truth) */}
            {BASE_COLS.map(colKey => {
              const col = STATIC_COLS.find(c => c.key === colKey);
              return (
                <TableCell key={colKey} sx={{
                  fontWeight: 700,
                  background: "#f3f4f6",
                  minWidth:
                    colKey === "id" ? 28 :
                    colKey === "question" ? 180 :
                    colKey === "ground_truth" ? 180 : 60,
                  maxWidth:
                    colKey === "question" ? 260 :
                    colKey === "ground_truth" ? 260 : 80,
                  fontSize: 14,
                  verticalAlign: "top",
                  textAlign: colKey === "id" ? "center" : "left"
                }}>
                  {col.label}
                </TableCell>
              );
            })}
            {/* Contexts header if enabled */}
            {showContexts && (
              <TableCell
                key="contexts"
                sx={{
                  fontWeight: 700,
                  background: "#f3f4f6",
                  minWidth: 180,
                  maxWidth: 240,
                  fontSize: 14,
                  verticalAlign: "top"
                }}
              >
                Contexts
              </TableCell>
            )}
            {/* For each top header (Answer, metric...) put colSpan = selectedModels.length */}
            {metricColHeaders.map(header => (
              <TableCell
                key={header.key}
                align="center"
                colSpan={selectedModels.length}
                sx={{
                  background: "#e0eefa",
                  fontWeight: 700,
                  fontSize: 14,
                  borderLeft: "2px solid #c8d8f8",
                  textAlign: "center"
                }}
              >
                {header.label}
              </TableCell>
            ))}
          </TableRow>
          <TableRow>
            {/* Empty cells for static columns */}
            {BASE_COLS.map(colKey => <TableCell key={colKey} />)}
            {showContexts && <TableCell key="contexts" />}
            {/* For each top-level col (Answer, metrics...) show a cell per model */}
            {metricColHeaders.map(header =>
              selectedModels.map(model => (
                <TableCell key={header.key + "-" + model} align="center" sx={{
                  background: "#f6fafd",
                  fontWeight: 600,
                  fontSize: 13,
                  borderLeft: "1px solid #ddeefd",
                  textAlign: "center"
                }}>
                  {model.toUpperCase()}
                </TableCell>
              ))
            )}
          </TableRow>
        </TableHead>
        <TableBody>
          {alignedRows.map((row, idx) => (
            <TableRow key={row.id || idx}>
              {/* Static columns */}
              {BASE_COLS.map(colKey => (
                <TableCell key={colKey}>
                  <TruncatedCell
                    value={row[colKey]}
                    isExpanded={expandedCell?.key === `${idx}-${colKey}`}
                    onToggle={makeExpandHandler(idx, colKey)}
                    maxLines={2}
                  />
                </TableCell>
              ))}
              {showContexts && (
                <TableCell key="contexts">
                  <TruncatedCell
                    value={Array.isArray(row["contexts"]) ? row["contexts"].join(" || ") : row["contexts"]}
                    isExpanded={expandedCell?.key === `${idx}-contexts`}
                    onToggle={makeExpandHandler(idx, "contexts")}
                    maxLines={2}
                  />
                </TableCell>
              )}
              {/* For each metric column, render one cell per model */}
              {metricColHeaders.map(header =>
                selectedModels.map(model => {
                  // Show as TruncatedCell for "answer", Chip for metric
                  const val = header.key === "answer"
                    ? (row[model]?.answer)
                    : row[model]?.[header.key];

                  if (header.key === "answer") {
                    return (
                      <TableCell key={header.key + "-" + model}>
                        <TruncatedCell
                          value={val}
                          isExpanded={expandedCell?.key === `${idx}-${header.key}-${model}`}
                          onToggle={makeExpandHandler(idx, header.key, model)}
                          maxLines={2}
                        />
                      </TableCell>
                    );
                  }
                  return (
                    <TableCell key={header.key + "-" + model} align="center">
                      <Chip
                        label={typeof val === "number" ? val.toFixed(3) : "-"}
                        size="small"
                        sx={{
                          bgcolor: getMetricColor(val),
                          color: "#111",
                          fontWeight: 600,
                          fontSize: 14,
                          px: 1,
                          minWidth: 40,
                          borderRadius: 1.3,
                          border: "1px solid #e0e0e0",
                        }}
                      />
                    </TableCell>
                  );
                })
              )}
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </Box>
  );
}
