import AssignmentOutlinedIcon from "@mui/icons-material/AssignmentOutlined";
import AutoAwesomeOutlinedIcon from "@mui/icons-material/AutoAwesomeOutlined";
import InsightsOutlinedIcon from "@mui/icons-material/InsightsOutlined";
import SchoolOutlinedIcon from "@mui/icons-material/SchoolOutlined";
import SourceOutlinedIcon from "@mui/icons-material/SourceOutlined";
import TerminalOutlinedIcon from "@mui/icons-material/TerminalOutlined";
import { Box, Chip, Stack, Tooltip, Typography } from "@mui/material";
import { NavLink, Outlet, useLocation } from "react-router-dom";

const navItems = [
  { to: "/", label: "Ask", icon: AutoAwesomeOutlinedIcon },
  { to: "/sources", label: "Sources", icon: SourceOutlinedIcon },
  { to: "/assessment", label: "Assess", icon: AssignmentOutlinedIcon },
  { to: "/evaluate", label: "Evaluate", icon: InsightsOutlinedIcon },
  { to: "/monitor", label: "Monitor", icon: TerminalOutlinedIcon },
];

const pageLabels = {
  "/": { title: "Ask Workspace", subtitle: "Grounded answers with evidence trace" },
  "/sources": { title: "Source Library", subtitle: "Upload, index, and cache summaries" },
  "/assessment": { title: "Assessment Studio", subtitle: "Generate papers from structured summaries" },
  "/evaluate": { title: "RAGAS Evaluation", subtitle: "Compare retrieval and answer quality" },
  "/monitor": { title: "System Monitor", subtitle: "Usage telemetry and application flow logs" },
};

export function AppShell({ apiBaseUrl }) {
  const location = useLocation();
  const current = pageLabels[location.pathname] || pageLabels["/"];

  return (
    <Box className="app-surface workbench-shell">
      <aside className="workbench-rail">
        <Tooltip title="Educational RAG" placement="right">
          <Box className="brand-mark">
            <SchoolOutlinedIcon />
          </Box>
        </Tooltip>

        <Stack gap={0.75} component="nav" aria-label="Primary navigation">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink key={item.to} to={item.to} end={item.to === "/"} className="rail-link">
                <Icon />
                <span>{item.label}</span>
              </NavLink>
            );
          })}
        </Stack>
      </aside>

      <Box className="workbench-main">
        <Box className="context-bar">
          <Box
            sx={{
              width: "min(1440px, calc(100% - 32px))",
              mx: "auto",
              minHeight: 64,
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              gap: 2,
            }}
          >
            <Box sx={{ minWidth: 0 }}>
              <Typography variant="subtitle1" fontWeight={850}>
                {current.title}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {current.subtitle}
              </Typography>
            </Box>
            <Stack direction="row" gap={1} alignItems="center" flexWrap="wrap" justifyContent="flex-end">
              <Chip size="small" label="OpenAI only" color="primary" variant="outlined" />
              <Chip
                size="small"
                label={apiBaseUrl.replace(/^https?:\/\//, "")}
                sx={{ maxWidth: 260 }}
              />
            </Stack>
          </Box>
        </Box>

        <main className="content-shell">
          <Outlet />
        </main>
      </Box>
    </Box>
  );
}
