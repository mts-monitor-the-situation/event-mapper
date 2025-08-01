from nlp.location import process_text


def handle_message(data: dict):
    try:
        # Decode bytes → string if needed
        text = data.get(b"data") or data.get("data")
        if isinstance(text, bytes):
            text = text.decode()

        print(f"[Message] {text}")
        process_text(text)

    except Exception as e:
        print(f"Error handling message: {e}")
