
import { useState } from "react";
import { api } from "../api";

export default function GeneratorPage() {
  const [resume, setResume] = useState("");
  const [job, setJob] = useState("");
  const [userName, setUserName] = useState("");
  const [company, setCompany] = useState("");
  const [style, setStyle] = useState<
    "concise" | "enthusiastic" | "professional" | "entry-level"
  >("professional");
  const [length, setLength] = useState<"short" | "medium" | "long">("medium");
  const [loading, setLoading] = useState(false);
  const [letter, setLetter] = useState("");

  async function onGenerate() {
    if (!resume.trim() || !job.trim()) {
      alert("Please paste your resume and a job description.");
      return;
    }
    setLoading(true);
    setLetter("");
    try {
      const data = await api.generateCoverLetter({
        resume,
        job_description: job,
        style,
        user_name: userName || undefined,
        company_name: company || undefined,
        length,
      });
      setLetter(data.cover_letter);
    } catch (e: any) {
      console.error(e);
      setLetter("An error occurred while generating the cover letter.");
    } finally {
      setLoading(false);
    }
  }

  function copy() {
    if (!letter) return;
    navigator.clipboard.writeText(letter);
    alert("Copied!");
  }

  function printPDF() {
    if (!letter) return;
    const w = window.open("", "_blank");
    if (!w) return;
    w.document.write(
      `<pre style="white-space:pre-wrap;font:14px/1.4 monospace;padding:24px;">${letter
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")}</pre>`
    );
    w.document.close();
    w.print();
  }

  return (
    <div className="grid">
      <section className="card">
        <header>Resume</header>
        <textarea
          value={resume}
          onChange={(e) => setResume(e.target.value)}
          rows={12}
          maxLength={25000}
          placeholder="Paste your resume here…"
        />
        <div className="counter">{resume.length} / 25,000</div>
      </section>

      <section className="card">
        <header>Job Description</header>
        <textarea
          value={job}
          onChange={(e) => setJob(e.target.value)}
          rows={12}
          maxLength={25000}
          placeholder="Paste the job description here…"
        />
        <div className="counter">{job.length} / 25,000</div>
      </section>

      <section className="card row">
        <div className="field">
          <label>Your Name (optional)</label>
          <input value={userName} onChange={(e) => setUserName(e.target.value)} />
        </div>
        <div className="field">
          <label>Company Name (optional)</label>
          <input value={company} onChange={(e) => setCompany(e.target.value)} />
        </div>
        <div className="field">
          <label>Style</label>
          <select
            value={style}
            onChange={(e) => setStyle(e.target.value as any)}
          >
            <option value="professional">Professional</option>
            <option value="concise">Concise</option>
            <option value="enthusiastic">Enthusiastic</option>
            <option value="entry-level">Entry Level</option>
          </select>
        </div>
        <div className="field">
          <label>Length</label>
          <select
            value={length}
            onChange={(e) => setLength(e.target.value as any)}
          >
            <option value="short">Short</option>
            <option value="medium">Medium</option>
            <option value="long">Long</option>
          </select>
        </div>

        <div className="actions">
          <button onClick={onGenerate} disabled={loading}>
            {loading ? "Generating…" : "Generate Cover Letter"}
          </button>
          <button className="ghost" onClick={() => setLetter("")}>
            Clear Output
          </button>
        </div>
      </section>

      <section className="card">
        <header>Generated Cover Letter</header>
        <pre className="output">{letter || "Your letter will appear here…"}</pre>
        <div className="actions">
          <button onClick={copy} disabled={!letter}>
            Copy to Clipboard
          </button>
          <button className="ghost" onClick={printPDF} disabled={!letter}>
            Print / Save as PDF
          </button>
        </div>
      </section>
    </div>
  );
}
