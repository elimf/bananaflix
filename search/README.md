# API Search FastAPI 

Cette partie du projet fournit une API **FastAPI** avec **Redis** et gestion de la recherche via **Tortoise ORM**.  

---

## Prérequis

- Python 3.10+  
- pip  
- (Optionnel) Git si tu clônes le projet  

---

## Installation

1. **Créer un environnement virtuel** (venv) :

```bash
cd stats
python3 -m venv venv
```

2. **Activer le venv** :

* macOS / Linux :

```bash
source venv/bin/activate
```

* Windows (PowerShell) :

```powershell
.\venv\Scripts\Activate
```

3. **Installer les dépendances** :

```bash
pip install -r requirements.txt
```


---

## Lancer l’API

Depuis le dossier `search` avec le venv activé :

```bash
python main.py
```

* L’API sera accessible sur : `http://127.0.0.1:8001`
* La documentation Swagger : `http://127.0.0.1:8001/docs`

---

## Routes principales

| Méthode | Endpoint  | Description                                      |
| ------- | --------- | ------------------------------------------------ |
| GET     | /search   | Rechercher une vidéo                             |
| GET     | /suggestions| Recuperer des suggestions de recherche         |

---

## Licence

MIT
## Author
@JeremyBala