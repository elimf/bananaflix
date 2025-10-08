import os

SECRET_KEY = "secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOUR = 7
STATS_SERVICE_URL = "http://stats:8001"
PLAYER_VIDEO_URL = "http://video-player:8004"
BOOKMARK_SERVICE_URL = "http://bookmarks:8003"
MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
UPLOAD_SERVICE_URL = "http://upload-service:8006"
CONVERTER_SERVICE_URL = "http://video-convert-service:8002"
