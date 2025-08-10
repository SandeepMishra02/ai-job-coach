export const BASE_URL =
  (import.meta.env.VITE_BACKEND_URL as string | undefined)?.replace(/\/+$/, "") ||
  "";

async function request<T>(
  path: string,
  options: RequestInit & { json?: Record<string, unknown> } = {}
): Promise<T> {
  const url = `${BASE_URL}${path}`;
  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };

  const res = await fetch(url, {
    method: options.method || "GET",
    headers,
    body: options.json ? JSON.stringify(options.json) : options.body,
  });

  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`HTTP ${res.status} on ${path} – ${text || res.statusText}`);
  }
  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

// ---- Endpoints ----
export type Application = {
  id: number;
  company: string;
  role: string;
  status: "applied" | "interview" | "offer" | "rejected";
  date_applied: string; // ISO date
  notes?: string;
};

export type AnalyticsOverview = {
  total_applications: number;
  by_status: Record<string, number>;
  by_company: Record<string, number>;
  by_month: Record<string, number>;
  avg_days_to_response?: number | null;
};

export const api = {
  // Generator
  generateCoverLetter: (payload: {
    resume: string;
    job_description: string;
    style?: "concise" | "enthusiastic" | "professional" | "entry-level";
    user_name?: string | null;
    company_name?: string | null;
    length?: "short" | "medium" | "long";
  }) =>
    request<{ cover_letter: string }>("/generate-cover-letter", {
      method: "POST",
      json: payload,
    }),

  // Resume tailor
  tailorResume: (payload: {
    resume: string;
    job_description: string;
    style?: string;
    length?: "short" | "medium" | "long";
  }) =>
    request<{ tailored_resume: string }>("/resume/tailor", {
      method: "POST",
      json: payload,
    }),

  // Interview coach
  interviewCoach: (message: string) =>
    request<{ reply: string }>("/interview/coach", {
      method: "POST",
      json: { message },
    }),

  // Applications
  listApplications: () => request<Application[]>("/applications"),
  createApplication: (app: Omit<Application, "id">) =>
    request<Application>("/applications", { method: "POST", json: app }),
  updateApplication: (id: number, app: Partial<Application>) =>
    request<Application>(`/applications/${id}`, { method: "PUT", json: app }),
  deleteApplication: (id: number) =>
    request<void>(`/applications/${id}`, { method: "DELETE" }),

  // Analytics
  analyticsOverview: () => request<AnalyticsOverview>("/analytics/overview"),
};
