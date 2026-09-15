import { useState } from "react";

function App() {
  // Holds what the user is currently typing
  const [question, setQuestion] = useState("");

  // Holds the most recent answer and its sources, once received
  const [result, setResult] = useState(null);

  // Tracks whether a request is currently in progress, so the UI can
  // show a loading state instead of looking frozen or unresponsive
  const [loading, setLoading] = useState(false);

  function handleAsk() {
    if (!question.trim()) return;

    setLoading(true);
    setResult(null);

    fetch("http://localhost:3000/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    })
      .then((res) => res.json())
      .then((data) => {
        setResult(data);
        setLoading(false);
      });
  }

  return (
    <div className="p-8 max-w-2xl mx-auto">
      <h1 className="text-2xl font-semibold text-gray-900 mb-1">
        FastAPI Knowledge Assistant
      </h1>
      <p className="text-gray-500 mb-6">
        Ask a question about FastAPI, answered from the actual documentation.
      </p>

      <div className="flex gap-2 mb-6">
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="How do I make a query parameter optional?"
          className="flex-1 border border-gray-300 rounded-md px-3 py-2 text-sm"
        />
        <button
          onClick={handleAsk}
          className="px-4 py-2 rounded-md text-sm font-semibold bg-indigo-600 text-white hover:bg-indigo-700"
        >
          Ask
        </button>
      </div>

      {loading && <p className="text-gray-500">Thinking...</p>}

      {result && (
        <div className="border border-gray-200 rounded-md p-4">
          <p className="text-gray-900 mb-3">{result.answer}</p>
          {result.sources.length > 0 && (
            <>
              <p className="text-xs text-gray-400 uppercase font-semibold mb-1">
                Sources
              </p>
              <ul className="text-xs text-gray-500">
                {result.sources.map((source) => (
                  <li key={source}>{source}</li>
                ))}
              </ul>
            </>
          )}
        </div>
      )}
    </div>
  );
}

export default App;
