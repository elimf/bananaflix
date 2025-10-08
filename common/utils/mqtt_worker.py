from __future__ import annotations

import json
import logging
import os
from queue import Queue


logging.basicConfig(level=logging.DEBUG)

MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
MQTT_TOPIC_STATS = "metadata/stats-analyzed"

message_queue = Queue()

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logging.info("Connected to MQTT broker")
        client.subscribe(MQTT_TOPIC_STATS)
        logging.info(f"Listen to {MQTT_TOPIC_STATS}")
    else:
        logging.error(f"Failed to connect to MQTT broker: {rc}")

def on_disconnect(client, userdata, rc):
    logging.info("Disconnected from MQTT broker")

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
    except json.JSONDecodeError as e:
        logging.error(f"Erreur JSON: {e} - {msg.payload}")
        return

    logging.info(f"Received message {msg.topic}: {payload}")
    message_queue.put(payload)
