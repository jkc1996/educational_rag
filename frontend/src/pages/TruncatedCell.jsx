import React, { useRef, useEffect, useState } from "react";
import { Box, IconButton } from "@mui/material";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";

export default function TruncatedCell({ value, isExpanded, onToggle, maxLines = 3 }) {
  const boxRef = useRef(null);
  const [isOverflowing, setIsOverflowing] = useState(false);

  useEffect(() => {
    if (boxRef.current && !isExpanded) {
      setIsOverflowing(boxRef.current.scrollHeight > boxRef.current.clientHeight + 2);
    }
  }, [value, isExpanded, maxLines]);

  const shouldShowExpand = (isOverflowing && !isExpanded) || isExpanded;

  return (
    <Box
      ref={boxRef}
      sx={{
        position: "relative",
        overflow: isExpanded ? "visible" : "hidden",
        display: "-webkit-box",
        WebkitLineClamp: isExpanded ? "unset" : maxLines,
        WebkitBoxOrient: "vertical",
        whiteSpace: isExpanded ? "pre-line" : "normal",
        textOverflow: "ellipsis",
        cursor: shouldShowExpand ? "pointer" : "default",
        pr: shouldShowExpand ? 3 : 0,
        background: isExpanded ? "#f9fafb" : "inherit",
        transition: "all 0.2s",
        minHeight: "1em",
      }}
      onClick={shouldShowExpand ? onToggle : undefined}
    >
      {value}
      {shouldShowExpand && (
        <IconButton
          size="small"
          onClick={e => { e.stopPropagation(); onToggle(); }}
          sx={{
            position: "absolute", right: 0, top: 2, bgcolor: "#fff", p: "2px", zIndex: 2,
          }}
          aria-label={isExpanded ? "Collapse" : "Expand"}
        >
          <ExpandMoreIcon
            sx={{
              fontSize: 18,
              transform: isExpanded ? "rotate(180deg)" : "rotate(0deg)",
              transition: "0.2s"
            }}
          />
        </IconButton>
      )}
      {isOverflowing && !isExpanded && (
        <Box
          sx={{
            position: "absolute", left: 0, right: 0, bottom: 0, height: "1em",
            background: "linear-gradient(180deg,transparent, #fff 100%)",
            pointerEvents: "none"
          }}
        />
      )}
    </Box>
  );
}
