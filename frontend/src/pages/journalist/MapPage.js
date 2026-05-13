// frontend/src/pages/journalist/MapPage.js
// UC-15: Interactive map with color-coded risk pins.
// Uses Leaflet + react-leaflet + GeoJSON endpoint.

import React, { useEffect, useState } from "react";
import { MapContainer, TileLayer, CircleMarker, Popup } from "react-leaflet";
import { Link } from "react-router-dom";
import { getProjectsMap } from "../../api/endpoints";
import "leaflet/dist/leaflet.css";

// Risk level → circle color
const RISK_COLOR = {
  LOW   : "#16a34a",  // green
  MEDIUM: "#d97706",  // amber
  HIGH  : "#dc2626",  // red
};

const STATUS_LABEL = {
  OPEN      : "Open",
  REVIEW    : "Under Review",
  EXECUTION : "In Execution",
  COMPLETED : "Completed",
};

export default function MapPage() {
  const [features, setFeatures] = useState([]);
  const [filter,   setFilter]   = useState({ risk: "ALL", status: "ALL" });

  useEffect(() => {
    getProjectsMap().then((res) => setFeatures(res.data.features || []));
  }, []);

  const filtered = features.filter((f) => {
    const p = f.properties;
    if (filter.risk   !== "ALL" && p.risk_level !== filter.risk)   return false;
    if (filter.status !== "ALL" && p.status     !== filter.status) return false;
    return true;
  });

  return (
    <div className="h-screen flex flex-col">
      {/* Top bar */}
      <div className="bg-white border-b px-4 py-3 flex items-center gap-4 z-10 shadow-sm">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 bg-green-600 rounded-full flex items-center justify-center">
            <span className="text-white text-xs font-bold">G</span>
          </div>
          <span className="font-bold text-gray-800">GreenTrace</span>
        </div>

        {/* Filters */}
        <div className="flex gap-2 ml-4">
          <select
            value={filter.risk}
            onChange={(e) => setFilter({ ...filter, risk: e.target.value })}
            className="border border-gray-200 rounded-lg px-2 py-1 text-sm"
          >
            <option value="ALL">All Risk Levels</option>
            <option value="LOW">Low (Green)</option>
            <option value="MEDIUM">Medium (Amber)</option>
            <option value="HIGH">High (Red)</option>
          </select>
          <select
            value={filter.status}
            onChange={(e) => setFilter({ ...filter, status: e.target.value })}
            className="border border-gray-200 rounded-lg px-2 py-1 text-sm"
          >
            <option value="ALL">All Statuses</option>
            <option value="OPEN">Open</option>
            <option value="EXECUTION">In Execution</option>
            <option value="COMPLETED">Completed</option>
          </select>
        </div>

        {/* Legend */}
        <div className="ml-auto flex items-center gap-3 text-xs text-gray-600">
          {Object.entries(RISK_COLOR).map(([k, c]) => (
            <span key={k} className="flex items-center gap-1">
              <span className="w-3 h-3 rounded-full inline-block" style={{ background: c }} />
              {k}
            </span>
          ))}
          <span className="flex items-center gap-1">
            <span className="w-3 h-3 rounded-full inline-block border-2 border-red-600 bg-red-100" />
            Red Flag
          </span>
        </div>

        <Link to="/login" className="text-sm text-green-700 font-medium hover:underline">Sign In</Link>
      </div>

      {/* Map */}
      <MapContainer
        center={[41.33, 19.82]}  // Tirana, Albania
        zoom={8}
        className="flex-1"
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='© <a href="https://osm.org">OpenStreetMap</a>'
        />

        {filtered.map((f) => {
          const [lon, lat] = f.geometry.coordinates;
          const p          = f.properties;
          const color      = RISK_COLOR[p.risk_level] || "#6b7280";

          return (
            <CircleMarker
              key={p.id}
              center={[lat, lon]}
              radius={p.red_flag ? 12 : 9}
              pathOptions={{
                color      : p.red_flag ? "#dc2626" : color,
                fillColor  : color,
                fillOpacity: 0.85,
                weight     : p.red_flag ? 3 : 1,
              }}
            >
              <Popup>
                <div className="min-w-[180px]">
                  <p className="font-semibold text-gray-800 mb-1">{p.title}</p>
                  <p className="text-xs text-gray-500 mb-2">{STATUS_LABEL[p.status] || p.status}</p>

                  <div className="flex items-center gap-1 mb-1">
                    <span
                      className="w-2 h-2 rounded-full inline-block"
                      style={{ background: color }}
                    />
                    <span className="text-xs">{p.risk_level} Risk</span>
                  </div>

                  {p.red_flag && (
                    <p className="text-xs text-red-600 font-medium mb-2">🚩 Red Flag</p>
                  )}

                  <Link
                    to={`/projects/${p.id}`}
                    className="text-xs text-green-700 font-medium hover:underline"
                  >
                    View Details →
                  </Link>
                </div>
              </Popup>
            </CircleMarker>
          );
        })}
      </MapContainer>
    </div>
  );
}
