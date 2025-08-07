import { useState } from "react";
import "./App.css";

function App() {
  const [resume, setResume] = useState("");
  const [jobDescription, setJobDescription] = useState("");
  const [coverLetter, setCoverLetter] = useState("");
  const [loading, setLoading] = useState(false);

  // Optional if you want to support dynamic fields later
  // const [userName, setUserName] = useState("");
  // const [companyName, setCompanyName] = useState("");

  const generateCoverLetter = async () => {
    setLoading(true);
    setCoverLetter("");
    try {
      const response = await fetch(`${import.meta.env.VITE_BACKEND_URL}/generate-cover-letter`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          resume,
          job_description: jobDescription,
          // user_name: userName,
          // company_name: companyName
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to generate cover letter");
      }

      const data = await response.json();
      setCoverLetter(data.cover_letter);
    } catch (error) {
      console.error("Error generating cover letter:", error);
      setCoverLetter("An error occurred while generating the cover letter.");
    } finally {
      setLoading(false);
    }
  };

  // ✅ Copy cover letter to clipboard
  const copyToClipboard = () => {
    if (coverLetter) {
      navigator.clipboard.writeText(coverLetter);
      alert("Cover letter copied to clipboard!");
    }
  };

  // ✅ Download cover letter as .txt
  const downloadCoverLetter = () => {
    if (coverLetter) {
      const blob = new Blob([coverLetter], { type: "text/plain" });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.download = "cover_letter.txt";
      link.href = url;
      link.click();
      URL.revokeObjectURL(url);
    }
  };

  return (
    <div style={{ maxWidth: 800, margin: "auto", padding: 20 }}>
      <h1>AI Cover Letter Generator</h1>

      <label>Resume:</label>
      <textarea
        value={resume}
        onChange={(e) => setResume(e.target.value)}
        rows={6}
        style={{ width: "100%" }}
      />

      <label>Job Description:</label>
      <textarea
        value={jobDescription}
        onChange={(e) => setJobDescription(e.target.value)}
        rows={6}
        style={{ width: "100%" }}
      />

      {/* Optional inputs */}
      {/* <label>Your Name:</label>
      <input
        type="text"
        value={userName}
        onChange={(e) => setUserName(e.target.value)}
        style={{ width: "100%", marginBottom: 10 }}
      />

      <label>Company Name:</label>
      <input
        type="text"
        value={companyName}
        onChange={(e) => setCompanyName(e.target.value)}
        style={{ width: "100%", marginBottom: 10 }}
      /> */}

      <button onClick={generateCoverLetter} disabled={loading} style={{ marginTop: 10 }}>
        {loading ? "Generating..." : "Generate Cover Letter"}
      </button>

      {loading && <p>Generating your cover letter, please wait...</p>}

      {!loading && coverLetter && (
        <>
          <h2>Generated Cover Letter</h2>
          <pre>{coverLetter}</pre>

          {/* 📋 Copy and 📄 Download buttons */}
          <div style={{ marginTop: 10 }}>
            <button onClick={copyToClipboard} style={{ marginRight: 10 }}>
              Copy to Clipboard
            </button>
            <button onClick={downloadCoverLetter}>Download</button>
          </div>
        </>
      )}
    </div>
  );
}


export default App;
