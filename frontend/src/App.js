// frontend/src/App.js
// Role-based routing:
//   /               → redirect based on role
//   /login          → LoginPage
//   /register       → RegisterPage
//   /admin/*        → AdminLayout  (role=ADMIN)
//   /business/*     → BusinessLayout (role=BUSINESS)
//   /map            → MapPage (public)
//   /projects/:id   → ProjectDetailPage (public)

import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { Toaster } from "react-hot-toast";

import { AuthProvider, useAuth } from "./context/AuthContext";

// Auth
import LoginPage    from "./pages/auth/LoginPage";
import RegisterPage from "./pages/auth/RegisterPage";

// Admin
import AdminDashboard   from "./pages/admin/AdminDashboard";
import AdminProjects    from "./pages/admin/AdminProjects";
import AdminMilestones  from "./pages/admin/AdminMilestones";
import AdminReports     from "./pages/admin/AdminReports";
import AdminAuditLog    from "./pages/admin/AdminAuditLog";

// Business
import BusinessDashboard  from "./pages/business/BusinessDashboard";
import BusinessMilestones from "./pages/business/BusinessMilestones";
import CarbonCalculator   from "./pages/business/CarbonCalculator";
import TenderApply        from "./pages/business/TenderApply";

// Journalist / Public
import MapPage           from "./pages/journalist/MapPage";
import ProjectListPage   from "./pages/journalist/ProjectListPage";
import ProjectDetailPage from "./pages/journalist/ProjectDetailPage";
import ReportForm        from "./pages/journalist/ReportForm";
import EcoScoreComparePage from "./pages/journalist/EcoScoreComparePage";


// ── Route guards ─────────────────────────────────────────────────

function RequireAuth({ role, children }) {
  const { user, loading } = useAuth();
  if (loading) return <div className="flex items-center justify-center h-screen text-gray-500">Loading…</div>;
  if (!user)   return <Navigate to="/login" replace />;
  if (role && user.role !== role) return <Navigate to="/" replace />;
  return children;
}

function RoleRedirect() {
  const { user, loading } = useAuth();
  if (loading) return null;
  if (!user)            return <Navigate to="/login"      replace />;
  if (user.role === "ADMIN")      return <Navigate to="/admin"    replace />;
  if (user.role === "BUSINESS")   return <Navigate to="/business" replace />;
  return <Navigate to="/map" replace />;
}


// ── App ───────────────────────────────────────────────────────────

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Toaster position="top-right" />
        <Routes>
          {/* Public */}
          <Route path="/"         element={<RoleRedirect />} />
          <Route path="/login"    element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/map"      element={<MapPage />} />
          <Route path="/projects" element={<ProjectListPage />} />
          <Route path="/projects/:id" element={<ProjectDetailPage />} />
          <Route path="/report"   element={<ReportForm />} />
          <Route path="/compare"  element={<EcoScoreComparePage />} />

          {/* Admin */}
          <Route path="/admin" element={<RequireAuth role="ADMIN"><AdminDashboard /></RequireAuth>} />
          <Route path="/admin/projects"   element={<RequireAuth role="ADMIN"><AdminProjects /></RequireAuth>} />
          <Route path="/admin/milestones" element={<RequireAuth role="ADMIN"><AdminMilestones /></RequireAuth>} />
          <Route path="/admin/reports"    element={<RequireAuth role="ADMIN"><AdminReports /></RequireAuth>} />
          <Route path="/admin/audit"      element={<RequireAuth role="ADMIN"><AdminAuditLog /></RequireAuth>} />

          {/* Business */}
          <Route path="/business"            element={<RequireAuth role="BUSINESS"><BusinessDashboard /></RequireAuth>} />
          <Route path="/business/milestones" element={<RequireAuth role="BUSINESS"><BusinessMilestones /></RequireAuth>} />
          <Route path="/business/carbon"     element={<RequireAuth role="BUSINESS"><CarbonCalculator /></RequireAuth>} />
          <Route path="/business/apply/:id"  element={<RequireAuth role="BUSINESS"><TenderApply /></RequireAuth>} />

          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
