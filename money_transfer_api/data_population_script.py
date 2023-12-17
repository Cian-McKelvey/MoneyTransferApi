from random import randint, choice
from faker import Faker
import uuid
import datetime
from datetime import datetime, timedelta

from pymongo.collection import Collection

from constants import CLIENT_CONNECTION, USERS_COLLECTION, DATABASE_CONNECTION, TRANSFERS_COLLECTION
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import bcrypt
import pprint


"""
    The variety of methods in this class have been used sporatically to add more data to the database.
    The example run that is commented out at the bottom was the most recent part ran.
"""

# List of the cities that are available for choice on the frontend, random one can be chosen when generating a user
cities_ireland = [
    "Dublin", "Cork", "Galway", "Limerick", "Waterford",
    "Derry", "Belfast", "Newry", "Lisburn", "Armagh",
    "Derry", "Enniskillen", "Coleraine", "Kilkenny", "Tralee",
    "Sligo", "Wexford", "Athlone", "Drogheda", "Kilkenny",
]

fake = Faker()   # Faker package is used to generate fake emails and passwords


# Creates a random datetime, in the last year
def random_datetime_last_year() -> datetime:
    # Get the current datetime
    now = datetime.now()

    # Calculate the datetime from exactly one year ago
    last_year = now - timedelta(days=365)

    # Generate a random number of days between 0 and the number of days in the last year
    random_days = randint(0, (now - last_year).days)

    # Add the random number of days to the datetime from last year
    random_date = last_year + timedelta(days=random_days)

    # Generate random hours, minutes, and seconds
    random_time = timedelta(
        hours=randint(0, 23),
        minutes=randint(0, 59),
        seconds=randint(0, 59)
    )

    # Add the random time to the randomly chosen date
    random_datetime = random_date + random_time

    # Return the resulting random datetime
    return random_datetime


# Deletes all transfers. Not needed anymore really, but nice to have
def delete_all_transfers(collection: Collection) -> None:
    collection.delete_many({})


# Creates a fake user and adds them to the database
def create_fake_user(collection: Collection) -> None:
    next_id = str(uuid.uuid1())
    user_email = fake.email()  # Generates a fake email using faker
    # Generates a fake password using faker, and hashes it
    user_password = bcrypt.hashpw(fake.password().encode('utf-8'), bcrypt.gensalt())
    user_location = choice(cities_ireland)  # Generates a random choice from the cities library
    user_balance = randint(1, 1000)  # Generates a random balance between 1 - 1000
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
    collection.insert_one(fake_user)


# Fetches every users email, can be used when generating fake transfers etc...
def fetch_emails(collection: Collection):
    print("Connection established, fetching all emails...")
    cursor = collection.find({}, {"_id": 0, "email": 1})
    # Extract emails from each document and add them to a list
    email_list = [document["email"] for document in cursor]
    return email_list


"""
    Generating fake transfers
"""


# Can be used to have many outgoing emails from the main accounts used for demonstration
# Has been used to generate a vast transfer history for my video demonstration account
def outgoing_main_fake_transfer(collection: Collection, fake_email_list: list, real_email_list: list) -> None:
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
    collection.insert_one(fake_transfer)


# Can be used to have many incoming emails to the main accounts used for demonstration
# Has been used to generate a vast transfer history for my video demonstration account
def incoming_main_fake_transfer(collection: Collection, fake_email_list: list, real_email_list: list) -> None:
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
    collection.insert_one(fake_transfer)


# Generates random transfers between random users
def random_fake_transfer(collection: Collection, fake_email_list: list):
    fake_transfer_id = str(uuid.uuid1())
    fake_sender_email = choice(fake_email_list)
    fake_receiver_email = choice(fake_email_list)
    fake_transfer_amount = randint(1, 100)
    fake_sender_datetime = random_datetime_last_year()
    if fake_sender_email is not fake_receiver_email:
        fake_transfer = {
            "transfer_id": fake_transfer_id,
            "sender_email": fake_sender_email,
            "receiver_email": fake_receiver_email,
            "amount_sent": fake_transfer_amount,
            "transaction_date": fake_sender_datetime
        }
        pprint.pprint(fake_transfer)
        collection.insert_one(fake_transfer)


# if __name__ == '__main__':
#     client = MongoClient(CLIENT_CONNECTION, server_api=ServerApi('1'))
#     db = client[DATABASE_CONNECTION]
#     users_collection = db[USERS_COLLECTION]
#     transfer_collection = db[TRANSFERS_COLLECTION]
#     emails = fetch_emails(collection=users_collection)
#     for _ in range(50):
#         random_fake_transfer(collection=transfer_collection, fake_email_list=emails)

