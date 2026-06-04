import { FormControl, InputLabel, MenuItem, Select } from "@mui/material";

export function SubjectSelect({ subjects, value, onChange, label = "Subject", disabled = false }) {
  return (
    <FormControl fullWidth size="small">
      <InputLabel>{label}</InputLabel>
      <Select label={label} value={value} onChange={(event) => onChange(event.target.value)} disabled={disabled}>
        <MenuItem value="" disabled>
          Select subject
        </MenuItem>
        {subjects.map((subject) => (
          <MenuItem key={subject} value={subject}>
            {subject}
          </MenuItem>
        ))}
      </Select>
    </FormControl>
  );
}
