// frontend/src/context/AuthContext.js
// Global auth state: user, role, login, logout.

import React, { createContext, useContext, useState, useEffect } from "react";
import { login as apiLogin, logout as apiLogout, getMe } from "../api/endpoints";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user,    setUser]    = useState(null);
  const [loading, setLoading] = useState(true);

  // On mount: restore session from localStorage
  useEffect(() => {
    const token = localStorage.getItem("access");
    if (token) {
      getMe()
        .then((res) => setUser(res.data))
        .catch(()   => { localStorage.clear(); setUser(null); })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (email, password) => {
    const res = await apiLogin({ username: email, password });
    localStorage.setItem("access",  res.data.access);
    localStorage.setItem("refresh", res.data.refresh);
    const me = await getMe();
    setUser(me.data);
    return me.data;
  };

  const logout = async () => {
    const refresh = localStorage.getItem("refresh");
    try { await apiLogout(refresh); } catch {}
    localStorage.clear();
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
