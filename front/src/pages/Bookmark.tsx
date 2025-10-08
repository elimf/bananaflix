import { useAuth } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import "../style/Bookmark.css";
import type { BookmarkVideo } from "../types";
import { allImages } from "../data/sections";



export default function Bookmark() {
  const { token } = useAuth();
  const navigate = useNavigate();
  const [bookmarks, setBookmarks] = useState<BookmarkVideo[]>([]);
  const [loading, setLoading] = useState(true);
  if (!token) {
    navigate("/login");
    return null;
  }

  useEffect(() => {
    const fetchBookmarks = async () => {
      try {
        const res = await fetch(`http://localhost:8000/bookmarks/user`, {
          headers: { Authorization: `Bearer ${token}` },
        });

        if (!res.ok) throw new Error("Erreur lors de la récupération des favoris");

        const data: BookmarkVideo[] = await res.json();
        setBookmarks(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchBookmarks();
  }, [token]);

  const handleDeleteBookmark = async (bookmark_uuid: string) => {
    if (!bookmark_uuid) return;

    try {
      const res = await fetch(`http://localhost:8000/bookmarks`, {
        method: "DELETE",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ uuid: bookmark_uuid })
      });

      if (!res.ok) throw new Error("Impossible de supprimer le favori");
      setBookmarks((prev) => prev.filter((b) => b.bookmark_uuid !== bookmark_uuid));

      console.log("Favori supprimé !");
    } catch (err) {
      console.error("Erreur lors de la suppression du favori :", err);
    }
  };



  if (loading) {
    return <p>Chargement des favoris...</p>;
  }

  return (
    <div className="fav__container">
      <section className="fav__top_bar">
        <div className="fav__title">
          <h1>Ma liste</h1>
        </div>
        <div className="fav__filter_buttons">
          <p className="fav__btn fav__btn_all">Voir tous les favoris</p>
          <p className="fav__btn fav__btn_genres">Voir les genres</p>
        </div>
      </section>

      <section className="fav__list__items">
        {bookmarks.map((video) => (
          <div
            key={video.bookmark_uuid}
            className="fav__list_item"
          >
            {/* Tu peux remplacer l'image par un thumbnail réel si tu as */}
            {/* <img
                src={allImages[randomIndex]}
                alt={video.title}
              /> */}
            {bookmarks.map((bookmark) => {
              const randomIndex = Math.floor(Math.random() * allImages.length);
              return (
                <div
                  key={bookmark.bookmark_uuid}
                  className="video-card"
                  onClick={() => navigate(`/player/${bookmark.video_id}`)}
                  style={{ cursor: "pointer" }}
                >
                  <img src={allImages[randomIndex]} alt={video.title} />
                  <h3>{video.title}</h3>
                  <button
                    className="fav__delete_btn"
                    onClick={() => handleDeleteBookmark(video.bookmark_uuid)}
                  >
                    Supprimer
                  </button>
                </div>
              );
            })}
          </div>
        ))}
      </section>
    </div>
  );
}
