from pymongo.server_api import ServerApi

from constants import CLIENT_CONNECTION, USERS_COLLECTION, DATABASE_CONNECTION, TRANSFERS_COLLECTION
from pymongo.mongo_client import MongoClient
from datetime import datetime, timedelta
from collections import Counter

"""
    Collection of methods used to retrieve insights from the database
    Will probably be very compute intensive but it'll be grand, just try to think of optimisations
    
    INSIGHTS: 
    1. Find the most common town amongst users
    2. Find the town with the highest average balance
    3. Town with the most transactions amongst users
    4. Find the net sent/received transfer amount
    
"""


def incoming_vs_outgoing(email: str) -> int:
    client = MongoClient(CLIENT_CONNECTION, server_api=ServerApi('1'))
    db = client[DATABASE_CONNECTION]
    transfer_collection = db[TRANSFERS_COLLECTION]

    incoming_amount = 0
    for doc in transfer_collection.find({"receiver_email": email}, {"_id": 0, "amount_sent": 1}):
        incoming_amount += doc['amount_sent']

    outgoing_amount = 0
    for doc in transfer_collection.find({"sender_email": email}, {"_id": 0, "amount_sent": 1}):
        outgoing_amount += doc['amount_sent']

    total_amount = incoming_amount - outgoing_amount

    return total_amount


# Fetches the town with the most users
def most_common_town() -> str:
    client = MongoClient(CLIENT_CONNECTION, server_api=ServerApi('1'))
    db = client[DATABASE_CONNECTION]
    collection = db[USERS_COLLECTION]

    cursor = collection.find({}, {"_id": 0, "location": 1})
    # Extract locations from each document and add them to a list
    location_list = [document["location"] for document in cursor]

    common_town = most_common_element(location_list)
    client.close()
    return common_town


# Fetches the town with the highest average balance
def highest_average_balance_town() -> str:
    client = MongoClient(CLIENT_CONNECTION, server_api=ServerApi('1'))
    db = client[DATABASE_CONNECTION]
    collection = db[USERS_COLLECTION]

    cursor = collection.find({}, {"_id": 0, "location": 1, "balance": 1})

    # Create a dictionary to store location and a list of balances
    balance_location_dict = {}

    for item in cursor:
        location = item.get("location")
        balance = item.get("balance")

        if location and balance is not None:
            if location not in balance_location_dict:
                balance_location_dict[location] = {"total_balance": 0, "user_count": 0}

            balance_location_dict[location]["total_balance"] += balance
            balance_location_dict[location]["user_count"] += 1

    average_balances = {location: data["total_balance"] / data["user_count"] for location, data
                        in balance_location_dict.items()}

    client.close()
    return max(average_balances, key=average_balances.get)


"""
    Tasks: 
    1. Find all the transactions and add each sender to a list
    2. Find the town each sender is from
    3. Find the town that is mentioned most often
    4. Kind optional, but find the total amount transferred by that town
"""


# This will return a dict with two items, The number of transfers create, and the total amount of transfers
def highest_transaction_town():
    client = MongoClient(CLIENT_CONNECTION, server_api=ServerApi('1'))
    db = client[DATABASE_CONNECTION]
    transfer_collection = db[TRANSFERS_COLLECTION]
    user_collection = db[USERS_COLLECTION]

    # Creates a list of all the emails that sent transfers
    cursor = transfer_collection.find({}, {"_id": 0, "sender_email": 1})
    sender_list = list([document["sender_email"] for document in cursor])


# Methods below here are helper methods


def most_common_element(lst):
    counter = Counter(lst)
    most_common_tuples = counter.most_common()
    common_element, _ = most_common_tuples[0]
    return common_element

