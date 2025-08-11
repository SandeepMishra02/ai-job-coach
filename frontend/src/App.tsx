import { useEffect, useState } from "react";

import GeneratorPage from "./pages/GeneratorPage";
import ApplicationsPage from "./pages/ApplicationsPage";
import AnalyticsPage from "./pages/AnalyticsPage";
import InterviewPage from "./pages/InterviewPage";
import TailorPage from "./pages/TailorPage";
import JobsPage from "./pages/JobsPage";

import "./App.css";

type Tab = "generator" | "applications" | "analytics" | "interview" | "tailor" | "jobs";

export default function App() {
  const [tab, setTab] = useState<Tab>("generator");

  // Optional global setter for debugging/navigation from console
  useEffect(() => {
    (window as any).setAppTab = (t: Tab) => setTab(t);
    return () => { delete (window as any).setAppTab; };
  }, []);

  return (
    <div className="app">
      <header className="app-header">
        <div className="brand">AI Job Coach v1.1</div>
        <nav className="tabs">
          <button className={tab === "generator" ? "active" : ""} onClick={() => setTab("generator")}>
            Generator
          </button>
          <button className={tab === "applications" ? "active" : ""} onClick={() => setTab("applications")}>
            Applications
          </button>
          <button className={tab === "analytics" ? "active" : ""} onClick={() => setTab("analytics")}>
            Analytics
          </button>
          <button className={tab === "interview" ? "active" : ""} onClick={() => setTab("interview")}>
            Interview Coach
          </button>
          <button className={tab === "tailor" ? "active" : ""} onClick={() => setTab("tailor")}>
            Resume Tailor
          </button>
          {/* ⬇️ New Jobs tab */}
          <button className={tab === "jobs" ? "active" : ""} onClick={() => setTab("jobs")}>
            Jobs
          </button>
        </nav>
      </header>

      <main className="content">
        {tab === "generator" && <GeneratorPage />}
        {tab === "applications" && <ApplicationsPage />}
        {tab === "analytics" && <AnalyticsPage />}
        {tab === "interview" && <InterviewPage />}
        {tab === "tailor" && (
          <TailorPage
            onBack={() => setTab("generator")}
            // If you prefer to return to whatever tab you were on:
            // onBack={() => setTab(prevTabRef.current)}
          />
        )}
        {/* ⬇️ Render Jobs page */}
        {tab === "jobs" && <JobsPage />}
      </main>
    </div>
  );
}
