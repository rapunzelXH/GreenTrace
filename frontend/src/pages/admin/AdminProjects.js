// frontend/src/pages/admin/AdminProjects.js
import React, { useEffect, useState } from "react";
import { getProjects, createProject } from "../../api/endpoints";
import toast from "react-hot-toast";

const RISK_BADGE   = { LOW: "bg-green-100 text-green-700", MEDIUM: "bg-amber-100 text-amber-700", HIGH: "bg-red-100 text-red-700" };
const STATUS_BADGE = { DRAFT:"bg-gray-100 text-gray-600", OPEN:"bg-blue-100 text-blue-700", REVIEW:"bg-yellow-100 text-yellow-700", EXECUTION:"bg-purple-100 text-purple-700", COMPLETED:"bg-green-100 text-green-700" };

export default function AdminProjects() {
  const [projects, setProjects] = useState([]);
  const [creating, setCreating] = useState(false);
  const [form, setForm] = useState({ title:"", description:"", location:"", risk_level:"MEDIUM", submission_deadline:"", budget:"" });

  useEffect(() => {
    getProjects().then((r) => setProjects(r.data.results || r.data));
  }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      await createProject(form);
      toast.success("Project created.");
      setCreating(false);
      const r = await getProjects();
      setProjects(r.data.results || r.data);
    } catch (err) {
      toast.error(err.response?.data ? JSON.stringify(err.response.data) : "Failed.");
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Projects</h1>
          <p className="text-gray-500 text-sm">{projects.length} total</p>
        </div>
        <button onClick={() => setCreating(true)}
          className="bg-green-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-green-700">
          + New Project
        </button>
      </div>

      <div className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 text-gray-500 text-xs border-b">
            <tr>
              <th className="px-5 py-3 text-left">Title</th>
              <th className="px-5 py-3 text-left">Status</th>
              <th className="px-5 py-3 text-left">Risk</th>
              <th className="px-5 py-3 text-left">Location</th>
              <th className="px-5 py-3 text-left">Deadline</th>
              <th className="px-5 py-3 text-left">Flag</th>
            </tr>
          </thead>
          <tbody>
            {projects.map((p) => (
              <tr key={p.id} className="border-t hover:bg-gray-50">
                <td className="px-5 py-3 font-medium text-gray-800">{p.title}</td>
                <td className="px-5 py-3"><span className={`text-xs px-2 py-0.5 rounded-full ${STATUS_BADGE[p.status]||"bg-gray-100 text-gray-600"}`}>{p.status}</span></td>
                <td className="px-5 py-3"><span className={`text-xs px-2 py-0.5 rounded-full ${RISK_BADGE[p.risk_level]||""}`}>{p.risk_level}</span></td>
                <td className="px-5 py-3 text-gray-500">{p.location}</td>
                <td className="px-5 py-3 text-gray-500">{new Date(p.submission_deadline).toLocaleDateString()}</td>
                <td className="px-5 py-3">{p.has_red_flag ? "🚩" : "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {creating && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-xl p-6 w-full max-w-lg">
            <h3 className="font-bold text-gray-900 mb-4">Create New Project</h3>
            <form onSubmit={handleCreate} className="space-y-3">
              {[["Title","title"],["Description","description"],["Location","location"]].map(([l,n])=>(
                <div key={n}>
                  <label className="block text-sm font-medium text-gray-700 mb-1">{l}</label>
                  <input value={form[n]} onChange={(e)=>setForm({...form,[n]:e.target.value})} required
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" />
                </div>
              ))}
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Risk Level</label>
                  <select value={form.risk_level} onChange={(e)=>setForm({...form,risk_level:e.target.value})}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm">
                    <option value="LOW">Low</option><option value="MEDIUM">Medium</option><option value="HIGH">High</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Budget</label>
                  <input type="number" value={form.budget} onChange={(e)=>setForm({...form,budget:e.target.value})}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Submission Deadline</label>
                <input type="datetime-local" required value={form.submission_deadline}
                  onChange={(e)=>setForm({...form,submission_deadline:e.target.value})}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" />
              </div>
              <div className="flex gap-3 pt-2">
                <button type="submit" className="flex-1 bg-green-600 text-white py-2 rounded-lg font-medium hover:bg-green-700">Create</button>
                <button type="button" onClick={()=>setCreating(false)} className="px-4 py-2 border rounded-lg text-gray-600 hover:bg-gray-50">Cancel</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
