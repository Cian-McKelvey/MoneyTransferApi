import uuid
import datetime

from constants import CLIENT_CONNECTION, USERS_COLLECTION, DATABASE_CONNECTION, TRANSFERS_COLLECTION
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo.errors import PyMongoError


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

    "sender_id": "xxxx10xsshf381",

    "receiver_id": "43hhg3rbfh53",

    "amount_sent": 500,

    "transaction_date": datetime.datetime.now()

}


"""
    Methods related to database operations
"""


# User Database Methods
def user_exists(email, password):
    client = MongoClient(CLIENT_CONNECTION, server_api=ServerApi('1'))
    db = client[DATABASE_CONNECTION]
    collection = db[USERS_COLLECTION]

    user = collection.find_one({"email": email, "password": password})
    return user


def add_user(new_user: dict):

    client = MongoClient(CLIENT_CONNECTION, server_api=ServerApi('1'))
    db = client[DATABASE_CONNECTION]
    collection = db[USERS_COLLECTION]

    try:
        collection.insert_one(new_user)
    except PyMongoError as e:
        print(f"Cannot add new user: {e}")

    client.close()


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


def delete_user(user_email: str, user_password: str) -> bool:
    client = MongoClient(CLIENT_CONNECTION, server_api=ServerApi('1'))
    db = client[DATABASE_CONNECTION]
    collection = db[USERS_COLLECTION]

    try:
        result = collection.delete_one({"email": user_email, "password": user_password})
        print(f"Deleted: {result}")

        # Check if a document was deleted (result.deleted_count > 0) to indicate success
        if result.deleted_count > 0:
            return True
        else:
            return False
    except PyMongoError as e:
        print(f"An error occurred: {e}")
        return False  # Return False in case of an error or if the document wasn't found

    finally:
        client.close()


def update_users_password(user_email: str, old_password: str, new_password: str):
    client = MongoClient(CLIENT_CONNECTION, server_api=ServerApi('1'))
    db = client[DATABASE_CONNECTION]
    collection = db[USERS_COLLECTION]

    try:
        result = collection.update_one(
            {"email": user_email, "password": old_password},
            {"$set": {"password": new_password}}
        )

        print("Password updated!")
        return result

    except PyMongoError as e:
        print(f"An error occurred: {e}")

    client.close()


"""
    Methods related to transferring money
"""


def get_user_balance(account_id) -> int:
    client = MongoClient(CLIENT_CONNECTION, server_api=ServerApi('1'))
    db = client[DATABASE_CONNECTION]
    collection = db[USERS_COLLECTION]

    document = collection.find_one({'user_id': account_id}, {'balance': 1, '_id': 0})

    if document:
        balance = document.get('balance')
        if balance is not None:
            # Convert the balance to an integer
            sender_account_balance = int(balance)
            return sender_account_balance
        else:
            print(f"No balance property found for user {account_id}")
            return -1
    else:
        print(f"No document found for user {account_id}")
        return -1


def update_user_balance(sending_id: str, receiving_id: str, transfer_amount: int) -> bool:
    client = MongoClient(CLIENT_CONNECTION, server_api=ServerApi('1'))
    db = client[DATABASE_CONNECTION]
    collection = db[USERS_COLLECTION]

    sender_account_balance = get_user_balance(sending_id)
    receiver_account_balance = get_user_balance(receiving_id)

    try:

        if sender_account_balance > transfer_amount and receiver_account_balance != -1:

            collection.update_one(
                {"user_id": sending_id},
                {"$set": {"balance": sender_account_balance - transfer_amount}}
            )

            collection.update_one(
                {"user_id": receiving_id},
                {"$set": {"balance": receiver_account_balance + transfer_amount}}
            )

            return True

        else:
            print("Insufficient funds to make the transfer")
            return False

    except PyMongoError as e:
        print(f"Exception occured, transfer was not sent: {e}")
        return False


def add_transfer(new_transfer: dict) -> None:
    client = MongoClient(CLIENT_CONNECTION, server_api=ServerApi('1'))
    db = client[DATABASE_CONNECTION]
    collection = db[TRANSFERS_COLLECTION]

    try:
        collection.insert_one(new_transfer)
    except PyMongoError as e:
        print(f"Cannot add new transfer: {e}")

    client.close()