import  { useEffect, useState } from "react";
import { api } from "../api";

type Job = {
  id: number;
  source: string;
  board?: string | null;
  company: string;
  title: string;
  location?: string | null;
  url: string;
  remote?: boolean | null;
  posted_at?: string | null;
  created_at: string;
};

export default function JobsPage() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [q, setQ] = useState("");
  const [company, setCompany] = useState("");
  const [location, setLocation] = useState("");
  const [remote, setRemote] = useState<"" | "true" | "false">("");
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.listJobs({
        q: q || undefined,
        company: company || undefined,
        location: location || undefined,
        remote:
          remote === ""
            ? undefined
            : remote === "true"
            ? true
            : false,
      });
      setJobs(data);
    } catch (e: any) {
      setError(e.message || "Failed to load jobs");
    } finally {
      setLoading(false);
    }
  };

  const refresh = async () => {
    setRefreshing(true);
    setError(null);
    try {
      await api.refreshJobs();
      await load();
    } catch (e: any) {
      setError(e.message || "Failed to refresh");
    } finally {
      setRefreshing(false);
    }
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="page">
      <h2>Live SWE Internships</h2>

      <div className="controls row" style={{ gap: 8, alignItems: "center" }}>
        <input placeholder="Search title/company…" value={q} onChange={(e) => setQ(e.target.value)} />
        <input placeholder="Company filter" value={company} onChange={(e) => setCompany(e.target.value)} />
        <input placeholder="Location filter" value={location} onChange={(e) => setLocation(e.target.value)} />
        <select value={remote} onChange={(e) => setRemote(e.target.value as any)}>
          <option value="">Remote: Any</option>
          <option value="true">Remote</option>
          <option value="false">Onsite/Hybrid</option>
        </select>
        <button onClick={load} disabled={loading}>Search</button>
        <button onClick={refresh} disabled={refreshing}>{refreshing ? "Refreshing…" : "Refresh Feed"}</button>
      </div>

      {error && <div className="error">{error}</div>}
      {loading && <div className="muted">Loading jobs…</div>}

      <ul className="list">
        {jobs.map((j) => (
          <li key={j.id} className="card">
            <div className="row" style={{ justifyContent: "space-between" }}>
              <div>
                <div className="title">{j.title}</div>
                <div className="muted">
                  {j.company} · {j.location || "—"} {j.remote ? "· Remote" : ""}
                </div>
                <div className="muted small">
                  Source: {j.source}
                  {j.posted_at ? ` · Posted ${new Date(j.posted_at).toLocaleDateString()}` : ""}
                </div>
              </div>
              <div>
                <a className="btn" href={j.url} target="_blank" rel="noreferrer">View</a>
              </div>
            </div>
          </li>
        ))}
      </ul>

      {!loading && jobs.length === 0 && <div className="muted">No jobs match your filters.</div>}
    </div>
  );
}
