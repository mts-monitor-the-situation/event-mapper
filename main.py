from consumer.redis_consumer import start_consumer


def main():
    print("[Service] Starting GeoInference Redis Stream Consumer...")
    start_consumer()


if __name__ == "__main__":
    main()
