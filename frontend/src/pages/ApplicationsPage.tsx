import { useEffect, useState } from "react";
import { api, type Application } from "../api";

const EMPTY: Application[] = [];

export default function ApplicationsPage() {
  const [items, setItems] = useState<Application[]>(EMPTY);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // form state
  const [company, setCompany] = useState("");
  const [role, setRole] = useState("");
  const [status, setStatus] = useState<Application["status"]>("applied");
  const [date, setDate] = useState(() => new Date().toISOString().slice(0, 10));
  const [notes, setNotes] = useState("");

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.listApplications();
      setItems(Array.isArray(data) ? data : []);
    } catch (e: any) {
      setError(e.message || "Failed to load applications");
      setItems([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const add = async () => {
    try {
      const created = await api.createApplication({
        company: company.trim(),
        role: role.trim(),
        status,
        date_applied: date,
        notes: notes.trim() || undefined,
      });
      setItems((prev) => [created, ...prev]);
      setCompany("");
      setRole("");
      setStatus("applied");
      setNotes("");
    } catch (e: any) {
      alert(e.message || "Create failed");
    }
  };

  const update = async (id: number, patch: Partial<Application>) => {
    try {
      const upd = await api.updateApplication(id, patch);
      setItems((prev) => prev.map((a) => (a.id === id ? upd : a)));
    } catch (e: any) {
      alert(e.message || "Update failed");
    }
  };

  const remove = async (id: number) => {
    if (!confirm("Delete this application?")) return;
    try {
      await api.deleteApplication(id);
      setItems((prev) => prev.filter((x) => x.id !== id));
    } catch (e: any) {
      alert(e.message || "Delete failed");
    }
  };

  return (
    <div className="page">
      <h2>Applications</h2>

      <div className="grid three">
        <input placeholder="Company" value={company} onChange={(e) => setCompany(e.target.value)} />
        <input placeholder="Role" value={role} onChange={(e) => setRole(e.target.value)} />
        <select value={status} onChange={(e) => setStatus(e.target.value as Application["status"])}>
          <option value="applied">applied</option>
          <option value="interview">interview</option>
          <option value="offer">offer</option>
          <option value="rejected">rejected</option>
        </select>

        <input type="date" value={date} onChange={(e) => setDate(e.target.value)} />
        <input placeholder="Notes (optional)" value={notes} onChange={(e) => setNotes(e.target.value)} />
        <button onClick={add}>Add</button>
      </div>

      {loading && <p>Loading…</p>}
      {error && <p className="error">{error}</p>}

      <table className="striped">
        <thead>
          <tr>
            <th>Company</th>
            <th>Role</th>
            <th>Status</th>
            <th>Date</th>
            <th>Notes</th>
            <th />
          </tr>
        </thead>
        <tbody>
          {items.map((a) => (
            <tr key={a.id}>
              <td>{a.company}</td>
              <td>{a.role}</td>
              <td>
                <select
                  value={a.status}
                  onChange={(e) => update(a.id, { status: e.target.value as Application["status"] })}
                >
                  <option value="applied">applied</option>
                  <option value="interview">interview</option>
                  <option value="offer">offer</option>
                  <option value="rejected">rejected</option>
                </select>
              </td>
              <td>{a.date_applied || "-"}</td>
              <td>{a.notes || "-"}</td>
              <td>
                <button onClick={() => remove(a.id)}>Delete</button>
              </td>
            </tr>
          ))}
          {!loading && items.length === 0 && (
            <tr>
              <td colSpan={6} style={{ textAlign: "center" }}>
                No applications yet.
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}



