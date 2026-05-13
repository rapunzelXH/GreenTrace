// frontend/src/api/endpoints.js
// One function per API endpoint — matches backend urls.py exactly.

import client from "./client";

// ── Auth ─────────────────────────────────────────────────────────
export const register  = (data)    => client.post("/auth/register/", data);
export const login     = (data)    => client.post("/auth/login/",    data);
export const logout    = (refresh) => client.post("/auth/logout/",   { refresh });
export const getMe     = ()        => client.get("/auth/me/");
export const updateMe  = (data)    => client.put("/auth/me/",        data);

// ── Projects ──────────────────────────────────────────────────────
export const getProjects      = (params) => client.get("/projects/",         { params });
export const getProject       = (id)     => client.get(`/projects/${id}/`);
export const createProject    = (data)   => client.post("/projects/",        data);
export const updateProject    = (id, d)  => client.patch(`/projects/${id}/`, d);
export const getProjectsMap   = ()       => client.get("/projects/map/");
export const getProjectMilestones = (id) => client.get(`/projects/${id}/milestones/`);

// ── Milestones ────────────────────────────────────────────────────
export const getMilestones    = (params) => client.get("/milestones/",           { params });
export const createMilestone  = (data)   => client.post("/milestones/",          data);
export const reviewMilestone  = (id, d)  => client.post(`/milestones/${id}/review/`, d);

// ── Tender Applications ───────────────────────────────────────────
export const getApplications  = ()       => client.get("/applications/");
export const createApplication= (data)   => client.post("/applications/",         data, { headers: {"Content-Type": "multipart/form-data"} });
export const submitApplication= (id)     => client.post(`/applications/${id}/submit/`);
export const evaluateApplication=(id,d)  => client.post(`/applications/${id}/evaluate/`, d);

// ── Compliance Evidence ───────────────────────────────────────────
export const uploadEvidence   = (data)   => client.post("/evidence/",  data, { headers: {"Content-Type": "multipart/form-data"} });
export const getEvidence      = (params) => client.get("/evidence/",   { params });

// ── Carbon Data ───────────────────────────────────────────────────
export const getCarbonData    = (params) => client.get("/carbon/",     { params });
export const submitCarbonData = (data)   => client.post("/carbon/",    data);

// ── Extension Requests ────────────────────────────────────────────
export const requestExtension = (data)   => client.post("/extensions/",          data, { headers: {"Content-Type": "multipart/form-data"} });
export const reviewExtension  = (id, d)  => client.post(`/extensions/${id}/review/`, d);

// ── Discrepancy Reports ───────────────────────────────────────────
export const getReports       = ()       => client.get("/reports/");
export const submitReport     = (data)   => client.post("/reports/",             data, { headers: {"Content-Type": "multipart/form-data"} });
export const respondToReport  = (id, d)  => client.post(`/reports/${id}/respond/`, d);

// ── Project Follow ────────────────────────────────────────────────
export const getFollows       = ()       => client.get("/follows/");
export const followProject    = (data)   => client.post("/follows/",   data);
export const unfollowProject  = (id)     => client.delete(`/follows/${id}/`);

// ── Company Profile ───────────────────────────────────────────────
export const getMyCompany     = ()       => client.get("/companies/");
export const createCompany    = (data)   => client.post("/companies/",  data, { headers: {"Content-Type": "multipart/form-data"} });
export const updateCompany    = (id, d)  => client.patch(`/companies/${id}/`, d, { headers: {"Content-Type": "multipart/form-data"} });
export const compareEcoScores = (ids)    => client.post("/companies/compare/", { company_ids: ids });

// ── Audit Log ─────────────────────────────────────────────────────
export const getAuditLog      = (params) => client.get("/audit/",      { params });
