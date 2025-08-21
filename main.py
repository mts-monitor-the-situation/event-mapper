import threading
import signal
from concurrent.futures import ThreadPoolExecutor
import traceback

import googlemaps
import redis
from consumer.redis_consumer import start_consumer, retry_stalled_messages
from config import Config
from mongo import get_collection


def main():
    # Load the configuration file
    print("Loading configuration...")
    config = Config("config.yaml")
    google_maps_api_key = config.get("google_maps_api_key")
    redis_connection_string = config.get("redis_connection_string")
    mongodb_connection_string = config.get("mongodb_connection_string")

    # Initialize Redis and MongoDB connections
    r = redis.Redis.from_url(redis_connection_string)
    collection = get_collection(mongodb_connection_string)

    # Initialize Google Maps client
    gmaps = googlemaps.Client(key=google_maps_api_key)

    print("[Service] Starting GeoInference Redis Stream Consumer...")
    stop_event = threading.Event()

    # Handle shutdown signals
    def handle_shutdown(signum, frame):
        print(f"\n[Shutdown] Received signal {signum}. Stopping workers gracefully...")
        # print("Stack at interruption:")
        # traceback.print_stack(frame)
        stop_event.set()

    # Register for SIGTERM (docker/k8s) and SIGINT (Ctrl+C)
    signal.signal(signal.SIGTERM, handle_shutdown)
    signal.signal(signal.SIGINT, handle_shutdown)

    with ThreadPoolExecutor(max_workers=2) as executor:
        future_consumer = executor.submit(start_consumer, stop_event, r, collection, gmaps)
        future_retry = executor.submit(retry_stalled_messages, stop_event, r, collection, gmaps)

        # Wait for both threads to finish (or be interrupted)
        try:
            future_consumer.result()
            future_retry.result()
        except Exception as e:
            print(f"[FATAL] A thread crashed or was killed: {e}")
            stop_event.set()
            executor.shutdown(wait=True)
            raise SystemExit(1)

    print("[Service] Shutdown complete.")


if __name__ == "__main__":
    main()
