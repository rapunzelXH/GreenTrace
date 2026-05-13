import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { getProjects, submitReport } from "../../api/endpoints";
import toast from "react-hot-toast";

export default function ReportForm() {
  const navigate = useNavigate();
  const [projects, setProjects] = useState([]);
  const [form, setForm] = useState({ project:"", title:"", description:"", is_anonymous:false, evidence_file:null });
  const [loading, setLoading] = useState(false);

  useEffect(() => { getProjects().then((r)=>setProjects(r.data.results||r.data)); },[]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    const fd = new FormData();
    Object.entries(form).forEach(([k,v])=>{ if(v!==null) fd.append(k,v); });
    try {
      await submitReport(fd);
      toast.success("Report submitted. Thank you.");
      navigate("/map");
    } catch { toast.error("Submission failed."); }
    finally { setLoading(false); }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8 flex items-start justify-center">
      <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-8 w-full max-w-lg">
        <h1 className="text-xl font-bold text-gray-900 mb-1">Report a Discrepancy</h1>
        <p className="text-gray-500 text-sm mb-6">UC-16 · Whistleblowing form</p>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Project</label>
            <select required value={form.project} onChange={(e)=>setForm({...form,project:e.target.value})} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm">
              <option value="">Select a project…</option>
              {projects.map((p)=><option key={p.id} value={p.id}>{p.title}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Title</label>
            <input required value={form.title} onChange={(e)=>setForm({...form,title:e.target.value})} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
            <textarea required rows={4} value={form.description} onChange={(e)=>setForm({...form,description:e.target.value})} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Evidence (photo/video)</label>
            <input type="file" accept="image/*,video/*" onChange={(e)=>setForm({...form,evidence_file:e.target.files[0]})} className="w-full text-sm" />
          </div>
          <label className="flex items-center gap-2 text-sm text-gray-700 cursor-pointer">
            <input type="checkbox" checked={form.is_anonymous} onChange={(e)=>setForm({...form,is_anonymous:e.target.checked})} className="rounded" />
            Submit anonymously
          </label>
          <button type="submit" disabled={loading} className="w-full bg-red-600 text-white py-2 rounded-lg font-medium hover:bg-red-700 disabled:opacity-50">
            {loading ? "Submitting…" : "Submit Report"}
          </button>
        </form>
      </div>
    </div>
  );
}
