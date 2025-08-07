import React from "react";
import { Dialog, DialogTitle, DialogContent, Typography, IconButton, Box } from "@mui/material";
import CloseIcon from "@mui/icons-material/Close";

const metricInfo = [
  {
    category: "Retrieval Metrics",
    metrics: [
      {
        name: "context_precision",
        desc: "Proportion of retrieved context that is actually relevant to the ground truth answer."
      },
      {
        name: "context_recall",
        desc: "Proportion of relevant ground truth context that was actually retrieved."
      },
      {
        name: "faithfulness",
        desc: "Measures whether the answer is supported by the retrieved context."
      },
    ]
  },
  {
    category: "Nvidia Metrics",
    metrics: [
      {
        name: "nv_accuracy",
        desc: "Measures if the answer is correct according to NVIDIA’s ground truth (used for benchmark datasets)."
      },
      {
        name: "nv_context_relevance",
        desc: "Assesses how relevant the retrieved context is for the answer (NVIDIA eval)."
      },
      {
        name: "nv_response_groundedness",
        desc: "Measures if the model’s answer is grounded in the provided context (NVIDIA eval)."
      }
    ]
  },
  {
    category: "Language Metrics",
    metrics: [
      {
        name: "factual_correctness(mode=f1)",
        desc: "F1-based correctness of the answer compared to the ground truth."
      },
      {
        name: "semantic_similarity",
        desc: "Semantic similarity between the predicted and the true answer."
      },
      {
        name: "bleu_score",
        desc: "Measures n-gram overlap between the answer and the reference (BLEU)."
      },
      {
        name: "rouge_score(mode=fmeasure)",
        desc: "Measures overlap in word sequences (ROUGE F-measure)."
      },
      {
        name: "string_present",
        desc: "Binary check: is the ground truth string present in the answer?"
      },
      {
        name: "exact_match",
        desc: "Checks if the answer matches the ground truth exactly."
      }
    ]
  }
];

export default function MatrixInfoDialog({ open, onClose }) {
  return (
    <Dialog
      open={open}
      onClose={onClose}
      fullWidth
      maxWidth="lg"
      PaperProps={{
        sx: { borderRadius: 3, minHeight: 440 }
      }}
    >
      <DialogTitle sx={{ fontWeight: 700, fontSize: 22, pb: 1 }}>
        <Box display="flex" alignItems="center" justifyContent="space-between">
          Metric Explanations
          <IconButton onClick={onClose} sx={{ ml: 2 }}>
            <CloseIcon />
          </IconButton>
        </Box>
      </DialogTitle>
      <DialogContent dividers>
        {metricInfo.map(cat => (
          <Box key={cat.category} mb={3}>
            <Typography sx={{ fontWeight: 700, color: "#163872", mb: 1.2 }} variant="h6">
              {cat.category}
            </Typography>
            {cat.metrics.map(m => (
              <Box key={m.name} mb={1} pl={2}>
                <Typography sx={{ display: "inline-block", fontFamily: "monospace", fontWeight: 600, color: "#273985", mr: 1 }}>
                  {m.name}:
                </Typography>
                <Typography sx={{ display: "inline", color: "#333" }}>
                  {m.desc}
                </Typography>
              </Box>
            ))}
          </Box>
        ))}
      </DialogContent>
    </Dialog>
  );
}
