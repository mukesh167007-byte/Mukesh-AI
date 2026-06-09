from users import set_user

OWNER_CODE = "*59*#$5"
JOIN_CODE = "/878@##8"

def handle_join(user_id, code):

    if code == OWNER_CODE:
        set_user(user_id, {"role": "owner"})
        return "Owner logged in 👑"

    if code == JOIN_CODE:
        set_user(user_id, {"step": "relation"})
        return "Select your relation to Mukesh"

    return "Invalid code ❌"