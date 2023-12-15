from flask import Flask, request, make_response, jsonify, render_template
from flask_cors import CORS
from pymongo import MongoClient
from pymongo.server_api import ServerApi

from database_methods import add_user, delete_user, update_users_password, receive_transfer_by_email, get_user_balance, \
    add_balance
from database_methods import update_user_balance, add_transfer, unique_email_check
from insights import incoming_vs_outgoing, highest_average_balance_town, highest_transaction_town, \
    highest_user_count
from constants import (SECRET_KEY, CLIENT_CONNECTION, DATABASE_CONNECTION,
                       USERS_COLLECTION, BLACKLIST_COLLECTION, TRANSFERS_COLLECTION)

import datetime
import uuid
import jwt
from functools import wraps
import bcrypt


app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY

# This config might help at a later point, if the code does not work for any reason come back and check
cors_config = {
    "origins": ["http://localhost:4200"],  # Adjust the port as needed
    "methods": ["GET", "POST", "PUT", "DELETE"],
    "allow_headers": ["Content-Type", "Authorization"],
    "supports_credentials": True,
}
# CORS(app, **cors_config)
CORS(app)

client = MongoClient(CLIENT_CONNECTION, server_api=ServerApi('1'))
db = client[DATABASE_CONNECTION]
users_collection = db[USERS_COLLECTION]
transfers_collection = db[TRANSFERS_COLLECTION]
blacklist_collection = db[BLACKLIST_COLLECTION]


