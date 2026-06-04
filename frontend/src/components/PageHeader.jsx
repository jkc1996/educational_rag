import { Box, Typography } from "@mui/material";

export function PageHeader({ title, description }) {
  return (
    <Box sx={{ mb: 3 }}>
      <Typography variant="h4" color="primary.dark">
        {title}
      </Typography>
      {description && (
        <Typography color="text.secondary" sx={{ mt: 0.5, maxWidth: 820 }}>
          {description}
        </Typography>
      )}
    </Box>
  );
}

