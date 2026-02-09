# Bananaflix 🎬

**Bananaflix** est une plateforme de streaming vidéo moderne conçue pour gérer, rechercher et visionner facilement des vidéos. Elle combine une interface intuitive, un moteur de recherche puissant, et une architecture backend robuste pour offrir une expérience utilisateur fluide et réactive.

---

## 🛠️ Fonctionnalités principales

* **Recherche avancée de vidéos** par titre et genre.
* **Suggestions dynamiques** pour faciliter la recherche.
* **Gestion des vidéos** avec statut actif/inactif.
* **Streaming optimisé** avec conversion vidéo et traitement en arrière-plan.
* **Statistiques d’utilisation** pour analyser les performances et l’engagement.
* **Support multi-services** grâce à une architecture microservices :

  * `main-service` : gestion principale de l’application.
  * `search-service`: recherche et suggestion de vidéos.
  * `upload-service` : upload et gestion des fichiers vidéo.
  * `video-convert-service` : conversion et traitement des vidéos.
  * `video-player-service`: visualisation des vidéos.
  * `stats-service` : collecte et analyse des statistiques.
  * `mqtt` : communication en temps réel entre services.
  * `redis` et `PostgreSQL` : stockage des données et cache.

---

## ⚡ Technologies utilisées

* **Frontend** : React, TypeScript, Hooks, Datastores pour suggestions.
* **Backend** : FastAPI (Python), Uvicorn, MQTT pour messages temps réel.
* **Base de données** : PostgreSQL, Redis.
* **Microservices & DevOps** : Docker, Docker Compose pour orchestrer les services.

---

## 🚀 Installation et lancement

1. **Cloner le dépôt**

```bash
git clone https://github.com/ton-utilisateur/banaflix.git
cd banaflix
```

2. **Lancer tous les services**

```bash
docker-compose up --build
```

3. **Accéder à l’application**

* Frontend : `http://localhost:5173` (ou le port configuré)
* API backend : `http://localhost:8000` (service principal)

---

## 🧩 Structure du projet

```
/banaflix
├─ frontend/            # Interface React
├─ main-service/        # Backend principal (FastAPI)
├─ upload-service/      # Upload & gestion fichiers
├─ search-service/      # Recherche et suggestion de vidéos
├─ video-convert-service/ # Conversion vidéo
├─ video-player-service/ # Visualisation vidéo
├─ stats-service/       # Analyse des statistiques
├─ docker-compose.yml
└─ README.md
```

---

## 👨‍💻 Authors

* **Eddy** – Développeur  – [GitHub](https://github.com/EddyMzf)
* **Safouane** – Développeur  – [GitHub](https://github.com/Safouuuuu)
* **Moise** – Développeur  – [GitHub](https://github.com/Moiseng)
* **Jéremy** – Développeur  – [GitHub](https://github.com/JeremyBala)
* **Elim** – Développeur  – [GitHub](https://github.com/elimf)

---

## 📜 Licence

Ce projet est sous licence **MIT** – voir le fichier [LICENSE](LICENSE) pour plus de détails.

