import { useAuth } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";

export default function Account() {
  const { token,logout } = useAuth();
  const navigate = useNavigate();

  if (!token) {
    navigate("/login");
    return null;
  }

  return (
    <div>
      <h1>Mon compte</h1>
        <button
              onClick={logout}
              className="btn-primary"
            >
              Déconnexion
            </button>
    </div>
  );
}
