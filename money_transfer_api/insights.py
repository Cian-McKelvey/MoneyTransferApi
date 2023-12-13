from pymongo.server_api import ServerApi

from constants import CLIENT_CONNECTION, USERS_COLLECTION, DATABASE_CONNECTION, TRANSFERS_COLLECTION
from pymongo.mongo_client import MongoClient
from datetime import datetime, timedelta
from collections import Counter

"""
    Collection of methods used to retrieve insights from the database
    
    INSIGHTS:
    1. Find the net sent/received transfer amount for the logged in user 
    2. Find the town with the most users
    3. Find the town with the highest average balance
    4. Town with the most transactions amongst users
    
"""


# 1. Retunrs the net incoming/transactions for the logged-in user
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


# 2. Returns the town with the most users
def highest_user_count() -> str:
    client = MongoClient(CLIENT_CONNECTION, server_api=ServerApi('1'))
    db = client[DATABASE_CONNECTION]
    collection = db[USERS_COLLECTION]

    cursor = collection.find({}, {"_id": 0, "location": 1})
    # Extract each location and add them to a list
    location_list = [document["location"] for document in cursor]

    common_town = most_common_element(location_list)
    client.close()
    return common_town


# 3. Returns the town with the highest average balance
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


# 4. Returns the town with the highest number of transactions
def highest_transaction_town() -> str:
    client = MongoClient(CLIENT_CONNECTION, server_api=ServerApi('1'))
    db = client[DATABASE_CONNECTION]
    transfer_collection = db[TRANSFERS_COLLECTION]
    user_collection = db[USERS_COLLECTION]

    transfer_list = []
    location_list = []

    # Creates a list of all the emails that sent transfers
    transfer_cursor = transfer_collection.find({}, {"_id": 0, "sender_email": 1})
    for item in transfer_cursor:
        transfer_list.append(item['sender_email'])

    for email in transfer_list:
        # Use find_one to get a single document
        user_document = user_collection.find_one({"email": email}, {"_id": 0, "location": 1})
        if user_document:
            location_list.append(user_document['location'])

    return most_common_element(location_list)


# Methods below here are helper methods


def most_common_element(lst):
    counter = Counter(lst)
    most_common_tuples = counter.most_common()
    common_element, _ = most_common_tuples[0]
    return common_element
