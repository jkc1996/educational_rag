import { createTheme } from "@mui/material/styles";

export const theme = createTheme({
  palette: {
    mode: "light",
    primary: {
      main: "#1f6f68",
      dark: "#123f3b",
    },
    secondary: {
      main: "#7b4acb",
    },
    success: {
      main: "#23845f",
    },
    warning: {
      main: "#bd6b21",
    },
    error: {
      main: "#c64242",
    },
    info: {
      main: "#2d6cdf",
    },
    background: {
      default: "#f6f7f4",
      paper: "#ffffff",
    },
    text: {
      primary: "#17201f",
      secondary: "#5d6866",
    },
  },
  shape: {
    borderRadius: 8,
  },
  typography: {
    fontFamily: "'Inter', 'Segoe UI', Arial, sans-serif",
    h3: {
      fontWeight: 850,
      letterSpacing: 0,
    },
    h4: {
      fontWeight: 850,
      letterSpacing: 0,
    },
    h5: {
      fontWeight: 800,
      letterSpacing: 0,
    },
    h6: {
      fontWeight: 800,
      letterSpacing: 0,
    },
    button: {
      textTransform: "none",
      fontWeight: 700,
    },
  },
  components: {
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: "none",
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          fontWeight: 650,
        },
      },
    },
    MuiTableCell: {
      styleOverrides: {
        head: {
          fontWeight: 800,
        },
      },
    },
  },
});
