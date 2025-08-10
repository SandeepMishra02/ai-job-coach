// src/pages/ApplicationsPage.tsx
import { useEffect, useMemo, useState } from "react";
import { api } from "../api";
import type { Application } from "../api";

const STATUSES: Application["status"][] = [
  "applied",
  "interview",
  "offer",
  "rejected",
];

const emptyForm: Omit<Application, "id"> = {
  company: "",
  role: "",
  status: "applied",
  date_applied: new Date().toISOString().slice(0, 10),
  notes: "",
};

export default function ApplicationsPage() {
  const [items, setItems] = useState<Application[]>([]);
  const [loading, setLoading] = useState(false);
  const [filter, setFilter] = useState<{ status?: string; q?: string }>({});
  const [editing, setEditing] = useState<Application | null>(null);
  const [form, setForm] = useState<Omit<Application, "id">>(emptyForm);

  async function refresh() {
    setLoading(true);
    try {
      const data = await api.listApplications();
      setItems(data);
    } catch (e) {
      console.error(e);
      alert("Failed to load applications.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    refresh();
  }, []);

  const filtered = useMemo(() => {
    return items.filter((it) => {
      if (filter.status && it.status !== filter.status) return false;
      if (filter.q) {
        const q = filter.q.toLowerCase();
        if (
          !`${it.company} ${it.role} ${it.notes || ""}`.toLowerCase().includes(q)
        )
          return false;
      }
      return true;
    });
  }, [items, filter]);

  function startNew() {
    setEditing(null);
    setForm(emptyForm);
    (document.getElementById("app-modal") as HTMLDialogElement).showModal();
  }

  function startEdit(app: Application) {
    setEditing(app);
    setForm({
      company: app.company,
      role: app.role,
      status: app.status,
      date_applied: app.date_applied.slice(0, 10),
      notes: app.notes || "",
    });
    (document.getElementById("app-modal") as HTMLDialogElement).showModal();
  }

  async function onSave() {
    try {
      if (editing) {
        const updated = await api.updateApplication(editing.id, form);
        setItems((prev) => prev.map((p) => (p.id === updated.id ? updated : p)));
      } else {
        const created = await api.createApplication(form);
        setItems((prev) => [created, ...prev]);
      }
      (document.getElementById("app-modal") as HTMLDialogElement).close();
    } catch (e) {
      console.error(e);
      alert("Save failed.");
    }
  }

  async function onDelete(id: number) {
    if (!confirm("Delete this application?")) return;
    try {
      await api.deleteApplication(id);
      setItems((prev) => prev.filter((p) => p.id !== id));
    } catch (e) {
      console.error(e);
      alert("Delete failed.");
    }
  }

  return (
    <div className="stack">
      <section className="card row">
        <div className="field">
          <label>Status</label>
          <select
            value={filter.status || ""}
            onChange={(e) =>
              setFilter((f) => ({
                ...f,
                status: e.target.value || undefined,
              }))
            }
          >
            <option value="">All</option>
            {STATUSES.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </div>
        <div className="field">
          <label>Search</label>
          <input
            placeholder="Company / Role / Notes"
            value={filter.q || ""}
            onChange={(e) => setFilter((f) => ({ ...f, q: e.target.value }))}
          />
        </div>
        <div className="actions">
          <button onClick={refresh} disabled={loading}>
            {loading ? "Loading…" : "Refresh"}
          </button>
          <button onClick={startNew}>Add Application</button>
        </div>
      </section>

      <section className="card">
        <header>Applications</header>
        <div className="table">
          <div className="thead">
            <div>Company</div>
            <div>Role</div>
            <div>Status</div>
            <div>Applied</div>
            <div>Notes</div>
            <div>Actions</div>
          </div>
          {filtered.map((it) => (
            <div className="trow" key={it.id}>
              <div>{it.company}</div>
              <div>{it.role}</div>
              <div className={`pill ${it.status}`}>{it.status}</div>
              <div>{it.date_applied.slice(0, 10)}</div>
              <div className="ellipsis">{it.notes}</div>
              <div className="row gap">
                <button className="sm ghost" onClick={() => startEdit(it)}>
                  Edit
                </button>
                <button className="sm danger" onClick={() => onDelete(it.id)}>
                  Delete
                </button>
              </div>
            </div>
          ))}
          {filtered.length === 0 && (
            <div className="trow empty">No applications yet.</div>
          )}
        </div>
      </section>

      <dialog id="app-modal">
        <form
          method="dialog"
          className="modal"
          onSubmit={(e) => {
            e.preventDefault();
            onSave();
          }}
        >
          <h3>{editing ? "Edit Application" : "Add Application"}</h3>
          <div className="row">
            <div className="field">
              <label>Company</label>
              <input
                required
                value={form.company}
                onChange={(e) =>
                  setForm((f) => ({ ...f, company: e.target.value }))
                }
              />
            </div>
            <div className="field">
              <label>Role</label>
              <input
                required
                value={form.role}
                onChange={(e) => setForm((f) => ({ ...f, role: e.target.value }))}
              />
            </div>
            <div className="field">
              <label>Status</label>
              <select
                value={form.status}
                onChange={(e) =>
                  setForm((f) => ({ ...f, status: e.target.value as any }))
                }
              >
                {STATUSES.map((s) => (
                  <option key={s} value={s}>
                    {s}
                  </option>
                ))}
              </select>
            </div>
            <div className="field">
              <label>Date Applied</label>
              <input
                type="date"
                value={form.date_applied}
                onChange={(e) =>
                  setForm((f) => ({ ...f, date_applied: e.target.value }))
                }
              />
            </div>
          </div>
          <div className="field">
            <label>Notes</label>
            <textarea
              rows={4}
              value={form.notes}
              onChange={(e) => setForm((f) => ({ ...f, notes: e.target.value }))}
            />
          </div>
          <div className="actions right">
            <button
              type="button"
              className="ghost"
              onClick={() =>
                (document.getElementById("app-modal") as HTMLDialogElement).close()
              }
            >
              Cancel
            </button>
            <button type="submit">Save</button>
          </div>
        </form>
      </dialog>
    </div>
  );
}

