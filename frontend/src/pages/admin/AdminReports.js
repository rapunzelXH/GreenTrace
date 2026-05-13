import React, { useEffect, useState } from "react";
import { getReports, respondToReport } from "../../api/endpoints";
import toast from "react-hot-toast";

export default function AdminReports() {
  const [reports, setReports] = useState([]);
  const [selected, setSelected] = useState(null);
  const [form, setForm] = useState({ status:"RESOLVED", admin_response:"" });

  useEffect(() => { getReports().then((r)=>setReports(r.data.results||r.data)); },[]);

  const handleRespond = async () => {
    try {
      await respondToReport(selected.id, form);
      toast.success("Response submitted.");
      setSelected(null);
      const r = await getReports();
      setReports(r.data.results||r.data);
    } catch { toast.error("Failed."); }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Discrepancy Reports</h1>
      <div className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 text-gray-500 text-xs border-b">
            <tr><th className="px-5 py-3 text-left">Title</th><th className="px-5 py-3 text-left">Project</th><th className="px-5 py-3 text-left">Reporter</th><th className="px-5 py-3 text-left">Status</th><th className="px-5 py-3 text-left">Action</th></tr>
          </thead>
          <tbody>
            {reports.map((r)=>(
              <tr key={r.id} className="border-t hover:bg-gray-50">
                <td className="px-5 py-3 font-medium text-gray-800">{r.title}</td>
                <td className="px-5 py-3 text-gray-500">{r.project}</td>
                <td className="px-5 py-3 text-gray-500">{r.reported_by||"Anonymous"}</td>
                <td className="px-5 py-3"><span className="text-xs px-2 py-0.5 rounded-full bg-amber-100 text-amber-700">{r.status}</span></td>
                <td className="px-5 py-3"><button onClick={()=>{setSelected(r);setForm({status:"RESOLVED",admin_response:""}); }} className="text-green-700 text-xs font-medium hover:underline">Respond</button></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {selected && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-xl p-6 w-full max-w-md">
            <h3 className="font-bold mb-4">Respond to: {selected.title}</h3>
            <select value={form.status} onChange={(e)=>setForm({...form,status:e.target.value})} className="w-full border rounded-lg px-3 py-2 text-sm mb-3">
              <option value="UNDER_REVIEW">Under Review</option><option value="RESOLVED">Resolved</option><option value="DISMISSED">Dismissed</option>
            </select>
            <textarea value={form.admin_response} onChange={(e)=>setForm({...form,admin_response:e.target.value})} rows={4} placeholder="Official response…" className="w-full border rounded-lg px-3 py-2 text-sm mb-4" />
            <div className="flex gap-3">
              <button onClick={handleRespond} className="flex-1 bg-green-600 text-white py-2 rounded-lg font-medium">Submit</button>
              <button onClick={()=>setSelected(null)} className="px-4 py-2 border rounded-lg text-gray-600">Cancel</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
