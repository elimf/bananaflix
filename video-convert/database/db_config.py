import os

DB_URL = "postgresql://localhost:5432/banana-db"

TORTOISE_ORM = {
    "connections": {
        "default": DB_URL,
    },
    "apps": {
        "models": {
            "models": ["models.video", "models.genre", "aerich.models"],
            "default_connection": "default"
        }
    }
}
