import React from "react";
import { BrowserRouter as Router, Routes, Route, useLocation, useNavigate } from "react-router-dom";
import UploadPage from "./pages/UploadPage";
import QAPage from "./pages/QAPage";
import {
  AppBar, Toolbar, Typography, Tabs, Tab, Box
} from "@mui/material";
import MenuBookIcon from "@mui/icons-material/MenuBook";

function NavTabs() {
  const location = useLocation();
  const navigate = useNavigate();
  const tabValue = location.pathname === "/qa" ? 1 : 0;

  const handleTabChange = (_, newValue) => {
    if (newValue === 0) navigate("/");
    if (newValue === 1) navigate("/qa");
  };

  return (
    <Tabs
      value={tabValue}
      onChange={handleTabChange}
      indicatorColor="secondary"
      textColor="inherit"
      centered
      sx={{
        ml: "auto",
        "& .MuiTab-root": {
          fontWeight: 700,
          letterSpacing: "0.04em",
          fontSize: 16,
          color: "#fff",
          opacity: 1,
          minWidth: 150,
        },
        "& .Mui-selected": {
          color: "#fff",
          borderBottom: "3px solid #ffbe0b"
        }
      }}
    >
      <Tab label="UPLOAD PDF" disableRipple />
      <Tab label="ASK QUESTION" disableRipple />
    </Tabs>
  );
}

function App() {
  return (
    <Router>
      <AppBar position="fixed" color="primary" elevation={2}>
        <Toolbar sx={{ minHeight: 90, px: 4 }}>
          <MenuBookIcon sx={{ fontSize: 46, color: "#fff", mr: 2 }} />
          <Typography
            variant="h4"
            noWrap
            sx={{
              fontWeight: 900,
              letterSpacing: "0.02em",
              fontFamily: "Montserrat, Roboto, Arial",
              color: "#fff",
              fontSize: 28,
            }}
          >
            edu-rag Academic QA System
          </Typography>
          <NavTabs />
        </Toolbar>
      </AppBar>
      {/* Main Content (spaced down for AppBar) */}
      <Box sx={{ mt: 11, bgcolor: "#f7f8fa", minHeight: "100vh", px: { xs: 1, md: 5 } }}>
        <Routes>
          <Route path="/" element={<UploadPage />} />
          <Route path="/qa" element={<QAPage />} />
        </Routes>
      </Box>
    </Router>
  );
}

export default App;
