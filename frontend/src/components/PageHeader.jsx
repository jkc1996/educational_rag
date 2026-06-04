import { Box, Chip, Stack, Typography } from "@mui/material";

export function PageHeader({ title, description, eyebrow, actions }) {
  return (
    <Box sx={{ mb: 3, display: "flex", justifyContent: "space-between", gap: 2, alignItems: { xs: "stretch", md: "flex-start" }, flexDirection: { xs: "column", md: "row" } }}>
      <Box>
        {eyebrow && <Chip size="small" label={eyebrow} color="primary" variant="outlined" sx={{ mb: 1 }} />}
        <Typography variant="h4" color="primary.dark">
          {title}
        </Typography>
        {description && (
          <Typography color="text.secondary" sx={{ mt: 0.75, maxWidth: 820 }}>
            {description}
          </Typography>
        )}
      </Box>
      {actions && (
        <Stack direction="row" gap={1} justifyContent="flex-end" flexWrap="wrap">
          {actions}
        </Stack>
      )}
    </Box>
  );
}
