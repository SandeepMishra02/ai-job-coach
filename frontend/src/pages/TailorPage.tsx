// src/pages/TailorPage.tsx
import { useState } from "react";
import { api } from "../api";

export default function TailorPage() {
  const [resume, setResume] = useState("");
  const [job, setJob] = useState("");
  const [style, setStyle] = useState("professional");
  const [length, setLength] = useState<"short" | "medium" | "long">("medium");
  const [out, setOut] = useState("");
  const [loading, setLoading] = useState(false);

  async function tailor() {
    if (!resume.trim() || !job.trim()) {
      alert("Paste your resume and the job description.");
      return;
    }
    setLoading(true);
    setOut("");
    try {
      const data = await api.tailorResume({
        resume,
        job_description: job,
        style,
        length,
      });
      setOut(data.tailored_resume);
    } catch (e) {
      console.error(e);
      setOut("An error occurred while tailoring the resume.");
    } finally {
      setLoading(false);
    }
  }

  function copy() {
    if (!out) return;
    navigator.clipboard.writeText(out);
    alert("Copied!");
  }

  return (
    <div className="grid">
      <section className="card">
        <header>Resume</header>
        <textarea
          rows={10}
          value={resume}
          onChange={(e) => setResume(e.target.value)}
          placeholder="Paste your resume"
        />
      </section>

      <section className="card">
        <header>Job Description</header>
        <textarea
          rows={10}
          value={job}
          onChange={(e) => setJob(e.target.value)}
          placeholder="Paste the job description"
        />
      </section>

      <section className="card row">
        <div className="field">
          <label>Style</label>
          <input
            value={style}
            onChange={(e) => setStyle(e.target.value)}
            placeholder="e.g. ‘results-driven’, ‘concise’, ‘senior’"
          />
        </div>
        <div className="field">
          <label>Length</label>
          <select value={length} onChange={(e) => setLength(e.target.value as any)}>
            <option value="short">Short</option>
            <option value="medium">Medium</option>
            <option value="long">Long</option>
          </select>
        </div>
        <div className="actions">
          <button onClick={tailor} disabled={loading}>
            {loading ? "Tailoring…" : "Tailor Resume"}
          </button>
        </div>
      </section>

      <section className="card">
        <header>Tailored Resume</header>
        <pre className="output">{out || "Output will appear here…"}</pre>
        <div className="actions">
          <button onClick={copy} disabled={!out}>
            Copy
          </button>
        </div>
      </section>
    </div>
  );
}
