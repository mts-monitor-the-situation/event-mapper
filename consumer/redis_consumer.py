import redis
from mongo import update_item_by_id
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
            messages = r.xreadgroup(groupname="consumer1", consumername="consumer1", streams={"rss:unprocessed": ">"}, count=10, block=5000)  # 5 seconds

            if not messages:
                print("No new messages, waiting...")
                continue

            for _, message_data in messages:
                for message_id, data in message_data:
                    # print(f"[Raw fields] {data}")
                    # print(f"[Stream] {stream} | [ID] {message_id}")

                    # Find item by ID in MongoDB
                    item_id = data.get(b"id").decode()
                    item_description = data.get(b"description", b"").decode()
                    item_title = data.get(b"title", b"").decode()

                    # Merge title and description for NLP processing
                    text = f"{item_title} {item_description}".strip()

                    # Process the text to extract locations
                    res = process_text(text)

                    #  Update the item in MongoDB with the processed locations
                    if res:
                        update_fields = {"locations": res}
                        update_result = update_item_by_id(item_id, update_fields)
                        if update_result.modified_count > 0:
                            print(f"Updated item {item_id} with locations: {res}")
                        else:
                            print(f"No changes made to item {item_id}.")

                    r.xack("rss:unprocessed", "consumer1", message_id)

        except Exception as e:
            print(f"Error in consumer loop: {e}")
