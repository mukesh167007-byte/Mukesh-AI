users = {}

def set_user(user_id, data):
    if user_id not in users:
        users[user_id] = {}
    users[user_id].update(data)

def get_user(user_id):
    return users.get(user_id, {})