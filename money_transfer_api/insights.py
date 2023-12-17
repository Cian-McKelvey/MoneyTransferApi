from pymongo.server_api import ServerApi
from pymongo.collection import Collection

from constants import CLIENT_CONNECTION, USERS_COLLECTION, DATABASE_CONNECTION, TRANSFERS_COLLECTION
from pymongo.mongo_client import MongoClient
from collections import Counter

"""
    Collection of methods used to retrieve insights from the database
    
    INSIGHTS:
    1. Find the net sent/received transfer amount for the logged in user 
    2. Find the town with the most users
    3. Find the town with the highest average balance
    4. Town with the most transactions amongst users
    
"""


# 1. Returns the net incoming/transactions for the logged-in user
def incoming_vs_outgoing(transfer_collection: Collection, email: str) -> int:
    incoming_amount = 0
    for doc in transfer_collection.find({"receiver_email": email}, {"_id": 0, "amount_sent": 1}):
        incoming_amount += doc['amount_sent']

    outgoing_amount = 0
    for doc in transfer_collection.find({"sender_email": email}, {"_id": 0, "amount_sent": 1}):
        outgoing_amount += doc['amount_sent']

    total_amount = incoming_amount - outgoing_amount

    return total_amount


# 2. Returns the town with the most users
def highest_user_count(user_collection: Collection) -> str:

    cursor = user_collection.find({}, {"_id": 0, "location": 1})
    # Extract each location and add them to a list
    location_list = [document["location"] for document in cursor]
    # Finds the most common element in the list
    common_town = most_common_element(location_list)

    return common_town


# 3. Returns the town with the highest average balance
def highest_average_balance_town(user_collection: Collection) -> str:
    cursor = user_collection.find({}, {"_id": 0, "location": 1, "balance": 1})

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

    average_balances = {}
    for location, data in balance_location_dict.items():
        average_balances[location] = data["total_balance"] / data["user_count"]

    return max(average_balances, key=average_balances.get)


# 4. Returns the town with the highest number of transactions
def highest_transaction_town(user_collection: Collection, transfer_collection: Collection) -> str:

    transfer_list = []
    location_list = []

    # Fetches all the emails that sent transfers
    transfer_cursor = transfer_collection.find({}, {"_id": 0, "sender_email": 1})
    # Adds them to the list
    for item in transfer_cursor:
        transfer_list.append(item['sender_email'])

    # Goes through the fetched emails
    for email in transfer_list:
        # Finds their location
        user_document = user_collection.find_one({"email": email}, {"_id": 0, "location": 1})
        # Adds to location list
        if user_document:
            location_list.append(user_document['location'])

    # Returns which location occurred most often
    return most_common_element(location_list)


# Methods below here are helper methods


def most_common_element(lst):
    counter = Counter(lst)
    most_common_tuples = counter.most_common()
    common_element, _ = most_common_tuples[0]
    return common_element
