import {useState} from "react";
import axios from "axios";
import {useNavigate, Link} from "react-router-dom";

export default function Register() {
    const [pseudo, setPseudo] = useState("");
    const [password, setPassword] = useState("");
    const navigate = useNavigate();

    const handleRegister = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            await axios.post("http://localhost:8000/register", {pseudo, password});
            alert("Compte crée");
            navigate("/login");
        // eslint-disable-next-line @typescript-eslint/no-unused-vars
        } catch (err) {
            alert("Une erreur est survenue.");
        }
    };

    return (
        <div className="auth-container">
            <form onSubmit={handleRegister} className="auth-form">
                <h1 className="auth-title">BananaFlix - Register</h1>
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
                <button type="submit" className="auth-btn">S'incrire</button>
                <p className="auth-footer">
                    Déjà un compte ? <Link to="/login">Connectez-vous ici</Link>
                </p>
            </form>
        </div>

    );
}
