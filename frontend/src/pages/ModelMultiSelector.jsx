import React from "react";
import { FormControl, InputLabel, Select, MenuItem, Checkbox, ListItemText } from "@mui/material";

export default function ModelMultiSelector({ selected, onChange, options, sx }) {
  return (
    <FormControl sx={{ ...sx }}>
      <InputLabel id="model-multi-label">Models</InputLabel>
      <Select
        size="small"
        labelId="model-multi-label"
        multiple
        value={selected}
        onChange={e => onChange(e.target.value)}
        renderValue={selected => selected.map(
          v => options.find(opt => opt.value === v)?.label || v
        ).join(", ")}
      >
        {options.map(opt => (
          <MenuItem key={opt.value} value={opt.value}>
            <Checkbox checked={selected.indexOf(opt.value) > -1} />
            <ListItemText primary={opt.label} />
          </MenuItem>
        ))}
      </Select>
    </FormControl>
  );
}
