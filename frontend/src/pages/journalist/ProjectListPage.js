import React, { useEffect, useState } from "react";
import { getProjects } from "../../api/endpoints";
import { Link } from "react-router-dom";

export default function ProjectListPage() {
  const [projects, setProjects] = useState([]);
  const [search, setSearch] = useState("");
  useEffect(() => { getProjects().then((r)=>setProjects(r.data.results||r.data)); },[]);
  const filtered = projects.filter((p)=>p.title.toLowerCase().includes(search.toLowerCase())||p.location.toLowerCase().includes(search.toLowerCase()));
  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-1">Projects</h1>
      <input value={search} onChange={(e)=>setSearch(e.target.value)} placeholder="Search by title or location…" className="w-full max-w-sm border border-gray-300 rounded-lg px-3 py-2 text-sm mb-6 focus:outline-none focus:ring-2 focus:ring-green-600" />
      <div className="grid grid-cols-3 gap-4">
        {filtered.map((p)=>(
          <Link key={p.id} to={`/projects/${p.id}`} className="bg-white rounded-xl border border-gray-100 shadow-sm p-5 hover:shadow-md transition block">
            <div className="flex items-start justify-between mb-2">
              <p className="font-semibold text-gray-800 text-sm">{p.title}</p>
              {p.has_red_flag && <span className="text-red-600 text-xs">🚩</span>}
            </div>
            <p className="text-xs text-gray-500 mb-3">{p.location}</p>
            <span className={`text-xs px-2 py-0.5 rounded-full ${p.risk_level==="HIGH"?"bg-red-100 text-red-700":p.risk_level==="MEDIUM"?"bg-amber-100 text-amber-700":"bg-green-100 text-green-700"}`}>{p.risk_level}</span>
          </Link>
        ))}
      </div>
    </div>
  );
}
