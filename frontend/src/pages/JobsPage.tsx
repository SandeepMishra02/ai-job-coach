import { useEffect, useMemo, useState } from "react";
import { BASE_URL } from "../api"; // uses your existing api.ts BASE_URL

type Job = {
  source?: "lever" | "greenhouse" | string;
  company?: string;
  title?: string;
  location?: string;
  url?: string;
  createdAt?: number | string | null;
  updatedAt?: number | string | null;
  ts?: number; // backend-normalized unix seconds (if present)
};

type Mode = "Any" | "Onsite/Hybrid" | "Remote";

function toUnixSeconds(v?: number | string | null): number {
  if (v == null) return 0;
  if (typeof v === "number") {
    return v > 10_000_000_000 ? v / 1000 : v; // ms → s
  }
  const s = String(v).trim();
  if (/^\d+$/.test(s)) {
    const n = parseInt(s, 10);
    return n > 10_000_000_000 ? n / 1000 : n;
  }
  try {
    const iso = s.endsWith("Z") ? s.replace("Z", "+00:00") : s;
    const t = Date.parse(iso);
    return isNaN(t) ? 0 : Math.floor(t / 1000);
  } catch {
    return 0;
  }
}

function timeAgo(sec: number): string {
  if (!sec) return "";
  const diff = Math.max(0, Math.floor(Date.now() / 1000) - sec);
  if (diff < 60) return `${diff}s ago`;
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
  return `${Math.floor(diff / 86400)}d ago`;
}

export default function JobsPage() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [view, setView] = useState<Job[]>([]);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // filters
  const [search, setSearch] = useState("");
  const [company, setCompany] = useState("");
  const [location, setLocation] = useState("");
  const [mode, setMode] = useState<Mode>("Any");

  // initial load
  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        setLoading(true);
        setError(null);
        const res = await fetch(`${BASE_URL}/jobs`, {
          headers: { "Content-Type": "application/json" },
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data: Job[] = await res.json();

        // make sure we can sort even if backend didn't add ts
        const normalized = (data || []).map((j) => ({
          ...j,
          ts: j.ts ?? toUnixSeconds(j.updatedAt ?? j.createdAt),
        }));

        if (mounted) {
          // newest first
          normalized.sort((a, b) => (b.ts || 0) - (a.ts || 0));
          setJobs(normalized);
          setView(normalized); // show everything by default
        }
      } catch (e: any) {
        if (mounted) setError(e?.message || "Failed to load jobs.");
      } finally {
        if (mounted) setLoading(false);
      }
    })();
    return () => {
      mounted = false;
    };
  }, []);

  const onRefresh = async () => {
    try {
      setRefreshing(true);
      setError(null);
      const res = await fetch(`${BASE_URL}/jobs/refresh`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      });
      if (!res.ok) {
        const t = await res.text().catch(() => "");
        throw new Error(`HTTP ${res.status} on /jobs/refresh – ${t}`);
      }
      // after refresh, re-list
      const r2 = await fetch(`${BASE_URL}/jobs`);
      const data: Job[] = await r2.json();
      const normalized = (data || []).map((j) => ({
        ...j,
        ts: j.ts ?? toUnixSeconds(j.updatedAt ?? j.createdAt),
      }));
      normalized.sort((a, b) => (b.ts || 0) - (a.ts || 0));
      setJobs(normalized);
      setView(normalized);
    } catch (e: any) {
      setError(e?.message || "Refresh failed.");
    } finally {
      setRefreshing(false);
    }
  };

  const filtered = useMemo(() => {
    const s = search.trim().toLowerCase();
    const c = company.trim().toLowerCase();
    const l = location.trim().toLowerCase();

    return jobs.filter((j) => {
      const title = (j.title || "").toLowerCase();
      const comp = (j.company || "").toLowerCase();
      const loc = (j.location || "").toLowerCase();

      const titleMatch =
        !s || title.includes(s) || comp.includes(s); // search matches title or company
      const companyMatch = !c || comp.includes(c);
      const locationMatch = !l || loc.includes(l);

      // If you ever map "Onsite/Hybrid"/"Remote" explicitly, check here.
      const modeMatch = mode === "Any" || !mode;

      return titleMatch && companyMatch && locationMatch && modeMatch;
    });
  }, [jobs, search, company, location, mode]);

  const onSearch = () => setView(filtered);
  const onClear = () => {
    setSearch("");
    setCompany("");
    setLocation("");
    setMode("Any");
    setView(jobs); // reset to all
  };

  return (
    <div className="page">
      <h2>Live SWE Internships</h2>

      <div className="toolbar" style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
        <input
          placeholder="Search title/company..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="input"
          style={{ width: 220 }}
        />
        <input
          placeholder="Company filter"
          value={company}
          onChange={(e) => setCompany(e.target.value)}
          className="input"
          style={{ width: 200 }}
        />
        <input
          placeholder="Location filter"
          value={location}
          onChange={(e) => setLocation(e.target.value)}
          className="input"
          style={{ width: 200 }}
        />
        <select value={mode} onChange={(e) => setMode(e.target.value as Mode)} className="input">
          <option>Any</option>
          <option>Onsite/Hybrid</option>
          <option>Remote</option>
        </select>

        <button className="btn" onClick={onSearch}>Search</button>
        <button className="btn" onClick={onClear}>Clear</button>
        <button className="btn" onClick={onRefresh} disabled={refreshing}>
          {refreshing ? "Refreshing..." : "Refresh Feed"}
        </button>
      </div>

      {loading && <div className="muted" style={{ marginTop: 12 }}>Loading jobs…</div>}
      {error && (
        <div className="error" style={{ marginTop: 12 }}>
          {error}
        </div>
      )}

      {!loading && !error && (
        <>
          <div className="muted" style={{ margin: "12px 0" }}>
            Showing {view.length} of {jobs.length} jobs
          </div>

          {view.length === 0 ? (
            <div className="muted">No jobs match your filters.</div>
          ) : (
            <ul className="jobs-list" style={{ listStyle: "none", padding: 0, marginTop: 8 }}>
              {view.map((j, idx) => {
                const ts = j.ts ?? toUnixSeconds(j.updatedAt ?? j.createdAt);
                return (
                  <li
                    key={`${j.url || j.title || "job"}-${idx}`}
                    className="job-card"
                    style={{
                      border: "1px solid var(--border)",
                      borderRadius: 8,
                      padding: 12,
                      marginBottom: 10,
                      background: "var(--card)",
                    }}
                  >
                    <div style={{ display: "flex", justifyContent: "space-between", gap: 8 }}>
                      <div>
                        <div style={{ fontWeight: 600 }}>
                          {j.title || "(Untitled role)"}{" "}
                          <span className="muted">• {j.company || "Unknown company"}</span>
                        </div>
                        <div className="muted" style={{ marginTop: 4 }}>
                          {(j.location || "Location n/a")} • {j.source || "source n/a"}
                        </div>
                      </div>
                      <div className="muted">{timeAgo(ts)}</div>
                    </div>
                    {j.url && (
                      <div style={{ marginTop: 8 }}>
                        <a href={j.url} target="_blank" rel="noreferrer" className="link">
                          View posting →
                        </a>
                      </div>
                    )}
                  </li>
                );
              })}
            </ul>
          )}
        </>
      )}
    </div>
  );
}
