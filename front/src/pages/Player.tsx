import { useEffect, useRef, useState } from "react";
import type { VideoDetail, VideoStats, VideoUserInfo } from "../types";
import { useAuth } from "../context/AuthContext";
import { useParams } from "react-router-dom";
import "../style/Player.css";

export default function Player() {
    const { token } = useAuth();
    const { id } = useParams<{ id: string }>();
    const videoRef = useRef<HTMLVideoElement | null>(null);
    const [quality, setQuality] = useState<string>("720p");
    const [userVideoInfo, setUserVideoInfo] = useState<VideoUserInfo | null>(null);
    const [videoInfo, setVideoInfo] = useState<VideoDetail | null>(null);
    const [videoStats, setVideoStats] = useState<VideoStats | null>(null);
    const [bookmarkAdded, setBookmarkAdded] = useState(false);

    const saveProgress = async () => {
        if (!videoRef.current || userVideoInfo == null) return;
        if (videoRef.current.paused) return
        const progress = videoRef.current.currentTime;

        try {
            await fetch("http://localhost:8000/videos/progress/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    video_user_info: userVideoInfo.id,
                    progress_duration: Math.round(progress)
                })
            });
        } catch (error) {
            console.error("Erreur lors de la sauvegarde de la progression :", error);
        }
    };
    const handleAddBookmark = async () => {
        if (!id) return;

        try {
            const res = await fetch("http://localhost:8000/bookmarks", {
                method: "POST",
                headers: {
                    "Authorization": `Bearer ${token}`,
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    user_id: userVideoInfo?.user_id,
                    video_id: Number(id)
                })
            });

            if (!res.ok) throw new Error("Impossible d'ajouter aux favoris");

            setBookmarkAdded(true);
            console.log("Vidéo ajoutée aux favoris !");
        } catch (err) {
            console.error("Erreur lors de l'ajout aux favoris :", err);
        }
    };

    // eslint-disable-next-line react-hooks/exhaustive-deps
    const sendStat = async (key: string) => {
        try {
            await fetch("http://localhost:8000/videos/stats/", {
                method: "POST",
                headers: {
                    "Authorization": `Bearer ${token}`,
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    video_id: id,
                    event_stat: key
                })
            });
        } catch (error) {
            console.error("Erreur lors de la sauvegarde de la progression :", error);
        }
    }

    useEffect(() => {
        const videoEl = videoRef.current;
        if (!videoEl) return;

        let hasSentView = false;

        const handlePlay = () => {
            if (!hasSentView) {
                sendStat("as_view");
                hasSentView = true;
            }
            sendStat("play");
        };

        const handlePause = () => sendStat("pause");

        const handleBeforeUnload = () => {
            sendStat("stop");
        };

        videoEl.addEventListener("play", handlePlay);
        videoEl.addEventListener("pause", handlePause);
        window.addEventListener("beforeunload", handleBeforeUnload);

        return () => {
            videoEl.removeEventListener("play", handlePlay);
            videoEl.removeEventListener("pause", handlePause);
            window.removeEventListener("beforeunload", handleBeforeUnload);

            sendStat("stop");
        };
    }, [sendStat, videoInfo]);


    useEffect(() => {
        const videoEl = videoRef.current;
        if (!videoEl) return;

        const fetchProgressAndStart = async () => {
            try {
                const res = await fetch(
                    `http://localhost:8000/video-info-user/?video_id=${id}&quality=${quality}`, {
                    method: "GET",
                    headers: {
                        "Authorization": `Bearer ${token}`,
                        "Content-Type": "application/json",
                    },
                });
                const data = await res.json();
                setUserVideoInfo(data.user_info_video)
                setVideoInfo(data.video)

                const progress = data.user_info_video.progress_duration ?? 0;

                videoEl.src = `http://localhost:8000/videos/${id}?quality=${quality}`;
                videoEl.load();
                videoEl.currentTime = progress;
                videoEl.play().catch((err) =>
                    console.warn("Lecture automatique impossible :", err)
                );
            } catch (error) {
                console.error("Erreur lors de la récupération de la vidéo :", error);
            }
        };

        const fetchGlobalStats = async () => {
            try {
                const res = await fetch(`http://localhost:8000/stats/video/${id}`);
                if (!res.ok) throw new Error("Erreur lors de la récupération des stats");
                const data = await res.json();
                console.log(data);
                setVideoStats(data);
            } catch (err) {
                console.error(err);
            }
        };

        fetchProgressAndStart();
        fetchGlobalStats();
    }, [id, quality]);

    useEffect(() => {
        if (!userVideoInfo) return;

        const intervalId = setInterval(saveProgress, 5000);

        return () => clearInterval(intervalId);
    }, [userVideoInfo]);

    return (
        <div className="player-container">
            <h1 className="player-title">{videoInfo?.title}</h1>

            <div className="video-wrapper">
                <video ref={videoRef} controls className="video-player" />
            </div>

            {videoInfo && (
                <div className="quality-selector">
                    {Object.keys(videoInfo.qualities).map((q) => (
                        <label key={q} className="quality-option">
                            <input
                                type="radio"
                                name="quality"
                                value={q}
                                checked={quality === q}
                                onChange={() => setQuality(q as keyof typeof videoInfo.qualities)}
                            />
                            <span>{q}</span>
                        </label>
                    ))}
                </div>
            )}

            {/* Infos vidéo */}
            {videoInfo && videoStats && (
                <div className="video-info">
                    <h2>Infos vidéo</h2>
                    <p><strong>Titre :</strong> {videoInfo.title}</p>
                    <p><strong>Description :</strong> {videoInfo.description}</p>
                    <h2>Stats globales</h2>
                    <ul>
                        <li><strong>Vues :</strong> {videoStats.stats.as_view}</li>
                        <li><strong>Pause :</strong> {videoStats.stats.pause}</li>
                        <li><strong>Play :</strong> {videoStats.stats.play}</li>
                        <li><strong>Arrêts :</strong> {videoStats.stats.stop}</li>
                        <li><strong>Ajouts favoris :</strong> {videoStats.stats.add_bookmark}</li>
                        <li><strong>Retraits favoris :</strong> {videoStats.stats.remove_bookmark}</li>
                    </ul>
                    <div className="bookmark-button">
                        <button onClick={handleAddBookmark} disabled={bookmarkAdded}>
                            {bookmarkAdded ? "Ajouté aux favoris ✅" : "Ajouter aux favoris"}
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
}
