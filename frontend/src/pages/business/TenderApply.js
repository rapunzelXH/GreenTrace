import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { getProject, createApplication, submitApplication } from "../../api/endpoints";
import toast from "react-hot-toast";

export default function TenderApply() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [project, setProject] = useState(null);
  const [form, setForm] = useState({ technical_proposal:null, env_impact_statement:null, financial_bid:"" });
  const [loading, setLoading] = useState(false);

  useEffect(() => { getProject(id).then((r)=>setProject(r.data)); },[id]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    const fd = new FormData();
    fd.append("project", id);
    fd.append("technical_proposal", form.technical_proposal);
    fd.append("env_impact_statement", form.env_impact_statement);
    fd.append("financial_bid", form.financial_bid);
    try {
      const res = await createApplication(fd);
      await submitApplication(res.data.id);
      toast.success("Application submitted!");
      navigate("/business");
    } catch (err) {
      toast.error(err.response?.data ? JSON.stringify(err.response.data) : "Failed.");
    } finally { setLoading(false); }
  };

  if (!project) return <div className="p-8 text-gray-500">Loading…</div>;

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-1">Apply for Tender</h1>
      <p className="text-gray-500 text-sm mb-6">{project.title}</p>
      <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-6 max-w-lg">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Technical Proposal (PDF)</label>
            <input type="file" accept=".pdf" required onChange={(e)=>setForm({...form,technical_proposal:e.target.files[0]})} className="w-full text-sm" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Environmental Impact Statement (PDF)</label>
            <input type="file" accept=".pdf" required onChange={(e)=>setForm({...form,env_impact_statement:e.target.files[0]})} className="w-full text-sm" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Financial Bid (ALL)</label>
            <input type="number" required value={form.financial_bid} onChange={(e)=>setForm({...form,financial_bid:e.target.value})} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" placeholder="0" />
          </div>
          <button type="submit" disabled={loading} className="w-full bg-green-600 text-white py-2 rounded-lg font-medium hover:bg-green-700 disabled:opacity-50">
            {loading ? "Submitting…" : "Submit Application"}
          </button>
        </form>
      </div>
    </div>
  );
}
