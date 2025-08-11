import { useState } from "react";
import { api } from "../api";

type TailorPageProps = {
  onBack: () => void;
};

export default function TailorPage({ onBack }: TailorPageProps) {
  const [resume, setResume] = useState("");
  const [jobDescription, setJobDescription] = useState("");
  const [focus, setFocus] = useState<"skills" | "experience" | "impact">("skills");
  const [length, setLength] = useState<"short" | "medium" | "long">("medium");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState("");

  async function handleTailor() {
    setLoading(true);
    setError(null);
    setResult("");

    try {
      // Keep api.ts unchanged — if its typing differs, we coerce just this call.
      const res = await api.tailorResume({
        resume,
        job_description: jobDescription,
        // Map our UI focus to API's "style" – some versions of api.ts expect this

        style: focus,
        length,
      } as any);

      // Support both shapes without changing api.ts:
      const text =
        // @ts-ignore – handle either response key
        (res as any)?.tailored_resume ??
        // @ts-ignore
        (res as any)?.tailored ??
        "";

      setResult(text);
    } catch (err) {
      console.error(err);
      setError("An error occurred while tailoring the resume.");
    } finally {
      setLoading(false);
    }
  }

  function handleCopy() {
    if (!result) return;
    navigator.clipboard.writeText(result).catch(() => {});
  }

  function handleClear() {
    setResult("");
    setError(null);
    setLoading(false);
  }

  return (
    <div className="page">
      <header className="app-header">
        <div className="brand">Resume Tailor</div>
        <div className="toolbar">
          <button className="btn" onClick={onBack} aria-label="Back to main">
            ← Back
          </button>
        </div>
      </header>

      <main className="grid-2">
        <section className="card">
          <h3>Resume</h3>
          <textarea
            value={resume}
            onChange={(e) => setResume(e.target.value)}
            rows={12}
            placeholder="Paste your resume text here…"
          />
          <div className="muted right">{resume.length} chars</div>
        </section>

        <section className="card">
          <h3>Job Description</h3>
          <textarea
            value={jobDescription}
            onChange={(e) => setJobDescription(e.target.value)}
            rows={12}
            placeholder="Paste the job description here…"
          />
          <div className="muted right">{jobDescription.length} chars</div>
        </section>

        <section className="card row">
          <div className="field">
            <label>Focus</label>
            <select value={focus} onChange={(e) => setFocus(e.target.value as any)}>
              <option value="skills">Skills</option>
              <option value="experience">Experience</option>
              <option value="impact">Impact</option>
            </select>
          </div>

          <div className="field">
            <label>Length</label>
            <select value={length} onChange={(e) => setLength(e.target.value as any)}>
              <option value="short">Short</option>
              <option value="medium">Medium</option>
              <option value="long">Long</option>
            </select>
          </div>

          <div className="spacer" />

          <div className="buttons">
            <button className="btn primary" onClick={handleTailor} disabled={loading}>
              {loading ? "Tailoring…" : "Tailor Resume"}
            </button>
            <button className="btn" onClick={handleClear} disabled={loading && !result}>
              Clear
            </button>
            <button className="btn" onClick={onBack}>
              Back
            </button>
          </div>
        </section>

        <section className="card col-span-2">
          <h3>Tailored Resume</h3>

          {error && <div className="error">{error}</div>}
          {!error && !result && !loading && (
            <div className="muted">Your tailored resume will appear here…</div>
          )}
          {loading && <div className="muted">Working on it…</div>}

          {result && (
            <>
              <pre className="output">{result}</pre>
              <div className="buttons">
                <button className="btn" onClick={handleCopy}>
                  Copy to Clipboard
                </button>
                <button className="btn" onClick={onBack}>
                  Done / Back
                </button>
              </div>
            </>
          )}
        </section>
      </main>
    </div>
  );
}
