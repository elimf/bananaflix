import { useState } from "react";
import { useAuth } from "../context/AuthContext";
import axios from "axios";
import { useNavigate,Link } from "react-router-dom";
import '../style/Auth.css';

export default function Login() {
  const [pseudo, setPseudo] = useState("");
  const [password, setPassword] = useState("");
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await axios.post("http://localhost:8000/login", { pseudo, password });
      login(res.data.access_token);
      navigate("/home");
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    } catch (err) {
      alert("Une erreur est survenue lors de la connexion");
    }
  };

  return (
    <div className="auth-container">
      <form onSubmit={handleLogin} className="auth-form">
        <h1 className="auth-title">Bananaflix - Login</h1>

        <input
          className="auth-input"
          value={pseudo}
          onChange={(e) => setPseudo(e.target.value)}
          placeholder="Pseudo"
          required
        />

        <input
          className="auth-input"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Mot de passe"
          required
        />

        <button type="submit" className="auth-btn">Connexion</button>
          <p className="auth-footer">
          Pas de compte ? <Link to="/register">Inscrivez-vous ici</Link>
        </p>
      </form>
    </div>
  );
}
