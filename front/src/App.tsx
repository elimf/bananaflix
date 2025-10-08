import './style/App.css';
import { Outlet, Link } from "react-router-dom";
import { useAuth } from "./context/AuthContext";

export default function App() {
  const { token, role } = useAuth();

  return (
    <div className="app">
      {token && (
        <div>
          <header>
            <div className="netflixLogo">
              <Link id="logo" to="/home" className="logo">Bananaflix</Link>
            </div>
            <nav className="main-nav">
              <Link to="/home" >Accueil</Link>
              <a>Séries</a>
              <a>Films</a>
              <a>Jeux</a>
              <a>Nouveautés les plus regardées</a>
              <Link to="/bookmark" >Ma Liste</Link>
              {role == 'admin' && (<Link to="/admin" >Page admin</Link>)}
            </nav>
            <nav className="sub-nav">
              <Link to="/search"><i className="fas fa-search sub-nav-logo"></i></Link>
              <a><i className="fas fa-bell sub-nav-logo"></i></a>
              <Link to="/account">Mon Compte</Link>
            </nav>
          </header>
        </div>
      )}
      <main className="main-content">
        <Outlet />
      </main>
    </div>
  );
}
