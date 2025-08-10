
import { useEffect, useState } from "react";
import { api } from "../api";
import type { AnalyticsOverview } from "../api";

function Bar({ label, value, max }: { label: string; value: number; max: number }) {
  const pct = max ? Math.round((value / max) * 100) : 0;
  return (
    <div className="bar">
      <div className="bar-label">{label}</div>
      <div className="bar-track">
        <div className="bar-fill" style={{ width: `${pct}%` }} />
      </div>
      <div className="bar-value">{value}</div>
    </div>
  );
}

export default function AnalyticsPage() {
  const [data, setData] = useState<AnalyticsOverview | null>(null);
  const [loading, setLoading] = useState(false);

  async function refresh() {
    setLoading(true);
    try {
      const res = await api.analyticsOverview();
      setData(res);
    } catch (e) {
      console.error(e);
      alert("Failed to load analytics.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    refresh();
  }, []);

  const maxByStatus = data ? Math.max(1, ...Object.values(data.by_status)) : 1;
  const maxByCo = data ? Math.max(1, ...Object.values(data.by_company)) : 1;
  const maxByMonth = data ? Math.max(1, ...Object.values(data.by_month)) : 1;

  return (
    <div className="stack">
      <section className="card row">
        <div className="stat">
          <div className="stat-num">{data?.total_applications ?? "—"}</div>
          <div className="stat-label">Total Applications</div>
        </div>
        <div className="stat">
          <div className="stat-num">
            {data?.avg_days_to_response != null
              ? Math.round(data.avg_days_to_response)
              : "—"}
          </div>
          <div className="stat-label">Avg Days to Response</div>
        </div>
        <div className="actions">
          <button onClick={refresh} disabled={loading}>
            {loading ? "Loading…" : "Refresh"}
          </button>
        </div>
      </section>

      <section className="card">
        <header>By Status</header>
        {data ? (
          Object.entries(data.by_status).map(([k, v]) => (
            <Bar key={k} label={k} value={v} max={maxByStatus} />
          ))
        ) : (
          <div>Loading…</div>
        )}
      </section>

      <section className="card">
        <header>By Company</header>
        {data ? (
          Object.entries(data.by_company).map(([k, v]) => (
            <Bar key={k} label={k} value={v} max={maxByCo} />
          ))
        ) : (
          <div>Loading…</div>
        )}
      </section>

      <section className="card">
        <header>By Month</header>
        {data ? (
          Object.entries(data.by_month).map(([k, v]) => (
            <Bar key={k} label={k} value={v} max={maxByMonth} />
          ))
        ) : (
          <div>Loading…</div>
        )}
      </section>
    </div>
  );
}

