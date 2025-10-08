import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import App from "./App";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Home from "./pages/Home";
import { AuthProvider } from "./context/AuthContext";
import Bookmark from "./pages/Bookmark.tsx";
import Account from "./pages/Account.tsx";
import Player from "./pages/Player.tsx";
import Search from "./pages/Search.tsx";
import Admin from "./pages/Admin.tsx";
import AdminRoute from "./components/AdminRoute.tsx";

ReactDOM.createRoot(document.getElementById("root")!).render(
    <React.StrictMode>
        <BrowserRouter>
            <AuthProvider>
                <Routes>
                    <Route path="/" element={<App />}>
                        <Route path="login" index element={<Login />} />
                        <Route path="home" element={<Home />} />
                        <Route path="login" element={<Login />} />
                        <Route path="register" element={<Register />} />
                        <Route path="bookmark" element={<Bookmark />} />
                        <Route path="account" element={<Account />} />
                        <Route path="search" element={<Search />} />
                        <Route path="admin" element={<AdminRoute>
                            <Admin />
                        </AdminRoute>} />
                        <Route path="player/:id" element={<Player />} />
                    </Route>
                </Routes>
            </AuthProvider>
        </BrowserRouter>
    </React.StrictMode>
);
