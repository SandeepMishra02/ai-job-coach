// src/App.tsx
import { useState } from "react";
import GeneratorPage from "./pages/GeneratorPage.tsx";
import ApplicationsPage from "./pages/ApplicationsPage.tsx";
import AnalyticsPage from "./pages/AnalyticsPage.tsx";
import InterviewPage from "./pages/InterviewPage.tsx";
import TailorPage from "./pages/TailorPage.tsx";

import { BASE_URL } from "./api";

type Tab =
  | "generator"
  | "applications"
  | "analytics"
  | "interview"
  | "tailor";

export default function App() {
  const [tab, setTab] = useState<Tab>("generator");

  return (
    <div className="app">
      <header className="app-header">
        <div className="brand">
          AI Job Coach <span className="tag">v1.1</span>
        </div>
        <nav className="tabs">
          <button
            className={tab === "generator" ? "active" : ""}
            onClick={() => setTab("generator")}
          >
            Generator
          </button>
          <button
            className={tab === "applications" ? "active" : ""}
            onClick={() => setTab("applications")}
          >
            Applications
          </button>
          <button
            className={tab === "analytics" ? "active" : ""}
            onClick={() => setTab("analytics")}
          >
            Analytics
          </button>
          <button
            className={tab === "interview" ? "active" : ""}
            onClick={() => setTab("interview")}
          >
            Interview Coach
          </button>
          <button
            className={tab === "tailor" ? "active" : ""}
            onClick={() => setTab("tailor")}
          >
            Resume Tailor
          </button>
        </nav>
      </header>

      <main className="page">
        {tab === "generator" && <GeneratorPage />}
        {tab === "applications" && <ApplicationsPage />}
        {tab === "analytics" && <AnalyticsPage />}
        {tab === "interview" && <InterviewPage />}
        {tab === "tailor" && <TailorPage />}
      </main>

      <footer className="app-footer">
        <span>
          Backend: <a href={BASE_URL}>{BASE_URL || "ENV NOT SET"}</a>
        </span>
        <span>© 2025 AI Job Coach. For demos and practice.</span>
      </footer>
    </div>
  );
}
