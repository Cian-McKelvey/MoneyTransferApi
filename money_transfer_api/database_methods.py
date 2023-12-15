import uuid
import datetime

from pymongo.database import Database
from pymongo.collection import Collection

from constants import CLIENT_CONNECTION, USERS_COLLECTION, DATABASE_CONNECTION, TRANSFERS_COLLECTION
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo.errors import PyMongoError


# Example dicts below are used while writing methods to remember what each collection contains
example_user = {

    "user_id": str(uuid),

    "email": "cian@gmail.com",

    "password": "ExamplePassword",

    "location": "Belfast",

    "balance": 0,

    "creation_datetime": datetime.datetime

}

example_transfer = {

    "transfer_id": str(uuid),

    "sender_email": "cian@gmail.com",

    "receiver_email": "viv@gmail.com",

    "amount_sent": 500,

    "transaction_date": datetime.datetime.now()

}


"""
    Methods related to database operations
"""


# User Database Methods
# Below method isn't used, can probably be deleted
def user_exists(db: Database, email: str, password: str):
    collection = db[USERS_COLLECTION]

    user = collection.find_one({"email": email, "password": password})
    return user


def unique_email_check(user_collection: Collection, email: str):
    # Check if the email already exists
    existing_user = user_collection.find_one({"email": email})

    if existing_user:
        print("Email already exists")
        return False
    else:
        return True


# Code to add a new user, added additional logic whereby users emails must be unique
def add_user(user_collection: Collection, new_user: dict) -> bool:
    try:
        user_collection.insert_one(new_user)
        return True
    except PyMongoError as e:
        print(f"Cannot add new user: {e}")
        return False


# Not used either, delete if verified safe
def read_user(user_account_id: str) -> dict:
    client = MongoClient(CLIENT_CONNECTION, server_api=ServerApi('1'))
    db = client[DATABASE_CONNECTION]
    collection = db[USERS_COLLECTION]

    try:
        result = collection.find_one({'user_id': user_account_id})
        return result
    except PyMongoError as e:
        print(f"An error occurred: {e}")

    client.close()


def delete_user(users_collection: Collection, user_id: str) -> bool:
    try:
        result = users_collection.delete_one({'user_id': user_id})
        print(f"Deleted: {result}")

        # Check if a document was deleted
        if result.deleted_count > 0:
            return True
        else:
            return False
    except PyMongoError as e:
        print(f"An error occurred: {e}")
        return False


# def update_users_password(user_collection: Collection, user_email: str, new_password: str):
#     try:
#         user_collection.update_one(
#             {"email": user_email},
#             {"$set": {"password": new_password}}
#         )
#         print("Password updated!")
#         return True
#
#     except PyMongoError as e:
#         print(f"An error occurred: {e}")
#         return False



"""
    Methods related to transferring money, or updating a users balance
"""


def get_user_balance(user_collection: Collection, email: str) -> int:

    document = user_collection.find_one({'email': email}, {'balance': 1, '_id': 0})

    if document:
        balance = document.get('balance')
        if balance is not None:
            # Convert the balance to an integer
            sender_account_balance = int(balance)
            return sender_account_balance
        else:
            print(f"No balance property found for user {email}")
            return -1
    else:
        print(f"No document found for user {email}")
        return -1


def add_balance(user_collection: Collection,
                email: str,
                amount: int) -> bool:

    valid_user = user_collection.find_one({'email': email})

    if valid_user:

        account_balance = get_user_balance(user_collection, email)
        user_collection.update_one(
                {"email": email},
                {"$set": {"balance": account_balance + amount}}
        )
        return True
    else:
        return False


def update_user_balance(user_collection: Collection,
                        sending_email: str,
                        receiving_email: str,
                        transfer_amount: int) -> bool:

    if sending_email == receiving_email:
        return False

    sender_account_balance = get_user_balance(user_collection, sending_email)
    receiver_account_balance = get_user_balance(user_collection, receiving_email)

    try:
        if sender_account_balance > transfer_amount and receiver_account_balance != -1:
            user_collection.update_one(
                {"email": sending_email},
                {"$set": {"balance": sender_account_balance - transfer_amount}}
            )
            user_collection.update_one(
                {"email": receiving_email},
                {"$set": {"balance": receiver_account_balance + transfer_amount}}
            )
            return True

        else:
            print("Insufficient funds to make the transfer")
            return False

    except PyMongoError as e:
        print(f"Exception occured, transfer was not sent: {e}")
        return False


def add_transfer(transfer_collection: Collection, new_transfer: dict) -> None:
    try:
        transfer_collection.insert_one(new_transfer)
    except PyMongoError as e:
        print(f"Cannot add new transfer: {e}")


def receive_transfer_by_email(transfer_collection: Collection, email: str):
    combined_query = {
        "$or": [
            {"sender_email": email},
            {"receiver_email": email}
        ]
    }

    result = list(transfer_collection.find(combined_query, {"_id": 0}))
    result.reverse()  # Reverses the order of the fetched items so they're shown most recent first in UI

    return result


# Also is unused so can be deleted if safe
def retrieve_all_transfers(transfer_collection: Collection) -> list:
    all_documents = list(transfer_collection.find({}, {'_id': 0}))
    return all_documents
