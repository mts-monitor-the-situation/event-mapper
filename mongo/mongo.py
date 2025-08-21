from pymongo import MongoClient


def get_collection(mongodb_connection_string: str):
    """
    Get the MongoDB collection for feed items.
    """
    client = MongoClient(mongodb_connection_string)
    db = client["mts"]
    return db["feed_items"]


def find_item_by_id(collection, item_id):
    """
    Find an item in the MongoDB collection by its ID.
    :param item_id: The ID of the item to find.
    :return: The item if found, None otherwise.
    """
    return collection.find_one({"_id": item_id}, {"_id": 1, "title": 1, "description": 1})


def update_item_by_id(collection, item_id, update_fields):
    """
    Update an item in the MongoDB collection.
    :param item_id: The ID of the item to update.
    :param update_fields: A dictionary of fields to update.
    :return: The result of the update operation.
    """
    return collection.update_one({"_id": item_id}, {"$set": update_fields})