# Decorator function used to protect from unregistered calls by requiring a valid token
def jwt_required(func):
    @wraps(func)
    def jwt_required_wrapper(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return jsonify({'message': 'Token is missing'}, 401)

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        except Exception as e:
            return jsonify({'message': f'Error decoding token: {str(e)}'}, 401)

        blacklist_token = blacklist_collection.find_one({"token": token})
        if blacklist_token is not None:
            return make_response({"message": "Token is blacklisted, can no longer be used"}, 401)

        return func(*args, **kwargs)

    return jwt_required_wrapper


# Home route of app
@app.route('/')
def hello_world():
    # Can add a html template here that can show routes or something else
    return "<h1>Hello World!<h1>"


"""
    Endpoints here are used to manage user accounts
"""


@app.route('/api/v1.0/login', methods=['POST'])
def login():
    auth = request.authorization

    if auth:
        user = users_collection.find_one({'email': auth.username})
        # Checks for a valid user, if so continue
        if user is not None:

            # Checks for a valid password, and if so returns token
            if bcrypt.checkpw(auth.password.encode('utf-8'), user['password']):
                # Token is created that contains the username and expiry time
                token = jwt.encode({
                    'user': auth.username,
                    'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
                }, app.config['SECRET_KEY'])
                return make_response(jsonify({'token': token, "user_id": user['user_id']}), 200)
            # Otherwise returns an error
            else:
                return make_response(jsonify({'message': 'Bad password'}), 401)

        else:
            return make_response(jsonify({'message': 'Bad username'}), 401)

    # this isn't working, it will only return bad username if nothing is sent
    return make_response(jsonify({'message': 'Authentication credentials were not provided'}), 401)


@app.route("/api/v1.0/logout", methods=["POST"])
@jwt_required
def logout():
    token = request.headers['x-access-token']
    blacklist_collection.insert_one({"token": token})
    return make_response(jsonify({"message": "logout successful"}), 200)


@app.route("/api/v1.0/user/new", methods=["POST"])
def add_new_login():
    is_unique = unique_email_check(users_collection, request.form["email"])
    if not is_unique:
        return make_response(jsonify({"error": "Email already registered"}), 400)

    try:
        next_id = str(uuid.uuid1())
        hashed_password = bcrypt.hashpw(request.form["password"].encode('utf-8'), bcrypt.gensalt())
        next_user = {
            "user_id": next_id,
            "email": request.form["email"],
            "password": hashed_password,
            "location": request.form["location"],
            "balance": 0,
            "registration_date": datetime.datetime.now()
        }

        # Insert the new_login data into the database
        add_user(users_collection, next_user)

        # Remove the _id and password fields before returning the JSON response
        next_user.pop("_id", None)
        next_user.pop("password", None)

        return make_response(jsonify(next_user), 201)
    except KeyError as e:
        return make_response(jsonify({"error": f"Invalid Details Provided: {str(e)}"}), 400)


@app.route("/api/v1.0/user/delete/<string:id>", methods=["DELETE"])
def delete_user_account(id):
    delete_result = delete_user(users_collection, id)

    if delete_result:
        return make_response(jsonify({}), 204)
    else:
        return make_response(jsonify({"message": "User account not found or password incorrect."}), 404)


"""
    if auth:
        user = users_collection.find_one({'email': auth.username})
        # Checks for a valid user, if so continue
        if user is not None:

            # Checks for a valid password, and if so returns token
            if bcrypt.checkpw(bytes(auth.password, 'UTF-8'), user['password']):
"""


# @app.route("/api/v1.0/user/update-password", methods=["PUT"])
# def update_user_account_password():
#     user = users_collection.find_one({'email': request.form["email"]})
#     # Checks for a valid user, if so continue
#     if user is not None:
#         hashed_password = bcrypt.hashpw(request.form["password"].encode('utf-8'), bcrypt.gensalt())
#         update_result = update_users_password(user_collection=users_collection,
#                                               user_email=request.form["email"],
#                                               new_password=hashed_password)
#
#         if update_result:
#             return make_response(jsonify({"message": "User password updated."}), 201)
#         else:
#             return make_response(jsonify({"message": "Could not update user password."}), 400)
#     else:
#         return make_response(jsonify({"message": "Invalid email"}), 404)


@app.route("/api/v1.0/user/balance", methods=["POST"])
def get_balance():
    account_email = request.json["email"]
    balance = get_user_balance(users_collection, account_email)
    if balance is not None:
        return make_response(jsonify({"balance": balance}), 200)
    else:
        return make_response(jsonify({"message": "Could not fetch user balance"}), 400)


@app.route("/api/v1.0/user/balance/add", methods=["PUT"])
def add_user_balance():
    email = request.form["email"]
    amount = int(request.form["addAmount"])

    success = add_balance(users_collection, email=email, amount=amount)
    if success:
        return make_response(jsonify({"message": "User funds added."}), 201)
    else:
        return make_response(jsonify({"message": "Could not add funds"}), 401)


"""
    Below here are the endpoints for transfers
"""


@app.route("/api/v1.0/transfers/new", methods=["POST"])
def new_transfer():

    success = update_user_balance(
        user_collection=users_collection,
        sending_email=request.form["sending_email"],
        receiving_email=request.form["receiving_email"],
        transfer_amount=int(request.form["transfer_amount"])
    )

    if success:
        next_id = str(uuid.uuid1())
        transfer_data = {
            "id": next_id,
            "sender_email": request.form["sending_email"],
            "receiver_email": request.form["receiving_email"],
            "amount_sent": int(request.form["transfer_amount"]),
            "transaction_date": datetime.datetime.now()
        }

        add_transfer(transfers_collection, transfer_data)
        transfer_data.pop("_id", None)
        return make_response(jsonify(transfer_data), 201)

    else:
        return make_response(jsonify({"error": f"Invalid Details Provided"}), 400)


@app.route("/api/v1.0/transfers", methods=["POST"])
def transfers_by_email():
    try:
        data = receive_transfer_by_email(transfers_collection, request.json["email"])
        if data is not None:
            return make_response(jsonify(data), 200)
        else:
            return make_response(jsonify({'message': 'data could not be fetched successfully'}), 400)
    except KeyError:
        return make_response(jsonify({'message': 'email key not found in the request'}), 400)


@app.route("/api/v1.0/insights", methods=["POST"])
@jwt_required
def get_insights():
    try:
        transfer_net = incoming_vs_outgoing(request.json["email"])
        most_users = highest_user_count()
        highest_average_balance = highest_average_balance_town()
        most_transactions = highest_transaction_town()

        insight_dict = {
            "net_total": transfer_net,
            "most_users": most_users,
            "highest_average_balance": highest_average_balance,
            "most_transactions": most_transactions
        }

        return make_response(jsonify(insight_dict), 201)

    except KeyError as e:
        return make_response(jsonify({'message': 'Invalid request data. Please provide an "email" field.'}), 400)

    except Exception as e:
        return make_response(jsonify({'message': 'An unexpected error occurred.'}), 500)


if __name__ == '__main__':
    app.run(port=8000, debug=True)
