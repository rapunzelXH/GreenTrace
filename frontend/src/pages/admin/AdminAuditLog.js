import React, { useEffect, useState } from "react";
import { getAuditLog } from "../../api/endpoints";

export default function AdminAuditLog() {
  const [logs, setLogs] = useState([]);
  useEffect(() => { getAuditLog().then((r)=>setLogs(r.data.results||r.data)); },[]);
  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Audit Log</h1>
      <div className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
        <table className="w-full text-xs">
          <thead className="bg-gray-50 text-gray-500 border-b">
            <tr><th className="px-5 py-3 text-left">Timestamp</th><th className="px-5 py-3 text-left">User</th><th className="px-5 py-3 text-left">Action</th><th className="px-5 py-3 text-left">Model</th><th className="px-5 py-3 text-left">IP</th></tr>
          </thead>
          <tbody>
            {logs.map((l)=>(
              <tr key={l.id} className="border-t hover:bg-gray-50">
                <td className="px-5 py-2 text-gray-500">{new Date(l.timestamp).toLocaleString()}</td>
                <td className="px-5 py-2 font-medium">{l.user?.username||"System"}</td>
                <td className="px-5 py-2 text-gray-700">{l.action}</td>
                <td className="px-5 py-2 text-gray-500">{l.model_name}</td>
                <td className="px-5 py-2 text-gray-400">{l.ip_address||"—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
