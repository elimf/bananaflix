import React, { createContext, useState, useContext } from "react";
import type {AuthContextType, TokenPayload} from "../types";

const AuthContext = createContext<AuthContextType | undefined>(undefined);

function decodeJWT(token: string): TokenPayload | null {
  try {
    const payload = token.split(".")[1]; // récupérer la partie payload
    const decoded = JSON.parse(atob(payload));
    return decoded as TokenPayload;
  } catch (e) {
    console.error("Invalid token", e);
    return null;
  }
}

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [token, setToken] = useState<string | null>(localStorage.getItem("token"));
  const [role, setRole] = useState<string | null>(localStorage.getItem("role"));

  const login = (newToken: string) => {
    const decoded = decodeJWT(newToken);
    if (!decoded) return;

    setToken(newToken);
    setRole(decoded.role);

    localStorage.setItem("token", newToken);
    localStorage.setItem("role", decoded.role);
  };

  const logout = () => {
    setToken(null);
    setRole(null);
    localStorage.removeItem("token");
    localStorage.removeItem("role");
  };

  return (
    <AuthContext.Provider value={{ token, role, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used inside AuthProvider");
  return context;
};
