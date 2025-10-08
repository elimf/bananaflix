# API Upload FastAPI 

Cette partie du projet fournit une API **FastAPI** avec **Redis** et l'upload des videos via **Tortoise ORM**.  

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

Depuis le dossier `upload` avec le venv activé :

```bash
python main.py
```

* L’API sera accessible sur : `http://127.0.0.1:8006`
* La documentation Swagger : `http://127.0.0.1:8006/docs`

---

## Routes principales

| Méthode | Endpoint  | Description                                      |
| ------- | --------- | ------------------------------------------------ |
| POST     | /upload   | Upload une vidéo.                               |

---

## Licence

MIT
## Author
@Safouuuuu