import MenuBookIcon from "@mui/icons-material/MenuBook";
import {
  AppBar,
  Box,
  Button,
  Chip,
  Stack,
  Toolbar,
  Typography,
} from "@mui/material";
import { NavLink, Outlet } from "react-router-dom";

const navItems = [
  { to: "/", label: "Documents" },
  { to: "/qa", label: "QA" },
  { to: "/question-paper", label: "Question Paper" },
  { to: "/evaluation", label: "RAGAS" },
  { to: "/usage", label: "Usage" },
  { to: "/logs", label: "Logs" },
];

export function AppShell({ apiBaseUrl }) {
  return (
    <Box className="app-surface">
      <AppBar position="sticky" elevation={0} sx={{ borderBottom: "1px solid rgba(255,255,255,0.2)" }}>
        <Toolbar sx={{ gap: 2, minHeight: 72 }}>
          <MenuBookIcon sx={{ fontSize: 34 }} />
          <Box sx={{ minWidth: 220 }}>
            <Typography variant="h6" fontWeight={850}>
              Educational RAG
            </Typography>
            <Typography variant="caption" sx={{ color: "rgba(255,255,255,0.78)" }}>
              OpenAI-only RAG workspace
            </Typography>
          </Box>

          <Stack direction="row" gap={0.75} flexWrap="wrap" sx={{ flex: 1 }}>
            {navItems.map((item) => (
              <Button
                key={item.to}
                component={NavLink}
                to={item.to}
                sx={{
                  color: "white",
                  px: 1.4,
                  "&.active": {
                    backgroundColor: "rgba(255,255,255,0.18)",
                  },
                }}
              >
                {item.label}
              </Button>
            ))}
          </Stack>

          <Chip
            label={apiBaseUrl.replace(/^https?:\/\//, "")}
            size="small"
            sx={{ bgcolor: "rgba(255,255,255,0.16)", color: "white", maxWidth: 240 }}
          />
        </Toolbar>
      </AppBar>

      <main className="content-shell">
        <Outlet />
      </main>
    </Box>
  );
}

