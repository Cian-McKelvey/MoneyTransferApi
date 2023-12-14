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

    "sender_email": "cian@gmail.com",

    "receiver_email": "viv@gmail.com",

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


def unique_email_check(email: str):
    client = MongoClient(CLIENT_CONNECTION, server_api=ServerApi('1'))
    db = client[DATABASE_CONNECTION]
    collection = db[USERS_COLLECTION]

    # Check if the email already exists
    existing_user = collection.find_one({"email": email})

    if existing_user:
        print("Email already exists. Cannot add new user.")
        client.close()
        return False
    else:
        return True


# Code to add a new user, added additional logic whereby users emails must be unique
def add_user(new_user: dict) -> bool:

    client = MongoClient(CLIENT_CONNECTION, server_api=ServerApi('1'))
    db = client[DATABASE_CONNECTION]
    collection = db[USERS_COLLECTION]

    try:
        collection.insert_one(new_user)
        client.close()
        return True
    except PyMongoError as e:
        print(f"Cannot add new user: {e}")
        client.close()
        return False


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


# NEEDS EDITED TO WORK WITH HASHED PASSWORDS
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


# NEEDS EDITED TO WORK WITH HASHED PASSWORDS
def update_users_password(user_email: str, old_password, new_password):
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


def get_user_balance(email: str) -> int:
    client = MongoClient(CLIENT_CONNECTION, server_api=ServerApi('1'))
    db = client[DATABASE_CONNECTION]
    collection = db[USERS_COLLECTION]

    document = collection.find_one({'email': email}, {'balance': 1, '_id': 0})

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


def add_balance(email: str, amount: int) -> bool:
    client = MongoClient(CLIENT_CONNECTION, server_api=ServerApi('1'))
    db = client[DATABASE_CONNECTION]
    collection = db[USERS_COLLECTION]

    valid_user = collection.find_one({'email': email})

    if valid_user:

        account_balance = get_user_balance(email)
        collection.update_one(
                {"email": email},
                {"$set": {"balance": account_balance + amount}}
        )
        return True
    else:
        return False


def update_user_balance(sending_email: str, receiving_email: str, transfer_amount: int) -> bool:

    if sending_email == receiving_email:
        return False

    client = MongoClient(CLIENT_CONNECTION, server_api=ServerApi('1'))
    db = client[DATABASE_CONNECTION]
    collection = db[USERS_COLLECTION]

    sender_account_balance = get_user_balance(sending_email)
    receiver_account_balance = get_user_balance(receiving_email)

    try:

        if sender_account_balance > transfer_amount and receiver_account_balance != -1:

            collection.update_one(
                {"email": sending_email},
                {"$set": {"balance": sender_account_balance - transfer_amount}}
            )

            collection.update_one(
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


def add_transfer(new_transfer: dict) -> None:
    client = MongoClient(CLIENT_CONNECTION, server_api=ServerApi('1'))
    db = client[DATABASE_CONNECTION]
    collection = db[TRANSFERS_COLLECTION]

    try:
        collection.insert_one(new_transfer)
    except PyMongoError as e:
        print(f"Cannot add new transfer: {e}")

    client.close()


def receive_transfer_by_email(email: str):
    client = MongoClient(CLIENT_CONNECTION, server_api=ServerApi('1'))
    db = client[DATABASE_CONNECTION]
    collection = db[TRANSFERS_COLLECTION]

    combined_query = {
        "$or": [
            {"sender_email": email},
            {"receiver_email": email}
        ]
    }

    result = list(collection.find(combined_query, {"_id": 0}))
    result.reverse()

    return result


def retrieve_all_transfers():
    client = MongoClient(CLIENT_CONNECTION, server_api=ServerApi('1'))
    db = client[DATABASE_CONNECTION]
    collection = db[TRANSFERS_COLLECTION]

    # Retrieve all items in the collection and convert to a list
    all_documents = list(collection.find({}, {'_id': 0}))
    # Return the list of documents
    return all_documents
