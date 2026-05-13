// frontend/src/pages/admin/AdminDashboard.js
// UC-28: Admin dashboard — projects overview, milestone review, red flags.

import React, { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { getProjects, getReports, getMilestones } from "../../api/endpoints";
import { useAuth } from "../../context/AuthContext";

const RISK_COLOR  = { LOW: "bg-green-100 text-green-700", MEDIUM: "bg-amber-100 text-amber-700", HIGH: "bg-red-100 text-red-700" };
const STATUS_COLOR = { DRAFT: "bg-gray-100 text-gray-600", OPEN: "bg-blue-100 text-blue-700", EXECUTION: "bg-purple-100 text-purple-700", COMPLETED: "bg-green-100 text-green-700", SUSPENDED: "bg-red-100 text-red-700" };

function StatCard({ label, value, color = "text-gray-800" }) {
  return (
    <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-5">
      <p className="text-sm text-gray-500 mb-1">{label}</p>
      <p className={`text-3xl font-bold ${color}`}>{value}</p>
    </div>
  );
}

export default function AdminDashboard() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [projects,   setProjects]   = useState([]);
  const [milestones, setMilestones] = useState([]);
  const [reports,    setReports]    = useState([]);
  const [loading,    setLoading]    = useState(true);

  useEffect(() => {
    Promise.all([getProjects(), getMilestones(), getReports()])
      .then(([p, m, r]) => {
        setProjects(p.data.results   || p.data);
        setMilestones(m.data.results || m.data);
        setReports(r.data.results    || r.data);
      })
      .finally(() => setLoading(false));
  }, []);

  const pending    = milestones.filter((m) => m.status === "SUBMITTED");
  const redFlags   = projects.filter((p) => p.has_red_flag);
  const openTenders= projects.filter((p) => p.status === "OPEN");

  if (loading) return <Spinner />;

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
            ["Dashboard",  "/admin"],
            ["Projects",   "/admin/projects"],
            ["Milestones", "/admin/milestones"],
            ["Reports",    "/admin/reports"],
            ["Audit Log",  "/admin/audit"],
          ].map(([label, path]) => (
            <Link key={path} to={path}
              className="px-3 py-2 rounded-lg text-gray-600 hover:bg-gray-100 hover:text-gray-900 transition">
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

      {/* Main content */}
      <div className="ml-56 p-8">
        <h1 className="text-2xl font-bold text-gray-900 mb-1">Admin Dashboard</h1>
        <p className="text-gray-500 text-sm mb-8">Environmental procurement overview</p>

        {/* Stats */}
        <div className="grid grid-cols-4 gap-4 mb-8">
          <StatCard label="Total Projects"     value={projects.length} />
          <StatCard label="Open Tenders"       value={openTenders.length} color="text-blue-600" />
          <StatCard label="Pending Reviews"    value={pending.length}  color="text-amber-600" />
          <StatCard label="Red Flag Projects"  value={redFlags.length} color="text-red-600" />
        </div>

        {/* Pending milestone reviews */}
        <div className="bg-white rounded-xl border border-gray-100 shadow-sm mb-6">
          <div className="flex items-center justify-between px-6 py-4 border-b">
            <h2 className="font-semibold text-gray-800">Pending Milestone Reviews</h2>
            <Link to="/admin/milestones" className="text-sm text-green-700 hover:underline">View all</Link>
          </div>
          {pending.length === 0 ? (
            <p className="text-gray-500 text-sm px-6 py-4">No pending reviews.</p>
          ) : (
            <table className="w-full text-sm">
              <thead className="bg-gray-50 text-gray-500 text-xs">
                <tr>
                  <th className="px-6 py-3 text-left">Milestone</th>
                  <th className="px-6 py-3 text-left">Project</th>
                  <th className="px-6 py-3 text-left">Deadline</th>
                  <th className="px-6 py-3 text-left">Action</th>
                </tr>
              </thead>
              <tbody>
                {pending.slice(0, 5).map((m) => (
                  <tr key={m.id} className="border-t hover:bg-gray-50">
                    <td className="px-6 py-3 font-medium text-gray-800">{m.title}</td>
                    <td className="px-6 py-3 text-gray-500">{m.project}</td>
                    <td className="px-6 py-3 text-gray-500">{new Date(m.deadline).toLocaleDateString()}</td>
                    <td className="px-6 py-3">
                      <Link to="/admin/milestones"
                        className="text-green-700 font-medium hover:underline text-xs">Review →</Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        {/* Red Flag reports */}
        {redFlags.length > 0 && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-5">
            <h2 className="font-semibold text-red-700 mb-3">🚩 Projects with Red Flags</h2>
            <div className="flex flex-col gap-2">
              {redFlags.map((p) => (
                <div key={p.id} className="flex items-center justify-between bg-white rounded-lg px-4 py-2 border border-red-100">
                  <span className="text-sm font-medium text-gray-800">{p.title}</span>
                  <div className="flex items-center gap-3">
                    <span className={`text-xs px-2 py-0.5 rounded-full ${RISK_COLOR[p.risk_level]}`}>
                      {p.risk_level}
                    </span>
                    <Link to="/admin/reports" className="text-xs text-red-600 hover:underline">View report →</Link>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function Spinner() {
  return (
    <div className="flex items-center justify-center h-screen">
      <div className="w-8 h-8 border-4 border-green-600 border-t-transparent rounded-full animate-spin" />
    </div>
  );
}
