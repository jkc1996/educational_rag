import React from "react";
import { Select, MenuItem, Checkbox, ListItemText } from "@mui/material";
import { MODELS } from "../constants/models";

export default function ModelSelector({ multiple, value, onChange, disabled }) {
  return (
    <Select
      multiple={multiple}
      value={value}
      onChange={onChange}
      sx={{ minWidth: 200, background: "#f3f6fc", fontWeight: 500 }}
      disabled={disabled}
      size="small"
      renderValue={selected => multiple
        ? selected.map(val => MODELS.find(m => m.value === val)?.label).join(", ")
        : MODELS.find(m => m.value === value)?.label
      }
    >
      {MODELS.map(m => (
        <MenuItem key={m.value} value={m.value}>
          {multiple && <Checkbox checked={Array.isArray(value) ? value.includes(m.value) : false} />}
          <ListItemText primary={m.label} />
        </MenuItem>
      ))}
    </Select>
  );
}
