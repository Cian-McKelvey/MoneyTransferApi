from random import randint, choice
from faker import Faker
import uuid
import datetime
from datetime import datetime, timedelta
from constants import CLIENT_CONNECTION, USERS_COLLECTION, DATABASE_CONNECTION, TRANSFERS_COLLECTION
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import bcrypt
import pprint


"""
STEPS:
1. Delete all transfers from the database (DONE)

2. Create 50 new users (The two main accounts are cian01@gmail.com and viv01@gmail.com)

Every user that is created, should have their email added to a list

3. Create a bunch of random transfers,  from the main two accounts to people in the list

4. Create a load of random transfers from the new emails between themselves (Make sure the same email doesnt send and retrieve a transfer) 

"""


cities_ireland = [
    "Dublin",
    "Cork",
    "Galway",
    "Limerick",
    "Waterford",
    "Derry",
    "Belfast",
    "Newry",
    "Lisburn",
    "Armagh",
    "Derry",
    "Enniskillen",
    "Coleraine",
    "Kilkenny",
    "Tralee",
    "Sligo",
    "Wexford",
    "Athlone",
    "Drogheda",
    "Kilkenny",
]


fake = Faker()


# Creates a random datetime, in the last year
def random_datetime_last_year() -> datetime:
    now = datetime.now()
    last_year = now - timedelta(days=365)

    random_days = randint(0, (now - last_year).days)
    random_date = last_year + timedelta(days=random_days)

    # Add random hours, minutes, and seconds
    random_time = timedelta(
        hours=randint(0, 23),
        minutes=randint(0, 59),
        seconds=randint(0, 59)
    )

    random_datetime = random_date + random_time
    return random_datetime


# Deletes all transfers. Not needed anymore really, but nice to have
def delete_all_transfers() -> None:
    client = MongoClient(CLIENT_CONNECTION, server_api=ServerApi('1'))
    db = client[DATABASE_CONNECTION]
    collection = db[TRANSFERS_COLLECTION]

    collection.delete_many({})


"""
    example_user = {
        "user_id": str(uuid),
        "email": "cian@gmail.com",
        "password": "ExamplePassword",
        "location": "Belfast",
        "balance": 0,
        "creation_datetime": datetime.datetime
    }
"""


def create_fake_user() -> None:
    next_id = str(uuid.uuid1())
    user_email = fake.email()
    user_password = bcrypt.hashpw(fake.password().encode('utf-8'), bcrypt.gensalt())
    user_location = choice(cities_ireland)
    user_balance = randint(1, 1000)
    user_creation_datetime = random_datetime_last_year()

    fake_user = {
        "user_id": next_id,
        "email": user_email,
        "password": user_password,
        "location": user_location,
        "balance": user_balance,
        "creation_datetime": user_creation_datetime
    }
    pprint.pprint(fake_user)
    post_fake_user(fake_user)


def post_fake_user(user_dict: dict) -> None:
    client = MongoClient(CLIENT_CONNECTION, server_api=ServerApi('1'))
    db = client[DATABASE_CONNECTION]
    collection = db[USERS_COLLECTION]

    collection.insert_one(user_dict)


def fetch_emails():
    client = MongoClient(CLIENT_CONNECTION, server_api=ServerApi('1'))
    db = client[DATABASE_CONNECTION]
    collection = db[USERS_COLLECTION]

    print("Connection established, fetching all emails...")

    cursor = collection.find({}, {"_id": 0, "email": 1})

    # Extract emails from each document and add them to a list
    email_list = [document["email"] for document in cursor]

    client.close()
    return email_list


"""
X
"""


def outgoing_main_fake_transfer(fake_email_list: list, real_email_list: list) -> None:
    fake_transfer_id = str(uuid.uuid1())
    main_sender_email = choice(real_email_list)
    fake_receiver_email = choice(fake_email_list)
    fake_transfer_amount = randint(1, 100)
    fake_sender_datetime = random_datetime_last_year()

    fake_transfer = {
        "transfer_id": fake_transfer_id,
        "sender_email": main_sender_email,
        "receiver_email": fake_receiver_email,
        "amount_sent": fake_transfer_amount,
        "transaction_date": fake_sender_datetime
    }

    pprint.pprint(fake_transfer)
    post_fake_transfer(fake_transfer)


def incoming_main_fake_transfer(fake_email_list: list, real_email_list: list) -> None:
    fake_transfer_id = str(uuid.uuid1())
    fake_sender_email = choice(fake_email_list)
    real_receiver_email = choice(real_email_list)
    fake_transfer_amount = randint(1, 100)
    fake_sender_datetime = random_datetime_last_year()

    fake_transfer = {
        "transfer_id": fake_transfer_id,
        "sender_email": fake_sender_email,
        "receiver_email": real_receiver_email,
        "amount_sent": fake_transfer_amount,
        "transaction_date": fake_sender_datetime
    }

    pprint.pprint(fake_transfer)
    post_fake_transfer(fake_transfer)


def post_fake_transfer(fake_transfer: dict) -> None:
    client = MongoClient(CLIENT_CONNECTION, server_api=ServerApi('1'))
    db = client[DATABASE_CONNECTION]
    collection = db[TRANSFERS_COLLECTION]

    collection.insert_one(fake_transfer)


if __name__ == '__main__':
    fake_emails = fetch_emails()
    main_accounts = ["cian01@gmail.com", "viv01@gmail.com"]
    for _ in range(50):
        outgoing_main_fake_transfer(fake_email_list=fake_emails, real_email_list=main_accounts)
        print("\n")

