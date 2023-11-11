import bcrypt


def hash_password(password):
    # Hash a password for the first time
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed_password


def check_password(plain_password, hashed_password):
    # Check hashed password against the user-supplied password
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password)


# Example usage:
password_to_hash = "user_password"
new_hashed_password = hash_password(password_to_hash)

# Save `hashed_password` in the database

# Later, when checking a login attempt:
login_attempt = "user_password"
if check_password(login_attempt, new_hashed_password):
    print("Password is correct!")
else:
    print("Incorrect password.")
