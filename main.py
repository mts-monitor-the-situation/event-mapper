# from consumer.redis_consumer import start_consumer


# def main():
#     print("[Service] Starting GeoInference Redis Stream Consumer...")
#     start_consumer()


# if __name__ == "__main__":
#     main()
import threading
from concurrent.futures import ThreadPoolExecutor
from consumer.redis_consumer import start_consumer, retry_stalled_messages


def main():
    print("[Service] Starting GeoInference Redis Stream Consumer...")
    stop_event = threading.Event()

    with ThreadPoolExecutor(max_workers=2) as executor:
        future_consumer = executor.submit(start_consumer, stop_event)
        future_retry = executor.submit(retry_stalled_messages, stop_event)

        try:
            # Wait for both threads — raise if either crashes
            future_consumer.result()
            future_retry.result()

        except KeyboardInterrupt:
            print("Interrupted. Exiting...")
            stop_event.set()  # Signal both loops to stop
            # Optionally: wait for threads to finish their cleanup
            executor.shutdown(wait=True)
            raise SystemExit(0)
        except Exception as e:
            print(f"[FATAL] A thread crashed: {e}")
            stop_event.set()
            executor.shutdown(wait=True)
            raise SystemExit(1)


if __name__ == "__main__":
    main()
