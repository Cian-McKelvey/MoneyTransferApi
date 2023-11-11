from random import randint, choice
from database_methods import add_user
from faker import Faker
import uuid
import datetime


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


def create_user():
    balance = randint(1, 1000)
    email = fake.email()
    password = fake.password()
    next_id = str(uuid.uuid1())
    location = choice(cities_ireland)

    next_user = {
        "user_id": next_id,
        "email": email,
        "password": password,
        "location": location,
        "balance": balance,
        "registration_date": datetime.datetime.now()
    }

    add_user(next_user)


def populate_database(loop_count: int):
    for _ in range(loop_count):
        create_user()


if __name__ == "__main__":
    populate_database(100)
