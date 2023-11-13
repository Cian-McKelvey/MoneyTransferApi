from flask import Flask, request, make_response, jsonify, render_template
from database_methods import add_user, user_exists, delete_user, update_users_password
from database_methods import update_user_balance, add_transfer, unique_email_check
import datetime
import uuid


app = Flask(__name__)


# Home route of app
@app.route('/')
def hello_world():
    return "<h1>Hello World!<h1>"


@app.route("/api/v1.0/user/new", methods=["POST"])
def add_new_login():

    is_unique = unique_email_check(request.form["email"])
    if not is_unique:
        return make_response(jsonify({"error": "Email already registered"}), 400)

    try:
        next_id = str(uuid.uuid1())
        next_user = {
            "user_id": next_id,
            "email": request.form["email"],
            "password": request.form["password"],
            "location": request.form["location"],
            "balance": 0,
            "registration_date": datetime.datetime.now()
        }

        # Insert the new_login data into the database
        add_user(next_user)

        # Remove the _id field before returning the JSON response
        next_user.pop("_id", None)

        return make_response(jsonify(next_user), 201)
    except KeyError as e:
        return make_response(jsonify({"error": f"Invalid Details Provided: {str(e)}"}), 400)


@app.route("/api/v1.0/user/check", methods=["POST"])
def check_login():
    checked_user = user_exists(email=request.form["email"], password=request.form['password'])

    if checked_user is not None:
        # Remove the _id field before returning the JSON response
        checked_user.pop("_id", None)
        return make_response(jsonify(checked_user), 201)
    else:
        return make_response(jsonify({"login": "failure - account not found"}), 404)


@app.route("/api/v1.0/user/delete", methods=["DELETE"])
def delete_user_account():
    delete_result = delete_user(user_email=request.form["email"], user_password=request.form['password'])

    if delete_result:
        return make_response(jsonify({"message": "User account deleted."}), 204)
    else:
        return make_response(jsonify({"message": "User account not found or password incorrect."}), 404)


@app.route("/api/v1.0/user/update-password", methods=["PUT"])
def update_user_account_password():
    update_result = update_users_password(user_email=request.form["email"],
                                          old_password=request.form['old_password'],
                                          new_password=request.form['new_password'])

    if update_result.matched_count > 0 and update_result.modified_count > 0:
        return make_response(jsonify({"message": "User password updated."}), 201)
    else:
        return make_response(jsonify({"message": "Could not update user password."}), 400)


@app.route("/api/v1.0/transfers/new", methods=["POST"])
def new_transfer():

    success = update_user_balance(
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

        add_transfer(transfer_data)
        transfer_data.pop("_id", None)
        return make_response(jsonify(transfer_data), 201)

    else:
        return make_response(jsonify({"error": f"Invalid Details Provided"}), 400)


if __name__ == '__main__':
    app.run(debug=True)
