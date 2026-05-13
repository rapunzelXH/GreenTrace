import React, { useEffect, useState } from "react";
import { getMilestones, uploadEvidence } from "../../api/endpoints";
import toast from "react-hot-toast";

export default function BusinessMilestones() {
  const [milestones, setMilestones] = useState([]);
  const [uploading,  setUploading]  = useState(null);
  const [file, setFile] = useState(null);
  const [category, setCategory] = useState("PHOTO");

  useEffect(() => { getMilestones().then((r)=>setMilestones(r.data.results||r.data)); },[]);

  const handleUpload = async () => {
    if (!file) { toast.error("Select a file."); return; }
    const fd = new FormData();
    fd.append("milestone", uploading.id);
    fd.append("category",  category);
    fd.append("file",      file);
    try {
      await uploadEvidence(fd);
      toast.success("Evidence uploaded.");
      setUploading(null);
      const r = await getMilestones();
      setMilestones(r.data.results||r.data);
    } catch { toast.error("Upload failed."); }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">My Milestones</h1>
      <div className="flex flex-col gap-3">
        {milestones.map((m)=>(
          <div key={m.id} className="bg-white rounded-xl border border-gray-100 shadow-sm p-5 flex items-center justify-between gap-4">
            <div>
              <p className="font-semibold text-gray-800">{m.title}</p>
              <p className="text-sm text-gray-500">Deadline: {new Date(m.deadline).toLocaleDateString()} · Weight: {m.weight}</p>
            </div>
            <div className="flex items-center gap-3">
              <span className={`text-xs px-2 py-0.5 rounded-full ${m.status==="APPROVED"?"bg-green-100 text-green-700":m.status==="OVERDUE"?"bg-red-100 text-red-700":"bg-amber-100 text-amber-700"}`}>{m.status}</span>
              {["PENDING","OVERDUE","ACTION_REQUIRED"].includes(m.status) && (
                <button onClick={()=>setUploading(m)} className="bg-green-600 text-white text-sm px-3 py-1.5 rounded-lg hover:bg-green-700">Upload Evidence</button>
              )}
            </div>
          </div>
        ))}
      </div>
      {uploading && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-xl p-6 w-full max-w-md">
            <h3 className="font-bold mb-4">Upload Evidence: {uploading.title}</h3>
            <select value={category} onChange={(e)=>setCategory(e.target.value)} className="w-full border rounded-lg px-3 py-2 text-sm mb-3">
              <option value="PHOTO">Geotagged Photo</option><option value="DOCUMENT">Legal Document (PDF)</option>
            </select>
            <input type="file" accept={category==="PHOTO"?"image/*":".pdf"} onChange={(e)=>setFile(e.target.files[0])} className="w-full text-sm mb-4" />
            <div className="flex gap-3">
              <button onClick={handleUpload} className="flex-1 bg-green-600 text-white py-2 rounded-lg font-medium">Upload</button>
              <button onClick={()=>setUploading(null)} className="px-4 py-2 border rounded-lg text-gray-600">Cancel</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
