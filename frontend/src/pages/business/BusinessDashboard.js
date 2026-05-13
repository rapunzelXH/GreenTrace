// frontend/src/pages/business/BusinessDashboard.js
// Business user dashboard — milestones status, eco-score, quick actions.

import React, { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { getApplications, getMilestones, getMyCompany } from "../../api/endpoints";
import { useAuth } from "../../context/AuthContext";
import { RadialBarChart, RadialBar, ResponsiveContainer, Tooltip } from "recharts";

function EcoScoreGauge({ score }) {
  const color = score >= 70 ? "#16a34a" : score >= 40 ? "#d97706" : "#dc2626";
  const data  = [{ name: "Eco-Score", value: score, fill: color }];
  return (
    <div className="relative w-36 h-36 mx-auto">
      <ResponsiveContainer width="100%" height="100%">
        <RadialBarChart innerRadius="70%" outerRadius="100%" data={data} startAngle={90} endAngle={-270}>
          <RadialBar dataKey="value" cornerRadius={8} background={{ fill: "#f3f4f6" }} />
          <Tooltip />
        </RadialBarChart>
      </ResponsiveContainer>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-2xl font-bold" style={{ color }}>{score}</span>
        <span className="text-xs text-gray-500">/ 100</span>
      </div>
    </div>
  );
}

export default function BusinessDashboard() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [company,     setCompany]     = useState(null);
  const [milestones,  setMilestones]  = useState([]);
  const [applications,setApplications]= useState([]);
  const [loading,     setLoading]     = useState(true);

  useEffect(() => {
    Promise.all([getMyCompany(), getMilestones(), getApplications()])
      .then(([c, m, a]) => {
        const companies = c.data.results || c.data;
        setCompany(Array.isArray(companies) ? companies[0] : companies);
        setMilestones(m.data.results   || m.data);
        setApplications(a.data.results || a.data);
      })
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <Spinner />;

  const pending  = milestones.filter((m) => ["PENDING","OVERDUE"].includes(m.status));
  const approved = milestones.filter((m) => m.status === "APPROVED");

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Sidebar */}
      <div className="fixed left-0 top-0 h-full w-56 bg-white border-r flex flex-col py-6 px-4 z-20">
        <div className="flex items-center gap-2 mb-8">
          <div className="w-7 h-7 bg-green-600 rounded-full flex items-center justify-center">
            <span className="text-white text-xs font-bold">G</span>
          </div>
          <span className="font-bold text-gray-800 text-sm">GreenTrace</span>
        </div>
        <nav className="flex flex-col gap-1 text-sm flex-1">
          {[
            ["Dashboard",        "/business"],
            ["Milestones",       "/business/milestones"],
            ["Carbon Calculator","/business/carbon"],
            ["Browse Tenders",   "/projects"],
          ].map(([label, path]) => (
            <Link key={path} to={path}
              className="px-3 py-2 rounded-lg text-gray-600 hover:bg-gray-100 transition">
              {label}
            </Link>
          ))}
        </nav>
        <div className="border-t pt-4">
          <p className="text-xs text-gray-500 mb-2 truncate">{user?.email}</p>
          <button onClick={() => { logout(); navigate("/login"); }}
            className="text-xs text-red-500 hover:text-red-700">Sign out</button>
        </div>
      </div>

      {/* Content */}
      <div className="ml-56 p-8">
        <h1 className="text-2xl font-bold text-gray-900 mb-6">
          {company?.company_name || "Business Dashboard"}
        </h1>

        <div className="grid grid-cols-3 gap-6 mb-8">
          {/* Eco-Score card */}
          <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-6 col-span-1">
            <p className="text-sm font-medium text-gray-500 mb-4 text-center">Eco-Score</p>
            <EcoScoreGauge score={company?.eco_score || 0} />
            <p className="text-center text-xs text-gray-400 mt-3">
              Based on {approved.length} approved milestones
            </p>
          </div>

          {/* Stats */}
          <div className="col-span-2 grid grid-cols-3 gap-4">
            {[
              { label: "Total Milestones",  value: milestones.length },
              { label: "Pending / Overdue", value: pending.length,    color: "text-amber-600" },
              { label: "Approved",          value: approved.length,   color: "text-green-600" },
              { label: "Applications",      value: applications.length },
              { label: "Active Projects",   value: applications.filter(a => a.status === "APPROVED").length, color: "text-purple-600" },
              { label: "Profile Verified",  value: company?.is_verified ? "Yes" : "No", color: company?.is_verified ? "text-green-600" : "text-amber-600" },
            ].map(({ label, value, color = "text-gray-800" }) => (
              <div key={label} className="bg-white rounded-xl border border-gray-100 shadow-sm p-4">
                <p className="text-xs text-gray-500 mb-1">{label}</p>
                <p className={`text-2xl font-bold ${color}`}>{value}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Upcoming milestones */}
        <div className="bg-white rounded-xl border border-gray-100 shadow-sm">
          <div className="flex items-center justify-between px-6 py-4 border-b">
            <h2 className="font-semibold text-gray-800">Upcoming Milestones</h2>
            <Link to="/business/milestones" className="text-sm text-green-700 hover:underline">
              View all →
            </Link>
          </div>
          {pending.length === 0 ? (
            <p className="text-gray-500 text-sm px-6 py-4">All milestones up to date.</p>
          ) : (
            <table className="w-full text-sm">
              <thead className="bg-gray-50 text-xs text-gray-500 border-b">
                <tr>
                  <th className="px-5 py-3 text-left">Milestone</th>
                  <th className="px-5 py-3 text-left">Status</th>
                  <th className="px-5 py-3 text-left">Deadline</th>
                  <th className="px-5 py-3 text-left">Action</th>
                </tr>
              </thead>
              <tbody>
                {pending.slice(0, 5).map((m) => (
                  <tr key={m.id} className="border-t hover:bg-gray-50">
                    <td className="px-5 py-3 font-medium text-gray-800">{m.title}</td>
                    <td className="px-5 py-3">
                      <span className={`text-xs px-2 py-0.5 rounded-full ${
                        m.status === "OVERDUE"
                          ? "bg-red-100 text-red-700"
                          : "bg-amber-100 text-amber-700"
                      }`}>{m.status}</span>
                    </td>
                    <td className="px-5 py-3 text-gray-500">
                      {new Date(m.deadline).toLocaleDateString()}
                    </td>
                    <td className="px-5 py-3">
                      <Link to="/business/milestones"
                        className="text-green-700 font-medium text-xs hover:underline">
                        Upload →
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
}

function Spinner() {
  return <div className="flex items-center justify-center h-screen"><div className="w-8 h-8 border-4 border-green-600 border-t-transparent rounded-full animate-spin" /></div>;
}
