import os
import sys
import json
import django

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'foundyou_api')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from app.models import CustomUser

JSON_FILE = "app/json_forms/users.json"

def load_users_from_json(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            users = json.load(file)
            return users
    except FileNotFoundError:
        print(f"Error: File {file_path} not found.")
        return []
    except json.JSONDecodeError:
        print(f"Error: File {file_path} contains invalid JSON.")
        return []

def add_users_to_db(users):
    for user_data in users:
        try:
            user = CustomUser(
                username=user_data["username"],
                email=user_data["email"],
                sex=user_data["sex"],
                birthday=user_data["birthday"],
                bio=user_data["bio"],
                passions=user_data["passions"]
            )
            user.set_password(user_data["password"])
            user.save()

            print(f"Added user: {user.username}")
        except Exception as e:
            print(f"Error adding user {user_data.get('username')}: {e}")

if __name__ == "__main__":
    users = load_users_from_json(JSON_FILE)
    # if users:
    #     add_users_to_db(users)
    # else:
    #     print("No users to add.")
