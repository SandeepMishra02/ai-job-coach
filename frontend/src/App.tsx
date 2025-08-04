import React, { useState } from "react";
import axios from "axios";

function App() {
  const [resume, setResume] = useState("");
  const [jobDesc, setJobDesc] = useState("");
  const [result, setResult] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await axios.post("http://localhost:8000/generate-cover-letter", {
        resume,
        job_description: jobDesc,
      });
      setResult(res.data.cover_letter);
    } catch (error) {
      console.error(error);
      setResult("Something went wrong. Check the backend.");
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col items-center justify-center p-8">
      <h1 className="text-3xl font-bold mb-4">AI Job Coach</h1>
      <form
        onSubmit={handleSubmit}
        className="bg-white shadow p-6 rounded w-full max-w-xl space-y-4"
      >
        <textarea
          placeholder="Paste your resume here..."
          className="w-full border p-3 rounded"
          value={resume}
          onChange={(e) => setResume(e.target.value)}
        />
        <textarea
          placeholder="Paste job description here..."
          className="w-full border p-3 rounded"
          value={jobDesc}
          onChange={(e) => setJobDesc(e.target.value)}
        />
        <button
          type="submit"
          className="w-full bg-blue-600 text-white p-3 rounded hover:bg-blue-700"
        >
          Generate Cover Letter
        </button>
      </form>

      {result && (
        <div className="mt-6 p-4 bg-white rounded shadow max-w-xl w-full">
          <h2 className="text-lg font-semibold mb-2">Generated Cover Letter:</h2>
          <pre className="whitespace-pre-wrap text-sm text-gray-700">{result}</pre>
        </div>
      )}
    </div>
  );
}

export default App;
