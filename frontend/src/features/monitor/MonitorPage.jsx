import ReceiptLongOutlinedIcon from "@mui/icons-material/ReceiptLongOutlined";
import TerminalOutlinedIcon from "@mui/icons-material/TerminalOutlined";
import { Box, Tab, Tabs } from "@mui/material";
import { useState } from "react";

import { PageHeader } from "../../components/PageHeader.jsx";
import { LogsPage } from "../logs/LogsPage.jsx";
import { UsagePage } from "../usage/UsagePage.jsx";

export function MonitorPage() {
  const [tab, setTab] = useState("usage");

  return (
    <>
      <PageHeader
        eyebrow="Operational View"
        title="Monitor"
        description="Inspect OpenAI token spend, pricing snapshots, request IDs, and app-wide flow traces from one place."
      />

      <Box sx={{ borderBottom: 1, borderColor: "divider", mb: 2 }}>
        <Tabs value={tab} onChange={(_, value) => setTab(value)} aria-label="Monitor sections">
          <Tab icon={<ReceiptLongOutlinedIcon />} iconPosition="start" label="Usage" value="usage" />
          <Tab icon={<TerminalOutlinedIcon />} iconPosition="start" label="Logs" value="logs" />
        </Tabs>
      </Box>

      {tab === "usage" ? <UsagePage embedded /> : <LogsPage embedded />}
    </>
  );
}
