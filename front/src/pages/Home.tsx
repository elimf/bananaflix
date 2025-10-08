import { useAuth } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import "../style/Home.css";
import type { VideoDetail } from "../types";
import { allImages } from "../data/sections";



export default function Home() {
  const { token } = useAuth();
  const navigate = useNavigate();
  const [videos, setVideos] = useState<VideoDetail[]>([]);
  const [loading, setLoading] = useState(true);

  if (!token) {
    navigate("/login");
    return null;
  }

  useEffect(() => {
    const fetchVideos = async () => {
      try {
        const res = await fetch("http://localhost:8000/videos", {
          headers: { Authorization: `Bearer ${token}` },
        });
        const data = await res.json();
        setVideos(data.videos);
      } catch (err) {
        console.error("Erreur lors de la récupération des vidéos :", err);
      } finally {
        setLoading(false);
      }
    };
    fetchVideos();
  }, [token]);

  if (loading) return <p>Chargement des vidéos...</p>;

  return (
    <div className="main-container">
      <div className="section">
        <h1>Vidéos</h1>
        <div className="box">
          {videos.map((video) => {
            const randomIndex = Math.floor(Math.random() * allImages.length);
            return (
              <div
                key={video.id}
                className="video-card"
                onClick={() => navigate(`/player/${video.id}`)}
                style={{ cursor: "pointer" }}
              >
                <img src={allImages[randomIndex]} alt={video.title} />
                <h3>{video.title}</h3>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}