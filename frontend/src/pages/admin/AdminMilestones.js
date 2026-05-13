// frontend/src/pages/admin/AdminMilestones.js
// UC-11, UC-12: Admin reviews, approves or rejects compliance evidence.

import React, { useEffect, useState } from "react";
import { getMilestones, reviewMilestone } from "../../api/endpoints";
import toast from "react-hot-toast";

const STATUS_BADGE = {
  PENDING          : "bg-gray-100 text-gray-600",
  SUBMITTED        : "bg-blue-100 text-blue-700",
  APPROVED         : "bg-green-100 text-green-700",
  REJECTED         : "bg-red-100 text-red-700",
  OVERDUE          : "bg-red-200 text-red-800",
  ACTION_REQUIRED  : "bg-amber-100 text-amber-700",
  EXTENSION_PENDING: "bg-purple-100 text-purple-700",
};

export default function AdminMilestones() {
  const [milestones, setMilestones] = useState([]);
  const [selected,   setSelected]   = useState(null);
  const [comment,    setComment]     = useState("");
  const [loading,    setLoading]     = useState(true);

  const load = () =>
    getMilestones().then((res) => {
      setMilestones(res.data.results || res.data);
      setLoading(false);
    });

  useEffect(() => { load(); }, []);

  const handleReview = async (action) => {
    if (action === "reject" && !comment.trim()) {
      toast.error("A comment is required when rejecting.");
      return;
    }
    try {
      await reviewMilestone(selected.id, { action, comment });
      toast.success(`Milestone ${action === "approve" ? "approved" : "rejected"}.`);
      setSelected(null);
      setComment("");
      load();
    } catch (err) {
      toast.error(err.response?.data?.detail || "Action failed.");
    }
  };

  if (loading) return <Spinner />;

  const submitted = milestones.filter((m) => m.status === "SUBMITTED");
  const others    = milestones.filter((m) => m.status !== "SUBMITTED");

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-1">Milestone Reviews</h1>
      <p className="text-gray-500 text-sm mb-6">
        {submitted.length} pending review{submitted.length !== 1 ? "s" : ""}
      </p>

      {/* Submitted — needs action */}
      {submitted.length > 0 && (
        <div className="mb-8">
          <h2 className="font-semibold text-gray-700 mb-3 text-sm uppercase tracking-wide">
            Needs Review
          </h2>
          <div className="flex flex-col gap-3">
            {submitted.map((m) => (
              <div key={m.id}
                className="bg-white rounded-xl border border-blue-200 shadow-sm p-5 flex items-start justify-between gap-4">
                <div className="flex-1">
                  <p className="font-semibold text-gray-800">{m.title}</p>
                  <p className="text-sm text-gray-500 mt-0.5">
                    Deadline: {new Date(m.deadline).toLocaleDateString()} · Weight: {m.weight}
                  </p>
                </div>
                <button
                  onClick={() => { setSelected(m); setComment(""); }}
                  className="bg-green-600 text-white text-sm px-4 py-1.5 rounded-lg hover:bg-green-700 transition whitespace-nowrap">
                  Review
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* All other milestones */}
      <div>
        <h2 className="font-semibold text-gray-700 mb-3 text-sm uppercase tracking-wide">All Milestones</h2>
        <div className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 text-gray-500 text-xs border-b">
              <tr>
                <th className="px-5 py-3 text-left">Title</th>
                <th className="px-5 py-3 text-left">Status</th>
                <th className="px-5 py-3 text-left">Deadline</th>
                <th className="px-5 py-3 text-left">Weight</th>
              </tr>
            </thead>
            <tbody>
              {milestones.map((m) => (
                <tr key={m.id} className="border-t hover:bg-gray-50">
                  <td className="px-5 py-3 font-medium text-gray-800">{m.title}</td>
                  <td className="px-5 py-3">
                    <span className={`text-xs px-2 py-0.5 rounded-full ${STATUS_BADGE[m.status] || "bg-gray-100 text-gray-600"}`}>
                      {m.status.replace("_", " ")}
                    </span>
                  </td>
                  <td className="px-5 py-3 text-gray-500">{new Date(m.deadline).toLocaleDateString()}</td>
                  <td className="px-5 py-3 text-gray-500">{m.weight}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Review modal */}
      {selected && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-xl p-6 w-full max-w-md">
            <h3 className="font-bold text-gray-900 mb-1">Review Milestone</h3>
            <p className="text-sm text-gray-500 mb-4">{selected.title}</p>

            <label className="block text-sm font-medium text-gray-700 mb-1">
              Comment (required for rejection)
            </label>
            <textarea
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              rows={3}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm mb-4 focus:outline-none focus:ring-2 focus:ring-green-600"
              placeholder="Add a review comment…"
            />

            <div className="flex gap-3">
              <button
                onClick={() => handleReview("approve")}
                className="flex-1 bg-green-600 text-white py-2 rounded-lg font-medium hover:bg-green-700 transition">
                ✓ Approve
              </button>
              <button
                onClick={() => handleReview("reject")}
                className="flex-1 bg-red-500 text-white py-2 rounded-lg font-medium hover:bg-red-600 transition">
                ✗ Reject
              </button>
              <button
                onClick={() => setSelected(null)}
                className="px-4 py-2 border rounded-lg text-gray-600 hover:bg-gray-50 transition">
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function Spinner() {
  return <div className="flex items-center justify-center h-screen"><div className="w-8 h-8 border-4 border-green-600 border-t-transparent rounded-full animate-spin" /></div>;
}
