import { Chip } from "@mui/material";

const colorByStatus = {
  uploaded: "default",
  processing: "warning",
  completed: "success",
  failed: "error",
};

export function StatusChip({ status }) {
  return <Chip size="small" label={status || "unknown"} color={colorByStatus[status] || "default"} />;
}

