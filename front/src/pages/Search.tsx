import { useState, useEffect } from "react";
import type { Video } from "../types";

export default function Search() {
  const [title, setTitle] = useState("");
  const [genres, setGenres] = useState<string[]>([]);
  const [results, setResults] = useState<Video[]>([]);
  const [loading, setLoading] = useState(false);
  const [suggestions, setSuggestions] = useState<string[]>([]);

  const API_URL = "http://localhost:8005";

  const fetchSuggestions = async () => {
    try {
      const res = await fetch(`${API_URL}/suggestions`);
      const data = await res.json();
      setSuggestions(data);
    } catch (err) {
      console.error("Erreur suggestions:", err);
    }
  };

  useEffect(() => {
    fetchSuggestions();
  }, []);

  const toggleGenre = (g: string) => {
    setGenres((prev) =>
      prev.includes(g) ? prev.filter((x) => x !== g) : [...prev, g]
    );
  };

  const resetGenres = () => setGenres([]);

  const handleSearch = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (title) params.append("title", title);
      if (genres.length > 0) params.append("genre", genres.join(","));

      const res = await fetch(`${API_URL}/search?${params.toString()}`);
      const data = await res.json();
      setResults(Array.isArray(data) ? data : [data]);
    } catch (err) {
      console.error("Erreur API:", err);
      setResults([]);
    } finally {
      setLoading(false);
      fetchSuggestions();
    }
  };

  return (
    <div style={{ maxWidth: "900px", margin: "2rem auto", fontFamily: "sans-serif" }}>
      <h1 style={{ marginBottom: "1rem" }}>Recherche de vidéos</h1>

      {/* Zone de recherche */}
      <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem", marginBottom: "1.5rem" }}>
        <input
          type="text"
          placeholder="Titre..."
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          list="suggestions"
          style={{ padding: "0.5rem" }}
        />
        <datalist id="suggestions">
          {suggestions.map((s, i) => (
            <option key={i} value={s} />
          ))}
        </datalist>

        {/* Filtres genres */}
        <div style={{ display: "flex", gap: "0.5rem", marginBottom: "1rem" }}>
          {["Action", "Comedie", "SF"].map((g) => (
            <button
              key={g}
              onClick={() => toggleGenre(g)}
              style={{
                color: "black",
                padding: "0.5rem 1rem",
                border: genres.includes(g) ? "2px solid #007BFF" : "1px solid #ccc",
                borderRadius: "4px",
                background: genres.includes(g) ? "#E6F0FF" : "#fff",
                cursor: "pointer",
              }}
            >
              {g}
            </button>
          ))}

          {/* Bouton reset du filtre */}
          <button
            onClick={resetGenres}
            style={{
              color: "black",
              padding: "0.5rem 1rem",
              border: "1px solid #ccc",
              borderRadius: "4px",
              background: genres.length === 0 ? "#f8f8f8" : "#fff",
              cursor: "pointer",
            }}
          >
            Réinitialiser
          </button>
        </div>

        <div style={{ display: "flex", gap: "0.5rem" }}>
          <button onClick={handleSearch} style={{ flex: 1, padding: "0.5rem" }}>
            Rechercher
          </button>
        </div>
      </div>

      {/* Résultats */}
      {loading && <p style={{ textAlign: "center" }}>⏳ Chargement...</p>}

      {results.length > 0 ? (
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))",
            gap: "1rem",
          }}
        >
          {results.map((video) => (
            <div
              key={video.id}
              style={{
                border: "1px solid #ddd",
                borderRadius: "8px",
                overflow: "hidden",
                background: "#fff",
                boxShadow: "0 2px 5px rgba(0,0,0,0.1)",
              }}
            >
              {/* Zone miniature */}
              <div
                style={{
                  background: "#eee",
                  height: "120px",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontSize: "0.9rem",
                  color: "#888",
                }}
              >
                {video.title}
              </div>

              {/* Infos vidéo */}
              <div style={{ padding: "0.75rem", color: "#000" }}>
                <strong>{video.title}</strong>
                <p style={{ margin: "0.25rem 0", fontSize: "0.9rem", color: "#555" }}>
                  ⏱ {video.duration} min
                </p>
                <p style={{ margin: "0.25rem 0", fontSize: "0.85rem", color: "#777" }}>
                  {video.genre?.name || "Sans genre"}
                </p>
              </div>
            </div>
          ))}
        </div>
      ) : (
        !loading && <p style={{ textAlign: "center" }}>Aucun résultat</p>
      )}
    </div>
  );
}
