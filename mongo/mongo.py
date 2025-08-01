from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["mts"]
collection = db["feed_items"]


def find_item_by_id(item_id):
    """
    Find an item in the MongoDB collection by its ID.
    :param item_id: The ID of the item to find.
    :return: The item if found, None otherwise.
    """
    return collection.find_one({"_id": item_id}, {"_id": 1, "title": 1, "description": 1})
