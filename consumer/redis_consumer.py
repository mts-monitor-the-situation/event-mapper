import redis
import redis.commands
from mongo import update_item_by_id
from nlp import process_text

r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)


def create_consumer_group():
    try:
        r.xgroup_create("rss:unprocessed", "consumers", id="0", mkstream=True)
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
            messages = r.xreadgroup(groupname="consumers", consumername="consumer1", streams={"rss:unprocessed": ">"}, count=10, block=5000)  # 5 seconds

            if not messages:
                print("No new messages, waiting...")
                continue

            for _, message_data in messages:
                for message_id, data in message_data:
                    # print(f"[Raw fields] {data}")
                    # print(f"[Stream] {stream} | [ID] {message_id}")

                    # Find item by ID in MongoDB
                    item_id = data.get("id")
                    item_description = data.get("description")
                    item_title = data.get("title")

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
                    # Requires Redis version >= 8.2.0
                    # The library doesn't support XACKDEL yet, so we use execute_command directly
                    args = ["XACKDEL", "rss:unprocessed", "consumers", "ACKED", "IDS", 1, message_id]
                    r.execute_command(*args)

        except Exception as e:
            print(f"Error in consumer loop: {e}")
