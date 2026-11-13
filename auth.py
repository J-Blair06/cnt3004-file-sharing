# auth.py
import hashlib
import json
import secrets

USERS_FILE = "users.json"
ITERATIONS = 200000


def get_salt(username):
    users = load_users()
    if username not in users:
        return None
    return users[username]["salt"]

def check_hash(username, hashed_password):
    users = load_users()
    if username not in users:
        return False
    stored_hash = users[username]["hash"]
    return secrets.compare_digest(stored_hash.encode(), hashed_password.encode())

def load_users():
    try:
        with open(USERS_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_users(users):
    with open(USERS_FILE, "w") as file:
        json.dump(users, file, indent=2)

def add_user(username, password):
    if not password or any(c.isspace() for c in password):
        return False
    username = "_".join(username.split())
    if not username:
        return False
    salt = secrets.token_hex(16)
    users = load_users()
    if username in users:
        return False
    users[username] = {
        "salt": salt,
        "hash": hashlib.pbkdf2_hmac(
            "sha256", password.encode(), bytes.fromhex(salt), ITERATIONS
        ).hex(),
    }
    save_users(users)
    return True
