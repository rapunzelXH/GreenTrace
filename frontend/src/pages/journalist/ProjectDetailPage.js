import React, { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { getProject, getProjectMilestones, followProject } from "../../api/endpoints";
import { useAuth } from "../../context/AuthContext";
import toast from "react-hot-toast";

export default function ProjectDetailPage() {
  const { id } = useParams();
  const { user } = useAuth();
  const [project, setProject] = useState(null);
  const [milestones, setMilestones] = useState([]);

  useEffect(() => {
    getProject(id).then((r)=>setProject(r.data));
    getProjectMilestones(id).then((r)=>setMilestones(r.data));
  },[id]);

  const handleFollow = async () => {
    try { await followProject({ project_id: id, frequency: "REALTIME" }); toast.success("Following project!"); }
    catch { toast.error("Could not follow project."); }
  };

  if (!project) return <div className="p-8 text-gray-500">Loading…</div>;

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-3xl mx-auto">
        <Link to="/projects" className="text-sm text-green-700 hover:underline mb-4 block">← Back to projects</Link>
        <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-6 mb-6">
          <div className="flex items-start justify-between mb-3">
            <h1 className="text-xl font-bold text-gray-900">{project.title}</h1>
            {project.has_red_flag && <span className="text-red-600 text-sm font-medium">🚩 Red Flag</span>}
          </div>
          <p className="text-gray-500 text-sm mb-4">{project.description}</p>
          <div className="grid grid-cols-3 gap-4 text-sm">
            <div><p className="text-gray-400 text-xs">Location</p><p className="font-medium">{project.location}</p></div>
            <div><p className="text-gray-400 text-xs">Risk Level</p><p className="font-medium">{project.risk_level}</p></div>
            <div><p className="text-gray-400 text-xs">Status</p><p className="font-medium">{project.status}</p></div>
          </div>
          <div className="flex gap-3 mt-5">
            {user && <button onClick={handleFollow} className="bg-green-600 text-white text-sm px-4 py-1.5 rounded-lg hover:bg-green-700">Follow Project</button>}
            <Link to="/report" className="border border-red-300 text-red-600 text-sm px-4 py-1.5 rounded-lg hover:bg-red-50">Report Issue</Link>
          </div>
        </div>
        <h2 className="font-semibold text-gray-800 mb-3">Eco-Milestones ({milestones.length})</h2>
        <div className="flex flex-col gap-2">
          {milestones.map((m)=>(
            <div key={m.id} className="bg-white rounded-xl border border-gray-100 shadow-sm p-4 flex items-center justify-between">
              <div><p className="font-medium text-gray-800 text-sm">{m.title}</p><p className="text-xs text-gray-500">Deadline: {new Date(m.deadline).toLocaleDateString()} · Weight: {m.weight}</p></div>
              <span className={`text-xs px-2 py-0.5 rounded-full ${m.status==="APPROVED"?"bg-green-100 text-green-700":m.status==="OVERDUE"?"bg-red-100 text-red-700":"bg-gray-100 text-gray-600"}`}>{m.status}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
