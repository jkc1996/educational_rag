import { Box, Paper, Stack, Typography } from "@mui/material";

export function WorkspaceLayout({ children, inspector }) {
  return (
    <Box className="workspace-grid">
      <Box sx={{ minWidth: 0 }}>{children}</Box>
      {inspector && <Box className="workspace-inspector">{inspector}</Box>}
    </Box>
  );
}

export function WorkPanel({ children, sx = {}, ...props }) {
  return (
    <Paper className="work-panel" sx={{ p: 2.5, overflow: "hidden", ...sx }} {...props}>
      {children}
    </Paper>
  );
}

export function KpiCard({ label, value, helper, tone = "primary" }) {
  const toneColor = {
    primary: "primary.dark",
    secondary: "secondary.main",
    success: "success.main",
    warning: "warning.main",
    error: "error.main",
    muted: "text.secondary",
  }[tone];

  return (
    <Paper className="work-panel" sx={{ p: 2, minHeight: 96 }}>
      <Typography variant="body2" color="text.secondary">
        {label}
      </Typography>
      <Typography variant="h5" color={toneColor || "primary.dark"} sx={{ mt: 0.4 }}>
        {value}
      </Typography>
      {helper && (
        <Typography variant="caption" color="text.secondary">
          {helper}
        </Typography>
      )}
    </Paper>
  );
}

export function EmptyState({ icon, title, description, action }) {
  return (
    <Box className="muted-band" sx={{ p: 3, textAlign: "center" }}>
      <Stack alignItems="center" gap={1}>
        {icon}
        <Typography variant="h6">{title}</Typography>
        {description && (
          <Typography color="text.secondary" sx={{ maxWidth: 520 }}>
            {description}
          </Typography>
        )}
        {action}
      </Stack>
    </Box>
  );
}
