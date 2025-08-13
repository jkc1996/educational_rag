import React from "react";
import { Table, TableHead, TableRow, TableCell, TableBody, Chip } from "@mui/material";
import { STATIC_COLS, METRIC_LABELS, getMetricColor } from "../utils/metricUtils";
import TruncatedCell from "./TruncatedCell";
import { resolveMetricValue } from "../utils/metricUtils";

export default function MetricTable({
  results, metricsToShow, expandedCell, setExpandedCell, showContexts
}) {
  if (!results) return null;

  // Define column width and header style for static columns
  const colHeaderSx = colKey => ({
    fontWeight: 700,
    background: "#f3f4f6",
    fontSize: 15,
    whiteSpace: "normal",
    wordBreak: "break-word",
    textAlign: "left",
    lineHeight: 1.15,
    px: 1.7,
    py: 1.5,
    minWidth:
      colKey === "id" ? 15 :
      colKey === "question" ? 130 :
      colKey === "answer" ? 160 :
      colKey === "ground_truth" ? 140 :
      undefined,
    maxWidth:
      colKey === "id" ? 25 :
      colKey === "question" ? 150 :
      colKey === "answer" ? 180 :
      colKey === "ground_truth" ? 160 :
      undefined,
  });

  const metricHeaderSx = {
    textAlign: "center",
    fontWeight: 700,
    background: "#f3f4f6",
    minWidth: 85,
    maxWidth: 110,
    fontSize: 14,
    whiteSpace: "normal",
    wordBreak: "break-word",
    lineHeight: 1.15,
    px: 1.7,
    py: 1.5,
  };

  return (
    <Table size="small" stickyHeader sx={{ minWidth: 800 + metricsToShow.length * 100 }}>
      <TableHead>
        <TableRow>
          {STATIC_COLS.map(col => (
            <TableCell key={col.key} sx={colHeaderSx(col.key)}>
              {col.label}
            </TableCell>
          ))}
          {showContexts && (
            <TableCell
              key="contexts"
              sx={{
                ...colHeaderSx("contexts"),
                minWidth: 120,
                maxWidth: 160,
              }}
            >
              Contexts
            </TableCell>
          )}
          {metricsToShow.map(metric => (
            <TableCell key={metric} sx={metricHeaderSx}>
              {METRIC_LABELS[metric] || metric}
            </TableCell>
          ))}
        </TableRow>
      </TableHead>
      <TableBody>
        {results.map((row, idx) => (
          <TableRow key={row.id || idx}>
            {STATIC_COLS.map(col => {
              const shouldTruncate = ["question", "answer", "ground_truth", "contexts"].includes(col.key);
              const val = Array.isArray(row[col.key]) ? row[col.key].join(" || ") : row[col.key];
              const cellId = `${row.id || idx}-${col.key}`;
              const isExpanded = expandedCell && expandedCell.cellId === cellId;
              return (
                <TableCell
                  key={col.key}
                  sx={{
                    minWidth:
                      col.key === "id" ? 15 :
                      col.key === "question" ? 130 :
                      col.key === "answer" ? 160 :
                      col.key === "ground_truth" ? 140 :
                      undefined,
                    maxWidth:
                      col.key === "id" ? 25 :
                      col.key === "question" ? 150 :
                      col.key === "answer" ? 180 :
                      col.key === "ground_truth" ? 160 :
                      undefined,
                    fontSize: 14,
                    verticalAlign: "top",
                    whiteSpace: "normal",
                    wordBreak: "break-word",
                    position: "relative",
                  }}
                >
                  {shouldTruncate
                    ? (
                      <TruncatedCell
                        value={val}
                        isExpanded={isExpanded}
                        onToggle={() => setExpandedCell(isExpanded ? null : { cellId })}
                        maxLines={3}
                      />
                    )
                    : val
                  }
                </TableCell>
              );
            })}
            {showContexts && (
              <TableCell
                key="contexts"
                sx={{
                  minWidth: 160,
                  maxWidth: 180,
                  fontSize: 14,
                  verticalAlign: "top",
                  whiteSpace: "normal",
                  wordBreak: "break-word",
                  position: "relative",
                }}
              >
                <TruncatedCell
                  value={Array.isArray(row["contexts"]) ? row["contexts"].join(" || ") : row["contexts"]}
                  isExpanded={expandedCell && expandedCell.cellId === `${row.id || idx}-contexts`}
                  onToggle={() =>
                    setExpandedCell(
                      expandedCell && expandedCell.cellId === `${row.id || idx}-contexts`
                        ? null
                        : { cellId: `${row.id || idx}-contexts` }
                    )
                  }
                  maxLines={3}
                />
              </TableCell>
            )}
            {metricsToShow.map(metric => {
              let val = resolveMetricValue(row, metric);
              if (typeof val === "object" && val !== null && typeof val.score === "number") val = val.score;
              return (
                <TableCell key={metric} sx={{ textAlign: "center" }}>
                  <Chip
                    label={typeof val === "number" ? val.toFixed(3) : "-"}
                    size="small"
                    sx={{
                      bgcolor: getMetricColor(val),
                      color: "#111",
                      fontWeight: 600,
                      fontSize: 14,
                      px: 0.8,
                      minWidth: 40,
                      borderRadius: 1.3,
                      boxShadow: "0 1px 2px rgba(0,0,0,0.07)",
                      border: "1px solid #e0e0e0",
                    }}
                  />
                </TableCell>
              );
            })}
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
