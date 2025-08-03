# from consumer.redis_consumer import start_consumer


# def main():
#     print("[Service] Starting GeoInference Redis Stream Consumer...")
#     start_consumer()


# if __name__ == "__main__":
#     main()
from concurrent.futures import ThreadPoolExecutor
from consumer.redis_consumer import start_consumer, retry_stalled_messages


def main():
    print("[Service] Starting GeoInference Redis Stream Consumer...")

    with ThreadPoolExecutor(max_workers=2) as executor:
        future_consumer = executor.submit(start_consumer)
        future_retry = executor.submit(retry_stalled_messages)

        try:
            # Wait for both threads — raise if either crashes
            future_consumer.result()
            future_retry.result()

        except KeyboardInterrupt:
            print("Interrupted. Exiting...")
            raise SystemExit(0)
        except Exception as e:
            print(f"[FATAL] A thread crashed: {e}")
            raise SystemExit(1)


if __name__ == "__main__":
    main()
