import redis
from .handler import handle_message

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
                    print(f"[Raw fields] {data}")
                    #             print(f"[Stream] {stream} | [ID] {message_id}")
                    handle_message(data)
                    r.xack("rss:unprocessed", "consumer1", message_id)

        except Exception as e:
            print(f"Error in consumer loop: {e}")
