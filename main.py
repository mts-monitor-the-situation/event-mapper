import threading
import signal
from concurrent.futures import ThreadPoolExecutor
import traceback
from consumer.redis_consumer import start_consumer, retry_stalled_messages


def main():
    print("[Service] Starting GeoInference Redis Stream Consumer...")
    stop_event = threading.Event()

    # Handle shutdown signals
    def handle_shutdown(signum, frame):
        print(f"\n[Shutdown] Received signal {signum}. Stopping workers gracefully...")
        print("Stack at interruption:")
        traceback.print_stack(frame)
        stop_event.set()

    # Register for SIGTERM (docker/k8s) and SIGINT (Ctrl+C)
    signal.signal(signal.SIGTERM, handle_shutdown)
    signal.signal(signal.SIGINT, handle_shutdown)

    with ThreadPoolExecutor(max_workers=2) as executor:
        future_consumer = executor.submit(start_consumer, stop_event)
        future_retry = executor.submit(retry_stalled_messages, stop_event)

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
