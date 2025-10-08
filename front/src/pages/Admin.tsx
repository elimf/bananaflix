import { useState, useEffect } from "react";
import "../style/Admin.css";
import type { GlobalStats } from "../types";

export default function Admin() {
  const [file, setFile] = useState<File | null>(null);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [duration, setDuration] = useState<number>(0);
  const [genreId, setGenreId] = useState<number>(0);
  const [globalStats, setGlobalStats] = useState<GlobalStats>([]);
  const [genres, setGenres] = useState<{ uuid: number; name: string }[]>([]);

  const formatDuration = (seconds: number) => {
    const minutes = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${String(minutes).padStart(2, "0")}:${String(secs).padStart(2, "0")}`;
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    if (f) {
      setFile(f);

      const videoElement = document.createElement("video");
      videoElement.preload = "metadata";

      videoElement.onloadedmetadata = () => {
        window.URL.revokeObjectURL(videoElement.src);

        const meta = {
          name: f.name,
          duration: Math.floor(videoElement.duration),
        };
        setDuration(meta.duration);
        setTitle(meta.name)
      };

      videoElement.src = URL.createObjectURL(f);
    }
  };


  const handleUpload = async () => {
    if (!file) return;
    const formData = new FormData();
    formData.append("file", file);
    formData.append("title", title);
    formData.append("description", description);
    formData.append("duration", duration.toString());
    formData.append("genre_id", genreId.toString());
    formData.append("generate_trailer", "false");

    try {
      const response = await fetch("http://localhost:8000/upload", {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        alert("Upload réussi !");
      } else {
        const errorData = await response.json();
        alert("Erreur lors de l'upload : " + (errorData.detail || response.statusText));
      }
    } catch (err) {
      console.error(err);
      alert("Erreur lors de l'upload");
    }
  };

  useEffect(() => {
    const fetchGenres = async () => {
      try {
        const res = await fetch("http://localhost:8000/genres");
        if (!res.ok) throw new Error("Erreur lors de la récupération des genres");
        const data = await res.json();
        setGenres(data);
        if (data.length > 0) setGenreId(data[0].uuid);
      } catch (err) {
        console.error(err);
      }
    };
    const fetchGlobalStats = async () => {
      try {
        const res = await fetch("http://localhost:8000/stats/global");
        if (!res.ok) throw new Error("Erreur lors de la récupération des genres");
        const data = await res.json();
        if (data.length > 0) setGlobalStats(data);
      } catch (err) {
        console.error(err);
      }
    };
    fetchGenres();
    fetchGlobalStats();
  }, []);
  return (
    <div className="">
      <div className="upload-container">
        <h2>🎬 Upload Vidéo (Admin)</h2>

        <div className="form-group">
          <label>Fichier vidéo</label>
          <input type="file" accept="video/*" onChange={handleFileChange} />
        </div>

        {file && (
          <video className="preview" src={URL.createObjectURL(file)} controls />
        )}

        <div className="form-group">
          <label>Titre</label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Titre de la vidéo"
          />
        </div>

        <div className="form-group">
          <label>Description</label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Décris la vidéo"
          ></textarea>
        </div>

        <div className="form-group">
          <label>Genre</label>
          <select value={genreId} onChange={(e) => setGenreId(Number(e.target.value))}>
            {genres.map((genre) => (
              <option key={genre.uuid} value={genre.uuid}>
                {genre.name}
              </option>
            ))}
          </select>
        </div>

        {duration > 0 && (
          <p className="info">Durée détectée : {formatDuration(duration)}</p>
        )}

        <button onClick={handleUpload} disabled={!file}>
          Publier
        </button>
      </div>
      <div style={{ padding: "20px" }}>
        <h2>Stats Globales</h2>
        {globalStats.length === 0 ? (
          <p>Aucune donnée pour le moment</p>
        ) : (
          globalStats.map(({ video, stats }) => (
            <div
              key={video.id}
              style={{
                border: "1px solid #ddd",
                borderRadius: "8px",
                padding: "15px",
                marginBottom: "10px",
              }}
            >
              <h3>Titre:{video.title}</h3>
              <p>Description: {video.description}</p>
              <p>
                <strong>Durée :</strong> {video.duration}s |{" "}
                <strong>Status :</strong> {video.status}
              </p>
              <hr />
              <p>
                <strong>Stats :</strong>
              </p>
              <ul>
                <li>Vues : {stats.as_view}</li>
                <li>Bookmarks ajoutés : {stats.add_bookmark}</li>
                <li>Bookmarks supprimés : {stats.remove_bookmark}</li>
                <li>Pause : {stats.pause}</li>
                <li>Stop : {stats.stop}</li>
              </ul>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
