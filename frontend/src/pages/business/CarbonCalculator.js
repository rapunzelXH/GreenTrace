// frontend/src/pages/business/CarbonCalculator.js
// UC-10: Business inputs monthly carbon data and sees CO2 result.

import React, { useEffect, useState } from "react";
import { submitCarbonData, getCarbonData, getApplications } from "../../api/endpoints";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from "recharts";
import toast from "react-hot-toast";

const CO2_LIMIT = 5000;

export default function CarbonCalculator() {
  const [projects,  setProjects]  = useState([]);
  const [history,   setHistory]   = useState([]);
  const [form, setForm] = useState({
    project: "", period_month: new Date().getMonth() + 1,
    period_year: new Date().getFullYear(),
    fuel_liters: "", electricity_kwh: "",
  });
  const [preview,  setPreview]  = useState(null);
  const [loading,  setLoading]  = useState(false);

  useEffect(() => {
    getApplications().then((r) => {
      const approved = (r.data.results || r.data).filter((a) => a.status === "APPROVED");
      setProjects(approved);
      if (approved.length > 0)
        setForm((f) => ({ ...f, project: approved[0].project }));
    });
    getCarbonData().then((r) => setHistory(r.data.results || r.data));
  }, []);

  // Live CO2 preview (FR_24 formula)
  useEffect(() => {
    const fuel = parseFloat(form.fuel_liters)     || 0;
    const elec = parseFloat(form.electricity_kwh) || 0;
    if (fuel > 0 || elec > 0) {
      const total = fuel * 2.31 + elec * 0.233;
      setPreview({ total: total.toFixed(1), exceeds: total > CO2_LIMIT });
    } else {
      setPreview(null);
    }
  }, [form.fuel_liters, form.electricity_kwh]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await submitCarbonData(form);
      toast.success("Carbon data submitted successfully.");
      const r = await getCarbonData();
      setHistory(r.data.results || r.data);
      setForm((f) => ({ ...f, fuel_liters: "", electricity_kwh: "" }));
    } catch (err) {
      const msg = err.response?.data
        ? Object.values(err.response.data).flat().join(" ")
        : "Submission failed.";
      toast.error(msg);
    } finally {
      setLoading(false);
    }
  };

  // Chart data
  const chartData = [...history]
    .sort((a, b) => a.period_year - b.period_year || a.period_month - b.period_month)
    .slice(-12)
    .map((d) => ({
      name    : `${String(d.period_month).padStart(2, "0")}/${d.period_year}`,
      co2     : parseFloat(d.total_co2_kg) || 0,
      exceeds : d.exceeds_limit,
    }));

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-1">Carbon Calculator</h1>
      <p className="text-gray-500 text-sm mb-8">UC-10 · Monthly CO₂ footprint tracking</p>

      <div className="grid grid-cols-2 gap-8">
        {/* Input form */}
        <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-6">
          <h2 className="font-semibold text-gray-800 mb-4">Submit Monthly Data</h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Project */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Project</label>
              <select
                value={form.project}
                onChange={(e) => setForm({ ...form, project: e.target.value })}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
                required
              >
                {projects.map((a) => (
                  <option key={a.id} value={a.project}>{a.project}</option>
                ))}
              </select>
            </div>

            {/* Period */}
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Month</label>
                <select
                  value={form.period_month}
                  onChange={(e) => setForm({ ...form, period_month: parseInt(e.target.value) })}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
                >
                  {Array.from({ length: 12 }, (_, i) => (
                    <option key={i + 1} value={i + 1}>
                      {new Date(0, i).toLocaleString("default", { month: "long" })}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Year</label>
                <input
                  type="number"
                  value={form.period_year}
                  onChange={(e) => setForm({ ...form, period_year: parseInt(e.target.value) })}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
                  min="2020" max="2030"
                />
              </div>
            </div>

            {/* Fuel */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Fuel consumed (litres)
                <span className="text-gray-400 font-normal ml-1">× 2.31 kg CO₂/L</span>
              </label>
              <input
                type="number" step="0.1" min="0"
                value={form.fuel_liters}
                onChange={(e) => setForm({ ...form, fuel_liters: e.target.value })}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
                placeholder="0"
                required
              />
            </div>

            {/* Electricity */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Electricity consumed (kWh)
                <span className="text-gray-400 font-normal ml-1">× 0.233 kg CO₂/kWh</span>
              </label>
              <input
                type="number" step="0.1" min="0"
                value={form.electricity_kwh}
                onChange={(e) => setForm({ ...form, electricity_kwh: e.target.value })}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
                placeholder="0"
                required
              />
            </div>

            {/* Live preview */}
            {preview && (
              <div className={`rounded-lg p-4 border ${
                preview.exceeds
                  ? "bg-red-50 border-red-200 text-red-700"
                  : "bg-green-50 border-green-200 text-green-700"
              }`}>
                <p className="font-semibold text-sm">
                  Estimated CO₂: {preview.total} kg
                  {preview.exceeds && "  ⚠ Exceeds monthly limit!"}
                </p>
                <p className="text-xs mt-0.5">Monthly limit: {CO2_LIMIT.toLocaleString()} kg</p>
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-green-600 text-white py-2 rounded-lg font-medium hover:bg-green-700 transition disabled:opacity-50"
            >
              {loading ? "Submitting…" : "Submit Carbon Data"}
            </button>
          </form>
        </div>

        {/* Chart */}
        <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-6">
          <h2 className="font-semibold text-gray-800 mb-4">CO₂ History (last 12 months)</h2>
          {chartData.length === 0 ? (
            <p className="text-gray-400 text-sm text-center mt-12">No data yet.</p>
          ) : (
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={chartData} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip
                  formatter={(value) => [`${value} kg CO₂`, "CO₂"]}
                  contentStyle={{ fontSize: 12 }}
                />
                <ReferenceLine y={CO2_LIMIT} stroke="#dc2626" strokeDasharray="4 4"
                  label={{ value: "Limit", position: "right", fontSize: 11, fill: "#dc2626" }} />
                <Bar dataKey="co2" radius={[4, 4, 0, 0]}
                  fill="#16a34a"
                  label={false}
                />
              </BarChart>
            </ResponsiveContainer>
          )}

          {/* History table */}
          <div className="mt-4 max-h-48 overflow-y-auto">
            <table className="w-full text-xs">
              <thead className="text-gray-500 border-b">
                <tr>
                  <th className="py-1 text-left">Period</th>
                  <th className="py-1 text-right">Fuel (L)</th>
                  <th className="py-1 text-right">Elec (kWh)</th>
                  <th className="py-1 text-right">CO₂ (kg)</th>
                  <th className="py-1 text-right">Status</th>
                </tr>
              </thead>
              <tbody>
                {[...history].reverse().map((d) => (
                  <tr key={d.id} className="border-t">
                    <td className="py-1">{String(d.period_month).padStart(2,"0")}/{d.period_year}</td>
                    <td className="py-1 text-right">{d.fuel_liters}</td>
                    <td className="py-1 text-right">{d.electricity_kwh}</td>
                    <td className="py-1 text-right font-medium">{parseFloat(d.total_co2_kg).toFixed(1)}</td>
                    <td className="py-1 text-right">
                      {d.exceeds_limit
                        ? <span className="text-red-600 font-medium">⚠ Over</span>
                        : <span className="text-green-600">✓ OK</span>}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
