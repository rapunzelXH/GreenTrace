// frontend/src/pages/auth/RegisterPage.js
import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { register } from "../../api/endpoints";
import toast from "react-hot-toast";

export default function RegisterPage() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    username: "", email: "", password: "", password2: "",
    role: "JOURNALIST", first_name: "", last_name: "",
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (form.password !== form.password2) {
      toast.error("Passwords do not match.");
      return;
    }
    setLoading(true);
    try {
      await register(form);
      toast.success("Account created! Please log in.");
      navigate("/login");
    } catch (err) {
      const data = err.response?.data;
      const msg  = data ? Object.values(data).flat().join(" ") : "Registration failed.";
      toast.error(msg);
    } finally {
      setLoading(false);
    }
  };

  const field = (label, name, type = "text", placeholder = "") => (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-1">{label}</label>
      <input
        type={type}
        required
        value={form[name]}
        onChange={(e) => setForm({ ...form, [name]: e.target.value })}
        placeholder={placeholder}
        className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand"
      />
    </div>
  );

  return (
    <div className="min-h-screen bg-brand-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-lg p-8 w-full max-w-md">
        <div className="flex items-center gap-2 mb-6">
          <div className="w-8 h-8 bg-brand rounded-full flex items-center justify-center">
            <span className="text-white text-sm font-bold">G</span>
          </div>
          <span className="text-xl font-bold text-gray-800">GreenTrace</span>
        </div>
        <h1 className="text-2xl font-bold text-gray-900 mb-1">Create account</h1>
        <p className="text-gray-500 text-sm mb-6">Join the environmental accountability platform</p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            {field("First name", "first_name", "text", "John")}
            {field("Last name",  "last_name",  "text", "Doe")}
          </div>
          {field("Username", "username", "text", "john_doe")}
          {field("Email",    "email",    "email", "john@example.com")}

          {/* Role selector */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Role</label>
            <select
              value={form.role}
              onChange={(e) => setForm({ ...form, role: e.target.value })}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand"
            >
              <option value="JOURNALIST">Journalist / Public</option>
              <option value="BUSINESS">Business / Contractor</option>
            </select>
          </div>

          {field("Password",        "password",  "password", "Min 8 characters")}
          {field("Confirm password","password2", "password", "Repeat password")}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-brand text-white py-2 rounded-lg font-medium hover:bg-brand-900 transition disabled:opacity-50"
          >
            {loading ? "Creating account…" : "Create Account"}
          </button>
        </form>

        <p className="text-center text-sm text-gray-500 mt-4">
          Already have an account?{" "}
          <Link to="/login" className="text-brand font-medium hover:underline">Sign in</Link>
        </p>
      </div>
    </div>
  );
}
