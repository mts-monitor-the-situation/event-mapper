import redis
from mongo import find_item_by_id
from nlp import process_text

r = redis.Redis(host="localhost", port=6379, db=0)


def create_consumer_group():
    try:
        r.xgroup_create("rss:unprocessed", "consumer1", id="0", mkstream=True)
        print("Consumer group created.")
    except redis.exceptions.ResponseError as e:
        if "BUSYGROUP" in str(e):
            print("Consumer group already exists.")
        else:
            raise


def start_consumer():
    create_consumer_group()
    while True:
        try:
            messages = r.xreadgroup(groupname="consumer1", consumername="consumer1", streams={"rss:unprocessed": ">"}, count=10, block=1000)  # 1 second

            for stream, message_data in messages:
                for message_id, data in message_data:
                    # print(f"[Raw fields] {data}")
                    # print(f"[Stream] {stream} | [ID] {message_id}")

                    # Find item by ID in MongoDB
                    item_id = data.get(b"id").decode()

                    if item_id:
                        item = find_item_by_id(item_id)
                        if item:
                            # Combine the title and description for NLP processing
                            text = f"{item.get('title', '')} {item.get('description', '')}"
                            print(f"Processing item: {item_id} with text: {text}")
                            res = process_text(text)
                            print(f"Processed locations: {res}")
                        else:
                            print(f"Item with ID {item_id} not found in MongoDB.")

                    r.xack("rss:unprocessed", "consumer1", message_id)

        except Exception as e:
            print(f"Error in consumer loop: {e}")
