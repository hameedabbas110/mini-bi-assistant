
import { useState } from "react";
import "./App.css";

function App() {
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const examples = [
    "What is the total revenue?",
    "Which product generated the highest revenue?",
    "What is the monthly revenue trend?",
    "Which region generated the highest sales?",
    "Compare revenue between 2026-01 and 2026-02",
  ];

  async function askQuestion(text = question) {
    if (!text.trim()) {
      setError("Please enter a question.");
      return;
    }

    setQuestion(text);
    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await fetch("http://127.0.0.1:5000/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: text }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Request failed.");
      }

      setResult(data);
    } catch (err) {
      setError(
        err.message.includes("fetch")
          ? "Cannot connect to the backend. Make sure Flask is running on port 5000."
          : err.message
      );
    } finally {
      setLoading(false);
    }
  }

  function formatValue(value) {
    if (value === null || value === undefined) return "N/A";
    if (typeof value === "number") {
      return value.toLocaleString("en-IN", {
        maximumFractionDigits: 2,
      });
    }
    return String(value);
  }

  function answerSummary() {
    if (!result) return "";

    const a = result.answer;

    switch (result.intent) {
      case "total_revenue":
        return `Total revenue is ${formatValue(a.total_revenue)} across ${formatValue(a.transaction_count)} completed transactions.`;

      case "top_product":
        return a
          ? `${a.product} generated the highest revenue: ${formatValue(a.revenue)}.`
          : "No product data is available.";

      case "top_region":
        return a
          ? `${a.region} generated the highest revenue: ${formatValue(a.revenue)}.`
          : "No region data is available.";

      case "monthly_revenue":
        return "Here is the monthly revenue trend calculated from your database.";

      case "compare_months":
        return `Revenue changed by ${formatValue(a.change)} from ${a.month1} to ${a.month2}.${
          a.percentage_change === null
            ? " Percentage change is unavailable because the starting revenue is zero."
            : ` Percentage change: ${formatValue(a.percentage_change)}%.`
        }`;

      default:
        return "Results retrieved successfully.";
    }
  }

  return (
    <main className="app">
      <header className="header">
        <div className="logo">BI</div>
        <div>
          <h1>Mini AI Business Intelligence Assistant</h1>
          <p>Ask questions. Discover insights from your sales data.</p>
        </div>
      </header>

      <section className="panel">
        <h2>Ask your sales data</h2>
        <p className="muted">
          Ask a business question in natural language.
        </p>

        <form
          onSubmit={(event) => {
            event.preventDefault();
            askQuestion();
          }}
          className="question-form"
        >
          <input
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            placeholder="e.g. Which product generated the highest revenue?"
            aria-label="Business question"
          />
          <button disabled={loading} type="submit">
            {loading ? "Analyzing..." : "Ask"}
          </button>
        </form>

        <h3>Try an example</h3>
        <div className="examples">
          {examples.map((example) => (
            <button
              type="button"
              className="example"
              key={example}
              onClick={() => askQuestion(example)}
              disabled={loading}
            >
              {example}
            </button>
          ))}
        </div>
      </section>

      {error && <div className="error">{error}</div>}

      {result && (
        <section className="panel results">
          <span className="eyebrow">ANALYSIS RESULT</span>
          <h2>{answerSummary()}</h2>
          <p className="muted">
            Question: {result.question}
          </p>

          <h3>Supporting data</h3>

          {result.intent === "monthly_revenue" &&
          Array.isArray(result.answer) ? (
            <table>
              <thead>
                <tr>
                  <th>Month</th>
                  <th>Revenue</th>
                </tr>
              </thead>
              <tbody>
                {result.answer.map((row) => (
                  <tr key={row.month}>
                    <td>{row.month}</td>
                    <td>{formatValue(row.revenue)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <table>
              <tbody>
                {Object.entries(result.answer || {}).map(([key, value]) => (
                  <tr key={key}>
                    <th>{key.replaceAll("_", " ")}</th>
                    <td>{formatValue(value)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}

          <p className="source">
            Source: {result.source}
          </p>
        </section>
      )}

      <footer>
        Mini BI Assistant · Flask API · SQLite
      </footer>
    </main>
  );
}

export default App;
