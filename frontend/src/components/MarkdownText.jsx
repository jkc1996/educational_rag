import { Box, Link, Typography } from "@mui/material";
import ReactMarkdown from "react-markdown";
import rehypeKatex from "rehype-katex";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";
import "katex/dist/katex.min.css";

function normalizeMathDelimiters(value) {
  return String(value || "")
    .replace(/\\\[((?:.|\n)*?)\\\]/g, (_, math) => `\n\n$$\n${math.trim()}\n$$\n\n`)
    .replace(/\\\((.+?)\\\)/g, (_, math) => `$${math.trim()}$`);
}

export function MarkdownText({ children }) {
  return (
    <Box
      className="markdown-text"
      sx={{
        "& .katex-display": {
          overflowX: "auto",
          overflowY: "hidden",
          py: 1,
          px: 1.5,
          my: 1.5,
          bgcolor: "rgba(35, 79, 124, 0.05)",
          border: "1px solid rgba(35, 79, 124, 0.16)",
          borderRadius: 1,
        },
        "& .katex": {
          fontSize: "1.02em",
        },
      }}
    >
      <ReactMarkdown
        remarkPlugins={[remarkGfm, remarkMath]}
        rehypePlugins={[[rehypeKatex, { throwOnError: false, strict: false }]]}
        components={markdownComponents}
      >
        {normalizeMathDelimiters(children)}
      </ReactMarkdown>
    </Box>
  );
}

const markdownComponents = {
  h1: ({ children }) => (
    <Typography variant="h5" sx={{ mt: 2.5, mb: 1, fontWeight: 750 }}>
      {children}
    </Typography>
  ),
  h2: ({ children }) => (
    <Typography variant="h6" sx={{ mt: 2.25, mb: 0.75, fontWeight: 750 }}>
      {children}
    </Typography>
  ),
  h3: ({ children }) => (
    <Typography variant="subtitle1" sx={{ mt: 2, mb: 0.75, fontWeight: 750 }}>
      {children}
    </Typography>
  ),
  p: ({ children }) => (
    <Typography variant="body1" sx={{ mb: 1.5, lineHeight: 1.7 }}>
      {children}
    </Typography>
  ),
  ul: ({ children }) => (
    <Box component="ul" sx={{ mt: 0.5, mb: 1.5, pl: 3, "& li": { mb: 0.45 } }}>
      {children}
    </Box>
  ),
  ol: ({ children }) => (
    <Box component="ol" sx={{ mt: 0.5, mb: 1.5, pl: 3, "& li": { mb: 0.45 } }}>
      {children}
    </Box>
  ),
  li: ({ children }) => (
    <Typography component="li" variant="body1" sx={{ lineHeight: 1.65 }}>
      {children}
    </Typography>
  ),
  a: ({ href, children }) => (
    <Link href={href} target="_blank" rel="noreferrer">
      {children}
    </Link>
  ),
  code: ({ className, children }) => {
    const isBlock = className?.startsWith("language-");
    if (isBlock) {
      return (
        <Box component="code" className={className} sx={{ fontFamily: "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" }}>
          {children}
        </Box>
      );
    }
    return (
      <Box
        component="code"
        sx={{
          px: 0.5,
          py: 0.15,
          borderRadius: 0.75,
          bgcolor: "grey.100",
          fontFamily: "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace",
          fontSize: "0.92em",
        }}
      >
        {children}
      </Box>
    );
  },
  pre: ({ children }) => (
    <Box
      component="pre"
      sx={{
        p: 1.5,
        mb: 1.5,
        overflowX: "auto",
        borderRadius: 1,
        bgcolor: "grey.100",
        border: "1px solid",
        borderColor: "divider",
      }}
    >
      {children}
    </Box>
  ),
  table: ({ children }) => (
    <Box sx={{ overflowX: "auto", mb: 1.5 }}>
      <Box component="table" sx={{ borderCollapse: "collapse", minWidth: 420, "& th, & td": { border: "1px solid", borderColor: "divider", p: 1 } }}>
        {children}
      </Box>
    </Box>
  ),
};
