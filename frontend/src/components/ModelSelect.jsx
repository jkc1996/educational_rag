import { FormControl, InputLabel, MenuItem, Select } from "@mui/material";

export function ModelSelect({ models, value, onChange, label = "Model", disabled = false }) {
  const selected = value || models.find((model) => model.default)?.id || models[0]?.id || "";

  return (
    <FormControl fullWidth size="small">
      <InputLabel>{label}</InputLabel>
      <Select
        label={label}
        value={selected}
        onChange={(event) => onChange(event.target.value)}
        disabled={disabled || models.length === 0}
      >
        {models.length === 0 && (
          <MenuItem value="" disabled>
            No models configured
          </MenuItem>
        )}
        {models.map((model) => (
          <MenuItem key={model.id} value={model.id}>
            {model.label} ({model.role})
          </MenuItem>
        ))}
      </Select>
    </FormControl>
  );
}
