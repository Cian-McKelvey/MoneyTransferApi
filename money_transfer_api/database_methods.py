from pymongo.collection import Collection
from pymongo.errors import PyMongoError


"""
    Methods related to database operations
"""


""" 
    User Database Methods 
"""


# Returns true if the email hasn't been used already, false otherwise
def unique_email_check(user_collection: Collection, email: str):
    # Check if the email already exists
    existing_user = user_collection.find_one({"email": email})

    if existing_user:
        print("Email already exists")
        return False
    else:
        return True


# Add a new user, called from an endpoint whereby a complete User entry will be provided
def add_user(user_collection: Collection, new_user: dict) -> bool:
    try:
        user_collection.insert_one(new_user)
        return True
    except PyMongoError as e:
        print(f"Cannot add new user: {e}")
        return False


# Deletes a user by user_id
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


"""
    Methods related to transferring money, or updating a users balance
"""


# Gets a users balance
def get_user_balance(user_collection: Collection, email: str) -> int:

    # Attempts to find a documents balance by email
    document = user_collection.find_one({'email': email}, {'balance': 1, '_id': 0})

    # If there was a valid document
    if document:
        # Try to fetch account balance
        balance = document.get('balance')
        # If there was a valid balance fetched
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


# Used to add balance to a user account, returns true or false on success/failure
def add_balance(user_collection: Collection,
                email: str,
                amount: int) -> bool:
    # checks for a valid account
    valid_user = user_collection.find_one({'email': email})

    if valid_user:
        account_balance = get_user_balance(user_collection, email)  # Gets the current user balance
        # Updates the balance to be the current balance plus the added amount
        user_collection.update_one(
                {"email": email},
                {"$set": {"balance": account_balance + amount}})
        return True
    else:
        return False


# Method to updates an account balance
def update_user_balance(user_collection: Collection,
                        sending_email: str,
                        receiving_email: str,
                        transfer_amount: int) -> bool:

    # Checks so that you can't send to yourself
    if sending_email == receiving_email:
        return False

    # Gets the balance of both accounts
    sender_account_balance = get_user_balance(user_collection, sending_email)
    receiver_account_balance = get_user_balance(user_collection, receiving_email)

    try:
        # -1 is a default value, if nothing was found while fetching the balance of an account, -1 is returned
        if sender_account_balance > transfer_amount and receiver_account_balance != -1:
            # Deducts from senders balance
            user_collection.update_one(
                {"email": sending_email},
                {"$set": {"balance": sender_account_balance - transfer_amount}}
            )
            # Adds to receivers balance
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


# Adds a transfer dict to the database
def add_transfer(transfer_collection: Collection, new_transfer: dict) -> None:
    try:
        transfer_collection.insert_one(new_transfer)
    except PyMongoError as e:
        print(f"Cannot add new transfer: {e}")


# Fetches all transfers associated with an email
def receive_transfer_by_email(transfer_collection: Collection, email: str):
    # Combined query fetches if the email = sender_email OR receiver_email
    combined_query = {
        "$or": [
            {"sender_email": email},
            {"receiver_email": email}
        ]
    }

    result = list(transfer_collection.find(combined_query, {"_id": 0}))
    result.reverse()  # Reverses the order of the fetched items, so they're shown most recent first in UI

    return result
