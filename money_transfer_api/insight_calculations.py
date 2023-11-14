from constants import CLIENT_CONNECTION, USERS_COLLECTION, DATABASE_CONNECTION, TRANSFERS_COLLECTION
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo.errors import PyMongoError

"""
Methods to find insights about other users
1. get_most_common_location - Finds the most common location of the other users
"""


def get_most_common_location() -> str:
    return ""



"""
Methods to find insights about your current account
1. incoming_transfer_history - Find all incoming transfers in the last 30 days
2. outgoing_transfer_history - Find all outgoing transfers in the last 30 days
3. net_transactions_history - Find total outgoing and incoming totals in the last 30 days  
"""


def incoming_transfer_history(email: str):
    client = MongoClient(CLIENT_CONNECTION, server_api=ServerApi('1'))
    db = client[DATABASE_CONNECTION]
    collection = db[TRANSFERS_COLLECTION]

    try:
        data = collection.find({'receiving_email': email})
        client.close()
        return data
    except PyMongoError as e:
        print(f"Error with fetching incoming transfers {e}")
        client.close()
        return


def outgoing_transfer_history(email: str):
    client = MongoClient(CLIENT_CONNECTION, server_api=ServerApi('1'))
    db = client[DATABASE_CONNECTION]
    collection = db[TRANSFERS_COLLECTION]

    try:
        data = collection.find({'sending_email': email})
        client.close()
        return data
    except PyMongoError as e:
        print(f"Error with fetching outgoing transfers {e}")
        client.close()
        return


def net_transactions_history(email: str) -> dict:
    return_dict = {}
    outgoing_total = 0
    incoming_total = 0

    incoming_data = incoming_transfer_history(email)
    outgoing_data = outgoing_transfer_history(email)

    # Extract transfer_amount from incoming_data
    for entry in incoming_data:
        incoming_total += entry['transfer_amount']

    # Extract transfer_amount from outgoing_data
    for entry in outgoing_data:
        outgoing_total += entry['transfer_amount']

    return_dict["incoming_total"] = incoming_total
    return_dict["outgoing_total"] = outgoing_total
    return_dict["net_total"] = incoming_total - outgoing_total

    return return_dict

