from concurrent.futures import thread
import redis
from mongo import update_item_by_id
from nlp import process_text
import time
import threading

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


def start_consumer(stop_event=threading.Event):
    create_consumer_group()
    while not stop_event.is_set():
        while True:
            try:
                messages = r.xreadgroup(groupname="consumers", consumername="consumer1", streams={"rss:unprocessed": ">"}, count=10, block=5000)

                if not messages:
                    print("No new messages, waiting...")
                    continue

                for _, message_data in messages:
                    for message_id, data in message_data:
                        try:
                            item_id = data.get("id")
                            item_description = data.get("description")
                            item_title = data.get("title")
                            text = f"{item_title} {item_description}".strip()

                            res = process_text(text)

                            if res:
                                update_fields = {"locations": res}
                                update_result = update_item_by_id(item_id, update_fields)
                                if update_result.modified_count > 0:
                                    print(f"Updated item {item_id} with locations: {res}")
                                else:
                                    print(f"No changes made to item {item_id}.")

                            # ACK and delete only if processing succeeded
                            # Requires Redis version >= 8.2.0
                            # The library doesn't support XACKDEL yet, so we use execute_command directly
                            args = ["XACKDEL", "rss:unprocessed", "consumers", "ACKED", "IDS", 1, message_id]
                            r.execute_command(*args)

                        except Exception as item_error:
                            print(f"[ERROR] Failed to process message {message_id}: {item_error}")
                            # Optional: push to a DLQ stream for later inspection
                            # r.xadd("rss:failed", {"id": item_id, "reason": str(item_error)})

            except Exception as loop_error:
                print(f"[FATAL] Error in consumer loop: {loop_error}")


def retry_stalled_messages(
    stop_event=threading.Event,
    stream="rss:unprocessed",
    group="consumers",
    retry_consumer="consumer1",
    idle_threshold_ms=10 * 60 * 1000,  # 10 minutes
    batch_size=20,
    sleep_seconds=10,
):
    print("[Retry] Starting retry monitor...")
    while not stop_event.is_set():
        while True:
            try:
                cursor = "0-0"
                while True:
                    pending = r.xautoclaim(
                        name=stream,
                        groupname=group,
                        consumername=retry_consumer,
                        min_idle_time=idle_threshold_ms,
                        start_id=cursor,
                        count=batch_size,
                    )
                    cursor = pending[0]
                    messages = pending[1]

                    if not messages:
                        print("[Retry] No stalled messages found.")
                        break  # Nothing more to process in this pass

                    for message_id, data in messages:
                        try:
                            item_id = data.get("id")
                            item_description = data.get("description")
                            item_title = data.get("title")
                            text = f"{item_title} {item_description}".strip()

                            res = process_text(text)

                            if res:
                                update_fields = {"locations": res}
                                update_result = update_item_by_id(item_id, update_fields)
                                if update_result.modified_count > 0:
                                    print(f"[Retry] Updated item {item_id} with locations: {res}")
                                else:
                                    print(f"[Retry] No changes made to item {item_id}.")

                            # Atomically ACK and delete from the stream
                            args = ["XACKDEL", stream, group, "ACKED", "IDS", 1, message_id]
                            r.execute_command(*args)

                        except Exception as retry_error:
                            print(f"[Retry Error] Failed to process stalled message {message_id}: {retry_error}")

                    if cursor == "0-0":
                        break  # Done with PEL scan

            except Exception as e:
                print(f"[Retry Fatal] Retry monitor crashed: {e}")

            time.sleep(sleep_seconds)
