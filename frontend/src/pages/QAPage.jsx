import React, { useState } from "react";
import axios from "axios";

const SUBJECTS = [
  "Machine Learning",
  "Natural Language Processing"
];

const LLMS = [
  { value: "gemini", label: "Gemini (Google)" },
  { value: "groq", label: "Groq (Llama3)" },
  { value: "ollama", label: "Ollama (Local)" }
];

function QAPage() {
  const [subject, setSubject] = useState("");
  const [question, setQuestion] = useState("");
  const [llmChoice, setLlmChoice] = useState("gemini");
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setAnswer("");

    if (!subject || !question) {
      setError("Please select subject and enter your question.");
      return;
    }

    setLoading(true);

    const formData = new FormData();
    formData.append("subject", subject);
    formData.append("question", question);
    formData.append("llm_choice", llmChoice);

    try {
      const res = await axios.post("http://localhost:8000/ask-question/", formData);
      setAnswer(res.data.answer);
    } catch (err) {
      setError("Error getting answer from server.");
    }
    setLoading(false);
  };

  return (
    <div>
      <h2>Ask a Question</h2>
      <form onSubmit={handleSubmit} style={{ maxWidth: 500 }}>
        <div>
          <label>Subject:</label>
          <select
            value={subject}
            onChange={e => setSubject(e.target.value)}
            required
            style={{ width: "100%", marginBottom: 8 }}
          >
            <option value="">Select Subject</option>
            {SUBJECTS.map(s => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
        </div>
        <div>
          <label>Question:</label>
          <input
            type="text"
            value={question}
            onChange={e => setQuestion(e.target.value)}
            placeholder="Type your question"
            required
            style={{ width: "100%", marginBottom: 8 }}
          />
        </div>
        <div>
          <label>LLM:</label>
          <select
            value={llmChoice}
            onChange={e => setLlmChoice(e.target.value)}
            style={{ width: "100%", marginBottom: 8 }}
          >
            {LLMS.map(llm => (
              <option key={llm.value} value={llm.value}>{llm.label}</option>
            ))}
          </select>
        </div>
        <button type="submit" disabled={loading}>
          {loading ? "Getting Answer..." : "Ask"}
        </button>
      </form>
      {error && <p style={{ color: "red" }}>{error}</p>}
      {answer && (
        <div style={{ marginTop: 16, background: "#f9f9f9", padding: 12, borderRadius: 8 }}>
          <strong>Answer:</strong>
          <div>{answer}</div>
        </div>
      )}
    </div>
  );
}

export default QAPage;
