// frontend/src/pages/journalist/EcoScoreComparePage.js
// UC-18: Compare Eco-Scores of multiple companies side by side.

import React, { useState } from "react";
import { compareEcoScores } from "../../api/endpoints";
import { RadarChart, Radar, PolarGrid, PolarAngleAxis, ResponsiveContainer, Tooltip, Legend } from "recharts";
import toast from "react-hot-toast";

const COLORS = ["#16a34a", "#2563eb", "#d97706", "#7c3aed", "#dc2626"];

export default function EcoScoreComparePage() {
  const [ids,     setIds]     = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleCompare = async () => {
    const parsed = ids.split(",").map((s) => parseInt(s.trim())).filter(Boolean);
    if (parsed.length < 2) { toast.error("Enter at least 2 company IDs."); return; }
    if (parsed.length > 5) { toast.error("Maximum 5 companies at once."); return; }
    setLoading(true);
    try {
      const res = await compareEcoScores(parsed);
      setResults(res.data);
    } catch {
      toast.error("Comparison failed. Check the IDs.");
    } finally {
      setLoading(false);
    }
  };

  // Radar chart needs consistent keys
  const radarData = results.length > 0
    ? [{ subject: "Eco-Score", ...Object.fromEntries(results.map((c) => [c.company_name, c.eco_score])) }]
    : [];

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-1">Eco-Score Comparison</h1>
      <p className="text-gray-500 text-sm mb-6">UC-18 · Compare environmental performance of companies</p>

      {/* Input */}
      <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-5 mb-6 flex gap-3 items-end">
        <div className="flex-1">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Company IDs (comma-separated, 2–5 companies)
          </label>
          <input
            type="text"
            value={ids}
            onChange={(e) => setIds(e.target.value)}
            placeholder="e.g. 1, 2, 3"
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-600"
          />
        </div>
        <button
          onClick={handleCompare}
          disabled={loading}
          className="bg-green-600 text-white px-5 py-2 rounded-lg font-medium hover:bg-green-700 transition disabled:opacity-50"
        >
          {loading ? "Comparing…" : "Compare"}
        </button>
      </div>

      {results.length > 0 && (
        <>
          {/* Cards */}
          <div className="grid gap-4 mb-6" style={{ gridTemplateColumns: `repeat(${results.length}, 1fr)` }}>
            {results.map((c, i) => {
              const color = c.eco_score >= 70 ? "#16a34a" : c.eco_score >= 40 ? "#d97706" : "#dc2626";
              return (
                <div key={c.id} className="bg-white rounded-xl border shadow-sm p-5 text-center">
                  <div className="w-10 h-10 rounded-full mx-auto mb-3 flex items-center justify-center"
                    style={{ background: COLORS[i] + "22" }}>
                    <span className="font-bold text-sm" style={{ color: COLORS[i] }}>
                      {c.company_name.charAt(0)}
                    </span>
                  </div>
                  <p className="font-semibold text-gray-800 text-sm mb-1 truncate">{c.company_name}</p>
                  <p className="text-3xl font-bold mb-1" style={{ color }}>{c.eco_score}</p>
                  <p className="text-xs text-gray-400">/ 100</p>
                  <div className="mt-2">
                    <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                      <div className="h-full rounded-full transition-all"
                        style={{ width: `${c.eco_score}%`, background: color }} />
                    </div>
                  </div>
                  <p className={`text-xs mt-2 font-medium ${c.is_verified ? "text-green-600" : "text-gray-400"}`}>
                    {c.is_verified ? "✓ Verified" : "Not verified"}
                  </p>
                </div>
              );
            })}
          </div>

          {/* Radar chart */}
          <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-6">
            <h2 className="font-semibold text-gray-800 mb-4">Visual Comparison</h2>
            <ResponsiveContainer width="100%" height={300}>
              <RadarChart data={radarData}>
                <PolarGrid />
                <PolarAngleAxis dataKey="subject" />
                {results.map((c, i) => (
                  <Radar key={c.id} name={c.company_name} dataKey={c.company_name}
                    stroke={COLORS[i]} fill={COLORS[i]} fillOpacity={0.15} />
                ))}
                <Tooltip />
                <Legend />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </>
      )}
    </div>
  );
}
