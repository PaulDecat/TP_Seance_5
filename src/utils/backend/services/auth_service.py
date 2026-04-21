USERS = {
    "admin": {"password": "admin", "role": "admin"},
    "user": {"password": "user", "role": "user"}
}

def check_login(username, password):
    user = USERS.get(username)
    return user and user["password"] == password
